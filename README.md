# Catálogo de Emprendedores

Proyecto integrador de Programación Back End (TI3041), Caso 5: Emprendimiento y catálogo de productos.
MVP hecho con Django y MySQL donde cada vendedor publica sus productos y los compradores hacen pedidos.

## Requisitos previos

- Python 3.11 o superior
- MySQL 8 en ejecución

## Cómo levantar el proyecto

1. Crear y activar el entorno virtual (Windows):

   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Instalar dependencias:

   ```
   pip install -r requirements.txt
   ```

3. Crear la base de datos en MySQL:

   ```sql
   CREATE DATABASE catalogo_emprendedores CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

4. Copiar `.env.example` como `.env` y completar el usuario y la contraseña de MySQL.

5. Aplicar migraciones y crear el superusuario:

   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. Ejecutar el servidor:

   ```
   python manage.py runserver
   ```

7. (Opcional) Cargar los datos de prueba. Los usuarios ana, bruno y carla quedan con la contraseña `prueba12345`:

   ```
   python manage.py cargar_datos
   ```

## Decisiones del proyecto

- **Qué pasa al eliminar una categoría (requisito 12):** la relación `Producto.categoria` usa `on_delete=SET_NULL`. Si se elimina una categoría, sus productos no se borran: quedan "Sin categoría" y su vendedor puede asignarles otra. Elegí esto porque los productos pertenecen a los vendedores y no sería justo que perdieran sus publicaciones por un cambio en el catálogo. Además, el caso dice que la categoría es opcional. `CASCADE` borraría productos ajenos y `PROTECT` impediría reorganizar las categorías.
- **Dueño de cada producto:** el vendedor se asigna en la vista con `request.user` y no viene en el formulario. Solo el dueño puede editar o eliminar; el resto recibe un error 403 "Sin permiso".
- **Pedidos cancelados:** cuando el comprador cancela un pedido, no se borra, cambia al estado "cancelado". Así se mantiene el historial.
- **Aceptar un pedido descuenta stock:** al aceptar, se revisa otra vez que haya stock y se descuentan las unidades. Si el stock llega a 0, el producto pasa a "agotado". Se hace dentro de una transacción con `select_for_update` para no vender más de lo que hay.
- **Sin `date_hierarchy` en el admin:** necesita las tablas de zonas horarias de MySQL, que en Windows no vienen instaladas.


