from pydantic import BaseModel, EmailStr
from typing import Optional, List


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