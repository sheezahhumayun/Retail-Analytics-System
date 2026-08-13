#!/bin/sh
set -e
echo "Running database migrations..."
alembic -c database/alembic.ini upgrade head
echo "Starting backend API..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
