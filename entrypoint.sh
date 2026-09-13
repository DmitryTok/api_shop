#!/bin/sh

set -e

echo "--> Collect staticfiles..."
python api_shop/manage.py collectstatic --no-input

echo "--> Applying database migrations..."
python api_shop/manage.py migrate

export PORT="${PORT:-8000}"
echo "--> Rendering nginx config for PORT=${PORT}..."
envsubst '${PORT}' < /app/nginx/prod.conf.template > /etc/nginx/conf.d/default.conf

echo "--> Starting nginx + Gunicorn via supervisord..."
exec supervisord -c /app/supervisord.conf
