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
    assert client.get("/openapi.json").json()["info"]["title"] == "LogiConnect Admin Service"
    assert client.head("/ping").status_code == 200
    assert client.get("/head").status_code == 200
    assert client.post("/logistics/populate-vehicles").status_code == 404


def test_admin_login(client, monkeypatch):
    from controllers.admin_controller import AdminController

    monkeypatch.setattr(AdminController, "login_admin", AsyncMock(return_value={"access_token": "token"}))
    response = client.post("/admin/login", json={"email": "admin@example.com", "password": "secret"})
    assert response.status_code == 200
    assert client.post("/admin/login", json={}).status_code == 422


def test_fleet_routes(client, monkeypatch):
    from controllers.vehicle_driver_controller import VehicleDriverController

    monkeypatch.setattr(VehicleDriverController, "add_vehicle", AsyncMock(return_value={"vehicleid": "v1"}))
    monkeypatch.setattr(VehicleDriverController, "get_all_vehicles", AsyncMock(return_value={
        "total_count": 0, "total_pages": 0, "current_page": 1,
        "next_page": False, "prev_page": False, "vehicles": [],
    }))
    monkeypatch.setattr(VehicleDriverController, "add_driver", AsyncMock(return_value={"driverid": "d1"}))
    monkeypatch.setattr(VehicleDriverController, "get_all_drivers", AsyncMock(return_value={
        "total_count": 0, "total_pages": 0, "current_page": 1,
        "next_page": False, "prev_page": False, "drivers": [],
    }))

    vehicle = {
        "model_name": "Truck", "capacity_in_kg": 1000, "registration_number": "KA01AA0001",
        "current_latitude": 1, "current_longitude": 2, "is_available": True,
        "active_status": True, "fuel_type": "Diesel",
    }
    driver = {
        "driverid": None, "name": "Driver", "email": "driver@example.com", "mobile": "9999999999",
        "country": "IN", "state": "KA", "current_latitude": 1, "current_longitude": 2,
        "regions_available": ["KA"], "availability": True, "password": "secret", "country_code": "+91",
    }
    assert client.post("/logistics/vehicle/add", headers=AUTH, json=vehicle).status_code == 200
    assert client.get("/logistics/vehicle/all", headers=AUTH).status_code == 200
    assert client.post("/logistics/driver/add", headers=AUTH, json=driver).status_code == 200
    assert client.get("/logistics/driver/all", headers=AUTH).status_code == 200
    assert client.get("/logistics/vehicle/all").status_code == 422


def test_admin_controller_failure_is_preserved(client, monkeypatch):
    from controllers.admin_controller import AdminController

    monkeypatch.setattr(AdminController, "login_admin", AsyncMock(side_effect=RuntimeError("failed")))
    response = client.post("/admin/login", json={"email": "admin@example.com", "password": "secret"})
    assert response.status_code == 500
