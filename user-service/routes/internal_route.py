from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from config.database import get_db
from config.internal import require_internal_key
from models.models import BookingRequest


internal_router = APIRouter(
    prefix="/internal", dependencies=[Depends(require_internal_key)], include_in_schema=False
)


class BookingStatusUpdate(BaseModel):
    driver_id: str
    status_type: str
    update_to: str


def booking_dict(booking):
    return {column.name: getattr(booking, column.name) for column in BookingRequest.__table__.columns if column.name not in {"id", "created_at", "updated_at"}}


@internal_router.get("/bookings")
async def list_bookings(driver_id: str, request_status: str = Query("All"), db=Depends(get_db)):
    query = select(BookingRequest).filter(BookingRequest.driver_id == driver_id)
    if request_status != "All":
        query = query.filter(BookingRequest.request_status == request_status)
    bookings = (await db.execute(query)).scalars().all()
    if not bookings:
        raise HTTPException(status_code=404, detail="No bookings found")
    return [booking_dict(booking) for booking in bookings]


@internal_router.patch("/bookings/{booking_id}/driver-status")
async def update_driver_status(booking_id: str, data: BookingStatusUpdate, db=Depends(get_db)):
    booking = (await db.execute(select(BookingRequest).filter(
        BookingRequest.booking_id == booking_id, BookingRequest.driver_id == data.driver_id
    ))).scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or invalid.")
    if data.status_type == "Request":
        if data.update_to not in {"Accepted", "Rejected", "Completed"}:
            raise HTTPException(status_code=400, detail="Invalid request status update.")
        if booking.request_status == "Completed":
            raise HTTPException(status_code=400, detail="Cannot update a completed request.")
        booking.request_status = data.update_to
    elif data.status_type == "Delivery":
        if data.update_to not in {"In Transit", "Out for Delivery", "Delivered", "Canceled"}:
            raise HTTPException(status_code=400, detail="Invalid delivery status update.")
        if booking.delivery_status in {"Delivered", "Canceled"}:
            raise HTTPException(status_code=400, detail=f"Cannot update a {booking.delivery_status} delivery.")
        booking.delivery_status = data.update_to
    else:
        raise HTTPException(status_code=400, detail="Invalid status type. Use 'Request' or 'Delivery'.")
    await db.commit()
    return booking_dict(booking)
