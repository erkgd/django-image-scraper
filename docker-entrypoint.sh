#!/bin/bash
set -e

# Esperando a que Postgres esté disponible
echo "Esperando a que PostgreSQL esté disponible..."
until nc -z -v -w30 $POSTGRES_HOST $POSTGRES_PORT
do
  echo "Esperando conexión a PostgreSQL ($POSTGRES_HOST:$POSTGRES_PORT)..."
  sleep 2
done
echo "PostgreSQL disponible en $POSTGRES_HOST:$POSTGRES_PORT"

# Realizar migraciones de la base de datos
echo "Aplicando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe - usando valores directos sin expansión de variables
echo "Verificando superusuario..."
SUPERUSER=${DJANGO_SUPERUSER_USERNAME:-admin}
EMAIL=${DJANGO_SUPERUSER_EMAIL:-admin@example.com}
PASSWORD=${DJANGO_SUPERUSER_PASSWORD:-admin}

echo "Intentando crear superusuario: $SUPERUSER"
# Crear un script Python temporal con los valores ya expandidos
cat > /tmp/create_superuser.py << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${SUPERUSER}').exists():
    User.objects.create_superuser('${SUPERUSER}', '${EMAIL}', '${PASSWORD}')
    print('Superusuario ${SUPERUSER} creado.')
else:
    print('Superusuario ${SUPERUSER} ya existe.')
EOF

# Ejecutar el script temporal
python manage.py shell < /tmp/create_superuser.py
rm /tmp/create_superuser.py

# Iniciar Gunicorn con variables de entorno
echo "Iniciando Gunicorn..."
WORKERS=${GUNICORN_WORKERS:-4}
WORKER_CLASS=${GUNICORN_WORKER_CLASS:-gthread}
THREADS=${GUNICORN_THREADS:-2}
TIMEOUT=${GUNICORN_TIMEOUT:-120}

echo "Configuración: workers=$WORKERS, worker_class=$WORKER_CLASS, threads=$THREADS, timeout=$TIMEOUT"
exec gunicorn image_scraper.wsgi:application --bind 0.0.0.0:8000 \
    --workers $WORKERS \
    --worker-class $WORKER_CLASS \
    --threads $THREADS \
    --timeout $TIMEOUT
