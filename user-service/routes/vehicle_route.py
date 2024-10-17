from fastapi import APIRouter, Query, Depends, HTTPException, Header, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from controllers.vehicle_controller import VehicleController
from models.schema import VehicleSearch
from sqlalchemy import select
from models.models import Users
from utils.token import verification


vehicle_router = APIRouter(prefix="/vehicle", tags=["vehicles"])


@vehicle_router.post("/search")
async def search_vehicles(
    search_params: VehicleSearch,
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

    vehicle_instance = VehicleController(db)
    try:
        vehicle_search_result = await vehicle_instance.search_vehicle(search_params)
        return JSONResponse(content=vehicle_search_result, status_code=200)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to search vehicle",
        )


@vehicle_router.get("/search/driver")
async def search_drivers(
    vehicle_id: str = Query(...),
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

    vehicle_instance = VehicleController(db)
    try:
        driver_profile = await vehicle_instance.suggest_nearest_driver(vehicle_id)
        return JSONResponse(content=driver_profile, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to search driver",
        )
