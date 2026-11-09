"""Configuracion del proyecto Catalogo de Emprendedores."""
import os
from pathlib import Path

from dotenv import load_dotenv

# BASE_DIR es la carpeta raiz del proyecto, donde esta manage.py.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargo las variables del archivo .env para no dejar mi contraseña de MySQL escrita en el codigo.
# El .env esta en el .gitignore, asi que nunca llega a GitHub. En el repo solo subo .env.example.
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo-local")

# DEBUG viene como texto desde el .env, por eso lo comparo con "true" para pasarlo a booleano.
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Mis apps del proyecto. Si creo una app nueva y no la agrego aqui, Django no ve sus modelos.
    "catalogo",
    "pedidos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "emprendimiento.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Dejo una carpeta templates en la raiz para la plantilla base que compartiran todas las apps.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "emprendimiento.wsgi.application"


# Conexion a MySQL. Requisito 1: la base es propia del proyecto y la creo antes en MySQL.
# utf8mb4 lo uso para que se guarden bien tildes, ñ y emojis en nombres y descripciones.
# El modo STRICT hace que MySQL rechace datos invalidos en vez de cortarlos sin avisar.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME", "catalogo_emprendedores"),
        "USER": os.getenv("DB_USER", "root"),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Idioma y hora de Chile para que el admin y las fechas de publicacion salgan bien.
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
