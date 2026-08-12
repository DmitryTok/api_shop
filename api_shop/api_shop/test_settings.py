from .settings import *

DATABASES["default"].update(
    {
        "NAME": "test_postgres",
        "HOST": "test_db",
        "PORT": 5432,
    }
)

REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []

STORAGES["default"] = {
    "BACKEND": "django.core.files.storage.FileSystemStorage",
}
