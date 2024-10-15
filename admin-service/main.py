from fastapi import FastAPI, Depends
from config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from routes.admin_route import admin_route
from routes.vehicle_route import vehicle_route
from datetime import datetime, timezone

app = FastAPI()

app.include_router(admin_route)
app.include_router(vehicle_route)


@app.head("/ping")
async def ping(db: AsyncSession = Depends(get_db)):
    current_timestamp = datetime.now(timezone.utc).isoformat()

    headers = {
        "X-Ping-Status": "Admin Server is up and running",
        "X-Timestamp": current_timestamp,
    }
    return headers
