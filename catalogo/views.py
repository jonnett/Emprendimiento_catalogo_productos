from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from pedidos.models import Pedido

from .forms import ProductoForm
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


def listado(request):
    """Listado de productos con busqueda, filtro por categoria y paginas de a cinco."""

    # Igual que en la portada, traigo las relaciones de una vez para no hacer una consulta por cada fila.
    # Ordeno por fecha y despues por id. El id lo agrego porque si dos productos tienen la misma fecha,
    # MySQL podria devolverlos en distinto orden en cada pagina y un producto se repetiria o se perderia.
    productos = (
        Producto.objects
        .select_related("vendedor", "categoria")
        .prefetch_related("etiquetas")
        .order_by("-fecha_publicacion", "-id")
    )

    # Los datos de busqueda y filtro llegan por GET en la URL, por ejemplo ?q=miel&categoria=1
    # Uso GET y no POST porque solo estoy consultando, no cambio nada, y asi la URL se puede copiar o recargar.
    texto = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "")

    # Busqueda en dos campos: nombre y descripcion.
    # Q me deja combinar condiciones con | que significa OR. icontains busca el texto sin importar mayusculas.
    if texto:
        productos = productos.filter(Q(nombre__icontains=texto) | Q(descripcion__icontains=texto))

    # Filtro por categoria. Reviso con isdigit que sea un numero para que no se caiga si alguien escribe otra cosa en la URL.
    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=categoria_id)

    # Paginator corta los resultados en paginas de cinco.
    # get_page es tolerante: si la pagina no existe o no es un numero, devuelve la primera o la ultima en vez de dar error.
    paginador = Paginator(productos, 5)
    pagina = paginador.get_page(request.GET.get("page"))

    # Copio los parametros de la URL sin el numero de pagina.
    # Los pego en los enlaces de la paginacion para que al cambiar de pagina no se pierdan la busqueda ni el filtro.
    parametros = request.GET.copy()
    parametros.pop("page", None)

    contexto = {
        "pagina": pagina,
        "categorias": Categoria.objects.all(),
        "texto": texto,
        "categoria_id": categoria_id,
        "parametros": parametros.urlencode(),
    }
    return render(request, "catalogo/listado.html", contexto)


def detalle(request, pk):
    """Detalle de un producto con su categoria, etiquetas, vendedor y datos propios."""

    # pk llega desde la URL, por ejemplo /productos/3/ trae pk igual a 3.
    # get_object_or_404 busca el producto y si no existe devuelve la pagina de error 404 en vez de caerse con un error 500.
    # Le paso la consulta con select_related y prefetch_related para traer las relaciones en pocas consultas.
    producto = get_object_or_404(
        Producto.objects.select_related("vendedor", "categoria").prefetch_related("etiquetas"),
        pk=pk,
    )
    return render(request, "catalogo/detalle.html", {"producto": producto})


@login_required
def crear_producto(request):
    """Publicar un producto nuevo. El vendedor es siempre el usuario con la sesion."""

    if request.method == "POST":
        form = ProductoForm(request.POST, vendedor=request.user)
        if form.is_valid():
            # commit=False arma el producto con los datos del formulario pero todavia no lo guarda.
            # Lo necesito asi para ponerle el vendedor antes, porque ese campo no viene en el formulario.
            # Si el vendedor viniera en el formulario, cualquiera podria publicar a nombre de otro.
            producto = form.save(commit=False)
            producto.vendedor = request.user
            producto.save()
            messages.success(request, f"El producto «{producto.nombre}» fue publicado.")
            return redirect("catalogo:detalle", pk=producto.pk)
        messages.error(request, "No se pudo publicar el producto, revisa los errores del formulario.")
    else:
        form = ProductoForm(vendedor=request.user)

    contexto = {"form": form, "titulo": "Publicar producto", "boton": "Publicar"}
    return render(request, "catalogo/producto_form.html", contexto)


@login_required
def editar_producto(request, pk):
    """Editar un producto existente. Uso la misma plantilla que para crear."""

    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        # Con instance el formulario actualiza este producto en vez de crear uno nuevo.
        form = ProductoForm(request.POST, instance=producto, vendedor=producto.vendedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Los cambios fueron guardados.")
            return redirect("catalogo:detalle", pk=producto.pk)
        messages.error(request, "No se pudieron guardar los cambios, revisa los errores del formulario.")
    else:
        # Al abrir la pagina el formulario viene precargado con los datos actuales del producto.
        form = ProductoForm(instance=producto, vendedor=producto.vendedor)

    contexto = {"form": form, "producto": producto, "titulo": "Editar producto", "boton": "Guardar cambios"}
    return render(request, "catalogo/producto_form.html", contexto)


@login_required
def eliminar_producto(request, pk):
    """Eliminar un producto pidiendo confirmacion antes."""

    producto = get_object_or_404(Producto, pk=pk)

    # Con GET solo muestro la pagina de confirmacion, no borro nada.
    # El borrado real pasa solo con POST, cuando el usuario aprieta el boton de confirmar.
    # Asi un enlace o un clic por error no puede eliminar un producto.
    if request.method == "POST":
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"El producto «{nombre}» fue eliminado.")
        return redirect("catalogo:listado")

    # Cuento los pedidos para avisar que tambien se borran, porque Pedido tiene on_delete CASCADE.
    contexto = {"producto": producto, "total_pedidos": producto.pedidos.count()}
    return render(request, "catalogo/producto_confirmar_eliminar.html", contexto)
