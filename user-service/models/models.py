from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, func, Float, Boolean


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    country = Column(String, index=True)
    state = Column(String, index=True)
    country_code = Column(String, index=True)
    phone_number = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicleid = Column(String, unique=True, index=True)
    model_name = Column(String)
    capacity_in_kg = Column(Float)
    registration_number = Column(String, unique=True, index=True)
    current_latitude = Column(Float)
    current_longitude = Column(Float)
    is_available = Column(Boolean, default=True)
    active_status = Column(Boolean, default=False)
    fuel_type = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
