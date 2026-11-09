"""Rutas principales del proyecto."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Con include le paso a la app catalogo todas las rutas que empiezan desde la raiz del sitio.
    # Asi cada app maneja sus propias rutas en su archivo urls.py.
    path("", include("catalogo.urls")),
]
