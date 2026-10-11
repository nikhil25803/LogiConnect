# User Service API

The user service owns user accounts, vehicle and driver discovery, and user-side booking operations. Direct base URL: `http://localhost:3001`; gateway base URL: `http://localhost:3000`.

- Swagger: `http://localhost:3001/docs`
- ReDoc: `http://localhost:3001/redoc`
- OpenAPI: `http://localhost:3001/openapi.json`

## Configuration

Required variables are `DB_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REDIS_HOST`, `REDIS_PORT`, `CELERY_BROKER`, and `CELERY_BACKEND`. `GOOGLE_MAPS_API_KEY` is required for geocoding and route calculations.

## Endpoints

| Method | Path | Authentication | Description |
| --- | --- | --- | --- |
| POST | `/user/onboard` | None | Create a user account |
| POST | `/user/login` | None | Return a user bearer token |
| GET | `/user/profile?user_id=...` | User bearer token | Return the user's profile |
| POST | `/vehicle/search?user_id=...` | User bearer token | Find suitable nearby vehicles and prices |
| GET | `/vehicle/search/driver?vehicle_id=...&user_id=...` | User bearer token | Suggest the nearest available driver |
| GET | `/booking/coordinates?pickup_address=...&drop_address=...&user_id=...` | User bearer token | Geocode pickup and drop addresses |
| POST | `/booking/new?user_id=...` | User bearer token | Create a booking request |
| GET | `/booking/?user_id=...` | User bearer token | List the user's bookings |
| PUT | `/booking/update-order-status?booking_id=...&new_status=...&user_id=...` | User bearer token | Update the order acknowledgement status |
| GET | `/head` | None | Exercise database/cache dependencies |
| HEAD | `/ping` | None | Service liveness check |

## Examples

```bash
curl -X POST http://localhost:3000/user/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"secret"}'

curl 'http://localhost:3000/user/profile?user_id=<user-id>' \
  -H 'Authorization: Bearer <access-token>'
```

Validation errors use FastAPI's `422` response format. Retained application errors use the status and `detail` response currently defined by the service.
