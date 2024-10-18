.PHONY: run-postgres clean run-redis 

PG_USER := logiconnect
PG_PASSWORD := logiconnect@12345
PG_DB := logiconnectDB


run-redis:
	docker run -d \
		--name redis-stack \
		-p 6379:6379 \
		-p 8001:8001 \
		redis/redis-stack:latest

run-postgres:
	docker run --name my-postgres -d \
		-e POSTGRES_USER=$(PG_USER) \
		-e POSTGRES_PASSWORD=$(PG_PASSWORD) \
		-e POSTGRES_DB=$(PG_DB) \
		-p 5432:5432 \
		postgres:latest

# Run all services
run-all: run-postgres run-redis

# Clean up
clean:
	docker stop my-postgres redis-stack run-services  || true
	docker rm my-postgres redis-stack run-services  || true

# DOcker compose run and clean services
.PHONY: run-services
run-services:
	docker-compose up --build

.PHONY: clean-services
clean-services:
	docker-compose down