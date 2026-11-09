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

## Avance por hitos

- [ ] Hito 1: Modelo y datos (requisitos 1 a 3)
- [ ] Hito 2: Páginas públicas (requisitos 4 a 6)
- [ ] Hito 3: Cuentas y CRUD (requisitos 7 a 9)
- [ ] Hito 4: Seguridad, catálogos y etiquetas (requisitos 10 a 12)
- [ ] Hito 5: Solicitudes y cierre (requisitos 13 a 15)
