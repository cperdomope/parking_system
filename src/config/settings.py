# -*- coding: utf-8 -*-
"""
Configuración general del sistema de gestión de parqueadero
"""

from dataclasses import dataclass
from enum import Enum


@dataclass
class DatabaseConfig:
    """Configuración de conexión a la base de datos"""
    host: str = "localhost"
    user: str = "root"
    password: str = "root"  # Cambiar según tu configuración
    database: str = "parking_management"
    port: int = 3306


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
    "Asesor", "Auxiliar", "Conductor", "Contraloría", "Coordinador",
    "Director", "Jefe de Oficina", "Profesional", "Técnico"
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
    "Vehículo Oficial"
]