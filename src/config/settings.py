# -*- coding: utf-8 -*-
"""
Configuración del Sistema de Gestión de Parqueaderos
====================================================

Este módulo centraliza toda la configuración del sistema, cargando
variables de entorno desde el archivo .env de manera profesional.

Estructura:
    - Sección 1: Configuración de Aplicación
    - Sección 2: Configuración de Base de Datos
    - Sección 3: Configuración de Seguridad
    - Sección 4: Configuración de UI
    - Sección 5: Enumeraciones y Constantes
    - Sección 6: Listas de Datos

Uso:
    from parking_system.config import settings
    print(settings.APP_NAME)
    print(settings.DB_HOST)
    print(settings.DEBUG)

Requisitos:
    - python-dotenv: pip install python-dotenv
    - Archivo .env en el directorio raíz del proyecto (ver .env.example)
"""

import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


# ============================================================================
# CARGA DE VARIABLES DE ENTORNO
# ============================================================================

def _load_env_vars() -> Path:
    """
    Carga variables de entorno desde el archivo .env.

    Returns:
        Path: Ruta del archivo .env cargado (o None si no existe)

    Raises:
        ImportError: Si python-dotenv no está instalado
    """
    try:
        from dotenv import load_dotenv

        # Buscar .env en el directorio raíz del proyecto
        root_dir = Path(__file__).resolve().parent.parent.parent
        env_path = root_dir / ".env"

        if env_path.exists():
            load_dotenv(env_path)
            if os.getenv("DEBUG", "false").lower() == "true":
                print(f"[OK] Variables de entorno cargadas desde: {env_path}")
            return env_path
        else:
            print(f"[WARNING] Archivo .env no encontrado en {root_dir}")
            print("  Se usarán valores por defecto.")
            print(f"  Copiar .env.example como .env y configurar credenciales reales.")
            return None

    except ImportError:
        print("[ERROR] python-dotenv no instalado")
        print("  Instalar con: pip install python-dotenv")
        print("  Se usarán valores por defecto (NO RECOMENDADO para producción)")
        return None


# Cargar variables al importar el módulo
_ENV_PATH = _load_env_vars()

# Exportar ruta del archivo .env cargado (útil para debugging)
ENV_FILE = _ENV_PATH


# ============================================================================
# HELPERS - Funciones auxiliares para conversión de tipos
# ============================================================================

def _get_bool(key: str, default: bool = False) -> bool:
    """Convierte variable de entorno a booleano."""
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def _get_int(key: str, default: int = 0) -> int:
    """Convierte variable de entorno a entero."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def _get_str(key: str, default: str = "") -> str:
    """Obtiene variable de entorno como string."""
    return os.getenv(key, default)


def _get_path(key: str, default: Optional[str] = None) -> Optional[Path]:
    """Convierte variable de entorno a Path (si existe)."""
    value = os.getenv(key, default)
    return Path(value) if value else None


# ============================================================================
# SECCIÓN 1: CONFIGURACIÓN DE APLICACIÓN
# ============================================================================

# Información de la aplicación
APP_NAME = _get_str("APP_NAME", "Sistema de Gestión de Parqueaderos")
APP_VERSION = _get_str("APP_VERSION", "2.0.3")

# Modo de depuración (IMPORTANTE: False en producción)
DEBUG = _get_bool("DEBUG", True)

# Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = _get_str("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")

# Directorio de logs
LOG_DIR = _get_path("LOG_DIR", "logs")


# ============================================================================
# SECCIÓN 2: CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

@dataclass(frozen=True)
class DatabaseConfig:
    """
    Configuración de conexión a la base de datos MySQL/MariaDB.

    Todas las credenciales se cargan desde variables de entorno (.env)
    para cumplir con mejores prácticas de seguridad.

    IMPORTANTE:
        - Nunca hardcodear contraseñas en el código
        - Usar .env para desarrollo local
        - Usar variables de entorno del sistema en producción

    Atributos:
        host: Hostname o IP del servidor MySQL
        port: Puerto del servidor MySQL (por defecto 3306)
        user: Usuario de la base de datos
        password: Contraseña del usuario (DESDE .ENV)
        database: Nombre de la base de datos
        ssl_ca: Ruta al certificado CA (opcional, para SSL)
        ssl_cert: Ruta al certificado del cliente (opcional)
        ssl_key: Ruta a la clave privada del cliente (opcional)
        pool_size: Tamaño del pool de conexiones (opcional)
        max_overflow: Conexiones adicionales permitidas (opcional)
    """

    host: str = _get_str("DB_HOST", "localhost")
    port: int = _get_int("DB_PORT", 3306)
    user: str = _get_str("DB_USER", "root")
    password: str = _get_str("DB_PASSWORD", "root")  # ⚠️ CAMBIAR EN PRODUCCIÓN
    database: str = _get_str("DB_NAME", "parking_management")

    # Configuración SSL/TLS (opcional para producción)
    ssl_ca: Optional[str] = _get_str("DB_SSL_CA", None) or None
    ssl_cert: Optional[str] = _get_str("DB_SSL_CERT", None) or None
    ssl_key: Optional[str] = _get_str("DB_SSL_KEY", None) or None
    ssl_verify: bool = _get_bool("DB_SSL_VERIFY", False)

    # Pool de conexiones (opcional)
    pool_size: int = _get_int("DB_POOL_SIZE", 5)
    max_overflow: int = _get_int("DB_MAX_OVERFLOW", 10)

    def get_connection_url(self) -> str:
        """
        Genera URL de conexión para SQLAlchemy (si se usa en el futuro).

        Returns:
            str: URL en formato mysql+pymysql://user:password@host:port/database
        """
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def is_production(self) -> bool:
        """
        Verifica si la configuración parece ser de producción.

        Returns:
            bool: True si no usa credenciales por defecto
        """
        return not (self.password == "root" and self.user == "root")


# Instancia global de configuración de BD
# (Mantener compatibilidad con código existente)
DB_CONFIG = DatabaseConfig()

# Variables individuales para compatibilidad con código existente
DB_HOST = DB_CONFIG.host
DB_PORT = DB_CONFIG.port
DB_USER = DB_CONFIG.user
DB_PASSWORD = DB_CONFIG.password
DB_NAME = DB_CONFIG.database
DB_URL = DB_CONFIG.get_connection_url()


# ============================================================================
# SECCIÓN 3: CONFIGURACIÓN DE SEGURIDAD
# ============================================================================

# Clave secreta para sesiones y tokens
SECRET_KEY = _get_str(
    "SECRET_KEY",
    "dev-secret-key-CAMBIAR-EN-PRODUCCION-usar-secrets.token_hex(32)"
)

# Tiempo de expiración de sesión (en minutos)
SESSION_TIMEOUT = _get_int("SESSION_TIMEOUT", 480)  # 8 horas por defecto

# Control de intentos de login
MAX_LOGIN_ATTEMPTS = _get_int("MAX_LOGIN_ATTEMPTS", 5)
ACCOUNT_LOCKOUT_TIME = _get_int("ACCOUNT_LOCKOUT_TIME", 30)  # minutos

# Validar que SECRET_KEY no sea la default en producción
if not DEBUG and "CAMBIAR-EN-PRODUCCION" in SECRET_KEY:
    print("[WARNING] ⚠️  SECRET_KEY usando valor por defecto en producción!")
    print("  Generar nueva clave: python -c \"import secrets; print(secrets.token_hex(32))\"")


# ============================================================================
# SECCIÓN 4: CONFIGURACIÓN DE INTERFAZ DE USUARIO
# ============================================================================

# Tema de la interfaz
UI_THEME = _get_str("UI_THEME", "light")  # light | dark

# Idioma de la interfaz
UI_LANGUAGE = _get_str("UI_LANGUAGE", "es")  # es | en

# Mostrar tooltips de ayuda
SHOW_TOOLTIPS = _get_bool("SHOW_TOOLTIPS", True)


# ============================================================================
# SECCIÓN 5: CONFIGURACIÓN DE REPORTES Y EXPORTACIONES
# ============================================================================

# Directorio para reportes
REPORTS_DIR = _get_path("REPORTS_DIR", "reports")

# Formato por defecto de exportación
DEFAULT_EXPORT_FORMAT = _get_str("DEFAULT_EXPORT_FORMAT", "csv")  # csv | xlsx | pdf

# Retención de reportes (días)
REPORTS_RETENTION_DAYS = _get_int("REPORTS_RETENTION_DAYS", 30)


# ============================================================================
# SECCIÓN 6: ENUMERACIONES Y TIPOS
# ============================================================================

class TipoVehiculo(Enum):
    """
    Tipos de vehículo permitidos en el sistema.

    Valores:
        CARRO: Automóvil de 4 ruedas
        MOTO: Motocicleta de 2 ruedas
        BICICLETA: Bicicleta (sin motor)
    """
    CARRO = "Carro"
    MOTO = "Moto"
    BICICLETA = "Bicicleta"

    @classmethod
    def values(cls) -> list:
        """Retorna lista de valores posibles."""
        return [item.value for item in cls]


class TipoCirculacion(Enum):
    """
    Tipos de circulación según pico y placa.

    Valores:
        PAR: Vehículos con placa terminada en número par (0,2,4,6,8)
        IMPAR: Vehículos con placa terminada en número impar (1,3,5,7,9)
        NA: No aplica (motos, bicicletas, vehículos con pico y placa solidario)
    """
    PAR = "PAR"
    IMPAR = "IMPAR"
    NA = "N/A"

    @classmethod
    def values(cls) -> list:
        """Retorna lista de valores posibles."""
        return [item.value for item in cls]


class EstadoParqueadero(Enum):
    """
    Estados posibles de un parqueadero.

    Valores:
        DISPONIBLE: Sin vehículos asignados
        PARCIALMENTE_ASIGNADO: Con 1 vehículo (puede recibir 1 más si cumple reglas)
        COMPLETO: Con capacidad máxima ocupada
    """
    DISPONIBLE = "Disponible"
    PARCIALMENTE_ASIGNADO = "Parcialmente_Asignado"
    COMPLETO = "Completo"

    @classmethod
    def values(cls) -> list:
        """Retorna lista de valores posibles."""
        return [item.value for item in cls]


# ============================================================================
# SECCIÓN 7: LISTAS DE DATOS Y CONSTANTES
# ============================================================================

# Cargos disponibles en la organización
CARGOS_DISPONIBLES = [
    "Escolta",
    "Conductor",
    "Subdirector(a)",
    "Profesional",
    "Coordinador(a)",
    "Técnico",
    "Asesor(a)",
    "Jefe De Oficina",
    "Director(a)",
    "Auxiliar",
    "Profesional",
    "Coordinador(a)",
    "Asistencial",
    "Secretario(a)",
    "Coordinación",
    "Secretario E.",
    "Técnico Administrativo",
    "Contraloría",

  
    
]

# Direcciones/Departamentos de la organización
DIRECCIONES_DISPONIBLES = [
    "Vehículo Oficial",
    "Subdirector -Subdirección De Metodologías E Instrumentos De Supervisión",
    "Subdirector -Subdirección De Analítica",
    "Subdirector - Subdirección De Tecnologías De La Información",
    "Subdirección De Tecnologías De La Información",
    "Subdirección De Recursos Jurídicos",
    "Subdirección De Metodología E Instrumentos De Supervisión",
    "Subdirección De Analítica",
    "Subdirección - De Defensa Jurídica",
    "Soluciones Inmediatas",
    "Servicios Al Ciudadano Y Promoción De La Participación Ciudadana",
    "Secretaria General",
    "Oficina De Liquidaciones",
    "Oficina De Control Interno",
    "Oficina De Control Disciplinario Interno / Coordinación Grupo De Instrucción Disciplinaria",
    "Oficina De Control Disciplinario Interno",
    "Jurídica - Subdirección Recursos Jurídicos",
    "Jurídica - Subdirección De Defensa Jurídica",
    "Jurídica - Dirección Jurídica",
    "Jefe De Oficina - Oficina De Liquidaciones",
    "Jefe De Oficina - Oficina De Control Interno",
    "Jefe De Oficina - Oficina Asesora De Planeación",
    "Jefe De Oficina - Asesora De Comunicaciones",
    "Jefatura -Oficina De Control Disciplinario Interno",
    "Grupo SIG",
    "Director",
    "Dirección De Conciliación",
    "Director Técnico",
    "Director -Dirección De Talento Humano",
    "Director -Dirección De Servicio Al Ciudadano Y Promoción De La Participación Ciudadana",
    "Director -Dirección De Medidas Especiales Para Prestadores De Servicio De Salud",
    "Director -Dirección De Inspección Y Vigilancia Para Entidades De Aseguramiento En Salud",
    "Director - Dirección De Procesos Jurisdiccionales",
    "Director - Dirección Financiera",
    "Director - Dirección De Investigaciones Para Prestadores De Servicios De Salud",
    "Director - Dirección De Investigaciones Para Operadores Logísticos, Gestores Farmacéuticos, Entes Territoriales, Generadores, Recaudadores Y Administradores De Recursos Del Sistema General De Seguridad Social En Salud",
    "Director - Dirección De Investigaciones Para Entidades De Aseguramiento En Salud",
    "Director - Dirección De Inspección Y Vigilancia Para La Protección Del Usuario",
    "Director - Dirección De Inspección Y Vigilancia Para Generadores, Recaudadores Y Administradores De Recursos Del SGSSS",
    "Director - Dirección De Medidas Especiales Para EPS Y Entidades Adaptadas",
    "Director - Dirección De Inspección Y Vigilancia Para Prestadores De Servicios De Salud",
    "Director - Dirección De Contratación",
    "Dirección Jurídica",
    "Dirección IV Grupo",
    "Dirección IV",
    "Dirección Financiera / Grupo De Tesorería",
    "Dirección Financiera / Grupo De Contabilidad",
    "Dirección Financiera / Grupo De Contabilidad",
    "Dirección Financiera / Coordinación Grupo De Tesorería",
    "Dirección Financiera / Coordinación Grupo De Presupuesto",
    "Dirección Financiera / Coordinación Grupo De Contabilidad",
    "Dirección Financiera / Coordinación Grupo De Cobro Persuasivo Y Jurisdicción Coactiva",
    "Dirección Financiera / Coordinación Control Financiero De Cuentas",
    "Dirección Financiera / Control Financiero De Cuentas",
    "Dirección Financiera - Grupo Contabilidad",
    "Dirección Financiera - Coordinación Grupo De Contribución Y Apoyo Técnico",
    "Dirección Financiera",
    "Dirección De Talento Humano / Coordinación Grupo Para La Gestión Del Empleo Publico",
    "Dirección De Talento Humano / Coordinación Grupo Para El Desarrollo Del Talento Humano",
    "Dirección De Talento Humano / Coordinación Grupo De gestión De La Compensación E Historias Laborales",
    "Dirección De Talento Humano",
    "Dirección De Procesos Jurisdiccionales",
    "Dirección De Medidas Especiales Para P.S.S",
    "Dirección De Investigaciones Para Prestadores De Servicios De Salud",
    "Dirección De Investigaciones Para Prestadores De Servicios De Salud",
    "Dirección De Investigaciones Para Operadores Logísticos, Gestores Farmacéuticos, Entes Territoriales, Generadores, Recaudadores Y Administradores De Recursos Del Sistema General De Seguridad Social En Salud",
    "Dirección De Investigaciones Para Operadores Logísticos",
    "Dirección De Investigaciones Para Entidades De Aseguramiento En Salud",
    "Dirección De Inspección Y Vigilancia Para P.S.S",
    "Dirección De Inspección Y Vigilancia Para Entidades De Aseguramiento En Salud",
    "Dirección De Innovación Y Desarrollo",
    "Dirección De Innovación Y Desarrollo",
    "Dirección De Contratación / Grupo De Gestión Postcontractual",
    "Dirección De Contratación / Grupo De gestión Contractual",
    "Dirección De Contratación",
    "Dirección De Conciliación",
    "Dirección Administrativa / Coordinación Grupo De Recursos Físicos",
    "Dirección Administrativa / Coordinación Grupo Gestión De Notificaciones Y Comunicaciones",
    "Dirección Administrativa / Coordinación Grupo De Gestión Documental",
    "Dirección Administrativa - Grupo De Notificaciones",
    "Dirección Administrativa - Grupo De Correspondencia",
    "Dirección Administrativa - Director",
    "Dirección Administrativa - Coordinación Grupo De Correspondencia",
    "Dirección Administrativa",
    "Dirección Administrativa",
    "Dirección",
    "Despacho - Delegada",
    "Despacho - Asesor",
    "Despacho",
    "Delegatura Para Prestadores De Servicios De Salud",
    "Delegatura Para Operadores Logísticos De Tecnologías En Salud Y Gestores Farmacéuticos",
    "Delegatura Para La Protección Al Usuario",
    "Delegatura Para Entidades De Aseguramiento En Salud",
    "Delegatura Para Entidades De Aseguramiento En Salud",
    "Delegatura De Investigaciones Administrativas",
    "Coordinador - Dirección De Medidas Especiales Para EPS Y Entidades Adaptadas",
    "Coordinación Grupo Interno Jurídico De Medidas Especiales",
    "Coordinación Grupo Interno De Trabajo De Autorizaciones Y Modificaciones",
    "Coordinación Grupo Interno De Trabajo De Atención A PQRS Y Solicitudes De Información",
    "Coordinación Grupo Interno De Trabajo De Atención A La Ciudadanía Y Promoción De La Participación Ciudadana",
    "Coordinación Grupo De Tutelas",
    "Coordinación -Grupo De Secretaría De Investigaciones Administrativas Y Archivo De Gestión",
    "Coordinación Grupo De Inspección Y Vigilancia Al Siau Y La Participación Ciudadana",
    "Coordinación Grupo De Estadísticas Y Análisis PQRD",
    "Coordinación Grupo De Defensa Judicial",
    "Coordinación De Soluciones Inmediatas En Salud",
    "Coordinación Grupo De Secretaría Jurisdiccional",
    "Coordinación Grupo De Inspección Y Vigilancia Al Siau Y La Participación Ciudadana",
    "Grupo De Reconocimiento Económico",
    "Coordinación Grupo De Glosas",
    "Coordinación Grupo De Cobertura Y Afiliaciones",
    "Coordinación - Grupo Sistema Integrado De Gestión",
    "Coordinación - Grupo Proyectos De Inversión",
    "Coordinación - Grupo Interno De Trabajo Técnico – Científico De Medidas Especiales De EPS Y Adaptadas",
    "Coordinación - Grupo Interno De Trabajo Financiero De Medidas Especiales De EPS Y Adaptadas",
    "Coordinación - Grupo Interno De Trabajo De Inspección Y Vigilancia Técnico Científico EPS Y Adaptadas",
    "Coordinación - Grupo Interno De Trabajo De Inspección Y Vigilancia Otras Entidades De Aseguramiento En Salud",
    "Coordinación - Grupo Interno De Trabajo De Inspección Y Vigilancia Financiero",
    "Coordinación - Grupo De Trabajo Inspección Y Vigilancia A Las PQRD",
    "Coordinación - Grupo De Seguimiento A Rentas Cedidas Y Contribución De Vigilancia De Generado, Recauda Y Administrador De Recursos Del SGSSS",
    "Coordinación - Grupo De Inspección Y Vigilancia Para El Mejoramiento De Los Prestadores De Servicios De Salud",
    "Coordinación - Grupo De Inspección Y Vigilancia Financiero",
    "Coordinación - Grupo De Inspección Y Vigilancia En Salud",
    "Coordinación - Grupo De Inspección Y Vigilancia Al Acceso Y Garantía De Calidad De La Atención En Salud En Entidades Territoriales",
    "Coordinación - Grupo De Inspección Y Vigilancia A La Salud Pública En Entidades Territoriales",
    "Coordinación - Grupo De Conceptos, Derechos De Petición Y Apoyo Legislativo",
    "Contraloría",
    "Comunicaciones",
    "Análisis Y Evaluación",
    "Análisis",

]

# Cargos que tienen privilegios especiales
# (Pueden tener parqueadero exclusivo opcional, hasta 4 vehículos)
CARGOS_DIRECTIVOS = ["Director", "Coordinador", "Asesor"]

# Caracteres especiales peligrosos para SQL (para sanitización)
CARACTERES_ESPECIALES_SQL = [
    "'", '"', ";", "--", "/*", "*/", "xp_", "sp_",
    "DROP", "DELETE", "INSERT", "UPDATE", "SELECT",
    "UNION", "EXEC", "EXECUTE"
]


# ============================================================================
# SECCIÓN 8: CONFIGURACIÓN AVANZADA
# ============================================================================

# Modo de mantenimiento
MAINTENANCE_MODE = _get_bool("MAINTENANCE_MODE", False)
MAINTENANCE_MESSAGE = _get_str(
    "MAINTENANCE_MESSAGE",
    "Sistema en mantenimiento. Regresaremos pronto."
)

# Timezone
TIMEZONE = _get_str("TIMEZONE", "America/Bogota")

# Encoding
ENCODING = _get_str("ENCODING", "utf-8")


# ============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================================

def validate_config() -> tuple[bool, list[str]]:
    """
    Valida la configuración del sistema.

    Returns:
        tuple: (es_valida, lista_de_warnings)

    Example:
        >>> is_valid, warnings = validate_config()
        >>> if not is_valid:
        ...     for warning in warnings:
        ...         print(f"WARNING: {warning}")
    """
    warnings = []

    # Validar SECRET_KEY en producción
    if not DEBUG and "CAMBIAR-EN-PRODUCCION" in SECRET_KEY:
        warnings.append("SECRET_KEY usando valor por defecto en producción")

    # Validar credenciales de BD en producción
    if not DEBUG and not DB_CONFIG.is_production():
        warnings.append("Credenciales de BD usando valores por defecto en producción")

    # Validar que existe .env
    if _ENV_PATH is None:
        warnings.append("Archivo .env no encontrado - usando valores por defecto")

    # Validar directorio de logs
    if LOG_DIR and not LOG_DIR.exists():
        warnings.append(f"Directorio de logs no existe: {LOG_DIR}")

    # Validar directorio de reportes
    if REPORTS_DIR and not REPORTS_DIR.exists():
        warnings.append(f"Directorio de reportes no existe: {REPORTS_DIR}")

    is_valid = len(warnings) == 0
    return is_valid, warnings


# ============================================================================
# INFORMACIÓN DE CONFIGURACIÓN (para debugging)
# ============================================================================

def print_config_summary(hide_sensitive: bool = True):
    """
    Imprime un resumen de la configuración actual.

    Args:
        hide_sensitive: Si True, oculta valores sensibles (contraseñas, claves)

    Example:
        >>> print_config_summary()
        [CONFIG] Aplicación: Sistema de Gestión de Parqueaderos v2.0.3
        [CONFIG] Debug: True
        [CONFIG] Base de Datos: root@localhost:3306/parking_management
        ...
    """
    print("\n" + "=" * 70)
    print("CONFIGURACIÓN DEL SISTEMA")
    print("=" * 70)

    print(f"\n[APP] {APP_NAME} v{APP_VERSION}")
    print(f"[APP] Debug: {DEBUG}")
    print(f"[APP] Log Level: {LOG_LEVEL}")

    if hide_sensitive:
        password_display = "***" if DB_PASSWORD else "(vacía)"
        secret_display = "***" if SECRET_KEY else "(vacía)"
    else:
        password_display = DB_PASSWORD
        secret_display = SECRET_KEY

    print(f"\n[DB] Host: {DB_HOST}:{DB_PORT}")
    print(f"[DB] Database: {DB_NAME}")
    print(f"[DB] User: {DB_USER}")
    print(f"[DB] Password: {password_display}")
    print(f"[DB] Production Mode: {DB_CONFIG.is_production()}")

    print(f"\n[SECURITY] Secret Key: {secret_display}")
    print(f"[SECURITY] Session Timeout: {SESSION_TIMEOUT} minutos")

    print(f"\n[UI] Theme: {UI_THEME}")
    print(f"[UI] Language: {UI_LANGUAGE}")

    # Mostrar warnings
    is_valid, warnings = validate_config()
    if warnings:
        print(f"\n[WARNINGS] {len(warnings)} advertencias encontradas:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    else:
        print("\n[OK] Configuración válida")

    print("=" * 70 + "\n")


# ============================================================================
# EXPORTACIONES (para compatibilidad con código existente)
# ============================================================================

# Mantener compatibilidad con imports existentes
__all__ = [
    # Configuración de aplicación
    'APP_NAME',
    'APP_VERSION',
    'DEBUG',
    'LOG_LEVEL',
    'LOG_DIR',
    'ENV_FILE',

    # Configuración de base de datos
    'DatabaseConfig',
    'DB_CONFIG',
    'DB_HOST',
    'DB_PORT',
    'DB_USER',
    'DB_PASSWORD',
    'DB_NAME',
    'DB_URL',

    # Configuración de seguridad
    'SECRET_KEY',
    'SESSION_TIMEOUT',
    'MAX_LOGIN_ATTEMPTS',
    'ACCOUNT_LOCKOUT_TIME',

    # Configuración de UI
    'UI_THEME',
    'UI_LANGUAGE',
    'SHOW_TOOLTIPS',

    # Reportes
    'REPORTS_DIR',
    'DEFAULT_EXPORT_FORMAT',
    'REPORTS_RETENTION_DAYS',

    # Enumeraciones
    'TipoVehiculo',
    'TipoCirculacion',
    'EstadoParqueadero',

    # Listas y constantes
    'CARGOS_DISPONIBLES',
    'DIRECCIONES_DISPONIBLES',
    'CARGOS_DIRECTIVOS',
    'CARACTERES_ESPECIALES_SQL',

    # Funciones de utilidad
    'validate_config',
    'print_config_summary',
]


# ============================================================================
# AUTO-VALIDACIÓN AL IMPORTAR (solo en modo DEBUG)
# ============================================================================

if DEBUG:
    _, config_warnings = validate_config()
    if config_warnings:
        print("\n[CONFIG WARNING] Se encontraron advertencias en la configuración:")
        for warning in config_warnings:
            print(f"  - {warning}")
        print("")
