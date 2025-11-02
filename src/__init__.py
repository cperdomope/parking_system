# -*- coding: utf-8 -*-
"""
Sistema de Gestión de Parqueaderos
===================================

Sistema integral para la administración de espacios de parqueadero
con soporte para múltiples vehículos, reglas de asignación por pico y placa,
y gestión de funcionarios.

Características principales:
- Gestión de funcionarios, vehículos y parqueaderos
- Asignación inteligente con validación de reglas de negocio
- Soporte para pico y placa solidario y discapacidad
- Reportes y estadísticas en tiempo real
- Autenticación y gestión de usuarios

Uso básico:
    >>> import parking_system
    >>> print(parking_system.__version__)
    '2.0.3'

Componentes principales:
    - config: Configuración del sistema
    - models: Modelos de datos (Funcionario, Vehiculo, Parqueadero)
    - database: Gestión de base de datos
    - utils: Utilidades y validadores
    - ui: Interfaz de usuario (PyQt5)

Seguridad:
    - Las credenciales de base de datos se cargan desde .env
    - No se exponen objetos de conexión directamente
    - Validaciones centralizadas de entrada de datos
"""

__version__ = "2.0.3"
__author__ = "Sistema de Gestión de Parqueaderos"
__license__ = "Proprietary"

# ============================================================================
# EXPORTACIONES PÚBLICAS
# ============================================================================

# Configuración pública (sin credenciales sensibles)
from .config.settings import (
    TipoVehiculo,
    TipoCirculacion,
    CARGOS_DIRECTIVOS,
)

# Utilidades públicas
from .utils.formatters import format_numero_parqueadero

# Modelos públicos (sin exposición de DatabaseManager)
# NOTA: Los modelos requieren instancia de DatabaseManager,
# por lo que no se exportan directamente para evitar mal uso.
# Usar los modelos importándolos explícitamente cuando sea necesario.

# ============================================================================
# API PÚBLICA - Lo que está disponible con 'from parking_system import *'
# ============================================================================

__all__ = [
    # Información del paquete
    "__version__",
    "__author__",
    "__license__",

    # Enumeraciones y constantes
    "TipoVehiculo",
    "TipoCirculacion",
    "CARGOS_DIRECTIVOS",

    # Utilidades
    "format_numero_parqueadero",
]

# ============================================================================
# RESTRICCIONES DE SEGURIDAD
# ============================================================================
# NO EXPORTAR:
# - DatabaseManager (gestión interna de conexiones)
# - DatabaseConfig con credenciales
# - AuthManager con tokens/sesiones
# - Objetos de conexión directa a MySQL
# - Cursores de base de datos
# - Funciones de sanitización (uso interno)
# ============================================================================
