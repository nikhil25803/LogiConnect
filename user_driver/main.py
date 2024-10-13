from fastapi import FastAPI
from datetime import datetime, timezone
from models import models
from config.database import engine
from routes.customer_routes import user_router, driver_router

app = FastAPI()


@app.head("/ping")
async def ping():
    current_timestamp = datetime.now(timezone.utc).isoformat()

    headers = {
        "X-Ping-Status": "Server is up and running",
        "X-Timestamp": current_timestamp,
    }
    return headers


# Include routes
app.include_router(user_router)
app.include_router(driver_router)

models.Base.metadata.create_all(engine)
