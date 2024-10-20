from sqlalchemy import select
from fastapi import APIRouter, Depends, status, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from controllers.driver_controller import DriverController
from models.models import Driver
from models.schema import DriverOnboard, DriverLogin
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from utils.populate_data import populate_driver_data
from typing import Literal

from utils.token import verification

# Driver route
driver_route = APIRouter(prefix="/driver", tags=["drivers"])


# @driver_route.post("/onboard", response_model=dict)
# async def onboard_driver(
#     driver_data: DriverOnboard, db: AsyncSession = Depends(get_db)
# ):
#     try:
#         driver_instance = DriverController(db)
#         response = await driver_instance.create_driver(driver_data.dict())
#         return JSONResponse(
#             content=response,
#             media_type="application/json",
#             status_code=status.HTTP_201_CREATED,
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Server Error: Unable to onboard driver.",
#         )


@driver_route.post("/login", response_model=dict)
async def login_driver(driver_login: DriverLogin, db: AsyncSession = Depends(get_db)):
    try:
        driver_instance = DriverController(db)
        response = await driver_instance.login_driver(
            driver_login.email, driver_login.password
        )
        return JSONResponse(
            content=response,
            media_type="application/json",
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to login driver.",
        )


@driver_route.get("/profile")
async def get_driver_profile(
    driver_id: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    query = select(Driver).filter(Driver.driverid == driver_id)
    result = await db.execute(query)
    driver = result.scalars().first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )

    verification(token=authorization.split(" ")[1], role="driver", entity_id=driver_id)
    driver_instance = DriverController(db)
    try:
        driver_profile = await driver_instance.get_driver_profile(
            driver_id, authorization
        )
        return JSONResponse(content=driver_profile, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to get driver profile.",
        )


@driver_route.get("/booking")
async def get_driver_bookings(
    driver_id: str = Query(...),
    request_status: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    query = select(Driver).filter(Driver.driverid == driver_id)
    result = await db.execute(query)
    driver = result.scalars().first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )

    verification(token=authorization.split(" ")[1], role="driver", entity_id=driver_id)
    driver_instance = DriverController(db)
    try:
        driver_profile = await driver_instance.get_driver_bookings(
            driver_id, request_status
        )
        return JSONResponse(content=driver_profile, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to get driver bookings.",
        )


@driver_route.put("/booking")
async def update_booking_status(
    driver_id: str = Query(...),
    booking_id: str = Query(...),
    status_type: str = Query(...),
    update_to: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    query = select(Driver).filter(Driver.driverid == driver_id)
    result = await db.execute(query)
    driver = result.scalars().first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found",
        )

    verification(token=authorization.split(" ")[1], role="driver", entity_id=driver_id)
    driver_instance = DriverController(db)
    try:
        response = await driver_instance.update_booking_status(
            driver_id, booking_id, status_type, update_to
        )
        return JSONResponse(content=response, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to update booking status.",
        )


@driver_route.post("/populate")
async def populate_drivers(num_drivers: int = 1000, db: AsyncSession = Depends(get_db)):
    try:
        response = await populate_driver_data(db, num_drivers)
        return JSONResponse(content=response, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
