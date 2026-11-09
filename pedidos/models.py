from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from catalogo.models import Producto


class Pedido(models.Model):
    """Es la solicitud del caso. La crea un comprador sobre el producto de otro vendedor.

    Este modelo es el que une a dos usuarios: el comprador lo tengo directo en el campo comprador,
    y el vendedor lo saco a traves del producto, con pedido.producto.vendedor.
    """

    # Ademas de los tres estados del caso agregue cancelado.
    # Cuando el comprador cancela no borro el pedido, solo le cambio el estado.
    # Asi no pierdo el historial y el contador de pedidos realizados de la portada no baja.
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACEPTADO = "aceptado", "Aceptado"
        RECHAZADO = "rechazado", "Rechazado"
        CANCELADO = "cancelado", "Cancelado"

    # Si se borra el producto, sus pedidos ya no tienen sentido, por eso uso CASCADE.
    # Con related_name puedo pedir los pedidos de un producto como producto.pedidos.all()
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="pedidos",
        verbose_name="producto",
    )

    # Este es el segundo usuario de la relacion, el que hace el pedido.
    # Le puse related_name distinto a "productos" porque el usuario ya tiene esa relacion desde Producto,
    # y si dos relaciones al mismo modelo usan el mismo nombre Django da error.
    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pedidos_realizados",
        verbose_name="comprador",
    )

    # MinValueValidator(1) porque no tiene sentido pedir cero unidades.
    cantidad = models.PositiveIntegerField("cantidad", validators=[MinValueValidator(1)])

    fecha = models.DateTimeField("fecha", auto_now_add=True)

    estado = models.CharField(
        "estado",
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["-fecha"]
        constraints = [
            models.CheckConstraint(condition=Q(cantidad__gt=0), name="pedido_cantidad_mayor_que_cero"),
        ]

    def __str__(self):
        return f"Pedido #{self.pk} de {self.producto} ({self.get_estado_display()})"

    def clean(self):
        """Aqui reviso las reglas del caso antes de guardar un pedido nuevo.

        Django llama a este metodo cuando valido un ModelForm, y tambien lo usa el panel de administracion,
        asi que las reglas se cumplen en los dos lados sin repetir codigo.
        """
        super().clean()

        # Solo reviso las reglas cuando el pedido se esta creando.
        # Si despues el vendedor lo acepta o lo rechaza, no quiero que falle porque el stock cambio.
        if not self._state.adding:
            return

        # Si todavia no tengo producto o comprador no puedo comparar nada, el formulario ya avisa que faltan.
        if not self.producto_id or not self.comprador_id:
            return

        producto = self.producto

        # Regla: no se puede pedir un producto propio.
        if producto.vendedor_id == self.comprador_id:
            raise ValidationError("No puedes hacer un pedido de tu propio producto.")

        # Regla: no se piden productos agotados.
        if producto.estado == Producto.Estado.AGOTADO:
            raise ValidationError("Este producto está agotado y no se puede pedir.")

        # Regla: la cantidad no puede superar el stock.
        # Uso un diccionario con el nombre del campo para que el error salga junto al campo cantidad.
        if self.cantidad and self.cantidad > producto.stock:
            raise ValidationError(
                {"cantidad": f"Solo hay {producto.stock} unidades disponibles."}
            )

        # Regla: un comprador no puede tener dos pedidos pendientes del mismo producto.
        # Esto no lo puedo dejar como restriccion de la base porque MySQL no soporta indices unicos con condicion,
        # por eso lo reviso aqui con una consulta.
        ya_tiene_pendiente = Pedido.objects.filter(
            producto_id=self.producto_id,
            comprador_id=self.comprador_id,
            estado=self.Estado.PENDIENTE,
        ).exists()
        if ya_tiene_pendiente:
            raise ValidationError("Ya tienes un pedido pendiente de este producto.")
