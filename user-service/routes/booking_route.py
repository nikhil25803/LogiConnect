from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from controllers.booking_controller import BookingsController
from models.models import Users
from models.schema import BookingRequestCreate
from config.database import get_db
from fastapi.responses import JSONResponse

from utils.token import verification

booking_router = APIRouter(prefix="/booking", tags=["bookings"])


@booking_router.get("/coordinates")
async def get_coordinates(
    pickup_address: str = Query(...),
    drop_address: str = Query(...),
    user_id: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    query = select(Users).filter(Users.userid == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    verification(token=authorization.split(" ")[1], role="user", entity_id=user_id)

    controller = BookingsController(db)
    try:
        coordinates = await controller.get_coordinates(pickup_address, drop_address)
        return JSONResponse(content=coordinates, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to get coordinates.",
        )


@booking_router.post("/new")
async def create_booking(
    booking_data: BookingRequestCreate,
    user_id: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    query = select(Users).filter(Users.userid == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    verification(token=authorization.split(" ")[1], role="user", entity_id=user_id)
    controller = BookingsController(db)

    try:
        booking_response = await controller.create_booking(booking_data)
        return JSONResponse(
            content=booking_response,
            status_code=201,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to create booking.",
        )


@booking_router.get("/")
async def get_user_bookings(
    user_id: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    query = select(Users).filter(Users.userid == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    verification(token=authorization.split(" ")[1], role="user", entity_id=user_id)

    controller = BookingsController(db)
    try:
        user_bookings = await controller.get_user_bookings(user_id)
        return JSONResponse(content=user_bookings, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to fetch user bookings.",
        )


@booking_router.put("/update-order-status")
async def update_order_status(
    booking_id: str = Query(...),
    new_status: str = Query(...),
    user_id: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):

    query = select(Users).filter(Users.userid == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    verification(token=authorization.split(" ")[1], role="user", entity_id=user_id)
    try:
        controller = BookingsController(db)
        result = await controller.update_order_status(booking_id, new_status)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to update booking statuss",
        )
