from django.urls import path

from . import views

app_name = "cuentas"

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("ingresar/", views.iniciar_sesion, name="login"),
    path("salir/", views.cerrar_sesion, name="logout"),
    path("mi-cuenta/", views.mi_cuenta, name="mi_cuenta"),
    path("mi-cuenta/editar/", views.editar_cuenta, name="editar_cuenta"),
    path("mi-cuenta/contrasena/", views.cambiar_contrasena, name="cambiar_contrasena"),
]
