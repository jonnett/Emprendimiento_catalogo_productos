from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Categoria(models.Model):
    """Es el catalogo del caso: alimentos, artesania, ropa, etc."""

    # Pongo unique para no tener dos categorias con el mismo nombre en el filtro del listado.
    nombre = models.CharField("nombre", max_length=60, unique=True)

    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Etiqueta(models.Model):
    """Etiqueta comercial como nuevo, oferta o ecologico. Un producto puede tener varias."""

    nombre = models.CharField("nombre", max_length=40, unique=True)

    class Meta:
        verbose_name = "etiqueta"
        verbose_name_plural = "etiquetas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Entidad principal. Cada producto pertenece al vendedor que lo publica."""

    # Uso TextChoices para que el estado solo pueda ser uno de estos dos valores.
    # El primer valor es lo que se guarda en la base y el segundo es lo que se muestra.
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        AGOTADO = "agotado", "Agotado"

    # Relacion uno a muchos con el usuario: un vendedor tiene muchos productos.
    # Uso settings.AUTH_USER_MODEL en vez de importar User directo porque es la forma recomendada por Django.
    # CASCADE significa que si borro al vendedor, sus productos se borran con el.
    # Con related_name puedo pedir los productos de un usuario como usuario.productos.all()
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="productos",
        verbose_name="vendedor",
    )

    # Relacion uno a muchos con la categoria, pero opcional porque el caso dice que puede quedar sin catalogo.
    # null=True deja la columna vacia en la base y blank=True deja el campo vacio en los formularios.
    # Requisito 12: uso SET_NULL porque si borro una categoria no quiero perder los productos de los vendedores,
    # solo quedan sin categoria y el vendedor puede asignarles otra despues.
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
        verbose_name="categoría",
    )

    # Relacion muchos a muchos: un producto tiene varias etiquetas y una etiqueta esta en varios productos.
    # Django crea solo la tabla intermedia catalogo_producto_etiquetas, por eso el caso habla de seis tablas.
    # El limite de cinco etiquetas lo valido en el formulario, porque el modelo no puede revisar
    # las etiquetas antes de que el producto exista en la base.
    etiquetas = models.ManyToManyField(
        Etiqueta,
        blank=True,
        related_name="productos",
        verbose_name="etiquetas",
    )

    nombre = models.CharField("nombre", max_length=120)
    descripcion = models.TextField("descripción")

    # Uso un entero porque los precios en pesos chilenos no llevan decimales.
    # MinValueValidator(1) es la regla de que el precio debe ser mayor que cero.
    precio = models.PositiveIntegerField(
        "precio",
        validators=[MinValueValidator(1)],
        help_text="Precio en pesos chilenos, mayor que cero.",
    )

    # PositiveIntegerField ya no acepta numeros negativos, asi cumplo la regla del stock.
    stock = models.PositiveIntegerField("stock", default=0)

    estado = models.CharField(
        "estado",
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
    )

    # auto_now_add pone la fecha sola cuando se crea el producto y despues no cambia.
    fecha_publicacion = models.DateTimeField("fecha de publicación", auto_now_add=True)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        # Ordeno del mas nuevo al mas antiguo. Esto sirve para la portada y para que la paginacion no se desordene.
        ordering = ["-fecha_publicacion"]
        # Ademas de los validadores dejo las reglas en la base de datos.
        # Asi, aunque alguien guarde por fuera de los formularios, MySQL rechaza un precio cero o un stock negativo.
        constraints = [
            models.CheckConstraint(condition=Q(precio__gt=0), name="producto_precio_mayor_que_cero"),
            models.CheckConstraint(condition=Q(stock__gte=0), name="producto_stock_no_negativo"),
        ]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Antes de guardar reviso el stock para que el estado se mantenga solo.
        # Si no queda stock lo marco como agotado, y si estaba agotado y le cargan stock vuelve a activo.
        if self.stock == 0:
            self.estado = self.Estado.AGOTADO
        elif self.estado == self.Estado.AGOTADO:
            self.estado = self.Estado.ACTIVO
        super().save(*args, **kwargs)
