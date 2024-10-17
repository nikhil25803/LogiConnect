from celery import Celery
import asyncio
import os
from dotenv import load_dotenv


load_dotenv()

CELERY_BROKER = os.getenv("CELERY_BROKER")
CELERY_BACKEND = os.getenv("CELERY_BACKEND")


celery_app = Celery(
    "tasks",
    broker=CELERY_BROKER,
    backend=CELERY_BACKEND,
)


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)


async def async_task():
    await asyncio.sleep(10)
    print("Hello from background task")


@celery_app.task
def background_task():
    loop = asyncio.get_event_loop()
    loop.create_task(async_task())
