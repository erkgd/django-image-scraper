FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear usuario no root para seguridad
RUN addgroup --system app && adduser --system --group app

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        postgresql-client \
        netcat-traditional \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copiar el código del proyecto
COPY --chown=app:app . .

# Crear el script de entrada Docker
COPY --chown=app:app docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Crear directorios para media y static
RUN mkdir -p /app/media /app/static \
    && chown -R app:app /app/media /app/static

# Cambiar al usuario no root
USER app

# Exponer el puerto para Gunicorn
EXPOSE 8000

# Comando predeterminado
CMD ["/usr/local/bin/docker-entrypoint.sh"]
