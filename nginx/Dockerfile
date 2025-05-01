FROM nginx:1.25-alpine

# Eliminar la configuración predeterminada
RUN rm /etc/nginx/conf.d/default.conf

# Copiar nuestra configuración
COPY conf.d/app.conf /etc/nginx/conf.d/
