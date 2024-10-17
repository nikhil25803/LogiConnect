from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from uuid import uuid4
from utils.hashing import get_password_hash, verify_password
from utils.token import create_access_token, verification
from models.models import Driver, BookingRequest, Vehicle
from pydantic import EmailStr
from typing import Literal


class DriverController:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_driver_and_vehicle_availability(
        self, driver_id: str, vehicle_id: str, available: bool
    ):
        driver_query = select(Driver).filter(Driver.driverid == driver_id)
        driver_result = await self.db.execute(driver_query)
        driver = driver_result.scalars().first()

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )

        driver.availability = available
        await self.db.commit()
        await self.db.refresh(driver)

        vehicle_query = select(Vehicle).filter(Vehicle.vehicleid == vehicle_id)
        vehicle_result = await self.db.execute(vehicle_query)
        vehicle = vehicle_result.scalars().first()

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found",
            )

        vehicle.is_available = available
        vehicle.active_status = not available
        await self.db.commit()
        await self.db.refresh(vehicle)

    async def update_driver_and_vehicle_location(
        self,
        driver_id: str,
        vehicle_id: str,
        drop_latitude: float,
        drop_longitude: float,
    ):

        driver_query = select(Driver).filter(Driver.driverid == driver_id)
        driver_result = await self.db.execute(driver_query)
        driver = driver_result.scalars().first()

        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )

        driver.current_latitude = drop_latitude
        driver.current_longitude = drop_longitude
        await self.db.commit()
        await self.db.refresh(driver)

        vehicle_query = select(Vehicle).filter(Vehicle.vehicleid == vehicle_id)
        vehicle_result = await self.db.execute(vehicle_query)
        vehicle = vehicle_result.scalars().first()

        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found",
            )

        vehicle.current_latitude = drop_latitude
        vehicle.current_longitude = drop_longitude
        await self.db.commit()
        await self.db.refresh(vehicle)

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
        booking_filter: str = Literal[
            "All", "Pending", "Accepted", "Rejected", "Completed"
        ],
    ):
        driver_query = select(Driver).filter(Driver.driverid == driver_id)
        result = await self.db.execute(driver_query)
        driver = result.scalars().first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )

        if booking_filter == "Pending":
            booking_query = select(
                BookingRequest.booking_id,
                BookingRequest.pickup_location,
                BookingRequest.drop_location,
                BookingRequest.distance_to_cover,
                BookingRequest.request_status,
            ).filter(
                BookingRequest.driver_id == driver_id,
                BookingRequest.request_status == "Pending",
            )
        elif booking_filter == "Accepted":
            booking_query = select(
                BookingRequest.booking_id,
                BookingRequest.pickup_location,
                BookingRequest.pickup_latitude,
                BookingRequest.pickup_longitude,
                BookingRequest.drop_location,
                BookingRequest.drop_latitude,
                BookingRequest.drop_longitude,
                BookingRequest.distance_to_cover,
                BookingRequest.estimated_delivery_time,
                BookingRequest.total_price,
                BookingRequest.delivery_status,
                BookingRequest.order_status,
                BookingRequest.request_status,
            ).filter(
                BookingRequest.driver_id == driver_id,
                BookingRequest.request_status == "Accepted",
            )
        elif booking_filter == "Rejected":
            booking_query = select(
                BookingRequest.booking_id,
                BookingRequest.pickup_location,
                BookingRequest.drop_location,
                BookingRequest.distance_to_cover,
                BookingRequest.request_status,
            ).filter(
                BookingRequest.driver_id == driver_id,
                BookingRequest.request_status == "Rejected",
            )
        elif booking_filter == "Completed":
            booking_query = select(
                BookingRequest.booking_id,
                BookingRequest.pickup_location,
                BookingRequest.pickup_latitude,
                BookingRequest.pickup_longitude,
                BookingRequest.drop_location,
                BookingRequest.drop_latitude,
                BookingRequest.drop_longitude,
                BookingRequest.distance_to_cover,
                BookingRequest.estimated_delivery_time,
                BookingRequest.total_price,
                BookingRequest.request_status,
            ).filter(
                BookingRequest.driver_id == driver_id,
                BookingRequest.request_status == "Rejected",
            )
        else:
            booking_query = select(
                BookingRequest.booking_id,
                BookingRequest.pickup_location,
                BookingRequest.drop_location,
                BookingRequest.distance_to_cover,
                BookingRequest.delivery_status,
                BookingRequest.order_status,
                BookingRequest.request_status,
            ).filter(
                BookingRequest.driver_id == driver_id,
            )

        result = await self.db.execute(booking_query)
        bookings = result.fetchall()

        if not bookings:
            raise HTTPException(status_code=404, detail="No bookings found")

        formatted_bookings = []
        for booking in bookings:
            formatted_booking = {}

            if hasattr(booking, "pickup_location"):
                formatted_booking["pickup_location"] = booking.pickup_location
            if hasattr(booking, "pickup_latitude"):
                formatted_booking["pickup_latitude"] = booking.pickup_latitude
            if hasattr(booking, "pickup_longitude"):
                formatted_booking["pickup_longitude"] = booking.pickup_longitude
            if hasattr(booking, "drop_location"):
                formatted_booking["drop_location"] = booking.drop_location
            if hasattr(booking, "drop_latitude"):
                formatted_booking["drop_latitude"] = booking.drop_latitude
            if hasattr(booking, "drop_longitude"):
                formatted_booking["drop_longitude"] = booking.drop_longitude
            if hasattr(booking, "distance_to_cover"):
                formatted_booking["distance_to_cover"] = booking.distance_to_cover
            if hasattr(booking, "estimated_delivery_time"):
                formatted_booking["estimated_delivery_time"] = (
                    booking.estimated_delivery_time
                )
            if hasattr(booking, "total_price"):
                formatted_booking["total_price"] = booking.total_price
            if hasattr(booking, "delivery_status"):
                formatted_booking["delivery_status"] = booking.delivery_status
            if hasattr(booking, "order_status"):
                formatted_booking["order_status"] = booking.order_status
            if hasattr(booking, "request_status"):
                formatted_booking["request_status"] = booking.request_status
            if hasattr(booking, "booking_id"):
                formatted_booking["booking_id"] = booking.booking_id

            formatted_bookings.append(formatted_booking)

        return formatted_bookings

    async def update_booking_status(
        self,
        driver_id: str,
        booking_id: str,
        status_type: str = Literal["Request", "Delivery"],
        update_to: str = Literal[
            "Accepted",
            "Rejected",
            "Completed",
            "In Transit",
            "Out for Delivery",
            "Delivered",
            "Canceled",
        ],
    ):
        driver_query = select(Driver).filter(Driver.driverid == driver_id)
        driver_query_result = await self.db.execute(driver_query)
        driver = driver_query_result.scalars().first()
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )

        booking_query = select(BookingRequest).filter(
            BookingRequest.booking_id == booking_id,
            BookingRequest.driver_id == driver_id,
        )
        booking_query_result = await self.db.execute(booking_query)
        booking = booking_query_result.scalars().first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found or invalid.",
            )

        if status_type == "Request":
            if update_to not in ["Accepted", "Rejected", "Completed"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request status update.",
                )

            if booking.request_status == "Completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update a completed request.",
                )

            booking.request_status = update_to
            await self.db.commit()
            await self.db.refresh(booking)

            if update_to == "Accepted":
                await self.update_driver_and_vehicle_availability(
                    driver_id=driver_id, vehicle_id=booking.vehicle_id, available=False
                )

        elif status_type == "Delivery":
            if update_to not in [
                "In Transit",
                "Out for Delivery",
                "Delivered",
                "Canceled",
            ]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid delivery status update.",
                )

            if (
                booking.delivery_status == "Delivered"
                or booking.delivery_status == "Canceled"
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot update a {booking.delivery_status} delivery.",
                )

            booking.delivery_status = update_to
            await self.db.commit()
            await self.db.refresh(booking)

            if update_to == "Delivered":
                await self.update_driver_and_vehicle_location(
                    driver_id=driver_id,
                    vehicle_id=booking.vehicle_id,
                    drop_latitude=booking.drop_latitude,
                    drop_longitude=booking.drop_longitude,
                )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status type. Use 'Request' or 'Delivery'.",
            )

        return {
            "booking_id": booking.booking_id,
            "request_status": booking.request_status,
            "delivery_status": booking.delivery_status,
        }
