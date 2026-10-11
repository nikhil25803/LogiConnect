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


def test_internal_routes_are_protected_and_hidden(client):
    assert client.get("/internal/bookings?driver_id=d1").status_code == 401
    assert client.get("/internal/bookings?driver_id=d1", headers={"X-Internal-API-Key": "wrong"}).status_code == 401
    paths = client.get("/openapi.json").json()["paths"]
    assert not any(path.startswith("/internal") for path in paths)


def test_strict_role_and_entity_authorization():
    from fastapi import HTTPException
    from utils.token import create_access_token, verification

    token = create_access_token({"userid": "u1", "role": "User"})
    verification(token, "user", "u1")
    for role, entity in (("driver", "u1"), ("user", "u2")):
        try:
            verification(token, role, entity)
            assert False, "verification should reject a mismatched identity"
        except HTTPException as exc:
            assert exc.status_code == 401


def test_booking_uses_upstream_records_and_snapshots_driver(monkeypatch):
    from controllers.booking_controller import BookingsController
    from models.models import Users
    import controllers.booking_controller as controller_module

    result = MagicMock()
    result.scalar_one_or_none.return_value = Users(userid="u1")
    db = MagicMock()
    db.execute = AsyncMock(return_value=result)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    added = []
    db.add.side_effect = added.append

    async def upstream(method, base, path, **kwargs):
        if "drivers" in path:
            return {"name": "Driver", "email": "d@example.com", "mobile": "999"}
        return {"current_latitude": 1, "current_longitude": 2, "fuel_type": "Diesel"}

    monkeypatch.setattr(controller_module, "internal_request", upstream)
    controller = BookingsController(db)
    controller.logistic_calculator.calculate_distance_time_price = MagicMock(return_value={
        "pickup_coordinates": [1, 2], "drop_coordinates": [3, 4], "total_distance_km": 10,
        "estimated_delivery_time": 1, "base_price": 100, "gst": 28,
        "platform_fee": 15, "total_price": 143,
    })
    data = MagicMock(user_id="u1", driver_id="d1", vehicle_id="v1", pickup_location="A", drop_location="B")
    response = asyncio.run(controller.create_booking(data))
    assert response["message"] == "Booking has been successfully created"
    assert added[0].driver_name == "Driver"
    assert added[0].driver_email == "d@example.com"
