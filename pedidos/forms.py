from django import forms

from cuentas.forms import EstiloBootstrapMixin

from .models import Pedido


class PedidoForm(EstiloBootstrapMixin, forms.ModelForm):
    """Formulario para hacer un pedido. Solo pide la cantidad.

    El producto y el comprador no van en el formulario, los pongo yo en la vista,
    asi nadie puede hacer un pedido a nombre de otro ni cambiar el producto desde el HTML.
    Las reglas del caso no las repito aqui: estan en el clean() del modelo Pedido,
    y el ModelForm lo llama solo cuando ejecuto is_valid().
    """

    class Meta:
        model = Pedido
        fields = ["cantidad"]
        labels = {"cantidad": "Cantidad"}
        widgets = {"cantidad": forms.NumberInput(attrs={"min": 1})}
