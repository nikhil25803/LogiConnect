from fastapi import FastAPI, Depends
from models.schema import UserBase
from config.database import get_db
from models.models import User
from sqlalchemy.orm import Session


app = FastAPI()


@app.post("/user")
async def index(user: UserBase, db: Session = Depends(get_db)):
    db_user = User(name=user.name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.get("/user")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users}
