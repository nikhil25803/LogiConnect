from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from config.database import Base


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


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    driverid = Column(String, unique=True, index=True)
    availability = Column(Boolean, default=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    country_code = Column(String, index=True)
    mobile = Column(String, unique=True, index=True)
    regions = Column(ARRAY(String))
    password = Column(String)
    role = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicleid = Column(String, unique=True, index=True)
    driverid = Column(Integer, ForeignKey("drivers.id"), index=True)
    mobile = Column(String, index=True)
    capacity = Column(Integer)
    type = Column(String)
    availability = Column(Boolean, default=True)
    cost_per_km = Column(Float)
