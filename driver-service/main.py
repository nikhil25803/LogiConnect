from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from config.internal import close_internal_client, start_internal_client
from config.celery import background_task
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from config.cache import RedisCache
from routes.driver_routes import driver_route
from routes.internal_routes import internal_router
from datetime import datetime, timezone

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_internal_client()
    yield
    await close_internal_client()


app = FastAPI(
    title="LogiConnect Driver Service",
    description="Driver authentication, profiles, and booking workflow APIs.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(driver_route)
app.include_router(internal_router)

cache = RedisCache()


@app.get("/head")
async def head(db: AsyncSession = Depends(get_db)):
    """
    To check DB, Cache and Background Task
    """
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
        "X-Ping-Status": "Driver Server is up and running",
        "X-Timestamp": current_timestamp,
    }
    return headers
