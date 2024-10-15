from fastapi import FastAPI, Depends
from config.database import get_db
from models.models import Users
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from routes.user_route import user_router
from datetime import datetime, timezone

app = FastAPI()

app.include_router(user_router)

@app.head("/ping")
async def ping(db: AsyncSession = Depends(get_db)):
    current_timestamp = datetime.now(timezone.utc).isoformat()

    headers = {
        "X-Ping-Status": "Server is up and running",
        "X-Timestamp": current_timestamp,
    }
    return headers

