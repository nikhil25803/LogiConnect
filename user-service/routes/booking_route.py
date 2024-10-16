from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from controllers.booking_controller import BookingsController
from models.schema import BookingRequestCreate
from config.database import get_db
from fastapi.responses import JSONResponse

booking_router = APIRouter(prefix="/booking", tags=["bookings"])


@booking_router.post("/new")
async def create_booking(
    booking_data: BookingRequestCreate, db: AsyncSession = Depends(get_db)
):
    controller = BookingsController(db)

    try:
        booking_response = await controller.create_booking(booking_data)
        return JSONResponse(
            content=booking_response,
            status_code=201,
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@booking_router.get("/coordinates")
async def get_coordinates(
    pickup_address: str = Query(...),
    drop_address: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    controller = BookingsController(db)
    try:
        coordinates = await controller.get_coordinates(pickup_address, drop_address)
        return JSONResponse(content=coordinates, status_code=200)

    except HTTPException as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": e.detail},
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)},
        )


@booking_router.get("/")
async def get_user_bookings(
    user_id: str = Query(...), db: AsyncSession = Depends(get_db)
):
    controller = BookingsController(db)
    try:
        user_bookings = await controller.get_booking_by_userid(user_id)
        return JSONResponse(content=user_bookings, status_code=200)

    except HTTPException as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": e.detail},
        )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)},
        )
