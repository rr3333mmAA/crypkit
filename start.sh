#!/bin/sh

if [ -z "${DATABASE_URL}" ]; then
  echo "ERROR: DATABASE_URL environment variable is not set!"
  exit 1
fi

DB_HOST=$(echo "${DATABASE_URL}" | sed -E 's/.*@([^:]+):.*/\1/')
DB_PORT=$(echo "${DATABASE_URL}" | sed -E 's/.*:([0-9]+)\/.*/\1/')

echo "Extracted database connection info - Host: ${DB_HOST}, Port: ${DB_PORT}"
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z "${DB_HOST}" "${DB_PORT}"; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting the application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000