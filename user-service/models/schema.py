from pydantic import BaseModel, EmailStr
from typing import Optional


class UserOnboard(BaseModel):
    name: str
    email: EmailStr
    country: str
    state: str
    country_code: str
    phone_number: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class VehicleSearch(BaseModel):
    capacity_in_kg: float
    pickup_latitude: float
    pickup_longitude: float
    drop_latitude: float
    drop_longitude: float


class BookingRequestCreate(BaseModel):
    user_id: str
    vehicle_id: str
    driver_id: str
    pickup_location: str
    drop_location: str


class BookingRequestUserResponse(BaseModel):
    distance_from_vehicle: float
    distance_from_pickup_location: float
    pickup_location: str
    drop_location: str
    driver_name: str
    driver_email: str
    driver_mobile: str
    base_price: float
    gst: float
    platform_fee: float
    total_price: float
    request_status: str
    booking_status: str


class BookingRequestUserUpdate(BaseModel):
    order_completed: Optional[str] = None
