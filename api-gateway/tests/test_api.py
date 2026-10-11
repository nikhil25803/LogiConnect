from unittest.mock import AsyncMock

import httpx
from fastapi.testclient import TestClient

from main import app


def upstream_response(status=200, body=b'{"ok":true}', content_type="application/json"):
    return httpx.Response(status, content=body, headers={"content-type": content_type})


def test_openapi_metadata(client):
    assert client.get("/openapi.json").json()["info"]["title"] == "LogiConnect API Gateway"


def test_routes_every_service_prefix(client):
    mock_client = AsyncMock()
    mock_client.request.return_value = upstream_response()
    app.state.client = mock_client

    expected = {
        "/user/profile": "http://user-service:3001/user/profile",
        "/vehicle/search": "http://user-service:3001/vehicle/search",
        "/booking/": "http://user-service:3001/booking/",
        "/driver/profile": "http://driver-service:3002/driver/profile",
        "/admin/login": "http://admin-service:3003/admin/login",
        "/logistics/vehicle/all": "http://admin-service:3003/logistics/vehicle/all",
    }
    for path, url in expected.items():
        assert client.get(path).status_code == 200
        assert mock_client.request.await_args.kwargs["url"] == url


def test_forwards_method_query_body_and_authorization(client):
    mock_client = AsyncMock()
    mock_client.request.return_value = upstream_response(status=201)
    app.state.client = mock_client

    response = client.post(
        "/booking/new?user_id=u1",
        content=b'{"vehicle_id":"v1"}',
        headers={"Authorization": "Bearer token", "Content-Type": "application/json"},
    )
    forwarded = mock_client.request.await_args.kwargs
    assert response.status_code == 201
    assert forwarded["method"] == "POST"
    assert str(forwarded["params"]) == "user_id=u1"
    assert forwarded["content"] == b'{"vehicle_id":"v1"}'
    assert forwarded["headers"]["authorization"] == "Bearer token"


def test_preserves_upstream_error_and_content_type(client):
    mock_client = AsyncMock()
    mock_client.request.return_value = upstream_response(404, b"missing", "text/plain")
    app.state.client = mock_client

    response = client.get("/driver/missing")
    assert response.status_code == 404
    assert response.text == "missing"
    assert response.headers["content-type"].startswith("text/plain")


def test_unknown_path_and_unavailable_upstream(client):
    assert client.get("/unknown/path").status_code == 404

    mock_client = AsyncMock()
    mock_client.request.side_effect = httpx.ConnectError("offline")
    app.state.client = mock_client
    response = client.get("/user/profile")
    assert response.status_code == 502


def test_lifespan_closes_http_client():
    captured = {}

    with TestClient(app):
        captured["client"] = app.state.client

    assert captured["client"].is_closed
