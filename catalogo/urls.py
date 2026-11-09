from django.urls import path

from . import views

# Con app_name armo un espacio de nombres. En las plantillas uso {% url 'catalogo:portada' %}
# y asi no se confunde con otra ruta que se llame igual en otra app.
app_name = "catalogo"

urlpatterns = [
    path("", views.portada, name="portada"),
    path("productos/", views.listado, name="listado"),
]
