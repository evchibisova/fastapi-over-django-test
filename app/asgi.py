import os

from django.core.asgi import get_asgi_application
from fastapi import FastAPI

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django_app = get_asgi_application()

from app.api import router  # noqa: E402

app = FastAPI()
app.include_router(router)
app.mount("/legacy", django_app)
