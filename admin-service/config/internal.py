import os
import secrets

import httpx
from fastapi import Header, HTTPException, status


_client: httpx.AsyncClient | None = None


async def start_internal_client():
    global _client
    _client = httpx.AsyncClient(timeout=10.0)


async def close_internal_client():
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def internal_request(method: str, base_url: str, path: str, **kwargs):
    global _client
    if _client is None:
        await start_internal_client()
    headers = kwargs.pop("headers", {})
    headers["X-Internal-API-Key"] = os.environ["INTERNAL_API_KEY"]
    try:
        response = await _client.request(method, f"{base_url}{path}", headers=headers, **kwargs)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail="Internal service unavailable") from exc
    if response.is_error:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise HTTPException(status_code=response.status_code, detail=detail)
    return response.json()


async def require_internal_key(x_internal_api_key: str | None = Header(None)):
    expected = os.getenv("INTERNAL_API_KEY", "")
    if not expected or not x_internal_api_key or not secrets.compare_digest(x_internal_api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid internal API key")
