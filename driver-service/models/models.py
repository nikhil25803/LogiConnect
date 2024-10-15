from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from config.database import Base


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    driverid = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    state = Column(String, index=True)
    country = Column(String, index=True)
    country_code = Column(String, index=True)
    mobile = Column(String, unique=True, index=True)
    regions = Column(ARRAY(String))
    password = Column(String)
    availability = Column(Boolean, default=True)
    role = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
