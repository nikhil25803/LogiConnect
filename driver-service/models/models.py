from config.database import Base
from sqlalchemy import Column, Integer, String, DateTime, func, Float, Boolean, ARRAY


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
