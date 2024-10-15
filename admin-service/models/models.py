from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func
from config.database import Base


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
