#!/bin/sh

set -e

echo "--> Collect staticfiles..."
python api_shop/manage.py collectstatic --no-input

echo "--> Create DB Tables..."
python api_shop/manage.py migrate

echo "--> Create ADMIN User"
python api_shop/manage.py create_default_superuser || echo "ADMIN User already exists"

echo "--> Start Uvicorn..."

exec /opt/venv/bin/gunicorn --bind 0.0.0.0:$PORT --workers 3 --worker-class uvicorn.workers.UvicornWorker --chdir /app/api_shop api_shop.asgi:application