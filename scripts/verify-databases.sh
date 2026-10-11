#!/usr/bin/env bash
set -euo pipefail

env_file="${COMPOSE_ENV_FILE:-.env}"
if [[ ! -f "$env_file" ]]; then
  env_file=.env.example
fi
compose=(docker compose --env-file "$env_file")

user_tables="$("${compose[@]}" exec -T user-db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "select array_to_string(array_agg(tablename order by tablename), chr(44)) from pg_tables where schemaname=current_schema()"')"
driver_tables="$("${compose[@]}" exec -T driver-db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "select array_to_string(array_agg(tablename order by tablename), chr(44)) from pg_tables where schemaname=current_schema()"')"
admin_tables="$("${compose[@]}" exec -T admin-db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc "select array_to_string(array_agg(tablename order by tablename), chr(44)) from pg_tables where schemaname=current_schema()"')"

test "$user_tables" = "alembic_version,booking_requests,users"
test "$driver_tables" = "alembic_version,drivers"
test "$admin_tables" = "alembic_version,vehicles"

echo "Database ownership verified."
