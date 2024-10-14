from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.models import Driver
from uuid import uuid4
from utils.hashing import get_password_hash, verify_password
from utils.token import create_access_token, decode_access_token
from models.schema import DriverOnboard, DriverLogin, DriverUpdate, DriverProfile


class DriverController:
    def __init__(self, db: Session):
        self.db = db

    def onboard_driver(self, driver: DriverOnboard):
        # Check if the email or mobile already exists
        existing_driver = (
            self.db.query(Driver)
            .filter((Driver.email == driver.email) | (Driver.mobile == driver.mobile))
            .first()
        )
        if existing_driver:
            raise HTTPException(status_code=400, detail="Driver already exists")

        entity_id = str(uuid4())
        hashed_password = get_password_hash(driver.password)

        new_driver = Driver(
            driverid=entity_id,
            availability=driver.availability,
            name=driver.name,
            email=driver.email,
            state=driver.state,
            country=driver.country,
            country_code=driver.country_code,
            mobile=driver.mobile,
            regions=driver.regions if driver.regions else [],
            password=hashed_password,
            role="driver",
        )

        self.db.add(new_driver)
        self.db.commit()
        self.db.refresh(new_driver)

        return {
            "message": "Driver onboarded successfully",
            "driver_id": new_driver.driverid,
        }

    def login_driver(self, driver_login: DriverLogin):
        driver = (
            self.db.query(Driver).filter(Driver.email == driver_login.email).first()
        )

        if not driver:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials",
            )

        if not verify_password(driver_login.password, driver.password):
            raise HTTPException(
                status_code=401,
                detail="Invalid password",
            )

        access_token = create_access_token(
            data={
                "driverid": driver.driverid,
                "email": driver.email,
                "name": driver.name,
                "role": driver.role,
            }
        )

        return {"access_token": access_token, "token_type": "bearer"}

    def get_driver_details(self, driver_id: str, authorization: str):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        driver_id_from_token = payload.get("driverid")

        driver = self.db.query(Driver).filter(Driver.driverid == driver_id).first()

        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        if driver.driverid != driver_id_from_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access",
            )

        return {
            "name": driver.name,
            "email": driver.email,
            "country": driver.country,
            "state": driver.state,
            "phone_number": driver.mobile,
            "regions": driver.regions,
            "role": driver.role,
        }

    def update_driver_details(self, driver_id: str, data: dict, authorization: str):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        driver_id_from_token = payload.get("driverid")

        driver = self.db.query(Driver).filter(Driver.driverid == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        if driver.driverid != driver_id_from_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access",
            )

        for key, value in data.items():
            if value is not None:
                setattr(driver, key, value)

        self.db.commit()
        self.db.refresh(driver)

        return {"message": "User data updated successfully"}
