import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import BookingRequest
from models.schema import BookingRequestCreate
from sqlalchemy.future import select
from models.models import Users, Driver, Vehicle
from utils.helpers import LogisticsCalculations


class BookingsController:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logistic_calculator = LogisticsCalculations()

    async def get_coordinates(self, pickup_address, drop_address):
        try:
            pickup_coordinates = self.logistic_calculator.geocode_address(
                pickup_address
            )
            drop_coordinates = self.logistic_calculator.geocode_address(drop_address)

            if pickup_coordinates != None and drop_coordinates != None:
                return {
                    "pickup_coordinates": pickup_coordinates,
                    "drop_coordinates": drop_coordinates,
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Not able to find coordinates",
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating booking: {str(e)}",
            )

    async def create_booking(self, booking_data: BookingRequestCreate):
        try:
            user_query = select(Users).filter(Users.userid == booking_data.user_id)
            user_result = await self.db.execute(user_query)
            user = user_result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            driver_query = select(Driver).filter(
                Driver.driverid == booking_data.driver_id
            )
            driver_result = await self.db.execute(driver_query)
            driver = driver_result.scalar_one_or_none()
            if not driver:
                raise HTTPException(status_code=404, detail="Driver not found")

            vehicle_query = select(Vehicle).filter(
                Vehicle.vehicleid == booking_data.vehicle_id
            )
            vehicle_result = await self.db.execute(vehicle_query)
            vehicle = vehicle_result.scalar_one_or_none()
            if not vehicle:
                raise HTTPException(status_code=404, detail="Vehicle not found")

            calculation_results = (
                self.logistic_calculator.calculate_distance_time_price(
                    vehicle_lat=vehicle.current_latitude,
                    vehicle_lng=vehicle.current_longitude,
                    origin_address=booking_data.pickup_location,
                    destination_address=booking_data.drop_location,
                    fuel_type=vehicle.fuel_type,
                )
            )

            if calculation_results is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to create bookings",
                )

            new_booking = BookingRequest(
                booking_id=str(uuid.uuid4()),
                user_id=booking_data.user_id,
                vehicle_id=booking_data.vehicle_id,
                driver_id=booking_data.driver_id,
                pickup_location=booking_data.pickup_location,
                pickup_latitude=calculation_results["pickup_coordinates"][0],
                pickup_longitude=calculation_results["pickup_coordinates"][1],
                drop_location=booking_data.drop_location,
                drop_latitude=calculation_results["drop_coordinates"][0],
                drop_longitude=calculation_results["drop_coordinates"][1],
                distance_to_cover=float(calculation_results["total_distance_km"]),
                estimated_delivery_time=calculation_results["estimated_delivery_time"],
                base_price=calculation_results["base_price"],
                gst=calculation_results["gst"],
                platform_fee=calculation_results["platform_fee"],
                total_price=calculation_results["total_price"],
            )

            self.db.add(new_booking)
            await self.db.commit()

            await self.db.refresh(new_booking)
            response_dict = {
                "message": "Booking has been successfully created",
                "details": {
                    "booking_id": new_booking.booking_id,
                    "pickup_location": new_booking.pickup_location,
                    "drop_location": new_booking.drop_location,
                    "total_distance": new_booking.distance_to_cover,
                    "estimated_delivery_time": new_booking.estimated_delivery_time,
                    "base_price": new_booking.base_price,
                    "gst": new_booking.gst,
                    "platform_fee": new_booking.platform_fee,
                    "total_price": new_booking.total_price,
                },
            }

            return response_dict
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating booking: {str(e)}",
            )

    async def get_booking_by_userid(self, user_id: str):
        query = select(
            BookingRequest.distance_from_vehicle,
            BookingRequest.distance_from_pickup_location,
            BookingRequest.pickup_location,
            BookingRequest.drop_location,
            BookingRequest.driver_name,
            BookingRequest.driver_email,
            BookingRequest.driver_mobile,
            BookingRequest.base_price,
            BookingRequest.gst,
            BookingRequest.platform_fee,
            BookingRequest.total_price,
            BookingRequest.request_status,
            BookingRequest.booking_status,
        ).filter(BookingRequest.user_id == user_id)

        result = await self.db.execute(query)
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
                    "driver_name": booking.driver_name,
                    "driver_email": booking.driver_email,
                    "driver_mobile": booking.driver_mobile,
                    "base_price": booking.base_price,
                    "gst": booking.gst,
                    "platform_fee": booking.platform_fee,
                    "total_price": booking.total_price,
                    "request_status": booking.request_status,
                    "booking_status": booking.booking_status,
                }
            )

        return formatted_bookings

    # async def update_booking(self, booking_id: int, booking_data: BookingRequestUpdate):
    #     booking = await self.get_booking_by_id(booking_id)
    #     if not booking:
    #         raise HTTPException(status_code=404, detail="Booking not found")

    #     for key, value in booking_data.dict(exclude_unset=True).items():
    #         setattr(booking, key, value)

    #     await self.db.commit()
    #     await self.db.refresh(booking)
    #     return booking

    # async def delete_booking(self, booking_id: int):
    #     booking = await self.get_booking_by_id(booking_id)
    #     if not booking:
    #         raise HTTPException(status_code=404, detail="Booking not found")

    #     booking.is_active = False
    #     await self.db.commit()
    #     return {"detail": "Booking cancelled successfully"}
