#!/bin/sh

set -e

echo "--> Collect staticfiles..."
python api_shop/manage.py collectstatic --no-input

echo "--> Applying database migrations..."
python api_shop/manage.py migrate

echo "--> Starting Gunicorn..."

exec /opt/venv/bin/gunicorn --bind 0.0.0.0:"${PORT:-8000}" --workers 3 --chdir /app/api_shop api_shop.wsgi:application
