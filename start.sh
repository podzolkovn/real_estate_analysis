#!/bin/sh

set -e
echo "Run Migrations"
alembic upgrade head

echo "Starting FastAPI..."
exec uvicorn app.main:app --workers 3 --host 0.0.0.0 --port 12005 --log-config logging_config.yaml