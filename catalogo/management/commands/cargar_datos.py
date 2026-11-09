"""Comando para cargar los datos de prueba minimos del caso.

Lo ejecuto con: python manage.py cargar_datos

Django busca los comandos en la carpeta management/commands de cada app instalada,
y el nombre del archivo es el nombre del comando. Por eso las dos carpetas necesitan su __init__.py.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from catalogo.models import Categoria, Etiqueta, Producto
from pedidos.models import Pedido

# Esta contraseña es solo para los usuarios de prueba, para poder entrar con ellos y probar el sitio.
CLAVE_PRUEBA = "prueba12345"

USUARIOS = [
    {"username": "ana", "first_name": "Ana", "last_name": "Rojas", "email": "ana@ejemplo.cl"},
    {"username": "bruno", "first_name": "Bruno", "last_name": "Soto", "email": "bruno@ejemplo.cl"},
    {"username": "carla", "first_name": "Carla", "last_name": "Muñoz", "email": "carla@ejemplo.cl"},
]

CATEGORIAS = ["Alimentos", "Artesanía", "Ropa"]

ETIQUETAS = ["Nuevo", "Oferta", "Ecológico", "Hecho a mano", "Sin gluten"]

# Cada producto tiene su vendedor, categoria y etiquetas por nombre, y despues los busco en la base.
# Deje uno sin categoria porque el caso dice que el catalogo es opcional,
# y uno con stock cero para tener un producto agotado.
PRODUCTOS = [
    {
        "nombre": "Mermelada de murta",
        "descripcion": "Mermelada artesanal de murta del sur, frasco de 250 gramos.",
        "precio": 4500, "stock": 20, "vendedor": "ana", "categoria": "Alimentos",
        "etiquetas": ["Nuevo", "Ecológico", "Hecho a mano"],
    },
    {
        "nombre": "Galletas de avena",
        "descripcion": "Paquete de 12 galletas de avena sin gluten, endulzadas con miel.",
        "precio": 3000, "stock": 15, "vendedor": "ana", "categoria": "Alimentos",
        "etiquetas": ["Sin gluten", "Oferta"],
    },
    {
        "nombre": "Miel de ulmo",
        "descripcion": "Miel pura de ulmo cosechada en Chiloé, frasco de 500 gramos.",
        "precio": 7000, "stock": 0, "vendedor": "ana", "categoria": "Alimentos",
        "etiquetas": ["Ecológico"],
    },
    {
        "nombre": "Taza de greda",
        "descripcion": "Taza de greda de Pomaire pintada a mano.",
        "precio": 6500, "stock": 8, "vendedor": "bruno", "categoria": "Artesanía",
        "etiquetas": ["Hecho a mano"],
    },
    {
        "nombre": "Jabón de avena",
        "descripcion": "Jabón natural de avena y lavanda, 100 gramos.",
        "precio": 2500, "stock": 30, "vendedor": "bruno", "categoria": "Artesanía",
        "etiquetas": ["Ecológico", "Hecho a mano", "Oferta"],
    },
    {
        "nombre": "Aros de cobre",
        "descripcion": "Aros de cobre martillado con terminación brillante.",
        "precio": 8900, "stock": 5, "vendedor": "bruno", "categoria": "Artesanía",
        "etiquetas": ["Nuevo", "Hecho a mano"],
    },
    {
        "nombre": "Polerón bordado",
        "descripcion": "Polerón de algodón con bordado de flores nativas, tallas S a XL.",
        "precio": 19990, "stock": 10, "vendedor": "carla", "categoria": "Ropa",
        "etiquetas": ["Hecho a mano", "Oferta"],
    },
    {
        "nombre": "Gorro de lana",
        "descripcion": "Gorro tejido a palillo con lana de oveja teñida natural.",
        "precio": 9500, "stock": 12, "vendedor": "carla", "categoria": "Ropa",
        "etiquetas": ["Ecológico", "Hecho a mano"],
    },
    {
        "nombre": "Bolso de tela",
        "descripcion": "Bolso reutilizable de tela de algodón con estampado propio.",
        "precio": 5990, "stock": 25, "vendedor": "carla", "categoria": "Ropa",
        "etiquetas": ["Nuevo", "Ecológico"],
    },
    {
        "nombre": "Kit de velas aromáticas",
        "descripcion": "Tres velas de soya con aroma a eucalipto, canela y vainilla.",
        "precio": 11000, "stock": 7, "vendedor": "carla", "categoria": None,
        "etiquetas": ["Nuevo"],
    },
]

# Pedidos en distintos estados. Los arme cumpliendo las reglas del caso:
# nadie pide un producto propio, nadie pide uno agotado y la cantidad no supera el stock.
PEDIDOS = [
    {"producto": "Mermelada de murta", "comprador": "bruno", "cantidad": 2, "estado": Pedido.Estado.PENDIENTE},
    {"producto": "Polerón bordado", "comprador": "ana", "cantidad": 1, "estado": Pedido.Estado.PENDIENTE},
    {"producto": "Taza de greda", "comprador": "carla", "cantidad": 3, "estado": Pedido.Estado.ACEPTADO},
    {"producto": "Gorro de lana", "comprador": "bruno", "cantidad": 1, "estado": Pedido.Estado.RECHAZADO},
    {"producto": "Jabón de avena", "comprador": "ana", "cantidad": 4, "estado": Pedido.Estado.CANCELADO},
]


class Command(BaseCommand):
    help = "Carga los datos de prueba minimos: 3 usuarios, 3 categorias, 5 etiquetas, 10 productos y 5 pedidos."

    # Con atomic, si algo falla a la mitad se deshace todo y no quedan datos a medias en la base.
    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()

        # Uso get_or_create en todo para que si ejecuto el comando dos veces no se dupliquen los datos.
        # Devuelve el objeto y un booleano que dice si lo tuvo que crear.
        usuarios = {}
        for datos in USUARIOS:
            usuario, creado = User.objects.get_or_create(
                username=datos["username"],
                defaults={
                    "first_name": datos["first_name"],
                    "last_name": datos["last_name"],
                    "email": datos["email"],
                },
            )
            if creado:
                # set_password guarda la contraseña encriptada. Si la pusiera directo en el campo quedaria en texto plano
                # y Django no la reconoceria al iniciar sesion.
                usuario.set_password(CLAVE_PRUEBA)
                usuario.save()
            usuarios[usuario.username] = usuario

        categorias = {}
        for nombre in CATEGORIAS:
            categorias[nombre], _ = Categoria.objects.get_or_create(nombre=nombre)

        etiquetas = {}
        for nombre in ETIQUETAS:
            etiquetas[nombre], _ = Etiqueta.objects.get_or_create(nombre=nombre)

        productos = {}
        for datos in PRODUCTOS:
            producto, _ = Producto.objects.get_or_create(
                nombre=datos["nombre"],
                vendedor=usuarios[datos["vendedor"]],
                defaults={
                    "descripcion": datos["descripcion"],
                    "precio": datos["precio"],
                    "stock": datos["stock"],
                    # Si la categoria es None el producto queda sin catalogo.
                    "categoria": categorias.get(datos["categoria"]),
                },
            )
            # Las etiquetas se asignan despues de crear el producto, porque la relacion muchos a muchos
            # necesita que el producto ya tenga id. Con set reemplazo las que tuviera por estas.
            producto.etiquetas.set([etiquetas[nombre] for nombre in datos["etiquetas"]])
            productos[producto.nombre] = producto

        for datos in PEDIDOS:
            Pedido.objects.get_or_create(
                producto=productos[datos["producto"]],
                comprador=usuarios[datos["comprador"]],
                estado=datos["estado"],
                defaults={"cantidad": datos["cantidad"]},
            )

        self.stdout.write(self.style.SUCCESS(
            f"Datos cargados: {User.objects.count()} usuarios, {Categoria.objects.count()} categorías, "
            f"{Etiqueta.objects.count()} etiquetas, {Producto.objects.count()} productos "
            f"y {Pedido.objects.count()} pedidos."
        ))
        self.stdout.write(f"Los usuarios ana, bruno y carla tienen la contraseña: {CLAVE_PRUEBA}")
