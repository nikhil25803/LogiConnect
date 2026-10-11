from config.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Float,
    ForeignKey,
)


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


class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String, index=True, unique=True)
    user_id = Column(String, ForeignKey("users.userid"), index=True)
    vehicle_id = Column(String, index=True)
    driver_id = Column(String, index=True)
    driver_name = Column(String)
    driver_email = Column(String)
    driver_mobile = Column(String)
    pickup_location = Column(String)
    pickup_latitude = Column(Float)
    pickup_longitude = Column(Float)
    drop_location = Column(String)
    drop_latitude = Column(Float)
    drop_longitude = Column(Float)
    distance_to_cover = Column(Float)
    estimated_delivery_time = Column(Float)
    base_price = Column(Float)
    gst = Column(Float)
    platform_fee = Column(Float)
    total_price = Column(Float)
    request_status = Column(
        String, default="Pending"
    )  # ("Pending", "Accepted", "Rejected", "Completed")
    delivery_status = Column(
        String,
        default="Pending Pickup",
    )  # ( "Pending Pickup", "In Transit", "Out for Delivery", "Delivered", "Canceled")
    order_status = Column(String, default="Pending")  # ("Pending", "Received")
    payment_status = Column(
        String, default="Completed"
    )  # ("Pending", "Completed", "Failed", "Refunded")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
