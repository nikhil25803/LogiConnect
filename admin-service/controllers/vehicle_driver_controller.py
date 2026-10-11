import os
import uuid

from fastapi import HTTPException
from sqlalchemy import func, select

from config.internal import internal_request
from models.models import Vehicle
from utils.token import verification


class VehicleDriverController:
    def __init__(self, db):
        self.db = db
        self.admin_email = os.getenv("ADMIN_EMAIL")
        self.driver_url = os.getenv("DRIVER_SERVICE_URL", "http://driver-service:3002")

    async def add_vehicle(self, vehicle_data, token: str):
        verification(token=token, role="admin", entity_id=self.admin_email)
        existing = (await self.db.execute(select(Vehicle).where(
            Vehicle.registration_number == vehicle_data.registration_number
        ))).scalars().first()
        if existing:
            raise HTTPException(status_code=400, detail="Vehicle with this registration number already exists")
        vehicle = Vehicle(vehicleid=str(uuid.uuid4()), **vehicle_data.model_dump())
        self.db.add(vehicle)
        await self.db.commit()
        await self.db.refresh(vehicle)
        return vehicle

    async def get_all_vehicles(self, token: str, limit: int = 10, offset: int = 0):
        verification(token=token, role="admin", entity_id=self.admin_email)
        total = (await self.db.execute(select(func.count(Vehicle.id)))).scalar()
        vehicles = (await self.db.execute(select(Vehicle).limit(limit).offset(offset))).scalars().all()
        return {"total_count": total, "total_pages": (total + limit - 1) // limit,
                "current_page": offset // limit + 1, "next_page": offset + limit < total,
                "prev_page": offset > 0, "vehicles": vehicles}

    async def add_driver(self, driver_data, token: str):
        verification(token=token, role="admin", entity_id=self.admin_email)
        data = driver_data.model_dump(exclude={"driverid", "role"})
        return await internal_request("POST", self.driver_url, "/internal/drivers", json=data)

    async def get_all_drivers(self, token: str, limit: int = 10, offset: int = 0):
        verification(token=token, role="admin", entity_id=self.admin_email)
        return await internal_request(
            "GET", self.driver_url, "/internal/drivers", params={"limit": limit, "offset": offset}
        )
