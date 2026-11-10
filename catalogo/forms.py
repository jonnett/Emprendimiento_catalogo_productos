from django import forms

from cuentas.forms import EstiloBootstrapMixin

from .models import Categoria, Etiqueta, Producto

# Lo dejo en una constante para usar el mismo numero en la validacion y en el texto de ayuda.
MAXIMO_ETIQUETAS = 5


class ProductoForm(EstiloBootstrapMixin, forms.ModelForm):
    """Formulario propio para crear y editar productos desde el sitio.

    Es un ModelForm, o sea que esta ligado al modelo Producto: Django arma los campos a partir del modelo
    y al hacer save() guarda directo en la tabla. El vendedor, el estado y la fecha no van en el formulario,
    porque el vendedor lo pongo yo en la vista, el estado se calcula solo en el save() del modelo
    y la fecha la pone auto_now_add.
    """

    # Redefino estos dos campos para controlar como se ven y que opciones muestran.
    # La categoria es opcional porque el caso dice que un producto puede quedar sin catalogo.
    # empty_label es el texto de la opcion vacia de la lista.
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label="Sin categoría",
        label="Categoría",
    )

    # Las etiquetas las muestro como casillas, que es mas claro que una lista donde hay que apretar Ctrl.
    etiquetas = forms.ModelMultipleChoiceField(
        queryset=Etiqueta.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Etiquetas",
        help_text=f"Elige hasta {MAXIMO_ETIQUETAS} etiquetas.",
    )

    class Meta:
        model = Producto
        fields = ["nombre", "descripcion", "precio", "stock", "categoria", "etiquetas"]
        labels = {
            "nombre": "Nombre del producto",
            "descripcion": "Descripción",
            "precio": "Precio (CLP)",
            "stock": "Unidades disponibles",
        }
        help_texts = {
            "nombre": "Por ejemplo: Mermelada de murta 250 g.",
            "descripcion": "Cuenta qué es, cómo se hace o qué lo hace especial.",
            "precio": "Precio en pesos chilenos, sin puntos. Debe ser mayor que cero.",
            "stock": "Si pones 0 el producto queda como agotado.",
        }
        # Cambio el tipo de campo en el HTML. La descripcion como area de texto,
        # y precio y stock como numeros con minimo para que el navegador no deje bajar de ahi.
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
            "precio": forms.NumberInput(attrs={"min": 1}),
            "stock": forms.NumberInput(attrs={"min": 0}),
        }

    def __init__(self, *args, vendedor=None, **kwargs):
        # Recibo al vendedor desde la vista porque lo necesito para la validacion del nombre.
        # Lo recibo como parametro aparte para que no se lo pase al padre, porque ModelForm no conoce ese parametro.
        super().__init__(*args, **kwargs)
        self.vendedor = vendedor

    def clean_nombre(self):
        """Validacion propia: un vendedor no puede tener dos productos con el mismo nombre.

        Asi evito que alguien publique dos veces lo mismo por error y que el listado se llene de repetidos.
        Otro vendedor si puede usar el mismo nombre, porque son emprendimientos distintos.
        """
        nombre = self.cleaned_data["nombre"].strip()

        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 letras.")

        if self.vendedor is not None:
            repetidos = Producto.objects.filter(vendedor=self.vendedor, nombre__iexact=nombre)
            # Si estoy editando, excluyo el mismo producto para que no choque consigo mismo.
            if self.instance.pk:
                repetidos = repetidos.exclude(pk=self.instance.pk)
            if repetidos.exists():
                raise forms.ValidationError("Ya tienes un producto publicado con ese nombre.")

        return nombre

    def clean_etiquetas(self):
        # Regla del caso: hasta cinco etiquetas por producto.
        # Aqui ya tengo las etiquetas que marco el usuario y solo cuento cuantas son.
        etiquetas = self.cleaned_data["etiquetas"]
        if len(etiquetas) > MAXIMO_ETIQUETAS:
            raise forms.ValidationError(
                f"Puedes elegir como máximo {MAXIMO_ETIQUETAS} etiquetas, marcaste {len(etiquetas)}."
            )
        return etiquetas


class CategoriaForm(EstiloBootstrapMixin, forms.ModelForm):
    """Formulario para crear categorias desde el sitio."""

    class Meta:
        model = Categoria
        fields = ["nombre"]
        labels = {"nombre": "Nombre de la categoría"}
        help_texts = {"nombre": "Por ejemplo: Decoración, Cosmética natural, Juguetes."}

    def clean_nombre(self):
        # Quito espacios de sobra y dejo la primera letra en mayuscula para que el filtro del listado se vea ordenado.
        # Que no se repita lo revisa solo el ModelForm, porque en el modelo el nombre tiene unique=True.
        nombre = " ".join(self.cleaned_data["nombre"].split())
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 letras.")
        return nombre[0].upper() + nombre[1:]
