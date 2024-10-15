from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AddVehicle(BaseModel):
    model_name: str
    capacity_in_kg: float
    registration_number: str
    current_latitude: str
    current_longitude: str
    is_available: bool
    active_status: bool
    fuel_type: str


class UpdateVehicle(BaseModel):
    model_name: Optional[str] = None
    capacity_in_kg: Optional[float] = None
    registration_number: Optional[str] = None
    current_latitude: Optional[str] = None
    current_longitude: Optional[str] = None
    is_available: Optional[bool] = None
    active_status: Optional[bool] = None
    fuel_type: Optional[str] = None
