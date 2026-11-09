#!/usr/bin/env python
"""Herramienta de linea de comandos de Django para este proyecto."""
import os
import sys


def main():
    # Le digo a Django cual es mi archivo de configuracion antes de ejecutar cualquier comando.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "emprendimiento.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. Revisa que el entorno virtual este activo "
            "y que hayas instalado requirements.txt."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
