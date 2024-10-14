from fastapi import APIRouter, HTTPException, Depends, Header, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import EmailStr
from typing import Optional
from config.database import get_db
from models.models import Driver
from models.schema import DriverLogin, DriverOnboard, DriverUpdate
from controllers.driver_controller import DriverController


driver_router = APIRouter(prefix="/driver", tags=["driver"])


@driver_router.post("/onboard")
def onboard_driver(driver: DriverOnboard, db: Session = Depends(get_db)):
    driver_instance = DriverController(db)
    try:
        onboard_response = driver_instance.onboard_driver(driver)
        return JSONResponse(content=onboard_response, status_code=201)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@driver_router.post("/login")
def login_driver(driver_login: DriverLogin, db: Session = Depends(get_db)):
    driver_instance = DriverController(db)
    try:
        token = driver_instance.login_driver(driver_login)
        return JSONResponse(content=token, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@driver_router.get("/profile")
def get_driver_details(
    driver_id: str = Query(...),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    driver_instance = DriverController(db)
    try:
        driver_profile = driver_instance.get_driver_details(driver_id, authorization)
        return JSONResponse(content=driver_profile, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@driver_router.put("/update")
def update_driver_details(
    data: DriverUpdate,
    driver_id: str,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    driver_instance = DriverController(db)
    try:
        data_to_update = data.model_dump(exclude_unset=True)
        update_response = driver_instance.update_driver_details(
            driver_id, data_to_update, authorization
        )
        return JSONResponse(content=update_response, status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})
