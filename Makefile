.PHONY: run-postgres clean run-redis

# PostgreSQL configuration
PG_USER := logiconnect
PG_PASSWORD := logiconnect@12345
PG_DB := logiconnectDB

# # Redis configuration
# REDIS_PORT := 6379

# # RedisInsight configuration
# REDIS_INSIGHT_PORT := 8001

run-redis:
	docker run -d \
		--name redis-stack \
		-p 6379:6379 \
		-p 8001:8001 \
		redis/redis-stack:latest


# Run PostgreSQL instance
run-postgres:
	docker run --name my-postgres -d \
		-e POSTGRES_USER=$(PG_USER) \
		-e POSTGRES_PASSWORD=$(PG_PASSWORD) \
		-e POSTGRES_DB=$(PG_DB) \
		-p 5432:5432 \
		postgres:latest

# Run Redis instance
# run-redis:
# 	docker run --name my-redis -d -p $(REDIS_PORT):6379 redis:latest

# Run RedisInsight UI
# run-redis-ui:
# 	docker run --name redisinsight -d \
# 		-p $(REDIS_INSIGHT_PORT):8001 \
# 		--link my-redis:redis \
# 		redis/redisinsight

# Run all services
run-all: run-postgres run-redis

# Clean up
clean:
	docker stop my-postgres redis-stack  || true
	docker rm my-postgres redis-stack  || true
