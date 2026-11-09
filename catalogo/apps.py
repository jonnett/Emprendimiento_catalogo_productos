from django.apps import AppConfig


class CatalogoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalogo"
    # Este nombre es el que aparece como titulo de la seccion en el panel de administracion.
    verbose_name = "Catálogo de productos"
