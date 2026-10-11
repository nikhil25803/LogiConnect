import os
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response


SERVICE_URLS = {
    "user": os.getenv("USER_SERVICE_URL", "http://user-service:3001"),
    "driver": os.getenv("DRIVER_SERVICE_URL", "http://driver-service:3002"),
    "admin": os.getenv("ADMIN_SERVICE_URL", "http://admin-service:3003"),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient()
    yield
    await app.state.client.aclose()


app = FastAPI(
    title="LogiConnect API Gateway",
    description="Single entry point for the LogiConnect backend services.",
    version="1.0.0",
    lifespan=lifespan,
)


def resolve_service(path: str) -> str:
    prefix = path.split("/", 1)[0]
    if prefix in {"user", "vehicle", "booking"}:
        return SERVICE_URLS["user"]
    if prefix == "driver":
        return SERVICE_URLS["driver"]
    if prefix in {"admin", "logistics"}:
        return SERVICE_URLS["admin"]
    raise HTTPException(status_code=404, detail="Service not found")


async def proxy(request: Request, service_url: str) -> Response:
    body = await request.body()
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }

    try:
        upstream = await request.app.state.client.request(
            method=request.method,
            url=service_url,
            params=request.query_params,
            content=body,
            headers=headers,
        )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream service unavailable: {exc}")

    response_headers = {}
    if content_type := upstream.headers.get("content-type"):
        response_headers["content-type"] = content_type

    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=response_headers,
    )


async def gateway(request: Request, full_path: str):
    base_url = resolve_service(full_path)
    return await proxy(request, f"{base_url}/{full_path}")


for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]:
    app.add_api_route(
        "/{full_path:path}",
        gateway,
        methods=[method],
        name=f"gateway_{method.lower()}",
        operation_id=f"gateway_{method.lower()}",
    )
