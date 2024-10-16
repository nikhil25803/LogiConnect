from config.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Float,
    Boolean,
    ARRAY,
    ForeignKey,
)
from sqlalchemy.orm import relationship


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


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    driverid = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mobile = Column(String, unique=True)
    country = Column(String, index=True)
    state = Column(String, index=True)
    current_latitude = Column(Float)
    current_longitude = Column(Float)
    regions_available = Column(ARRAY(String), index=True)
    availability = Column(Boolean, default=True, index=True)
    password = Column(String)
    role = Column(String, index=True, default="driver")
    country_code = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String)
    user_id = Column(String, ForeignKey("users.userid"), index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.vehicleid"), index=True)
    driver_id = Column(String, ForeignKey("drivers.driverid"), index=True)
    user_name = Column(String)
    user_email = Column(String)
    user_mobile = Column(String)
    driver_name = Column(String)
    driver_email = Column(String)
    driver_mobile = Column(String)
    distance_from_vehicle = Column(Float)
    distance_from_pickup_location = Column(Float)
    pickup_latitude = Column(Float)
    pickup_longitude = Column(Float)
    pickup_location = Column(String)
    drop_latitude = Column(Float)
    drop_longitude = Column(Float)
    drop_location = Column(String)
    base_price = Column(Float)
    gst = Column(Float)
    platform_fee = Column(Float)
    total_price = Column(Float)
    request_status = Column(String, default="pending")
    booking_status = Column(String, default="pending")
    order_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
