# -*- coding: utf-8 -*-
"""
Core - Módulo Central del Sistema
==================================

Este paquete contiene componentes centrales del sistema de gestión de
parqueaderos, como logging, utilidades comunes, etc.

Autor: Sistema de Gestión de Parqueaderos
Versión: 2.0.3
"""

from .logger import logger, setup_logger

__all__ = [
    'logger',
    'setup_logger',
]
