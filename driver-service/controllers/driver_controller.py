from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from uuid import uuid4
from utils.hashing import get_password_hash, verify_password
from utils.token import create_access_token, verification
from models.models import Driver
from pydantic import EmailStr


class DriverController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_driver(self, data: dict):
        existing_user_query = select(Driver).filter(Driver.email == data["email"])
        result = await self.db.execute(existing_user_query)
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver with the given email is already registered",
            )

        entity_id = str(uuid4())
        hashed_password = get_password_hash(data["password"])

        new_user = Driver(
            driverid=entity_id,
            name=data.get("name"),
            email=data.get("email"),
            password=hashed_password,
            country=data.get("country"),
            country_code=data.get("country_code"),
            role="driver",
            state=data.get("state"),
            mobile=data.get("mobile"),
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        return {"message": "Driver onboarded successfully"}

    async def login_driver(self, email: EmailStr, password: str):
        query = select(Driver).filter(Driver.email == email)
        result = await self.db.execute(query)
        driver = result.scalars().first()

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid credentials",
            )

        if not verify_password(password, driver.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid password",
            )

        access_token = create_access_token(
            data={
                "driverid": driver.driverid,
                "email": driver.email,
                "name": driver.name,
                "role": driver.role,
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "driverid": driver.driverid,
        }

    async def get_driver_profile(self, driver_id: str, authorization: str):
        query = select(Driver).filter(Driver.driverid == driver_id)
        result = await self.db.execute(query)
        driver = result.scalars().first()

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )

        verification(
            token=authorization.split(" ")[1], role="driver", entity_id=driver_id
        )

        return {
            "name": driver.name,
            "email": driver.email,
            "country": driver.country,
            "state": driver.state,
            "mobile": driver.mobile,
            "role": driver.role,
        }
