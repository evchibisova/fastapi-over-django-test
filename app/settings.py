import os

SECRET_KEY = "demo-not-secret"
DEBUG = True
USE_TZ = True

INSTALLED_APPS = ["app.infrastructure"]
ROOT_URLCONF = "app.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "demo"),
        "USER": os.environ.get("POSTGRES_USER", "demo"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "demo"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
