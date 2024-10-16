from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Vehicle
from models.schema import VehicleSearch
from fastapi import HTTPException, status
from sqlalchemy import select
from utils.helpers import LogisticsCalculations
import asyncio


from models.models import Driver


class VehicleController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.radius = 50000

    async def search_vehicle(self, search_params: VehicleSearch):
        try:
            vehicles_query = select(Vehicle).filter(
                Vehicle.capacity_in_kg >= search_params.capacity_in_kg,
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

            return nearby_vehicles[:20]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching vehicles: {str(e)}",
            )

    async def suggest_nearest_driver(self, vehicle_id: str):
        try:
            vehicle_query = select(Vehicle).filter(Vehicle.vehicleid == vehicle_id)
            result = await self.db.execute(vehicle_query)
            vehicle = result.scalar()

            if not vehicle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
                )

            drivers_query = select(Driver).filter(Driver.availability == True)

            result = await self.db.execute(drivers_query)
            drivers = result.scalars().all()

            logistic_calculator = LogisticsCalculations()

            async def calculate_driver_distance(driver):
                driver_latitude = float(driver.current_latitude)
                driver_longitude = float(driver.current_longitude)

                distance = await asyncio.to_thread(
                    logistic_calculator.calculate_estimated_distance,
                    from_latitude=vehicle.current_latitude,
                    from_longitude=vehicle.current_longitude,
                    to_latitude=driver_latitude,
                    to_longitude=driver_longitude,
                )

                return driver, distance

            tasks = [calculate_driver_distance(driver) for driver in drivers]
            results = await asyncio.gather(*tasks)

            nearby_drivers = []
            for driver, distance in results:
                if distance <= self.radius:
                    nearby_drivers.append(
                        {
                            "driver_id": driver.driverid,
                            "name": driver.name,
                            "email": driver.email,
                            "mobile": driver.mobile,
                            "current_latitude": driver.current_latitude,
                            "current_longitude": driver.current_longitude,
                            "distance_from_vehicle": distance,
                        }
                    )

            nearby_drivers.sort(key=lambda x: x["distance_from_vehicle"])

            return nearby_drivers[0]

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching drivers: {str(e)}",
            )

    def __del__(self):
        pass
