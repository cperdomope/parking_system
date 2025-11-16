#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidad para gestión de rutas de recursos en PyInstaller

Este módulo proporciona funciones para obtener rutas absolutas a archivos
de recursos (imágenes, configuraciones, etc.) que funcionen tanto en modo
desarrollo como en modo ejecutable empaquetado con PyInstaller.

PyInstaller desempaqueta recursos en una carpeta temporal (_MEIPASS) cuando
la aplicación se ejecuta como ejecutable. Esta utilidad detecta automáticamente
el modo de ejecución y devuelve la ruta correcta.
"""

import os
import sys
from pathlib import Path
from typing import Union


def get_resource_path(relative_path: Union[str, Path]) -> str:
    """
    Obtiene la ruta absoluta a un archivo de recursos.

    Funciona tanto en modo desarrollo (script de Python) como en modo
    producción (ejecutable de PyInstaller).

    En PyInstaller, cuando la app se empaqueta con --onefile o --onedir,
    los recursos se extraen a una carpeta temporal accesible via sys._MEIPASS.

    Args:
        relative_path: Ruta relativa al recurso desde la raíz del proyecto
                      Ejemplos: ".env", "db/schema.sql", "assets/logo.png"

    Returns:
        str: Ruta absoluta al recurso

    Raises:
        FileNotFoundError: Si el archivo no existe en ninguna ubicación

    Examples:
        >>> env_path = get_resource_path(".env")
        >>> schema_path = get_resource_path("db/schema/parking_database_schema.sql")
        >>> logo_path = get_resource_path("assets/logo.png")
    """
    # Convertir a string si es Path
    if isinstance(relative_path, Path):
        relative_path = str(relative_path)

    # Detectar si estamos en modo PyInstaller (ejecutable empaquetado)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Modo PyInstaller: usar la carpeta temporal _MEIPASS
        base_path = Path(sys._MEIPASS)
        resource_path = base_path / relative_path
    else:
        # Modo desarrollo: usar la raíz del proyecto
        # Subimos 2 niveles desde src/utils/ hasta la raíz
        base_path = Path(__file__).resolve().parent.parent.parent
        resource_path = base_path / relative_path

    # Verificar que el archivo existe
    if not resource_path.exists():
        # Intentar rutas alternativas comunes
        alternatives = [
            base_path / relative_path,
            Path.cwd() / relative_path,
            Path(sys.argv[0]).parent / relative_path if sys.argv else None
        ]

        for alt_path in alternatives:
            if alt_path and alt_path.exists():
                return str(alt_path.resolve())

        # Si no se encuentra, lanzar error descriptivo
        raise FileNotFoundError(
            f"No se pudo encontrar el recurso: {relative_path}\n"
            f"Ruta buscada: {resource_path}\n"
            f"Directorio base: {base_path}\n"
            f"Modo: {'PyInstaller' if getattr(sys, 'frozen', False) else 'Desarrollo'}"
        )

    return str(resource_path.resolve())


def get_project_root() -> Path:
    """
    Obtiene la ruta absoluta a la raíz del proyecto.

    Returns:
        Path: Ruta a la raíz del proyecto

    Examples:
        >>> root = get_project_root()
        >>> env_file = root / ".env"
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # En PyInstaller, _MEIPASS es la raíz temporal
        return Path(sys._MEIPASS)
    else:
        # En desarrollo, subir 2 niveles desde src/utils/
        return Path(__file__).resolve().parent.parent.parent


def is_frozen() -> bool:
    """
    Detecta si la aplicación está ejecutándose como ejecutable de PyInstaller.

    Returns:
        bool: True si está empaquetada, False si es script de desarrollo

    Examples:
        >>> if is_frozen():
        ...     print("Ejecutando como .exe")
        ... else:
        ...     print("Ejecutando como script de Python")
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_data_dir() -> Path:
    """
    Obtiene el directorio donde se deben guardar datos persistentes.

    En modo desarrollo: usa la carpeta del proyecto
    En modo PyInstaller: usa AppData del usuario (datos persisten tras cerrar)

    Returns:
        Path: Directorio para datos persistentes

    Examples:
        >>> data_dir = get_data_dir()
        >>> config_file = data_dir / "config.json"
    """
    if is_frozen():
        # En producción: usar AppData del usuario de Windows
        if sys.platform == 'win32':
            appdata = Path(os.environ.get('APPDATA', Path.home()))
            data_dir = appdata / "SistemParqueadero"
        else:
            # Linux/Mac
            data_dir = Path.home() / ".sistema_parqueadero"

        # Crear directorio si no existe
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    else:
        # En desarrollo: usar la raíz del proyecto
        return get_project_root()


def get_logs_dir() -> Path:
    """
    Obtiene el directorio donde se deben guardar los logs.

    Returns:
        Path: Directorio para logs

    Examples:
        >>> logs_dir = get_logs_dir()
        >>> log_file = logs_dir / "app.log"
    """
    if is_frozen():
        # En producción: usar directorio de datos del usuario
        logs_dir = get_data_dir() / "logs"
    else:
        # En desarrollo: usar carpeta logs/ del proyecto
        logs_dir = get_project_root() / "logs"

    # Crear directorio si no existe
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


# Exportar funciones principales
__all__ = [
    'get_resource_path',
    'get_project_root',
    'is_frozen',
    'get_data_dir',
    'get_logs_dir'
]
