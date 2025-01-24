from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from controllers.funciones_home import connectionBD

# Importando conexión a BD
from controllers.funciones_home import *

@app.context_processor
def utility_processor():
    return dict(max=max)
@app.context_processor
def utility_processor():
    return dict(max=max, min=min)


@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_areas.html', areas=lista_areasBD(), dataLogin=dataLoginSesion())
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=lista_usuariosBD(), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles=lista_rolesBD())
    else:
        return redirect(url_for('inicioCpanel'))

# Ruta especificada para eliminar un usuario
@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))

@app.route('/borrar-area/<string:id_area>/', methods=['GET'])
def borrarArea(id_area):
    resp = eliminarArea(id_area)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_areas'))
    else:
        flash('Hay usuarios que pertenecen a esta área', 'error')
        return redirect(url_for('lista_areas'))

@app.route("/descargar-informe-accesos/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route("/reporte-accesos", methods=['GET'])
def reporteAccesos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        return render_template('public/perfil/reportes.html', reportes=dataReportes(), lastAccess=lastAccessBD(userData.get('cedula')), dataLogin=dataLoginSesion())

@app.route("/interfaz-clave", methods=['GET','POST'])
def claves():
    return render_template('public/usuarios/generar_clave.html', dataLogin=dataLoginSesion())

@app.route('/generar-y-guardar-clave/<string:id>', methods=['GET','POST'])
def generar_clave(id):
    print(id)
    clave_generada = crearClave()  # Llama a la función para generar la clave
    guardarClaveAuditoria(clave_generada, id)
    return clave_generada

# CREAR AREA
@app.route('/crear-area', methods=['GET','POST'])
def crearArea():
    if request.method == 'POST':
        area_name = request.form['nombre_area']  # Asumiendo que 'nombre_area' es el nombre del campo en el formulario
        resultado_insert = guardarArea(area_name)
        if resultado_insert:
            # Éxito al guardar el área
            flash('El Area fue creada correctamente', 'success')
            return redirect(url_for('lista_areas'))
        else:
            # Manejar error al guardar el área
            return "Hubo un error al guardar el área."
    return render_template('public/usuarios/lista_areas')

# ACTUALIZAR AREA
@app.route('/actualizar-area', methods=['POST'])
def updateArea():
    if request.method == 'POST':
        nombre_area = request.form['nombre_area']  # Asumiendo que 'nuevo_nombre' es el nombre del campo en el formulario
        id_area = request.form['id_area']
        resultado_update = actualizarArea(id_area, nombre_area)
        if resultado_update:
           # Éxito al actualizar el área
            flash('El área fue actualizada correctamente', 'success')
            return redirect(url_for('lista_areas'))
        else:
            # Manejar error al actualizar el área
            return "Hubo un error al actualizar el área."

    return redirect(url_for('lista_areas'))

def obtenerDatosTemperatura(id_ubicacion=None, pagina=1, registros_por_pagina=20):
    try:
        # Establecer conexión a la base de datos
        connection = connectionBD()
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Calcular el límite y el desplazamiento para la paginación
            offset = (pagina - 1) * registros_por_pagina
            
            # Consulta SQL con paginación
            if id_ubicacion:
                query = """
                    SELECT t.id_temperatura, t.fecha, t.temperatura, u.nombre_ubicacion 
                    FROM temperatura t 
                    INNER JOIN ubicaciones u ON t.id_ubicacion = u.id_ubicacion 
                    WHERE t.id_ubicacion = %s 
                    ORDER BY t.fecha DESC 
                    LIMIT %s OFFSET %s;
                """
                cursor.execute(query, (id_ubicacion, registros_por_pagina, offset))
            else:
                query = """
                    SELECT t.id_temperatura, t.fecha, t.temperatura, u.nombre_ubicacion 
                    FROM temperatura t 
                    INNER JOIN ubicaciones u ON t.id_ubicacion = u.id_ubicacion 
                    ORDER BY t.fecha DESC 
                    LIMIT %s OFFSET %s;
                """
                cursor.execute(query, (registros_por_pagina, offset))
            
            # Obtener los resultados
            datos = cursor.fetchall()
            
            # Obtener el total de registros para calcular las páginas
            if id_ubicacion:
                cursor.execute("SELECT COUNT(*) AS total FROM temperatura WHERE id_ubicacion = %s", (id_ubicacion,))
            else:
                cursor.execute("SELECT COUNT(*) AS total FROM temperatura")
            total_registros = cursor.fetchone()['total']
            
            total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina  # Redondeo hacia arriba
            
            cursor.close()
            connection.close()
            
            return datos, total_paginas
    
    except mysql.connector.Error as error:
        print(f"Error al obtener los datos de temperatura: {error}")
        return [], 0



def obtenerTodasUbicaciones():
    try:
        # Establecer conexión a la base de datos
        connection = connectionBD()
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)  # Para obtener los resultados como diccionario
            
            # Consulta SQL para obtener todas las ubicaciones
            query = "SELECT id_ubicacion, nombre_ubicacion FROM ubicaciones ORDER BY nombre_ubicacion;"
            cursor.execute(query)
            
            # Obtener los resultados
            ubicaciones = cursor.fetchall()
            cursor.close()  # Cerrar cursor
            connection.close()  # Cerrar conexión
            
            return ubicaciones
    
    except mysql.connector.Error as error:
        print(f"Error al obtener las ubicaciones: {error}")
        return []

# RUTA PARA MOSTRAR TEMPERATURA
@app.route("/temperatura", methods=['GET'])
def temperatura():
    if 'conectado' in session:
        # Parámetros de ubicación y página
        id_ubicacion = request.args.get('id_ubicacion', type=int)
        pagina = request.args.get('pagina', 1, type=int)

        # Obtener los datos de temperatura y el total de páginas
        datos_temperatura, total_paginas = obtenerDatosTemperatura(id_ubicacion=id_ubicacion, pagina=pagina)
        
        # Obtener todas las ubicaciones para el filtro
        ubicaciones = obtenerTodasUbicaciones()

        return render_template(
            'public/temperatura.html',
            datos_temperatura=datos_temperatura,
            ubicaciones=ubicaciones,
            id_ubicacion_seleccionada=id_ubicacion,
            pagina_actual=pagina,
            total_paginas=total_paginas,
            dataLogin=dataLoginSesion()
        )
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))




