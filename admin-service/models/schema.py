from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class AddVehicle(BaseModel):
    model_name: str
    capacity_in_kg: float
    registration_number: str
    current_latitude: float
    current_longitude: float
    is_available: bool
    active_status: bool
    fuel_type: str


class UpdateVehicle(BaseModel):
    model_name: Optional[str] = None
    capacity_in_kg: Optional[float] = None
    registration_number: Optional[str] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    is_available: Optional[bool] = None
    active_status: Optional[bool] = None
    fuel_type: Optional[str] = None
