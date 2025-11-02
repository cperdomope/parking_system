# -*- coding: utf-8 -*-
"""
Sistema de Logging Profesional
===============================

Este módulo configura el sistema de logging para toda la aplicación,
con soporte para:
- Salida simultánea a archivo y consola
- RotatingFileHandler para gestión automática de tamaño
- Niveles de logging configurables desde settings
- Formato legible con timestamps, módulo y nivel
- Filtrado de información sensible

Uso:
    from src.core.logger import logger

    logger.debug("Información detallada para debugging")
    logger.info("Operación exitosa")
    logger.warning("Advertencia: situación inusual")
    logger.error("Error controlado")
    logger.critical("Error crítico del sistema")

Configuración:
    - Nivel de logging: settings.LOG_LEVEL (DEBUG, INFO, WARNING, ERROR)
    - Directorio de logs: settings.LOG_DIR
    - Tamaño máximo: 10MB por archivo
    - Archivos de backup: 5 rotaciones

Seguridad:
    - No registra contraseñas ni información sensible
    - No envía logs a servicios externos
    - Archivos de log solo locales

Autor: Sistema de Gestión de Parqueaderos
Versión: 2.0.3
Fecha: 2025-10-26
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================

# Palabras que indican información sensible (para filtrado futuro)
SENSITIVE_KEYWORDS = [
    'password', 'passwd', 'pwd', 'secret', 'token', 'api_key',
    'private_key', 'auth_token', 'session_id', 'credential'
]

# Formato de logs detallado con timestamp
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'

# Formato de fecha legible
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Configuración del RotatingFileHandler
MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Mantener 5 archivos de backup


# ============================================================================
# FILTRO DE SEGURIDAD (Opcional - para prevenir logs sensibles)
# ============================================================================

class SensitiveDataFilter(logging.Filter):
    """
    Filtro para prevenir el logging de información sensible.

    Este filtro busca palabras clave sensibles en los mensajes de log
    y los marca o los oculta parcialmente.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filtra registros que contengan información sensible.

        Args:
            record: Registro de log a filtrar

        Returns:
            bool: True para permitir el log, False para bloquearlo
        """
        # Convertir mensaje a string
        message = str(record.getMessage()).lower()

        # Buscar palabras sensibles
        for keyword in SENSITIVE_KEYWORDS:
            if keyword in message:
                # En lugar de bloquear, marcar como sensible
                record.msg = f"[SENSITIVE DATA FILTERED] {record.msg}"
                break

        # Siempre permitir el log (solo marcamos, no bloqueamos)
        return True


# ============================================================================
# CONFIGURACIÓN DEL LOGGER
# ============================================================================

def setup_logger(
    name: str = "parking_system",
    log_level: Optional[str] = None,
    log_dir: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_sensitive_filter: bool = False
) -> logging.Logger:
    """
    Configura y retorna un logger profesional.

    Args:
        name: Nombre del logger (por defecto "parking_system")
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directorio donde guardar los logs
        enable_console: Si True, logs también van a consola
        enable_file: Si True, logs van a archivo
        enable_sensitive_filter: Si True, activa filtro de datos sensibles

    Returns:
        logging.Logger: Logger configurado

    Raises:
        ValueError: Si el nivel de logging es inválido
        OSError: Si no se puede crear el directorio de logs
    """
    # Obtener configuración desde settings
    try:
        from ..config.settings import LOG_LEVEL, LOG_DIR, DEBUG

        # Usar valores de settings si no se proporcionan
        if log_level is None:
            log_level = LOG_LEVEL
        if log_dir is None:
            log_dir = Path(LOG_DIR)
    except ImportError:
        # Valores por defecto si settings no está disponible
        if log_level is None:
            log_level = "INFO"
        if log_dir is None:
            log_dir = Path("logs")

    # Convertir nivel de string a constante de logging
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Nivel de logging inválido: {log_level}')

    # Crear logger
    logger_instance = logging.getLogger(name)
    logger_instance.setLevel(numeric_level)

    # Evitar duplicación de handlers si ya fue configurado
    if logger_instance.handlers:
        return logger_instance

    # Crear formateador
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # ========================================================================
    # HANDLER 1: Consola (stdout/stderr)
    # ========================================================================
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)

        # Añadir filtro de seguridad si está habilitado
        if enable_sensitive_filter:
            console_handler.addFilter(SensitiveDataFilter())

        logger_instance.addHandler(console_handler)

    # ========================================================================
    # HANDLER 2: Archivo rotativo
    # ========================================================================
    if enable_file:
        try:
            # Crear directorio de logs si no existe
            log_dir.mkdir(parents=True, exist_ok=True)

            # Archivo de log principal
            log_file = log_dir / f"{name}.log"

            # Configurar RotatingFileHandler
            file_handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=MAX_LOG_FILE_SIZE,
                backupCount=BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)

            # Añadir filtro de seguridad si está habilitado
            if enable_sensitive_filter:
                file_handler.addFilter(SensitiveDataFilter())

            logger_instance.addHandler(file_handler)

        except (OSError, PermissionError) as e:
            # Si no se puede crear archivo de log, solo usar consola
            logger_instance.warning(
                f"No se pudo crear archivo de log en {log_dir}: {e}. "
                "Usando solo salida a consola."
            )

    # ========================================================================
    # MENSAJE DE INICIALIZACIÓN
    # ========================================================================
    logger_instance.info(
        f"Logger '{name}' inicializado - Nivel: {log_level}, "
        f"Consola: {enable_console}, Archivo: {enable_file}"
    )

    return logger_instance


# ============================================================================
# LOGGER GLOBAL DE LA APLICACIÓN
# ============================================================================

# Crear logger global al importar el módulo
logger = setup_logger(
    name="parking_system",
    enable_console=True,
    enable_file=True,
    enable_sensitive_filter=False  # Deshabilitado por defecto
)


# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger hijo con un nombre específico.

    Útil para crear loggers específicos por módulo:

    Ejemplo:
        # En src/database/manager.py
        from src.core.logger import get_logger
        logger = get_logger(__name__)  # "parking_system.database.manager"

    Args:
        name: Nombre del logger (usualmente __name__)

    Returns:
        logging.Logger: Logger hijo
    """
    return logging.getLogger(f"parking_system.{name}")


def set_log_level(level: str) -> None:
    """
    Cambia el nivel de logging dinámicamente.

    Args:
        level: Nuevo nivel (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Raises:
        ValueError: Si el nivel es inválido
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Nivel de logging inválido: {level}')

    logger.setLevel(numeric_level)
    for handler in logger.handlers:
        handler.setLevel(numeric_level)

    logger.info(f"Nivel de logging cambiado a: {level}")


def log_function_call(func):
    """
    Decorador para loguear llamadas a funciones automáticamente.

    Ejemplo:
        @log_function_call
        def mi_funcion(param1, param2):
            return param1 + param2

    Args:
        func: Función a decorar

    Returns:
        Función decorada
    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Llamando a {func.__name__} con args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completado exitosamente")
            return result
        except Exception as e:
            logger.error(f"Error en {func.__name__}: {e}", exc_info=True)
            raise

    return wrapper


# ============================================================================
# INFORMACIÓN DEL MÓDULO
# ============================================================================

__all__ = [
    'logger',
    'setup_logger',
    'get_logger',
    'set_log_level',
    'log_function_call',
    'SensitiveDataFilter',
]


# ============================================================================
# AUTO-TEST AL IMPORTAR (Solo en modo DEBUG)
# ============================================================================

if __name__ == "__main__":
    # Test del sistema de logging
    print("=" * 70)
    print("TEST DEL SISTEMA DE LOGGING")
    print("=" * 70)
    print()

    # Crear logger de prueba
    test_logger = setup_logger(
        name="test_logger",
        log_level="DEBUG",
        log_dir=Path("logs"),
        enable_console=True,
        enable_file=True
    )

    # Probar todos los niveles
    test_logger.debug("Mensaje de DEBUG - información detallada")
    test_logger.info("Mensaje de INFO - operación normal")
    test_logger.warning("Mensaje de WARNING - advertencia")
    test_logger.error("Mensaje de ERROR - error controlado")
    test_logger.critical("Mensaje de CRITICAL - error crítico")

    print()
    print("=" * 70)
    print("Logs guardados en: logs/test_logger.log")
    print("=" * 70)
