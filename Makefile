.PHONY: setup start stop test docker-build config

setup:
	cp -n .env.example .env || true

start:
	docker compose up --build

stop:
	docker compose down

test:
	python3 -m pytest user-service/tests
	python3 -m pytest driver-service/tests
	python3 -m pytest admin-service/tests
	python3 -m pytest api-gateway/tests

docker-build:
	docker compose build

config:
	docker compose config --quiet
