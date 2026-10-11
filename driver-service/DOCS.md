# Driver Service API

The driver service owns driver authentication, profiles, assigned bookings, and delivery status transitions. Direct base URL: `http://localhost:3002`; gateway base URL: `http://localhost:3000`.

- Swagger: `http://localhost:3002/docs`
- ReDoc: `http://localhost:3002/redoc`
- OpenAPI: `http://localhost:3002/openapi.json`

## Configuration

Required variables are `DB_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REDIS_HOST`, `REDIS_PORT`, `CELERY_BROKER`, and `CELERY_BACKEND`.

## Endpoints

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| POST | `/driver/login` | None | Return a driver bearer token |
| GET | `/driver/profile?driver_id=...` | Driver bearer token | Return a driver profile |
| GET | `/driver/booking?driver_id=...&request_status=...` | Driver bearer token | List assigned bookings by request status |
| PUT | `/driver/booking?driver_id=...&booking_id=...&status_type=...&update_to=...` | Driver bearer token | Update request or delivery status |
| GET | `/head` | None | Exercise database/cache dependencies |
| HEAD | `/ping` | None | Service liveness check |

`request_status` accepts the service's existing `All`, `Pending`, `Accepted`, `Rejected`, and `Completed` values. Booking updates use `status_type=Request` or `status_type=Delivery` and the existing controller validation.

## Example

```bash
curl 'http://localhost:3000/driver/booking?driver_id=<driver-id>&request_status=Pending' \
  -H 'Authorization: Bearer <access-token>'
```

Validation errors use FastAPI's `422` response format. Retained application errors use the status and `detail` response currently defined by the service.
