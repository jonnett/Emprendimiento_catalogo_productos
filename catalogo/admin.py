from django import forms
from django.contrib import admin
from django.db.models import Count

from .models import Categoria, Etiqueta, Producto

# Cambio los titulos del panel para que no diga "Administración de Django".
admin.site.site_header = "Catálogo de Emprendedores"
admin.site.site_title = "Catálogo de Emprendedores"
admin.site.index_title = "Panel de administración"


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "total_productos"]
    search_fields = ["nombre"]

    def get_queryset(self, request):
        # Cuento los productos de cada categoria en la misma consulta con annotate.
        # Si lo hiciera con categoria.productos.count() en cada fila, haria una consulta extra por cada categoria.
        return super().get_queryset(request).annotate(cantidad=Count("productos"))

    # Con este decorador le pongo titulo a la columna y permito ordenar por ella.
    @admin.display(description="productos", ordering="cantidad")
    def total_productos(self, obj):
        return obj.cantidad


@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ["nombre"]
    search_fields = ["nombre"]


class ProductoAdminForm(forms.ModelForm):
    """Formulario del panel para revisar la regla de hasta cinco etiquetas por producto."""

    class Meta:
        model = Producto
        fields = "__all__"

    def clean_etiquetas(self):
        # Los metodos clean_ seguidos del nombre de un campo validan solo ese campo.
        # Aqui ya tengo las etiquetas elegidas y reviso que no sean mas de cinco.
        etiquetas = self.cleaned_data["etiquetas"]
        if len(etiquetas) > 5:
            raise forms.ValidationError("Un producto puede tener como máximo 5 etiquetas.")
        return etiquetas


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoAdminForm

    # Columnas que muestro en el listado.
    list_display = ["nombre", "vendedor", "categoria", "precio", "stock", "estado", "fecha_publicacion"]

    # Filtros del costado derecho.
    list_filter = ["estado", "categoria", "etiquetas", "fecha_publicacion"]

    # Campos donde busca la caja de busqueda. Con vendedor__username busco tambien por el nombre del vendedor.
    search_fields = ["nombre", "descripcion", "vendedor__username"]

    # Trae el vendedor y la categoria en la misma consulta con un JOIN.
    # Sin esto el listado haria una consulta mas por cada fila para mostrar esas dos columnas.
    list_select_related = ["vendedor", "categoria"]

    # Muestra las etiquetas como dos cajas para pasar de una a otra, mas comodo que la lista con Ctrl.
    filter_horizontal = ["etiquetas"]

    list_per_page = 20
    # No uso date_hierarchy porque necesita las tablas de zonas horarias de MySQL,
    # que en Windows no vienen instaladas, y daba el error "invalid datetime value".
    # Para filtrar por fecha me basta con el filtro de fecha_publicacion que puse en list_filter.
