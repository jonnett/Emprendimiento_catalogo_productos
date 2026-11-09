"""Punto de entrada WSGI, lo usa un servidor web para correr el proyecto."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emprendimiento.settings")

application = get_wsgi_application()
