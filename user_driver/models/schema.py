from pydantic import BaseModel, EmailStr
from typing import Optional


"""
User Pydantic Model
"""


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOnboard(BaseModel):
    name: str
    email: EmailStr
    country: str
    state: str
    country_code: str
    phone_number: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    country_code: Optional[str] = None
    phone_number: Optional[str] = None


"""
Driver Pydantic Model
"""


class DriverLogin(BaseModel):
    email: EmailStr
    password: str


class DriverOnboard(BaseModel):
    name: str
    email: EmailStr
    country_code: str
    mobile: str
    password: str
    regions: Optional[str] = None


class DriverProfile(BaseModel):
    id: int
    driverid: str
    availability: bool
    name: str
    email: EmailStr
    country_code: str
    mobile: str
    regions: Optional[str] = None
    created_at: str
    updated_at: str


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    country_code: Optional[str] = None
    mobile: Optional[str] = None
    password: Optional[str] = None
    regions: Optional[str] = None
