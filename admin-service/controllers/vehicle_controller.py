from models.schema import AddVehicle
from fastapi import HTTPException, status
from models.schema import UpdateVehicle
from sqlalchemy.ext.asyncio import AsyncSession
from utils.token import verification
from sqlalchemy.future import select
from models.models import Vehicle
import uuid
import os
from dotenv import load_dotenv

load_dotenv()


class VehicleController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.admin_email = os.getenv("ADMIN_EMAIL")

    async def add_vehicle(self, vehicle_data: AddVehicle, token: str):
        try:
            verification(token=token, role="admin", entity_id=self.admin_email)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        existing_vehicle = await self.db.execute(
            select(Vehicle).where(
                Vehicle.registration_number == vehicle_data.registration_number
            )
        )
        if existing_vehicle.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this registration number already exists",
            )

        new_vehicle = Vehicle(
            vehicleid=str(uuid.uuid4()),
            model_name=vehicle_data.model_name,
            capacity_in_kg=vehicle_data.capacity_in_kg,
            registration_number=vehicle_data.registration_number,
            current_latitude=vehicle_data.current_latitude,
            current_longitude=vehicle_data.current_longitude,
            is_available=vehicle_data.is_available,
            active_status=vehicle_data.active_status,
            fuel_type=vehicle_data.fuel_type,
        )

        self.db.add(new_vehicle)
        await self.db.commit()
        await self.db.refresh(new_vehicle)

        return new_vehicle

    async def update_vehicle(
        self, vehicleid: str, vehicle_data: UpdateVehicle, token: str
    ):
        try:
            verification(token=token, role="admin", entity_id=self.admin_email)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        vehicle = await self.db.execute(
            select(Vehicle).where(Vehicle.vehicleid == vehicleid)
        )
        existing_vehicle = vehicle.scalars().first()

        if not existing_vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
            )

        for key, value in vehicle_data.dict(exclude_unset=True).items():
            setattr(existing_vehicle, key, value)

        await self.db.commit()
        await self.db.refresh(existing_vehicle)

        return existing_vehicle

    async def get_all_vehicles(self, token: str):
        try:
            verification(token=token, role="admin", entity_id=self.admin_email)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)

        vehicles = await self.db.execute(select(Vehicle))
        return vehicles.scalars().all()
