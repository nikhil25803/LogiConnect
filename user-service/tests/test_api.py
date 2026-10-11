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


def test_openapi_and_health_contract(client, monkeypatch):
    from main import cache

    monkeypatch.setattr(cache, "get_cache", AsyncMock(return_value={"status": "ok"}))
    assert client.get("/openapi.json").json()["info"]["title"] == "LogiConnect User Service"
    assert client.head("/ping").status_code == 200
    assert client.get("/head").json() == {"status": "ok"}


def test_user_routes(client, monkeypatch):
    from controllers.user_controller import UserController
    import routes.user_route as routes

    monkeypatch.setattr(UserController, "create_user", AsyncMock(return_value={"message": "created"}))
    monkeypatch.setattr(UserController, "login_user", AsyncMock(return_value={"access_token": "token"}))
    monkeypatch.setattr(UserController, "get_user_profile", AsyncMock(return_value={"name": "User"}))
    monkeypatch.setattr(routes, "verification", lambda **_: None)

    onboard = {
        "name": "User", "email": "user@example.com", "country": "IN",
        "state": "KA", "country_code": "+91", "phone_number": "9999999999",
        "password": "secret",
    }
    assert client.post("/user/onboard", json=onboard).status_code == 201
    assert client.post("/user/login", json={"email": "user@example.com", "password": "secret"}).status_code == 200
    assert client.get("/user/profile?user_id=user-1", headers=AUTH).json() == {"name": "User"}
    assert client.get("/user/profile?user_id=user-1").status_code == 422


def test_vehicle_routes(client, monkeypatch):
    from controllers.vehicle_controller import VehicleController
    import routes.vehicle_route as routes

    monkeypatch.setattr(routes, "verification", lambda **_: None)
    monkeypatch.setattr(VehicleController, "search_vehicle", AsyncMock(return_value=[{"vehicle_id": "v1"}]))
    monkeypatch.setattr(VehicleController, "suggest_nearest_driver", AsyncMock(return_value={"driver_id": "d1"}))

    search = {
        "capacity_in_kg": 100, "pickup_latitude": 1, "pickup_longitude": 2,
        "drop_latitude": 3, "drop_longitude": 4,
    }
    assert client.post("/vehicle/search?user_id=u1", headers=AUTH, json=search).status_code == 200
    assert client.get("/vehicle/search/driver?vehicle_id=v1&user_id=u1", headers=AUTH).status_code == 200
    assert client.post("/vehicle/search?user_id=u1", json=search).status_code == 422


def test_booking_routes(client, monkeypatch):
    from controllers.booking_controller import BookingsController
    import routes.booking_route as routes

    monkeypatch.setattr(routes, "verification", lambda **_: None)
    monkeypatch.setattr(BookingsController, "__init__", lambda self, db: None)
    monkeypatch.setattr(BookingsController, "get_coordinates", AsyncMock(return_value={"pickup": [1, 2]}))
    monkeypatch.setattr(BookingsController, "create_booking", AsyncMock(return_value={"booking_id": "b1"}))
    monkeypatch.setattr(BookingsController, "get_user_bookings", AsyncMock(return_value=[]))
    monkeypatch.setattr(BookingsController, "update_order_status", AsyncMock(return_value={"order_status": "Received"}))

    assert client.get("/booking/coordinates?pickup_address=A&drop_address=B&user_id=u1", headers=AUTH).status_code == 200
    booking = {"user_id": "u1", "vehicle_id": "v1", "driver_id": "d1", "pickup_location": "A", "drop_location": "B"}
    assert client.post("/booking/new?user_id=u1", headers=AUTH, json=booking).status_code == 201
    assert client.get("/booking/?user_id=u1", headers=AUTH).status_code == 200
    assert client.put("/booking/update-order-status?booking_id=b1&new_status=Received&user_id=u1", headers=AUTH).status_code == 200
    assert client.get("/booking/?user_id=u1").status_code == 422


def test_validation_and_controller_failure(client, monkeypatch):
    from controllers.user_controller import UserController

    assert client.post("/user/login", json={}).status_code == 422
    monkeypatch.setattr(UserController, "login_user", AsyncMock(side_effect=RuntimeError("failed")))
    response = client.post("/user/login", json={"email": "user@example.com", "password": "secret"})
    assert response.status_code == 500
