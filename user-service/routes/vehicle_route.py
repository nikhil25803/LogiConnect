from fastapi import APIRouter, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from controllers.vehicle_controller import VehicleController
from models.schema import VehicleSearch


vehicle_router = APIRouter(prefix="/vehicle", tags=["booking"])


@vehicle_router.post("/search")
async def search_vehicles(
    search_params: VehicleSearch = Query(...),
    # user_id: str = Query(...),
    # authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    # query = select(Users).filter(Users.userid == user_id)
    # result = await db.execute(query)
    # user = result.scalars().first()
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not found",
    #     )

    # verification(token=authorization.split(" ")[1], role="user", entity_id=user_id)

    vehicle_instance = VehicleController(db)
    try:
        user_profile = await vehicle_instance.search_vehicle(search_params)
        return JSONResponse(content=user_profile, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )


@vehicle_router.get("/search/driver")
async def search_drivers(
    vehicle_id: str = Query(...),
    # user_id: str = Query(...),
    # authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    # query = select(Users).filter(Users.userid == user_id)
    # result = await db.execute(query)
    # user = result.scalars().first()
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not found",
    #     )

    # verification(token=authorization.split(" ")[1], role="user", entity_id=user_id)

    vehicle_instance = VehicleController(db)
    try:
        driver_profile = await vehicle_instance.suggest_nearest_driver(vehicle_id)
        return JSONResponse(content=driver_profile, status_code=200)
    except HTTPException as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
        )
