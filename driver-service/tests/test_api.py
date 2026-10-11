import asyncio
from unittest.mock import AsyncMock


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
