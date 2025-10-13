# -*- coding: utf-8 -*-
"""
Configuración general del sistema de gestión de parqueadero
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv

    # Buscar .env en el directorio raíz del proyecto
    root_dir = Path(__file__).resolve().parent.parent.parent
    env_path = root_dir / ".env"

    if env_path.exists():
        load_dotenv(env_path)
        print(f"[OK] Variables de entorno cargadas desde: {env_path}")
    else:
        print(f"[WARNING] Archivo .env no encontrado en {env_path}")
        print("  Usando valores por defecto. Crear .env para produccion.")
except ImportError:
    print("[WARNING] python-dotenv no instalado. Instalar con: pip install python-dotenv")


@dataclass
class DatabaseConfig:
    """
    Configuración de conexión a la base de datos

    IMPORTANTE: Las credenciales se cargan desde variables de entorno (.env)
    para mayor seguridad. Nunca hardcodear contraseñas en el código.
    """

    host: str = os.getenv("DB_HOST", "localhost")
    user: str = os.getenv("DB_USER", "root")
    password: str = os.getenv("DB_PASSWORD", "root")  # Desde .env
    database: str = os.getenv("DB_NAME", "parking_management")
    port: int = int(os.getenv("DB_PORT", "3306"))

    # Configuración SSL (opcional para producción)
    ssl_ca: str = os.getenv("DB_SSL_CA", None)
    ssl_cert: str = os.getenv("DB_SSL_CERT", None)
    ssl_key: str = os.getenv("DB_SSL_KEY", None)


class TipoVehiculo(Enum):
    """Tipos de vehículo permitidos"""

    CARRO = "Carro"
    MOTO = "Moto"
    BICICLETA = "Bicicleta"


class TipoCirculacion(Enum):
    """Tipos de circulación según pico y placa"""

    PAR = "PAR"
    IMPAR = "IMPAR"
    NA = "N/A"


# Listas de opciones para formularios
CARGOS_DISPONIBLES = [
    "Asesor",
    "Auxiliar",
    "Conductor",
    "Contraloría",
    "Coordinador",
    "Director",
    "Jefe de Oficina",
    "Profesional",
    "Técnico",
]

DIRECCIONES_DISPONIBLES = [
    "Direc de Proces Jurisdic",
    "Dirección Financ Grup de Tesorería",
    "Dirección Juridica",
    "Dirección TTHH",
    "Jurídica-Subd de Defensa Jurid",
    "Ofic Control Disc Interno",
    "Oficina de liquidaciones",
    "Secretaría General",
    "Serv al Ciudadano y Prom Partic Ciudadana",
    "Soluciones Inmediatas",
    "Subdirección de Analítica",
    "Subdirección de Defensa",
    "Vehículo Oficial",
]
