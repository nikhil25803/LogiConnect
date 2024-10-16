from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from uuid import uuid4
from utils.hashing import get_password_hash, verify_password
from utils.token import create_access_token, verification
from models.models import Driver, BookingRequest, Users
from pydantic import EmailStr
from typing import Literal


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

        new_driver = Driver(
            driverid=entity_id,
            name=data.get("name"),
            email=data.get("email"),
            password=hashed_password,
            country=data.get("country"),
            country_code=data.get("country_code"),
            state=data.get("state"),
            mobile=data.get("mobile"),
            current_latitude=data.get("current_latitude"),
            current_longitude=data.get("current_longitude"),
            regions_available=data.get("regions_available", []),
            availability=data.get("availability", True),
            role="driver",
        )

        self.db.add(new_driver)
        await self.db.commit()
        await self.db.refresh(new_driver)

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

    async def get_driver_bookings(
        self,
        driver_id: str,
        status: str = Literal["all", "pending", "accepted", "rejected"],
    ):
        driver_query = select(Driver).filter(Driver.driverid == driver_id)
        result = await self.db.execute(driver_query)
        driver = result.scalars().first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )

        if status == "pending":
            booking_query = select(
                BookingRequest.distance_from_vehicle,
                BookingRequest.distance_from_pickup_location,
                BookingRequest.pickup_location,
                BookingRequest.drop_location,
                BookingRequest.user_name,
                BookingRequest.user_email,
                BookingRequest.user_mobile,
                BookingRequest.base_price,
                BookingRequest.gst,
                BookingRequest.platform_fee,
                BookingRequest.total_price,
                BookingRequest.request_status,
                BookingRequest.booking_status,
            ).filter(
                BookingRequest.driver_id == driver_id,
                BookingRequest.request_status == "pending",
            )
        elif status == "accepted":
            booking_query = select(
                BookingRequest.distance_from_vehicle,
                BookingRequest.distance_from_pickup_location,
                BookingRequest.pickup_location,
                BookingRequest.drop_location,
                BookingRequest.user_name,
                BookingRequest.user_email,
                BookingRequest.user_mobile,
                BookingRequest.base_price,
                BookingRequest.gst,
                BookingRequest.platform_fee,
                BookingRequest.total_price,
                BookingRequest.request_status,
                BookingRequest.booking_status,
            ).filter(
                BookingRequest.driver_id == driver_id,
                BookingRequest.request_status == "accepted",
            )
        else:
            booking_query = select(
                BookingRequest.distance_from_vehicle,
                BookingRequest.distance_from_pickup_location,
                BookingRequest.pickup_location,
                BookingRequest.drop_location,
                BookingRequest.user_name,
                BookingRequest.user_email,
                BookingRequest.user_mobile,
                BookingRequest.base_price,
                BookingRequest.gst,
                BookingRequest.platform_fee,
                BookingRequest.total_price,
                BookingRequest.request_status,
                BookingRequest.booking_status,
            ).filter(BookingRequest.driver_id == driver_id)

        result = await self.db.execute(booking_query)
        bookings = result.fetchall()

        if not bookings:
            raise HTTPException(status_code=404, detail="No bookings found")

        formatted_bookings = []
        for booking in bookings:
            formatted_bookings.append(
                {
                    "distance_from_vehicle": booking.distance_from_vehicle,
                    "distance_from_pickup_location": booking.distance_from_pickup_location,
                    "pickup_location": booking.pickup_location,
                    "drop_location": booking.drop_location,
                    "user_name": booking.user_name,
                    "user_email": booking.user_email,
                    "user_mobile": booking.user_mobile,
                    "base_price": booking.base_price,
                    "gst": booking.gst,
                    "platform_fee": booking.platform_fee,
                    "total_price": booking.total_price,
                    "request_status": booking.request_status,
                    "booking_status": booking.booking_status,
                }
            )

        return formatted_bookings

    async def request_action(
        self, booking_id: str, driver_id: str, action: Literal["accept", "reject"]
    ):
        driver_query = select(Driver).filter(Driver.driverid == driver_id)
        result = await self.db.execute(driver_query)
        driver = result.scalars().first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )

        booking_query = select(BookingRequest).filter(
            BookingRequest.booking_id == booking_id
        )
        result = await self.db.execute(booking_query)
        booking = result.scalars().first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
            )

        if action == "Accept":
            booking.request_status = "accepted"
            booking.booking_status = "En-Route"
        elif action == "Reject":
            booking.request_status = "rejected"
            booking.booking_status = "Cancelled"

        await self.db.commit()
        await self.db.refresh(booking)

        return {
            "message": f"Booking request status has been updated to {action.lower()}ed successfully",
            "booking_id": booking.booking_id,
            "request_status": booking.request_status,
            "booking_status": booking.booking_status,
        }
