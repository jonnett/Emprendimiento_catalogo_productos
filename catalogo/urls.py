from django.urls import path

from . import views

# Con app_name armo un espacio de nombres. En las plantillas uso {% url 'catalogo:portada' %}
# y asi no se confunde con otra ruta que se llame igual en otra app.
app_name = "catalogo"

urlpatterns = [
    path("", views.portada, name="portada"),
    path("productos/", views.listado, name="listado"),
    # <int:pk> captura un numero de la URL y se lo pasa a la vista como el parametro pk.
    # Si en la URL viene algo que no es numero, Django ni siquiera llama a la vista y responde 404.
    path("productos/<int:pk>/", views.detalle, name="detalle"),
    path("productos/nuevo/", views.crear_producto, name="crear"),
    path("productos/<int:pk>/editar/", views.editar_producto, name="editar"),
    path("productos/<int:pk>/eliminar/", views.eliminar_producto, name="eliminar"),
    path("mis-productos/", views.mis_productos, name="mis_productos"),
    path("categorias/", views.categorias, name="categorias"),
]
