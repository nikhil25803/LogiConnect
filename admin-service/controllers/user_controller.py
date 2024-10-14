from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import uuid4
from utils.hashing import get_password_hash
from fastapi import status
from utils.hashing import verify_password
from utils.token import create_access_token, verification
from models.models import Users
from pydantic import EmailStr


class UserController:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, data: dict):
        existing_user = (
            self.db.query(Users).filter(Users.email == data["email"]).first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="User already registered")

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
        self.db.commit()
        self.db.refresh(new_user)

        return {"message": "User onboarded successfully"}

    def login_user(self, email: EmailStr, password: str):
        user = self.db.query(Users).filter(Users.email == email).first()

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

    def get_user_profile(self, user_id: str, authorization: str):
        user = self.db.query(Users).filter(Users.userid == user_id).first()

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

    def update_user(self, user_id: str, authorization: str, data: dict):
        user = self.db.query(Users).filter(Users.userid == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        verification(token=authorization.split(" ")[1], role="user", entity_id=user_id)

        for key, value in data.items():
            if value is not None:
                setattr(user, key, value)

        self.db.commit()
        self.db.refresh(user)

        return {"message": "User data updated successfully"}

    def __del__(self):
        pass
