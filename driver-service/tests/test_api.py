import asyncio
from unittest.mock import AsyncMock, MagicMock


AUTH = {"Authorization": "Bearer test-token"}


def test_cache_uses_json_and_expiry():
    from config.cache import RedisCache

    cache = RedisCache()
    cache.cache = AsyncMock()
    asyncio.run(cache.set_cache("key", {"status": "ok"}))
    cache.cache.set.assert_awaited_once_with("key", '{"status": "ok"}', ex=600)
    cache.cache.get.return_value = '{"status": "ok"}'
    assert asyncio.run(cache.get_cache("key")) == {"status": "ok"}


def test_openapi_health_and_removed_seed_route(client, monkeypatch):
    from main import cache

    monkeypatch.setattr(cache, "get_cache", AsyncMock(return_value={"status": "ok"}))
    assert client.get("/openapi.json").json()["info"]["title"] == "LogiConnect Driver Service"
    assert client.head("/ping").status_code == 200
    assert client.get("/head").status_code == 200
    assert client.post("/driver/populate").status_code == 404


def test_driver_routes(client, monkeypatch):
    from controllers.driver_controller import DriverController
    import routes.driver_routes as routes

    monkeypatch.setattr(routes, "verification", lambda **_: None)
    monkeypatch.setattr(DriverController, "login_driver", AsyncMock(return_value={"access_token": "token"}))
    monkeypatch.setattr(DriverController, "get_driver_profile", AsyncMock(return_value={"name": "Driver"}))
    monkeypatch.setattr(DriverController, "get_driver_bookings", AsyncMock(return_value=[{"booking_id": "b1"}]))
    monkeypatch.setattr(DriverController, "update_booking_status", AsyncMock(return_value={"request_status": "Accepted"}))

    assert client.post("/driver/login", json={"email": "driver@example.com", "password": "secret"}).status_code == 200
    assert client.get("/driver/profile?driver_id=d1", headers=AUTH).status_code == 200
    assert client.get("/driver/booking?driver_id=d1&request_status=All", headers=AUTH).status_code == 200
    update = "/driver/booking?driver_id=d1&booking_id=b1&status_type=Request&update_to=Accepted"
    assert client.put(update, headers=AUTH).status_code == 200


def test_driver_auth_and_validation_failures(client):
    assert client.get("/driver/profile?driver_id=d1").status_code == 422
    assert client.get("/driver/booking?driver_id=d1&request_status=All").status_code == 422
    assert client.post("/driver/login", json={}).status_code == 422


def test_driver_controller_failure_is_preserved(client, monkeypatch):
    from controllers.driver_controller import DriverController

    monkeypatch.setattr(DriverController, "login_driver", AsyncMock(side_effect=RuntimeError("failed")))
    response = client.post("/driver/login", json={"email": "driver@example.com", "password": "secret"})
    assert response.status_code == 500


def test_internal_routes_are_protected_and_hidden(client):
    assert client.get("/internal/drivers").status_code == 401
    assert client.get("/internal/drivers", headers={"X-Internal-API-Key": "wrong"}).status_code == 401
    assert not any(path.startswith("/internal") for path in client.get("/openapi.json").json()["paths"])


def test_admin_provisioned_password_is_hashed_and_not_returned():
    from controllers.driver_controller import DriverController
    from utils.hashing import verify_password

    result = MagicMock()
    result.scalars.return_value.first.return_value = None
    db = MagicMock()
    db.execute = AsyncMock(return_value=result)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    added = []
    db.add.side_effect = added.append
    data = {
        "name": "Driver", "email": "driver@example.com", "mobile": "999", "country": "IN",
        "state": "KA", "current_latitude": 1, "current_longitude": 2,
        "regions_available": ["KA"], "availability": True, "password": "secret", "country_code": "+91",
    }
    response = asyncio.run(DriverController(db).create_driver(data))
    assert "password" not in response
    assert added[0].password != "secret"
    assert verify_password("secret", added[0].password)


def test_upstream_failure_is_preserved(monkeypatch):
    from fastapi import HTTPException
    from controllers.driver_controller import DriverController
    import controllers.driver_controller as controller_module
    from models.models import Driver

    result = MagicMock()
    result.scalars.return_value.first.return_value = Driver(driverid="d1")
    db = AsyncMock()
    db.execute.return_value = result
    monkeypatch.setattr(controller_module, "internal_request", AsyncMock(side_effect=HTTPException(status_code=503, detail="down")))
    try:
        asyncio.run(DriverController(db).get_driver_bookings("d1", "All"))
        assert False, "upstream failure should propagate"
    except HTTPException as exc:
        assert exc.status_code == 503


def test_booking_status_transitions_update_owned_driver_and_vehicle(monkeypatch):
    from controllers.driver_controller import DriverController
    import controllers.driver_controller as controller_module
    from models.models import Driver

    driver = Driver(driverid="d1", availability=True, current_latitude=1, current_longitude=2)
    result = MagicMock()
    result.scalars.return_value.first.return_value = driver
    db = MagicMock()
    db.execute = AsyncMock(return_value=result)
    db.commit = AsyncMock()
    upstream = AsyncMock(side_effect=[
        {"booking_id": "b1", "vehicle_id": "v1", "request_status": "Accepted",
         "delivery_status": "Pending Pickup", "drop_latitude": 3, "drop_longitude": 4},
        {},
        {"booking_id": "b1", "vehicle_id": "v1", "request_status": "Accepted",
         "delivery_status": "Delivered", "drop_latitude": 3, "drop_longitude": 4},
        {},
    ])
    monkeypatch.setattr(controller_module, "internal_request", upstream)
    controller = DriverController(db)

    accepted = asyncio.run(controller.update_booking_status("d1", "b1", "Request", "Accepted"))
    assert accepted["request_status"] == "Accepted"
    assert driver.availability is False

    delivered = asyncio.run(controller.update_booking_status("d1", "b1", "Delivery", "Delivered"))
    assert delivered["delivery_status"] == "Delivered"
    assert (driver.current_latitude, driver.current_longitude) == (3, 4)
    assert upstream.await_count == 4
