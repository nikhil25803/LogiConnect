.PHONY: setup start stop migrate fresh-start test smoke docker-build config

setup:
	cp -n .env.example .env || true

start:
	docker compose up --build

stop:
	docker compose down

migrate:
	docker compose run --build --rm user-migrate
	docker compose run --build --rm driver-migrate
	docker compose run --build --rm admin-migrate

fresh-start:
	docker compose down --volumes --remove-orphans
	docker compose up --build

test:
	python3 -m pytest user-service/tests
	python3 -m pytest driver-service/tests
	python3 -m pytest admin-service/tests
	python3 -m pytest api-gateway/tests

smoke:
	bash scripts/verify-databases.sh
	bash scripts/smoke.sh

docker-build:
	docker compose build

config:
	docker compose config --quiet
