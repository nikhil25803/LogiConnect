from faker import Faker
from uuid import uuid4
from utils.hashing import get_password_hash
from models.models import Driver
from sqlalchemy.ext.asyncio import AsyncSession
import random
import logging
from sqlalchemy.exc import IntegrityError

fake = Faker("en_IN")

INDIAN_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
]


def generate_random_location():
    latitude = random.uniform(8.0, 37.0)
    longitude = random.uniform(68.0, 97.0)
    return latitude, longitude


async def populate_driver_data(db: AsyncSession, num_drivers: int = 1000):
    drivers_added = 0

    for _ in range(num_drivers):
        try:
            hashed_password = get_password_hash("Driver@12345")
            entity_id = str(uuid4())
            current_latitude, current_longitude = generate_random_location()

            driver = Driver(
                driverid=entity_id,
                name=fake.name(),
                email=fake.unique.email(),
                mobile=fake.unique.phone_number(),
                password=hashed_password,
                country="India",
                country_code="+91",
                state=random.choice(INDIAN_STATES),
                current_latitude=current_latitude,
                current_longitude=current_longitude,
                regions_available=[random.choice(INDIAN_STATES) for _ in range(3)],
                availability=True,
                role="driver",
            )

            db.add(driver)
            await db.commit()
            drivers_added += 1

        except IntegrityError as e:
            logging.error(f"Error adding driver: {e}")
            await db.rollback()

    return {
        "message": f"{drivers_added} out of {num_drivers} drivers have been successfully added to the database."
    }
