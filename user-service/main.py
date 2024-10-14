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

# @app.post("/user")
# async def create_user(user: UserBase, db: AsyncSession = Depends(get_db)):
#     db_user = Users(name=user.name)
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user


# @app.get("/user")
# async def get_users(db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(Users))
#     users = result.scalars().all()
#     return {"users": users}
