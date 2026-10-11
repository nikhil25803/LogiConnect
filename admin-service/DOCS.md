# Admin Service API

The admin service owns administrative authentication and vehicle/driver fleet management. Direct base URL: `http://localhost:3003`; gateway base URL: `http://localhost:3000`.

- Swagger: `http://localhost:3003/docs`
- ReDoc: `http://localhost:3003/redoc`
- OpenAPI: `http://localhost:3003/openapi.json`

## Configuration

Required variables are `DB_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `REDIS_HOST`, `REDIS_PORT`, `CELERY_BROKER`, and `CELERY_BACKEND`.

## Endpoints

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| POST | `/admin/login` | None | Return an admin bearer token |
| POST | `/logistics/vehicle/add` | Admin bearer token | Add a vehicle |
| GET | `/logistics/vehicle/all?limit=10&offset=0` | Admin bearer token | List vehicles with pagination metadata |
| POST | `/logistics/driver/add` | Admin bearer token | Add a driver |
| GET | `/logistics/driver/all?limit=10&offset=0` | Admin bearer token | List drivers with pagination metadata |
| GET | `/head` | None | Exercise database/cache dependencies |
| HEAD | `/ping` | None | Service liveness check |

## Example

```bash
curl -X POST http://localhost:3000/admin/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"change-me"}'

curl 'http://localhost:3000/logistics/vehicle/all?limit=10&offset=0' \
  -H 'Authorization: Bearer <access-token>'
```

Validation errors use FastAPI's `422` response format. Retained application errors use the status and `detail` response currently defined by the service.
