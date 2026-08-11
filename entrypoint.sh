#!/bin/sh

set -e

echo "--> Collect staticfiles..."
python api_shop/manage.py collectstatic --no-input

echo "--> Create DB Tables..."
python api_shop/manage.py migrate

# echo "--> Load Sizes and Colors"
# python api_shop/manage.py loaddata sizes.json colors.json

echo "--> Load Brands"
python api_shop/manage.py load_brands

echo "--> Load Categories"
python api_shop/manage.py load_category

echo "--> Load Terms"
python api_shop/manage.py load_terms

echo "--> Create ADMIN User"
python api_shop/manage.py create_default_superuser || echo "ADMIN User already exists"

echo "--> Start Uvicorn..."

exec /opt/venv/bin/gunicorn --bind 0.0.0.0:$PORT --workers 3 --chdir /app/api_shop api_shop.wsgi:application
