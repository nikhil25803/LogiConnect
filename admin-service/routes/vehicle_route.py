from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from models.schema import AddVehicle, UpdateVehicle
from controllers.vehicle_controller import VehicleController
from utils.populate_data import add_vehicles_without_token

vehicle_route = APIRouter(prefix="/vehicle", tags=["vehicles"])
vehicle_controller = VehicleController


@vehicle_route.post("/add")
async def add_vehicle(
    vehicle_data: AddVehicle,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.split(" ")[1]
    controller = vehicle_controller(db)
    try:
        return await controller.add_vehicle(vehicle_data=vehicle_data, token=token)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@vehicle_route.put("/update")
async def update_vehicle(
    vehicle_data: UpdateVehicle,
    vehicleid: str = Query(...),
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.split(" ")[1]
    controller = VehicleController(db)

    try:
        return await controller.update_vehicle(
            vehicleid=vehicleid, vehicle_data=vehicle_data, token=token
        )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@vehicle_route.get("/all", response_model=list[AddVehicle])
async def get_all_vehicles(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.split(" ")[1]
    controller = VehicleController(db)

    try:
        return await controller.get_all_vehicles(token=token)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@vehicle_route.post("/add-vehicles")
async def add_vehicles(num_vehicles: int = 10000, db=Depends(get_db)):
    await add_vehicles_without_token(db, num_vehicles)
    return {"message": f"{num_vehicles} vehicles added successfully!"}
