from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import CambiarContrasenaForm, EditarCuentaForm, LoginForm, RegistroForm


def registro(request):
    """Registro de usuarios nuevos."""

    # Si ya tiene sesion no tiene sentido que se registre otra vez, lo mando a la portada.
    if request.user.is_authenticated:
        return redirect("catalogo:portada")

    # La misma vista hace dos cosas segun el metodo.
    # GET es cuando abren la pagina: muestro el formulario vacio.
    # POST es cuando envian el formulario: lo lleno con request.POST y lo valido.
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            # save() crea el usuario y guarda la contraseña encriptada, eso lo hace UserCreationForm.
            usuario = form.save()
            # Despues de registrarse le inicio la sesion de inmediato para que no tenga que ingresar de nuevo.
            login(request, usuario)
            messages.success(request, f"Bienvenido {usuario.first_name}, tu cuenta fue creada.")
            # Redirijo despues del POST para que si recarga la pagina no se vuelva a enviar el formulario.
            return redirect("catalogo:portada")
        # Si no es valido no hago nada aqui: abajo se vuelve a mostrar el formulario con los errores.
    else:
        form = RegistroForm()

    return render(request, "cuentas/registro.html", {"form": form})


def iniciar_sesion(request):
    """Inicio de sesion con usuario y contraseña."""

    if request.user.is_authenticated:
        return redirect("catalogo:portada")

    # next es la pagina a la que queria entrar antes de que login_required lo mandara aqui.
    # Puede venir en la URL (GET) o en un campo oculto del formulario (POST).
    siguiente = request.POST.get("next") or request.GET.get("next", "")

    if request.method == "POST":
        # AuthenticationForm recibe el request como primer argumento y despues los datos.
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            # get_user me entrega el usuario que ya fue autenticado por el formulario.
            login(request, form.get_user())
            messages.success(request, "Iniciaste sesión correctamente.")
            # Reviso que next sea una direccion de mi propio sitio antes de redirigir.
            # Si no lo reviso, alguien podria mandar un enlace con next hacia una pagina falsa.
            if siguiente and url_has_allowed_host_and_scheme(siguiente, allowed_hosts={request.get_host()}):
                return redirect(siguiente)
            return redirect("catalogo:portada")
    else:
        form = LoginForm(request)

    return render(request, "cuentas/login.html", {"form": form, "next": siguiente})


# require_POST hace que esta vista solo acepte POST. Si alguien entra con GET recibe un error 405.
# Asi cerrar sesion solo se puede con el boton del menu, que lleva el token csrf.
@require_POST
def cerrar_sesion(request):
    logout(request)
    messages.info(request, "Cerraste sesión. ¡Vuelve pronto!")
    return redirect("catalogo:portada")


# login_required protege la vista: si no hay sesion, manda al usuario a LOGIN_URL con ?next=
# para que despues de ingresar vuelva aqui. Ocultar el enlace del menu no basta,
# porque igual podrian escribir la direccion a mano.
@login_required
def mi_cuenta(request):
    """Muestra los datos del usuario que tiene la sesion iniciada."""
    # No necesito buscar al usuario en la base, Django ya me lo entrega en request.user.
    return render(request, "cuentas/mi_cuenta.html")


@login_required
def editar_cuenta(request):
    """Editar nombre, apellido y correo del usuario con sesion."""

    # instance=request.user hace que el formulario venga precargado con sus datos
    # y que al guardar actualice ese mismo usuario en vez de crear uno nuevo.
    if request.method == "POST":
        form = EditarCuentaForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus datos fueron actualizados.")
            return redirect("cuentas:mi_cuenta")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        form = EditarCuentaForm(instance=request.user)

    return render(request, "cuentas/editar_cuenta.html", {"form": form})


@login_required
def cambiar_contrasena(request):
    """Cambiar la contraseña pidiendo la actual."""

    # PasswordChangeForm recibe primero el usuario, asi puede revisar que la contraseña actual sea la correcta.
    if request.method == "POST":
        form = CambiarContrasenaForm(request.user, request.POST)
        if form.is_valid():
            usuario = form.save()
            # Al cambiar la contraseña Django invalida las sesiones abiertas de ese usuario.
            # update_session_auth_hash actualiza la sesion actual para que no lo saque del sitio.
            update_session_auth_hash(request, usuario)
            messages.success(request, "Tu contraseña fue cambiada.")
            return redirect("cuentas:mi_cuenta")
        messages.error(request, "No se pudo cambiar la contraseña, revisa los errores.")
    else:
        form = CambiarContrasenaForm(request.user)

    return render(request, "cuentas/cambiar_contrasena.html", {"form": form})
