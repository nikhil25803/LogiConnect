from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from utils.token import create_access_token
import os
from dotenv import load_dotenv

load_dotenv()


class AdminController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.admin_email = os.getenv("ADMIN_EMAIL")
        self.admin_password = os.getenv("ADMIN_PASSWORD")

    async def login_admin(self, email: str, password: str):
        if email != self.admin_email or password != self.admin_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid admin credentials",
            )

        access_token = create_access_token(
            data={"email": self.admin_email, "role": "admin"}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": "admin",
        }
