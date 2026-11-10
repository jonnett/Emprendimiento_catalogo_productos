from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegistroForm


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
