"""Rutas principales del proyecto."""
from django.contrib import admin
from django.urls import path

# Por ahora solo tengo el panel de administracion. Las rutas de cada app las agrego aqui con include.
urlpatterns = [
    path("admin/", admin.site.urls),
]
