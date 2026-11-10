from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalogo.models import Producto

from .forms import PedidoForm
from .models import Pedido


@login_required
def crear_pedido(request, producto_pk):
    """Hacer un pedido sobre un producto de otro vendedor."""

    producto = get_object_or_404(Producto.objects.select_related("vendedor"), pk=producto_pk)

    # Antes de mostrar el formulario reviso los casos que no tienen sentido, para avisar de una vez.
    # Igual el modelo vuelve a revisar todo al validar, por si alguien manda el POST directo sin pasar por aqui.
    if producto.vendedor_id == request.user.id:
        messages.error(request, "No puedes hacer un pedido de tu propio producto.")
        return redirect("catalogo:detalle", pk=producto.pk)
    if producto.estado == Producto.Estado.AGOTADO:
        messages.error(request, "Este producto está agotado.")
        return redirect("catalogo:detalle", pk=producto.pk)

    # Creo el pedido en memoria con el producto y el comprador ya puestos, sin guardarlo todavia.
    # Se lo paso al formulario con instance para que el clean() del modelo pueda revisar las reglas
    # con esos datos: stock, producto propio, agotado y pedido pendiente repetido.
    pedido = Pedido(producto=producto, comprador=request.user)

    if request.method == "POST":
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f"Tu pedido de {pedido.cantidad} × {producto.nombre} fue enviado al vendedor.")
            return redirect("pedidos:mis_pedidos")
        messages.error(request, "No se pudo hacer el pedido.")
    else:
        form = PedidoForm(instance=pedido, initial={"cantidad": 1})

    return render(request, "pedidos/crear_pedido.html", {"form": form, "producto": producto})


@login_required
def mis_pedidos(request):
    """Mis solicitudes: los pedidos que hice como comprador."""

    # pedidos_realizados es el related_name del campo comprador en el modelo Pedido.
    # select_related trae el producto y su vendedor en la misma consulta para la tabla.
    pedidos = request.user.pedidos_realizados.select_related("producto__vendedor").order_by("-fecha", "-id")
    return render(request, "pedidos/mis_pedidos.html", {"pedidos": pedidos})


# Cancelar cambia datos, por eso solo acepto POST con su csrf_token, igual que eliminar y cerrar sesion.
@require_POST
@login_required
def cancelar_pedido(request, pk):
    """El comprador cancela uno de sus pedidos, solo si sigue pendiente."""

    pedido = get_object_or_404(Pedido, pk=pk)

    # Autorizacion: solo el comprador que hizo el pedido lo puede cancelar.
    if pedido.comprador_id != request.user.id:
        raise PermissionDenied("No puedes cancelar un pedido que no es tuyo.")

    # Regla del caso: solo se cancelan los que siguen pendientes.
    # Si el vendedor ya lo acepto o rechazo, ya no se puede cancelar.
    if pedido.estado != Pedido.Estado.PENDIENTE:
        messages.error(request, "Solo puedes cancelar pedidos que siguen pendientes.")
        return redirect("pedidos:mis_pedidos")

    # No borro el pedido, le cambio el estado. Asi queda en el historial.
    # update_fields hace que el UPDATE solo toque la columna estado.
    pedido.estado = Pedido.Estado.CANCELADO
    pedido.save(update_fields=["estado"])
    messages.success(request, "Tu pedido fue cancelado.")
    return redirect("pedidos:mis_pedidos")


@login_required
def pedidos_recibidos(request):
    """Solicitudes recibidas: los pedidos que otros hicieron sobre mis productos."""

    # Filtro siguiendo la relacion: pedidos cuyo producto tiene como vendedor al usuario con la sesion.
    # El doble guion bajo en producto__vendedor pasa del pedido al producto y del producto al vendedor.
    pedidos = (
        Pedido.objects
        .filter(producto__vendedor=request.user)
        .select_related("producto", "comprador")
        .order_by("-fecha", "-id")
    )
    return render(request, "pedidos/pedidos_recibidos.html", {"pedidos": pedidos})


@require_POST
@login_required
def responder_pedido(request, pk):
    """El vendedor acepta o rechaza un pedido pendiente de uno de sus productos."""

    # El boton que apreto el vendedor manda accion con el valor aceptar o rechazar.
    accion = request.POST.get("accion")

    # transaction.atomic hace que todo lo de adentro se guarde junto o no se guarde nada.
    # select_for_update bloquea la fila del pedido y la del producto mientras dura la transaccion.
    # Asi, si el vendedor acepta dos pedidos al mismo tiempo, el segundo espera al primero
    # y ve el stock ya descontado, y no se vende mas de lo que hay.
    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update().select_related("producto"),
            pk=pk,
        )
        producto = pedido.producto

        # Autorizacion: solo el vendedor del producto puede responder sus pedidos.
        if producto.vendedor_id != request.user.id:
            raise PermissionDenied("No puedes responder pedidos de productos que no son tuyos.")

        # Solo se responden los pendientes. Uno cancelado, aceptado o rechazado ya no cambia.
        if pedido.estado != Pedido.Estado.PENDIENTE:
            messages.error(request, "Este pedido ya no está pendiente.")
            return redirect("pedidos:recibidos")

        if accion == "aceptar":
            # Reviso el stock otra vez, porque pudo bajar desde que el comprador hizo el pedido.
            if pedido.cantidad > producto.stock:
                messages.error(
                    request,
                    f"No hay stock suficiente para aceptar este pedido. Quedan {producto.stock} unidades.",
                )
                return redirect("pedidos:recibidos")

            # Al aceptar descuento las unidades del stock.
            # El save() del producto se encarga de pasarlo a agotado si llega a cero.
            producto.stock -= pedido.cantidad
            producto.save()
            pedido.estado = Pedido.Estado.ACEPTADO
            pedido.save(update_fields=["estado"])
            messages.success(request, f"Aceptaste el pedido de {pedido.comprador.username}. El stock fue descontado.")

        elif accion == "rechazar":
            pedido.estado = Pedido.Estado.RECHAZADO
            pedido.save(update_fields=["estado"])
            messages.info(request, f"Rechazaste el pedido de {pedido.comprador.username}.")

        else:
            # Si alguien manda otro valor modificando el HTML, no hago nada.
            messages.error(request, "Acción no válida.")

    return redirect("pedidos:recibidos")
