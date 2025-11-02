# -*- coding: utf-8 -*-
"""
Configuración de pytest y fixtures compartidas
==============================================

Este módulo contiene fixtures reutilizables para todos los tests.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Agregar directorio raíz al path para importar el paquete src
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


@pytest.fixture
def mock_db_connection():
    """
    Mock de conexión a MySQL.
    Simula mysql.connector.connect() sin conectar a base de datos real.
    """
    with patch('mysql.connector.connect') as mock_connect:
        # Crear mock de conexión
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True

        # Crear mock de cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.execute.return_value = None

        # Configurar conexión para retornar cursor
        mock_conn.cursor.return_value = mock_cursor

        # Configurar connect para retornar conexión
        mock_connect.return_value = mock_conn

        yield {
            'connect': mock_connect,
            'connection': mock_conn,
            'cursor': mock_cursor
        }


@pytest.fixture
def mock_database_manager(mock_db_connection):
    """
    Mock de DatabaseManager con conexión simulada.
    """
    from src.database.manager import DatabaseManager

    # Crear instancia con conexión mockeada
    with patch.object(DatabaseManager, 'connect', return_value=True):
        db = DatabaseManager()
        db.connection = mock_db_connection['connection']
        db.cursor = mock_db_connection['cursor']
        yield db


@pytest.fixture
def sample_funcionario_data():
    """Datos de prueba para un funcionario."""
    return {
        'id': 1,
        'cedula': '1234567890',
        'nombre': 'Juan',
        'apellidos': 'Pérez García',
        'direccion_grupo': 'Dirección Administrativa',
        'cargo': 'Asesor',
        'celular': '3001234567',
        'no_tarjeta_proximidad': 'T001',
        'permite_compartir': True,
        'pico_placa_solidario': False,
        'discapacidad': False,
        'tiene_parqueadero_exclusivo': False,
        'tiene_carro_hibrido': False,
        'activo': True
    }


@pytest.fixture
def sample_vehiculo_data():
    """Datos de prueba para un vehículo."""
    return {
        'id': 1,
        'funcionario_id': 1,
        'tipo_vehiculo': 'Carro',
        'placa': 'ABC123',
        'tipo_circulacion': 'PAR',
        'activo': True
    }


@pytest.fixture
def sample_parqueadero_data():
    """Datos de prueba para un parqueadero."""
    return {
        'id': 1,
        'numero_parqueadero': 'P-001',
        'tipo_espacio': 'Carro',
        'estado': 'Disponible',
        'sotano': 'Sótano-1',
        'activo': True
    }


@pytest.fixture
def mock_env_vars():
    """Mock de variables de entorno para tests."""
    env_vars = {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_parking_db',
        'DB_PORT': '3306'
    }

    with patch.dict('os.environ', env_vars):
        yield env_vars


@pytest.fixture(autouse=True)
def suppress_db_print_output(monkeypatch):
    """
    Suprime los mensajes de print durante los tests.
    Hace que los tests sean más limpios.
    """
    # Redirigir print a una función que no hace nada
    def mock_print(*args, **kwargs):
        pass

    # Solo aplicar en funciones específicas
    # monkeypatch.setattr('builtins.print', mock_print)
    pass  # Deshabilitado por ahora para ver output de debugging
