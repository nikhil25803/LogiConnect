import os
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select

from config.internal import internal_request
from models.models import Driver
from utils.hashing import get_password_hash, verify_password
from utils.token import create_access_token, verification


def public_driver(driver):
    return {
        "driverid": driver.driverid, "name": driver.name, "email": driver.email,
        "mobile": driver.mobile, "country": driver.country, "state": driver.state,
        "current_latitude": driver.current_latitude, "current_longitude": driver.current_longitude,
        "regions_available": driver.regions_available, "availability": driver.availability,
        "role": driver.role, "country_code": driver.country_code,
    }


class DriverController:
    def __init__(self, db):
        self.db = db
        self.user_url = os.getenv("USER_SERVICE_URL", "http://user-service:3001")
        self.admin_url = os.getenv("ADMIN_SERVICE_URL", "http://admin-service:3003")

    async def create_driver(self, data: dict):
        existing = (await self.db.execute(select(Driver).filter(Driver.email == data["email"]))).scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="Driver with the given email is already registered")
        driver = Driver(
            driverid=str(uuid4()), name=data.get("name"), email=data.get("email"),
            password=get_password_hash(data["password"]), country=data.get("country"),
            country_code=data.get("country_code"), state=data.get("state"), mobile=data.get("mobile"),
            current_latitude=data.get("current_latitude"), current_longitude=data.get("current_longitude"),
            regions_available=data.get("regions_available", []), availability=data.get("availability", True),
            role="driver",
        )
        self.db.add(driver)
        await self.db.commit()
        await self.db.refresh(driver)
        return public_driver(driver)

    async def login_driver(self, email, password: str):
        driver = (await self.db.execute(select(Driver).filter(Driver.email == email))).scalars().first()
        if not driver or not verify_password(password, driver.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = create_access_token(data={
            "driverid": driver.driverid, "email": driver.email,
            "name": driver.name, "role": driver.role.lower(),
        })
        return {"access_token": token, "token_type": "bearer", "driverid": driver.driverid}

    async def get_driver_profile(self, driver_id: str, authorization: str):
        driver = (await self.db.execute(select(Driver).filter(Driver.driverid == driver_id))).scalars().first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        verification(token=authorization.split(" ", 1)[1], role="driver", entity_id=driver_id)
        return {key: public_driver(driver)[key] for key in ("name", "email", "country", "state", "mobile", "role")}

    async def get_driver_bookings(self, driver_id: str, booking_filter: str = "All"):
        driver = (await self.db.execute(select(Driver).filter(Driver.driverid == driver_id))).scalars().first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        bookings = await internal_request(
            "GET", self.user_url, "/internal/bookings",
            params={"driver_id": driver_id, "request_status": booking_filter},
        )
        accepted_fields = {
            "booking_id", "pickup_location", "pickup_latitude", "pickup_longitude",
            "drop_location", "drop_latitude", "drop_longitude", "distance_to_cover",
            "estimated_delivery_time", "total_price", "delivery_status", "order_status", "request_status",
        }
        basic_fields = {"booking_id", "pickup_location", "drop_location", "distance_to_cover", "request_status"}
        all_fields = basic_fields | {"delivery_status", "order_status"}
        fields = accepted_fields if booking_filter == "Accepted" else all_fields if booking_filter == "All" else basic_fields
        return [{key: value for key, value in booking.items() if key in fields} for booking in bookings]

    async def update_booking_status(self, driver_id: str, booking_id: str, status_type: str, update_to: str):
        driver = (await self.db.execute(select(Driver).filter(Driver.driverid == driver_id))).scalars().first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        booking = await internal_request(
            "PATCH", self.user_url, f"/internal/bookings/{booking_id}/driver-status",
            json={"driver_id": driver_id, "status_type": status_type, "update_to": update_to},
        )
        if status_type == "Request" and update_to == "Accepted":
            driver.availability = False
            await self.db.commit()
            await internal_request("PATCH", self.admin_url, f"/internal/vehicles/{booking['vehicle_id']}", json={
                "is_available": False, "active_status": True,
            })
        elif status_type == "Delivery" and update_to == "Delivered":
            driver.current_latitude = booking["drop_latitude"]
            driver.current_longitude = booking["drop_longitude"]
            await self.db.commit()
            await internal_request("PATCH", self.admin_url, f"/internal/vehicles/{booking['vehicle_id']}", json={
                "current_latitude": booking["drop_latitude"], "current_longitude": booking["drop_longitude"],
                "is_available": True, "active_status": False,
            })
        return {
            "booking_id": booking["booking_id"], "request_status": booking["request_status"],
            "delivery_status": booking["delivery_status"],
        }
