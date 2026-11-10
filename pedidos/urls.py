from django.urls import path

from . import views

app_name = "pedidos"

urlpatterns = [
    path("nuevo/<int:producto_pk>/", views.crear_pedido, name="crear"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("<int:pk>/cancelar/", views.cancelar_pedido, name="cancelar"),
    path("recibidos/", views.pedidos_recibidos, name="recibidos"),
    path("<int:pk>/responder/", views.responder_pedido, name="responder"),
]
