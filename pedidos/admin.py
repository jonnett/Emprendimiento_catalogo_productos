from django.contrib import admin

from .models import Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ["id", "producto", "comprador", "vendedor", "cantidad", "estado", "fecha"]
    list_filter = ["estado", "fecha"]

    # Busco por el nombre del producto, por el comprador y por el vendedor siguiendo las relaciones con doble guion bajo.
    search_fields = ["producto__nombre", "comprador__username", "producto__vendedor__username"]

    # Traigo producto, vendedor del producto y comprador en una sola consulta para no repetir consultas por fila.
    list_select_related = ["producto__vendedor", "comprador"]

    list_per_page = 20
    # Aqui tampoco uso date_hierarchy por el mismo problema de zonas horarias de MySQL en Windows.

    # El vendedor no es un campo del pedido, lo saco del producto. Por eso lo muestro con un metodo.
    @admin.display(description="vendedor", ordering="producto__vendedor__username")
    def vendedor(self, obj):
        return obj.producto.vendedor
