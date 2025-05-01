.PHONY: help build up down logs ps shell makemigrations migrate collectstatic superuser test clean

# Variables
COMPOSE = docker-compose

help:
	@echo "Comandos disponibles:"
	@echo "  build         : Construye todos los contenedores"
	@echo "  up            : Inicia todos los servicios (en segundo plano)"
	@echo "  down          : Detiene todos los servicios"
	@echo "  logs          : Muestra los logs de todos los servicios"
	@echo "  ps            : Lista los contenedores en ejecución"
	@echo "  shell         : Abre un shell en el contenedor web"
	@echo "  makemigrations: Crea nuevas migraciones"
	@echo "  migrate       : Aplica las migraciones"
	@echo "  collectstatic : Recopila archivos estáticos"
	@echo "  superuser     : Crea un superusuario"
	@echo "  test          : Ejecuta las pruebas"
	@echo "  clean         : Limpia todos los contenedores y volúmenes"

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

ps:
	$(COMPOSE) ps

shell:
	$(COMPOSE) exec web /bin/bash

makemigrations:
	$(COMPOSE) exec web python manage.py makemigrations

migrate:
	$(COMPOSE) exec web python manage.py migrate

collectstatic:
	$(COMPOSE) exec web python manage.py collectstatic --noinput

superuser:
	$(COMPOSE) exec web python manage.py createsuperuser

test:
	$(COMPOSE) exec web python manage.py test

clean:
	$(COMPOSE) down -v --remove-orphans
