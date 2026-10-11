from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select

from config.database import get_db
from config.internal import require_internal_key
from controllers.driver_controller import DriverController, public_driver
from models.models import Driver
from models.schema import DriverOnboard


internal_router = APIRouter(prefix="/internal", dependencies=[Depends(require_internal_key)], include_in_schema=False)


class DriverUpdate(BaseModel):
    availability: bool | None = None
    current_latitude: float | None = None
    current_longitude: float | None = None


@internal_router.post("/drivers", status_code=201)
async def create_driver(data: DriverOnboard, db=Depends(get_db)):
    return await DriverController(db).create_driver(data.model_dump())


@internal_router.get("/drivers")
async def list_drivers(
    available: bool | None = None, limit: int | None = Query(None), offset: int = 0, db=Depends(get_db)
):
    query = select(Driver)
    if available is not None:
        query = query.filter(Driver.availability == available)
    if limit is not None:
        query = query.limit(limit).offset(offset)
    drivers = (await db.execute(query)).scalars().all()
    items = [public_driver(driver) for driver in drivers]
    if limit is None:
        return items
    total = (await db.execute(select(func.count(Driver.id)))).scalar()
    return {"total_count": total, "total_pages": (total + limit - 1) // limit,
            "current_page": offset // limit + 1, "next_page": offset + limit < total,
            "prev_page": offset > 0, "drivers": items}


@internal_router.get("/drivers/{driver_id}")
async def get_driver(driver_id: str, db=Depends(get_db)):
    driver = (await db.execute(select(Driver).filter(Driver.driverid == driver_id))).scalars().first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return public_driver(driver)


@internal_router.patch("/drivers/{driver_id}")
async def update_driver(driver_id: str, data: DriverUpdate, db=Depends(get_db)):
    driver = (await db.execute(select(Driver).filter(Driver.driverid == driver_id))).scalars().first()
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    for key, value in data.model_dump(exclude_none=True).items():
        setattr(driver, key, value)
    await db.commit()
    return public_driver(driver)
