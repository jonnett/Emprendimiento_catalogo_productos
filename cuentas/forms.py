from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class EstiloBootstrapMixin:
    """Le pongo la clase de Bootstrap a todos los campos para no repetirlo en cada formulario.

    Un mixin es una clase pequeña que heredo junto con otra para sumarle un comportamiento.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-control"


class RegistroForm(EstiloBootstrapMixin, UserCreationForm):
    """Formulario de registro. Parto del UserCreationForm de Django, que ya valida las dos contraseñas,
    y le agrego nombre, apellido y correo."""

    # Redefino el correo para dejarlo obligatorio, porque en el modelo User de Django es opcional.
    email = forms.EmailField(label="Correo electrónico", required=True)
    first_name = forms.CharField(label="Nombre", max_length=150, required=True)
    last_name = forms.CharField(label="Apellido", max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean_email(self):
        # Validacion propia: el correo no se puede repetir.
        # El modelo User no tiene el correo como unico, por eso lo reviso yo antes de guardar.
        # Uso iexact para que Ana@ejemplo.cl y ana@ejemplo.cl cuenten como el mismo correo.
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email


class LoginForm(EstiloBootstrapMixin, AuthenticationForm):
    """Uso el formulario de ingreso de Django tal cual, solo le agrego los estilos.
    AuthenticationForm revisa el usuario y la contraseña y avisa si la cuenta esta inactiva."""
