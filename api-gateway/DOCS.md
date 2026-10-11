# API Gateway

The gateway exposes the backend through `http://localhost:3000` and preserves upstream status codes, bodies, content types, query parameters, and authorization/content headers.

- Swagger: `http://localhost:3000/docs`
- ReDoc: `http://localhost:3000/redoc`
- OpenAPI: `http://localhost:3000/openapi.json`

The gateway's OpenAPI page documents the proxy entry point. Use each service's `DOCS.md` or direct Swagger page for the complete domain API contract.

## Routing

| Path prefixes | Destination |
| --- | --- |
| `/user`, `/vehicle`, `/booking` | User Service |
| `/driver` | Driver Service |
| `/admin`, `/logistics` | Admin Service |

Unknown prefixes return `404`. A network failure connecting to an upstream service returns `502`; HTTP errors returned by a reachable service are passed through unchanged.

## Configuration

| Variable | Docker Compose value |
| --- | --- |
| `USER_SERVICE_URL` | `http://user-service:3001` |
| `DRIVER_SERVICE_URL` | `http://driver-service:3002` |
| `ADMIN_SERVICE_URL` | `http://admin-service:3003` |

## Example

```bash
curl 'http://localhost:3000/vehicle/search/driver?vehicle_id=<vehicle-id>&user_id=<user-id>' \
  -H 'Authorization: Bearer <access-token>'
```
