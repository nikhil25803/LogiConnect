from celery import Celery
import asyncio


celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
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
