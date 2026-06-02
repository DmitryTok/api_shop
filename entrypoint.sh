#!/bin/sh

set -e

echo "--> Collect staticfiles..."
python api_shop/manage.py collectstatic --no-input

echo "--> Create DB Tables..."
python api_shop/manage.py migrate

echo "--> Create ADMIN User"
python api_shop/manage.py create_default_superuser || echo "Суперпользователь уже существует или ошибка создания"

echo "--> Start Gunicorn..."
exec /opt/venv/bin/gunicorn --bind 0.0.0.0:$PORT --chdir /app api_shop.wsgi:application