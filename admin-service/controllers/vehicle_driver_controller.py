from models.schema import AddVehicle
from fastapi import HTTPException, status
from models.schema import UpdateVehicle
from sqlalchemy.ext.asyncio import AsyncSession
from utils.token import verification

# from sqlalchemy.future import select
from sqlalchemy import select, func
from models.models import Vehicle, Driver
from models.schema import AddDriver
import uuid
import os
from dotenv import load_dotenv

load_dotenv()


class VehicleDriverController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.admin_email = os.getenv("ADMIN_EMAIL")

    async def add_vehicle(self, vehicle_data: AddVehicle, token: str):
        try:
            verification(token=token, role="admin", entity_id=self.admin_email)

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
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server Error: Unable to add vhicles.",
            )

    # async def update_vehicle(
    #     self, vehicleid: str, vehicle_data: UpdateVehicle, token: str
    # ):
    #     try:
    #         verification(token=token, role="admin", entity_id=self.admin_email)
    #     except HTTPException as e:
    #         raise HTTPException(status_code=e.status_code, detail=e.detail)

    #     vehicle = await self.db.execute(
    #         select(Vehicle).where(Vehicle.vehicleid == vehicleid)
    #     )
    #     existing_vehicle = vehicle.scalars().first()

    #     if not existing_vehicle:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
    #         )

    #     for key, value in vehicle_data.dict(exclude_unset=True).items():
    #         setattr(existing_vehicle, key, value)

    #     await self.db.commit()
    #     await self.db.refresh(existing_vehicle)

    #     return existing_vehicle

    async def get_all_vehicles(self, token: str, limit: int = 10, offset: int = 0):
        try:
            verification(token=token, role="admin", entity_id=self.admin_email)

            total_count_query = select(func.count(Vehicle.id))
            total_count_result = await self.db.execute(total_count_query)
            total_count = total_count_result.scalar()

            vehicles_query = select(Vehicle).limit(limit).offset(offset)
            vehicles_result = await self.db.execute(vehicles_query)
            vehicles = vehicles_result.scalars().all()

            total_pages = (total_count + limit - 1) // limit

            return {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": (offset // limit) + 1,
                "next_page": (offset + limit) < total_count,
                "prev_page": offset > 0,
                "vehicles": vehicles,
            }
        except Exception as e:
            print("Exception: ", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server Error: Unable to fetch vehicles.",
            )

    async def add_driver(self, driver_data: AddDriver, token: str):
        try:
            verification(token=token, role="admin", entity_id=self.admin_email)

            existing_driver = await self.db.execute(
                select(Driver).where(Driver.email == driver_data.email)
            )
            if existing_driver.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Driver with this email already exists",
                )

            new_driver = Driver(
                driverid=str(uuid.uuid4()),
                name=driver_data.name,
                email=driver_data.email,
                mobile=driver_data.mobile,
                country=driver_data.country,
                state=driver_data.state,
                current_latitude=driver_data.current_latitude,
                current_longitude=driver_data.current_longitude,
                regions_available=driver_data.regions_available,
                availability=driver_data.availability,
                password=driver_data.password,
                country_code=driver_data.country_code,
            )

            self.db.add(new_driver)
            await self.db.commit()
            await self.db.refresh(new_driver)

            return new_driver
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Server Error: Unable to add driver. {str(e)}",
            )

    async def get_all_drivers(self, token: str, limit: int = 10, offset: int = 0):
        try:
            verification(token=token, role="admin", entity_id=self.admin_email)

            total_count_query = select(func.count(Driver.id))
            total_count_result = await self.db.execute(total_count_query)
            total_count = total_count_result.scalar()

            drivers_query = select(Driver).limit(limit).offset(offset)
            drivers_result = await self.db.execute(drivers_query)
            drivers = drivers_result.scalars().all()

            total_pages = (total_count + limit - 1) // limit

            return {
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": (offset // limit) + 1,
                "next_page": (offset + limit) < total_count,
                "prev_page": offset > 0,
                "drivers": drivers,
            }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server Error: Unable to fetch drivers.",
            )
