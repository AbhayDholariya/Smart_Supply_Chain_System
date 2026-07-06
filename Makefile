.PHONY: up down build migrate createsuperuser logs shell lint

## Start all services (dev mode)
up:
	docker compose up --build

## Stop all services
down:
	docker compose down

## Build images without starting
build:
	docker compose build

## Run Django migrations
migrate:
	docker compose exec backend python manage.py migrate

## Create a Django superuser
createsuperuser:
	docker compose exec backend python manage.py createsuperuser

## Tail logs for all services
logs:
	docker compose logs -f

## Open a Django shell
shell:
	docker compose exec backend python manage.py shell

## Run backend linting
lint:
	docker compose exec backend flake8 apps/ config/
