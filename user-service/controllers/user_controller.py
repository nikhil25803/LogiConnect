from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import uuid4
from utils.hashing import get_password_hash
from fastapi import status
from utils.hashing import verify_password
from utils.token import create_access_token, verification
from models.models import Users, Vehicle
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession


class UserController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: dict):
        existing_user = await self.db.execute(
            select(Users).filter(Users.email == data["email"])
        )
        if existing_user.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered",
            )

        entity_id = str(uuid4())
        hashed_password = get_password_hash(data["password"])

        new_user = Users(
            userid=entity_id,
            name=data.get("name"),
            email=data.get("email"),
            password=hashed_password,
            country=data.get("country"),
            country_code=data.get("country_code"),
            role="User",
            state=data.get("state"),
            phone_number=data.get("phone_number"),
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return {"message": "User onboarded successfully"}

    async def login_user(self, email: EmailStr, password: str):
        result = await self.db.execute(select(Users).filter(Users.email == email))
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid credentials",
            )

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password",
            )

        access_token = create_access_token(
            data={
                "userid": user.userid,
                "email": user.email,
                "name": user.name,
                "role": user.role,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "userid": user.userid,
        }

    async def get_user_profile(self, user_id: str, authorization: str):
        query = select(Users).filter(Users.userid == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        verification(token=authorization.split(" ")[1], role="user", entity_id=user_id)

        return {
            "name": user.name,
            "email": user.email,
            "country": user.country,
            "state": user.state,
            "phone_number": user.phone_number,
            "role": user.role,
        }

    def __del__(self):
        pass
