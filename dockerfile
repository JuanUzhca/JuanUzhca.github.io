# Usar una imagen base de Nginx
FROM nginx:latest
# Configurar el directorio de trabajo en el contenedor
WORKDIR /usr/share/nginx/html
# Copiar los archivos del sitio web al directorio de Nginx
COPY . /usr/share/nginx/html
# Exponer el puerto 80 dentro del contenedor
EXPOSE 80
# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
