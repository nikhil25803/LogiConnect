import asyncio
import os

from fastapi import HTTPException

from config.internal import internal_request
from utils.helpers import LogisticsCalculations


class VehicleController:
    def __init__(self, db):
        self.radius = 50000
        self.admin_url = os.getenv("ADMIN_SERVICE_URL", "http://admin-service:3003")
        self.driver_url = os.getenv("DRIVER_SERVICE_URL", "http://driver-service:3002")

    async def search_vehicle(self, search_params):
        vehicles = await internal_request(
            "GET", self.admin_url, "/internal/vehicles",
            params={"min_capacity": search_params.capacity_in_kg, "available": True, "active": True},
        )
        calculator = LogisticsCalculations()

        async def enrich(vehicle):
            distance = await asyncio.to_thread(
                calculator.calculate_estimated_distance,
                search_params.pickup_latitude, search_params.pickup_longitude,
                float(vehicle["current_latitude"]), float(vehicle["current_longitude"]),
            )
            price = calculator.calculate_estimated_price(
                vehicle["current_latitude"], vehicle["current_longitude"],
                search_params.pickup_latitude, search_params.pickup_longitude,
                search_params.drop_latitude, search_params.drop_longitude,
                vehicle["fuel_type"],
            )
            return vehicle, distance, price

        nearby = []
        for vehicle, distance, price in await asyncio.gather(*(enrich(item) for item in vehicles)):
            if distance <= self.radius:
                nearby.append({
                    "vehicle_id": vehicle["vehicleid"],
                    "registration_number": vehicle["registration_number"],
                    "model_name": vehicle["model_name"],
                    "capacity_in_kg": vehicle["capacity_in_kg"],
                    "current_latitude": vehicle["current_latitude"],
                    "current_longitude": vehicle["current_longitude"],
                    "fuel_type": vehicle["fuel_type"],
                    "distance_from_pickup": distance,
                    **price,
                })
        nearby.sort(key=lambda item: item["total_price"])
        return nearby[:20]

    async def suggest_nearest_driver(self, vehicle_id: str):
        vehicle = await internal_request("GET", self.admin_url, f"/internal/vehicles/{vehicle_id}")
        drivers = await internal_request(
            "GET", self.driver_url, "/internal/drivers", params={"available": True}
        )
        calculator = LogisticsCalculations()

        async def calculate(driver):
            value = await asyncio.to_thread(
                calculator.calculate_estimated_distance,
                vehicle["current_latitude"], vehicle["current_longitude"],
                driver["current_latitude"], driver["current_longitude"],
            )
            return driver, value

        nearby = []
        for driver, value in await asyncio.gather(*(calculate(item) for item in drivers)):
            if value <= self.radius:
                nearby.append({
                    "driver_id": driver["driverid"], "name": driver["name"],
                    "email": driver["email"], "mobile": driver["mobile"],
                    "current_latitude": driver["current_latitude"],
                    "current_longitude": driver["current_longitude"],
                    "distance_from_vehicle": value,
                })
        if not nearby:
            raise HTTPException(status_code=404, detail="No drivers found")
        return min(nearby, key=lambda item: item["distance_from_vehicle"])
