from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Vehicle
from models.schema import VehicleSearch
from config.database import get_db
from fastapi import HTTPException, status
from sqlalchemy import select
from utils.helpers import LogisticsCalculations
import asyncio


class VehicleController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.radius = 50000

    async def search_vehicle(self, search_params: VehicleSearch):
        try:
            vehicles_query = select(Vehicle).filter(
                Vehicle.capacity_in_kg >= search_params.capacity_in_kg,
                Vehicle.fuel_type == search_params.fuel_type,
                Vehicle.is_available == True,
                Vehicle.active_status == True,
            )

            result = await self.db.execute(vehicles_query)
            vehicles = result.scalars().all()

            logistic_calculator = LogisticsCalculations()

            async def calculate_distance_and_price(vehicle):
                vehicle_latitude = float(vehicle.current_latitude)
                vehicle_longitude = float(vehicle.current_longitude)

                distance = await asyncio.to_thread(
                    logistic_calculator.calculate_estimated_distance,
                    from_latitude=search_params.pickup_latitude,
                    from_longitude=search_params.pickup_longitude,
                    to_latitude=vehicle_latitude,
                    to_longitude=vehicle_longitude,
                )

                estimated_price = logistic_calculator.calculate_estimated_price(
                    vehicle_latitude,
                    vehicle_longitude,
                    search_params.pickup_latitude,
                    search_params.pickup_longitude,
                    search_params.drop_latitude,
                    search_params.drop_longitude,
                    vehicle.fuel_type,
                )

                return vehicle, distance, estimated_price

            tasks = [calculate_distance_and_price(vehicle) for vehicle in vehicles]
            results = await asyncio.gather(*tasks)

            nearby_vehicles = []
            for vehicle, distance, estimated_price in results:
                if distance <= self.radius:
                    nearby_vehicles.append(
                        {
                            "vehicle_id": vehicle.vehicleid,
                            "registration_number": vehicle.registration_number,
                            "model_name": vehicle.model_name,
                            "capacity_in_kg": vehicle.capacity_in_kg,
                            "current_latitude": vehicle.current_latitude,
                            "current_longitude": vehicle.current_longitude,
                            "fuel_type": vehicle.fuel_type,
                            "distance_from_pickup": distance,
                            "total_distance_km": estimated_price["total_distance_km"],
                            "base_price": estimated_price["base_price"],
                            "gst": estimated_price["gst"],
                            "platform_fee": estimated_price["platform_fee"],
                            "total_price": estimated_price["total_price"],
                        }
                    )

            nearby_vehicles.sort(key=lambda x: x["total_price"])

            return nearby_vehicles

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching vehicles: {str(e)}",
            )

    def __del__(self):
        pass
