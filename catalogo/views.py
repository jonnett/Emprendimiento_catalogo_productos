from django.shortcuts import render

from pedidos.models import Pedido

from .models import Categoria, Producto


def portada(request):
    """Portada del sitio: presenta la red, muestra los cuatro productos mas recientes y tres contadores."""

    # El modelo Producto ya esta ordenado por fecha de publicacion descendente, asi que con [:4] saco los cuatro mas nuevos.
    # El [:4] se traduce en un LIMIT 4 en la consulta, no trae todos los productos para despues cortarlos.
    # select_related trae vendedor y categoria con un JOIN en la misma consulta,
    # y prefetch_related trae todas las etiquetas de esos cuatro productos en una sola consulta extra.
    # Sin eso la plantilla haria consultas nuevas por cada producto al mostrar esos datos.
    ultimos_productos = (
        Producto.objects
        .select_related("vendedor", "categoria")
        .prefetch_related("etiquetas")[:4]
    )

    # Los contadores los calculo con count(), que hace un SELECT COUNT en la base sin traer los registros.
    # En pedidos realizados cuento todos, sin importar el estado, porque todos fueron pedidos que alguien hizo.
    contexto = {
        "ultimos_productos": ultimos_productos,
        "total_activos": Producto.objects.filter(estado=Producto.Estado.ACTIVO).count(),
        "total_categorias": Categoria.objects.count(),
        "total_pedidos": Pedido.objects.count(),
    }

    # render junta la plantilla con el contexto y devuelve la respuesta HTML.
    return render(request, "catalogo/portada.html", contexto)
