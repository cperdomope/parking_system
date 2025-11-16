# -*- coding: utf-8 -*-
"""
Módulo de utilidades

Proporciona funciones auxiliares para la aplicación, incluyendo:
- Gestión de rutas de recursos para PyInstaller
- Validaciones
- Formateo de datos
- Sanitización de inputs
"""

# Importar funciones de resource_path para facilitar el acceso
from .resource_path import (
    get_resource_path,
    get_project_root,
    is_frozen,
    get_data_dir,
    get_logs_dir
)

__all__ = [
    'get_resource_path',
    'get_project_root',
    'is_frozen',
    'get_data_dir',
    'get_logs_dir'
]
