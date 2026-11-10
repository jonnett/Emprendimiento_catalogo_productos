from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

User = get_user_model()


class EstiloBootstrapMixin:
    """Le pongo la clase de Bootstrap a todos los campos para no repetirlo en cada formulario.

    Un mixin es una clase pequeña que heredo junto con otra para sumarle un comportamiento.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap usa una clase distinta segun el tipo de campo, por eso reviso el widget de cada uno.
        # Las casillas de varias opciones van primero porque tambien son un tipo de Select por dentro.
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxSelectMultiple):
                campo.widget.attrs["class"] = "form-check-input"
            elif isinstance(campo.widget, forms.Select):
                campo.widget.attrs["class"] = "form-select"
            else:
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


class EditarCuentaForm(EstiloBootstrapMixin, forms.ModelForm):
    """Formulario de Mi cuenta para editar nombre, apellido y correo.
    El nombre de usuario no lo dejo editar porque es con lo que la persona ingresa al sitio."""

    email = forms.EmailField(label="Correo electrónico", required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {"first_name": "Nombre", "last_name": "Apellido"}

    def clean_email(self):
        # Igual que en el registro, el correo no puede ser de otra persona.
        # La diferencia es que aqui excluyo al propio usuario con exclude(pk=...),
        # porque si guarda sin cambiar su correo, el correo ya existe pero es el suyo.
        email = self.cleaned_data["email"].strip().lower()
        existe = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists()
        if existe:
            raise forms.ValidationError("Ese correo ya pertenece a otra cuenta.")
        return email


class CambiarContrasenaForm(EstiloBootstrapMixin, PasswordChangeForm):
    """Uso el formulario de Django para cambiar la contraseña.
    Pide la contraseña actual, la nueva dos veces, y aplica los validadores de AUTH_PASSWORD_VALIDATORS."""
