from pydantic import BaseModel, EmailStr
from typing import Optional, List


class DriverLogin(BaseModel):
    email: EmailStr
    password: str


class DriverOnboard(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    state: str
    country: str
    current_latitude: float
    current_longitude: float  #
    regions_available: Optional[List[str]] = None
    availability: Optional[bool] = True
    password: str
    country_code: str


class DriverProfile(BaseModel):
    id: int
    driverid: str
    availability: bool
    name: str
    email: EmailStr
    country_code: str
    mobile: str
    regions_available: Optional[List[str]] = None
    created_at: str
    updated_at: str


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    availability: Optional[bool] = None
    regions_available: Optional[List[str]] = None
    country_code: Optional[str] = None
    mobile: Optional[str] = None
    password: Optional[str] = None
