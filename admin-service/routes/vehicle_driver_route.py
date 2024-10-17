from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from models.schema import AddDriver, AddVehicle, VehiclesResponse, DriversResponse
from controllers.vehicle_driver_controller import VehicleDriverController
from utils.populate_data import add_vehicles_without_token

vehicle_driver_route = APIRouter(prefix="/logistics", tags=["admin"])


@vehicle_driver_route.post("/vehicle/add")
async def add_vehicle(
    vehicle_data: AddVehicle,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.split(" ")[1]

    controller = VehicleDriverController(db)
    try:
        return await controller.add_vehicle(vehicle_data=vehicle_data, token=token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to add vehicles.",
        )


# @vehicle_route.put("/update")
# async def update_vehicle(
#     vehicle_data: UpdateVehicle,
#     vehicleid: str = Query(...),
#     authorization: str = Header(...),
#     db: AsyncSession = Depends(get_db),
# ):
#     token = authorization.split(" ")[1]
#     controller = VehicleController(db)

#     try:
#         return await controller.update_vehicle(
#             vehicleid=vehicleid, vehicle_data=vehicle_data, token=token
#         )
#     except HTTPException as e:
#         raise HTTPException(status_code=e.status_code, detail=e.detail)
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="An unexpected error occurred",
#         )


@vehicle_driver_route.get("/vehicle/all", response_model=VehiclesResponse)
async def get_all_vehicles(
    authorization: str = Header(...),
    limit: int = Query(10, description="Limit the number of vehicles returned"),
    offset: int = Query(0, description="The starting point of vehicle retrieval"),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.split(" ")[1]
    vehicle_driver_controller = VehicleDriverController(db)

    try:
        return await vehicle_driver_controller.get_all_vehicles(
            token=token, limit=limit, offset=offset
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to fetch all vehicles.",
        )


@vehicle_driver_route.post("/driver/add")
async def add_driver(
    driver_data: AddDriver,
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.split(" ")[1]
    controller = VehicleDriverController(db)
    try:
        return await controller.add_driver(driver_data=driver_data, token=token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to add driver.",
        )


@vehicle_driver_route.get("/driver/all", response_model=DriversResponse)
async def get_all_drivers(
    authorization: str = Header(...),
    limit: int = Query(10, description="Limit the number of drivers returned"),
    offset: int = Query(0, description="The starting point of driver retrieval"),
    db: AsyncSession = Depends(get_db),
):
    token = authorization.split(" ")[1]
    vehicle_driver_controller = VehicleDriverController(db)

    try:
        return await vehicle_driver_controller.get_all_drivers(
            token=token, limit=limit, offset=offset
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server Error: Unable to fetch all drivers.",
        )


# @vehicle_driver_route.get("/driver/all", response_model=list[AddDriver])
# async def get_all_drivers(
#     authorization: str = Header(...),
#     db: AsyncSession = Depends(get_db),
# ):
#     token = authorization.split(" ")[1]
#     driver_controller = VehicleDriverController(db)

#     try:
#         return await driver_controller.get_all_drivers(token=token)
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Server Error: Unable to fetch all drivers.",
#         )


@vehicle_driver_route.post("/populate-vehicles")
async def populate_vehicles(num_vehicles: int = 10000, db=Depends(get_db)):
    await add_vehicles_without_token(db, num_vehicles)
    return {"message": f"{num_vehicles} vehicles added successfully!"}
