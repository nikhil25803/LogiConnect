from fastapi import FastAPI, Depends
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from routes.user_route import user_router
from routes.vehicle_route import vehicle_router
from routes.booking_route import booking_router
from datetime import datetime, timezone
from config.cache import RedisCache
from config.celery import background_task
from celery import Celery, signature, shared_task


app = FastAPI()


# Initialise cache and backgroundtask
cache = RedisCache()

# # Add event-handler
# app.add_event_handler("startup", init_cache)
# app.add_event_handler("shutdown", clear_cache)


# Include Routers
app.include_router(user_router)
app.include_router(vehicle_router)
app.include_router(booking_router)


@app.get("/head")
async def head(db: AsyncSession = Depends(get_db)):

    cached_result = await cache.get_cache("redis")
    if cached_result:
        print("From Cache")
        return cached_result
    else:
        current_timestamp = datetime.now(timezone.utc).isoformat()

        headers = {
            "X-Ping-Status": "Server is up and running",
            "X-Timestamp": current_timestamp,
        }

        response = {"timestamp": current_timestamp, "headers": headers}
        print("Adding to cache")

        background_task()

        await cache.set_cache(key="redis", value=response)

    return response


@app.head("/ping")
async def ping(db: AsyncSession = Depends(get_db)):
    current_timestamp = datetime.now(timezone.utc).isoformat()

    headers = {
        "X-Ping-Status": "Server is up and running",
        "X-Timestamp": current_timestamp,
    }
    return headers
