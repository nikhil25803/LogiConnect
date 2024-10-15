from fastapi import FastAPI, Depends
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from routes.driver_routes import driver_route
from datetime import datetime, timezone

app = FastAPI()

app.include_router(driver_route)


@app.head("/ping")
async def ping(db: AsyncSession = Depends(get_db)):
    current_timestamp = datetime.now(timezone.utc).isoformat()

    headers = {
        "X-Ping-Status": "Driver Server is up and running",
        "X-Timestamp": current_timestamp,
    }
    return headers
