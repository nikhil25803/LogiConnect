from fastapi import FastAPI, Request, HTTPException
import httpx
from contextlib import asynccontextmanager

app = FastAPI()

# Create a reusable async client session for performance and connection pooling
client = httpx.AsyncClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup: Create client connection before handling requests
    yield
    # Teardown: Close the client connection after handling requests
    await client.aclose()

app.lifespan = lifespan

async def proxy(request: Request, service_url: str):
    try:
        # Determine the HTTP method and make the appropriate request
        if request.method == "GET":
            response = await client.get(service_url, params=request.query_params)
        elif request.method == "POST":
            response = await client.post(service_url, json=await request.json())
        elif request.method == "PUT":
            response = await client.put(service_url, json=await request.json())
        elif request.method == "DELETE":
            response = await client.delete(service_url)
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")

        # Raise an error if the response was unsuccessful
        response.raise_for_status()

        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(request: Request, full_path: str):
    # Determine the service URL based on the request path
    if full_path.startswith("user/"):
        service_url = f"http://user-service:8000/{full_path}"
    elif full_path.startswith("driver/"):
        service_url = f"http://driver-service:8000/{full_path}"
    elif full_path.startswith("admin/"):
        service_url = f"http://admin-service:8000/{full_path}"
    else:
        raise HTTPException(status_code=404, detail="Service not found")

    return await proxy(request, service_url)
