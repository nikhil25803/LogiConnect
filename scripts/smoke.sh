#!/usr/bin/env bash
set -euo pipefail

base_url="${BASE_URL:-http://127.0.0.1:3000}"

admin_token="$(curl -fsS -X POST "$base_url/admin/login" -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"change-me"}' | jq -r .access_token)"

vehicle_id="$(curl -fsS -X POST "$base_url/logistics/vehicle/add" \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $admin_token" \
  -d '{"model_name":"Smoke Truck","capacity_in_kg":1000,"registration_number":"SMOKE-001","current_latitude":12.9716,"current_longitude":77.5946,"is_available":true,"active_status":true,"fuel_type":"Diesel"}' | jq -r .vehicleid)"

driver_id="$(curl -fsS -X POST "$base_url/logistics/driver/add" \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $admin_token" \
  -d '{"driverid":null,"name":"Smoke Driver","email":"driver.smoke@example.com","mobile":"9000000001","country":"IN","state":"KA","current_latitude":12.972,"current_longitude":77.595,"regions_available":["KA"],"availability":true,"password":"smoke-secret","country_code":"+91"}' | jq -r .driverid)"

test "$(curl -fsS "$base_url/logistics/driver/all" -H "Authorization: Bearer $admin_token" | jq -r .total_count)" = "1"

driver_login="$(curl -fsS -X POST "$base_url/driver/login" -H 'Content-Type: application/json' \
  -d '{"email":"driver.smoke@example.com","password":"smoke-secret"}')"
driver_token="$(jq -r .access_token <<<"$driver_login")"
test "$(curl -fsS "$base_url/driver/profile?driver_id=$driver_id" -H "Authorization: Bearer $driver_token" | jq -r .role)" = "driver"

curl -fsS -X POST "$base_url/user/onboard" -H 'Content-Type: application/json' \
  -d '{"name":"Smoke User","email":"user.smoke@example.com","country":"IN","state":"KA","country_code":"+91","phone_number":"9000000002","password":"smoke-secret"}' >/dev/null
user_login="$(curl -fsS -X POST "$base_url/user/login" -H 'Content-Type: application/json' \
  -d '{"email":"user.smoke@example.com","password":"smoke-secret"}')"
user_token="$(jq -r .access_token <<<"$user_login")"
user_id="$(jq -r .userid <<<"$user_login")"
test "$(curl -fsS "$base_url/user/profile?user_id=$user_id" -H "Authorization: Bearer $user_token" | jq -r .role)" = "user"

test "$(curl -fsS -X POST "$base_url/vehicle/search?user_id=$user_id" \
  -H 'Content-Type: application/json' -H "Authorization: Bearer $user_token" \
  -d '{"capacity_in_kg":500,"pickup_latitude":12.9716,"pickup_longitude":77.5946,"drop_latitude":13.0,"drop_longitude":77.6}' | jq 'length')" = "1"
test "$(curl -fsS "$base_url/vehicle/search/driver?vehicle_id=$vehicle_id&user_id=$user_id" \
  -H "Authorization: Bearer $user_token" | jq -r .driver_id)" = "$driver_id"

echo "Gateway smoke flow passed."
