#!/bin/sh

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting the application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000