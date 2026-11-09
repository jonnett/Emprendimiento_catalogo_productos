"""Punto de entrada ASGI, alternativa asincrona a wsgi.py."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emprendimiento.settings")

application = get_asgi_application()
