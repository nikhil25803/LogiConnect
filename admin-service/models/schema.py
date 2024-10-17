from pydantic import BaseModel, EmailStr
from typing import Optional, List


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


class AddDriver(BaseModel):
    driverid: Optional[str]
    name: str
    email: str
    mobile: str
    country: str
    state: str
    current_latitude: float
    current_longitude: float
    regions_available: List[str]
    availability: bool = True
    password: str
    role: str = "driver"
    country_code: str


from pydantic import BaseModel
from typing import List, Optional


class VehicleResponse(BaseModel):
    vehicleid: str
    model_name: str
    registration_number: str
    is_available: bool
    fuel_type: str


class VehiclesResponse(BaseModel):
    total_count: int
    total_pages: int
    current_page: int
    next_page: bool
    prev_page: bool
    vehicles: List[VehicleResponse]


class DriverResponse(BaseModel):
    driverid: str
    name: str
    email: str
    mobile: str
    availability: bool


class DriversResponse(BaseModel):
    total_count: int
    total_pages: int
    current_page: int
    next_page: bool
    prev_page: bool
    drivers: List[DriverResponse]
