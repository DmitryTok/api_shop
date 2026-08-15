import os

from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse


def health_check(request):
    """Used by Render's health check and manual smoke tests.

    Database is a hard dependency: if it's unreachable the app genuinely
    can't function, so this returns 503 (Render will restart the service).
    Redis is a soft dependency: it backs email activation/password-reset
    codes, but the rest of the API still works without it, and restarting
    the whole service wouldn't fix a Redis outage anyway — so a Redis
    failure is reported in the body without failing the check.
    """
    db_healthy = True
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
    except OperationalError:
        db_healthy = False

    redis_healthy = True
    try:
        cache_key = "health_check_probe"
        cache.set(cache_key, "ok", timeout=5)
        redis_healthy = cache.get(cache_key) == "ok"
    except Exception:
        redis_healthy = False

    payload = {
        "status": "ok" if db_healthy else "error",
        "database": "ok" if db_healthy else "unreachable",
        "redis": "ok" if redis_healthy else "unreachable",
        "environment": settings.APP_ENV,
        "version": os.getenv("RENDER_GIT_COMMIT", "unknown"),
    }

    return JsonResponse(payload, status=200 if db_healthy else 503)
