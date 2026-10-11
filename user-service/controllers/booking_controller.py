import os
import uuid

from fastapi import HTTPException
from sqlalchemy import select

from config.internal import internal_request
from models.models import BookingRequest, Users
from utils.helpers import LogisticsCalculations


class BookingsController:
    def __init__(self, db):
        self.db = db
        self.logistic_calculator = LogisticsCalculations()
        self.admin_url = os.getenv("ADMIN_SERVICE_URL", "http://admin-service:3003")
        self.driver_url = os.getenv("DRIVER_SERVICE_URL", "http://driver-service:3002")

    async def get_coordinates(self, pickup_address, drop_address):
        pickup = self.logistic_calculator.geocode_address(pickup_address)
        drop = self.logistic_calculator.geocode_address(drop_address)
        if pickup is None or drop is None:
            raise HTTPException(status_code=500, detail="Not able to find coordinates")
        return {"pickup_coordinates": pickup, "drop_coordinates": drop}

    async def create_booking(self, booking_data):
        user = (await self.db.execute(select(Users).filter(Users.userid == booking_data.user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        driver = await internal_request("GET", self.driver_url, f"/internal/drivers/{booking_data.driver_id}")
        vehicle = await internal_request("GET", self.admin_url, f"/internal/vehicles/{booking_data.vehicle_id}")
        calculation = self.logistic_calculator.calculate_distance_time_price(
            vehicle_lat=vehicle["current_latitude"], vehicle_lng=vehicle["current_longitude"],
            origin_address=booking_data.pickup_location,
            destination_address=booking_data.drop_location,
            fuel_type=vehicle["fuel_type"],
        )
        if calculation is None:
            raise HTTPException(status_code=500, detail="Unable to create bookings")
        booking = BookingRequest(
            booking_id=str(uuid.uuid4()), user_id=booking_data.user_id,
            vehicle_id=booking_data.vehicle_id, driver_id=booking_data.driver_id,
            driver_name=driver["name"], driver_email=driver["email"], driver_mobile=driver["mobile"],
            pickup_location=booking_data.pickup_location,
            pickup_latitude=calculation["pickup_coordinates"][0],
            pickup_longitude=calculation["pickup_coordinates"][1],
            drop_location=booking_data.drop_location,
            drop_latitude=calculation["drop_coordinates"][0],
            drop_longitude=calculation["drop_coordinates"][1],
            distance_to_cover=float(calculation["total_distance_km"]),
            estimated_delivery_time=calculation["estimated_delivery_time"],
            base_price=calculation["base_price"], gst=calculation["gst"],
            platform_fee=calculation["platform_fee"], total_price=calculation["total_price"],
        )
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return {"message": "Booking has been successfully created", "details": {
            "booking_id": booking.booking_id, "pickup_location": booking.pickup_location,
            "drop_location": booking.drop_location, "total_distance": booking.distance_to_cover,
            "estimated_delivery_time": booking.estimated_delivery_time,
            "base_price": booking.base_price, "gst": booking.gst,
            "platform_fee": booking.platform_fee, "total_price": booking.total_price,
        }}

    async def get_user_bookings(self, user_id: str):
        user = (await self.db.execute(select(Users).filter(Users.userid == user_id))).scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        bookings = (await self.db.execute(select(BookingRequest).filter(BookingRequest.user_id == user_id))).scalars().all()
        if not bookings:
            raise HTTPException(status_code=404, detail="No bookings found")
        return [{
            "pickup_location": booking.pickup_location,
            "drop_location": booking.drop_location,
            "distance_to_cover": booking.distance_to_cover,
            "estimated_delivery_time": booking.estimated_delivery_time,
            "total_price": booking.total_price,
            "request_status": booking.request_status,
            "delivery_status": booking.delivery_status,
            "driver_details": {"name": booking.driver_name, "email": booking.driver_email, "mobile": booking.driver_mobile},
        } for booking in bookings]

    async def update_order_status(self, booking_id: str, new_status: str):
        booking = (await self.db.execute(select(BookingRequest).filter(BookingRequest.booking_id == booking_id))).scalar_one_or_none()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if booking.request_status != "Accepted" or booking.delivery_status != "Delivered":
            raise HTTPException(status_code=400, detail="Order status can only be updated to 'Received' when request is accepted and delivery is completed")
        booking.order_status = new_status
        await self.db.commit()
        return {"message": f"Order status successfully updated to {new_status}"}
