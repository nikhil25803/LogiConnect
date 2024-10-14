from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.models import Driver, Vehicle
from uuid import uuid4
from utils.hashing import get_password_hash, verify_password
from utils.token import create_access_token, verification
from models.schema import DriverOnboard, DriverLogin, AddVehicle


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

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "driverid": driver.driverid,
        }

    def get_driver_details(self, driver_id: str, authorization: str):
        driver = self.db.query(Driver).filter(Driver.driverid == driver_id).first()

        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        verification(
            token=authorization.split(" ")[1], role="driver", entity_id=driver_id
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
        driver = self.db.query(Driver).filter(Driver.driverid == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        verification(
            token=authorization.split(" ")[1], role="driver", entity_id=driver_id
        )

        for key, value in data.items():
            if value is not None:
                setattr(driver, key, value)

        self.db.commit()
        self.db.refresh(driver)

        return {"message": "User data updated successfully"}

    def add_vehicle(self, driver_id: str, vehicle_data: AddVehicle, authorization: str):
        driver = self.db.query(Driver).filter(Driver.driverid == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        verification(
            token=authorization.split(" ")[1], role="driver", entity_id=driver_id
        )

        existing_vehicle = (
            self.db.query(Vehicle)
            .filter(Vehicle.registration_number == vehicle_data.registration_number)
            .first()
        )
        if existing_vehicle:
            raise HTTPException(
                status_code=400,
                detail="Vehicle with this registration number already exists",
            )

        vehicle_id = str(uuid4())
        new_vehicle = Vehicle(
            vehicleid=vehicle_id,
            driverid=driver.id,
            model=vehicle_data.model,
            registration_number=vehicle_data.registration_number,
            capacity=vehicle_data.capacity,
            availability=vehicle_data.availability,
            cost_per_km=vehicle_data.cost_per_km,
        )

        self.db.add(new_vehicle)
        self.db.commit()
        self.db.refresh(new_vehicle)

        return {"message": "Vehicle added successfully"}

    def get_driver_vehicles(self, driver_id: str, authorization: str):
        driver = self.db.query(Driver).filter(Driver.driverid == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        verification(
            token=authorization.split(" ")[1], role="driver", entity_id=driver_id
        )

        vehicles = self.db.query(Vehicle).filter(Vehicle.driverid == driver.id).all()

        if not vehicles:
            raise HTTPException(
                status_code=404, detail="No vehicles found for this driver"
            )

        vehicle_list = [
            {
                "vehicleid": vehicle.vehicleid,
                "model": vehicle.model,
                "registration_number": vehicle.registration_number,
                "capacity": vehicle.capacity,
                "availability": vehicle.availability,
                "cost_per_km": vehicle.cost_per_km,
            }
            for vehicle in vehicles
        ]

        return {
            "driver_id": driver_id,
            "vehicles": vehicle_list,
        }

    def update_vehicle_details(
        self, driver_id: str, vehicle_id: str, data: dict, authorization: str
    ):
        driver = self.db.query(Driver).filter(Driver.driverid == driver_id).first()
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")

        verification(
            token=authorization.split(" ")[1], role="driver", entity_id=driver_id
        )

        vehicle = self.db.query(Vehicle).filter(Vehicle.vehicleid == vehicle_id).first()

        if not vehicle:
            raise HTTPException(status_code=404, detail="Invalid vehicle ID")

        for key, value in data.items():
            if value is not None:
                setattr(vehicle, key, value)

        self.db.commit()
        self.db.refresh(vehicle)

        return {"message": "Vehicle data updated successfully"}
