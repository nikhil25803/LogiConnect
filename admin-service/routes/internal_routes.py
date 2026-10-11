from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from config.database import get_db
from config.internal import require_internal_key
from models.models import Vehicle


internal_router = APIRouter(prefix="/internal", dependencies=[Depends(require_internal_key)], include_in_schema=False)


class VehicleUpdate(BaseModel):
    is_available: bool | None = None
    active_status: bool | None = None
    current_latitude: float | None = None
    current_longitude: float | None = None


def vehicle_dict(vehicle):
    return {column.name: getattr(vehicle, column.name) for column in Vehicle.__table__.columns if column.name not in {"id", "created_at", "updated_at"}}


@internal_router.get("/vehicles")
async def list_vehicles(
    min_capacity: float | None = None, available: bool | None = None,
    active: bool | None = None, db=Depends(get_db),
):
    query = select(Vehicle)
    if min_capacity is not None:
        query = query.filter(Vehicle.capacity_in_kg >= min_capacity)
    if available is not None:
        query = query.filter(Vehicle.is_available == available)
    if active is not None:
        query = query.filter(Vehicle.active_status == active)
    return [vehicle_dict(vehicle) for vehicle in (await db.execute(query)).scalars().all()]


@internal_router.get("/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: str, db=Depends(get_db)):
    vehicle = (await db.execute(select(Vehicle).filter(Vehicle.vehicleid == vehicle_id))).scalars().first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle_dict(vehicle)


@internal_router.patch("/vehicles/{vehicle_id}")
async def update_vehicle(vehicle_id: str, data: VehicleUpdate, db=Depends(get_db)):
    vehicle = (await db.execute(select(Vehicle).filter(Vehicle.vehicleid == vehicle_id))).scalars().first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(vehicle, key, value)
    await db.commit()
    return vehicle_dict(vehicle)
