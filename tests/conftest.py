# -*- coding: utf-8 -*-
"""
Configuración global de pytest para Parking Management System
Fixtures compartidas, mocks y utilidades de testing
"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, date
from typing import Dict, List, Any

import pytest
from PyQt5.QtWidgets import QApplication

# Agregar src al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))


# ============================================================
# FIXTURES DE APLICACIÓN
# ============================================================

@pytest.fixture(scope="session")
def qapp():
    """
    Fixture de QApplication para tests de UI
    Scope session: Una instancia para toda la sesión de tests
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Cleanup no necesario, pytest maneja el ciclo de vida


# ============================================================
# FIXTURES DE BASE DE DATOS
# ============================================================

@pytest.fixture(scope="function")
def mock_db_connection():
    """
    Mock de conexión a base de datos
    Simula una conexión MySQL sin requerir BD real
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Configurar comportamiento del cursor
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None
    mock_cursor.execute.return_value = None
    mock_cursor.lastrowid = 1
    mock_cursor.rowcount = 1

    # Conectar cursor a conexión
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.return_value = None
    mock_conn.rollback.return_value = None
    mock_conn.is_connected.return_value = True

    return mock_conn, mock_cursor


@pytest.fixture(scope="function")
def mock_db_manager(mock_db_connection):
    """
    Mock del DatabaseManager
    """
    from src.database.manager import DatabaseManager

    mock_conn, mock_cursor = mock_db_connection

    with patch.object(DatabaseManager, '__new__') as mock_new:
        mock_instance = MagicMock()
        mock_instance.connection = mock_conn
        mock_instance.cursor = mock_cursor
        mock_instance.connect.return_value = True
        mock_instance.disconnect.return_value = None
        mock_instance.execute_query.return_value = True
        mock_instance.fetch_all.return_value = []
        mock_instance.fetch_one.return_value = None

        mock_new.return_value = mock_instance
        yield mock_instance


# ============================================================
# FIXTURES DE DATOS DE PRUEBA
# ============================================================

@pytest.fixture
def funcionario_valido():
    """Datos válidos de un funcionario"""
    return {
        "cedula": "12345678",
        "nombre": "Juan Carlos",
        "apellidos": "García López",
        "direccion_grupo": "Dirección Administrativa",
        "cargo": "Asesor",
        "celular": "3001234567",
        "tarjeta": "12345",
        "permite_compartir": True,
        "pico_placa_solidario": False,
        "discapacidad": False,
        "tiene_parqueadero_exclusivo": False,
        "tiene_carro_hibrido": False
    }


@pytest.fixture
def funcionario_director():
    """Funcionario con cargo de Director"""
    return {
        "cedula": "87654321",
        "nombre": "María",
        "apellidos": "Rodríguez",
        "direccion_grupo": "Dirección General",
        "cargo": "Director",
        "celular": "3109876543",
        "tarjeta": "54321",
        "permite_compartir": False,
        "pico_placa_solidario": False,
        "discapacidad": False,
        "tiene_parqueadero_exclusivo": True,
        "tiene_carro_hibrido": False
    }


@pytest.fixture
def vehiculo_valido():
    """Datos válidos de un vehículo"""
    return {
        "placa": "ABC123",
        "tipo_vehiculo": "Carro",
        "tipo_circulacion": "IMPAR",  # Termina en 3
        "funcionario_id": 1
    }


@pytest.fixture
def vehiculo_par():
    """Vehículo con circulación PAR"""
    return {
        "placa": "XYZ890",
        "tipo_vehiculo": "Carro",
        "tipo_circulacion": "PAR",  # Termina en 0
        "funcionario_id": 2
    }


@pytest.fixture
def parqueadero_disponible():
    """Parqueadero disponible"""
    return {
        "numero_parqueadero": "S1-001",
        "sotano": "Sotano-1",
        "tipo_espacio": "Carro",
        "estado": "Disponible"
    }


# ============================================================
# FIXTURES DE DATOS INVÁLIDOS (Para tests negativos)
# ============================================================

@pytest.fixture
def datos_invalidos_funcionario():
    """Conjunto de datos inválidos para tests de validación"""
    return {
        "cedula_corta": {
            "cedula": "123",  # Muy corta
            "nombre": "Test",
            "apellidos": "User"
        },
        "cedula_larga": {
            "cedula": "12345678901",  # Muy larga
            "nombre": "Test",
            "apellidos": "User"
        },
        "cedula_letras": {
            "cedula": "ABC12345",  # Contiene letras
            "nombre": "Test",
            "apellidos": "User"
        },
        "nombre_numeros": {
            "cedula": "12345678",
            "nombre": "Juan123",  # Contiene números
            "apellidos": "García"
        },
        "nombre_vacio": {
            "cedula": "12345678",
            "nombre": "",  # Vacío
            "apellidos": "García"
        }
    }


@pytest.fixture
def datos_invalidos_vehiculo():
    """Datos inválidos de vehículos"""
    return {
        "placa_corta": {
            "placa": "AB1",  # Muy corta
            "tipo_vehiculo": "Carro"
        },
        "placa_larga": {
            "placa": "ABC12345",  # Muy larga
            "tipo_vehiculo": "Carro"
        },
        "placa_especial": {
            "placa": "AB@123",  # Caracteres especiales
            "tipo_vehiculo": "Carro"
        },
        "tipo_invalido": {
            "placa": "ABC123",
            "tipo_vehiculo": "Camion"  # Tipo no permitido
        }
    }


# ============================================================
# FIXTURES DE SEGURIDAD
# ============================================================

@pytest.fixture
def payloads_sql_injection():
    """
    Payloads comunes de SQL Injection para tests de seguridad
    """
    return [
        "' OR '1'='1",
        "'; DROP TABLE usuarios; --",
        "admin'--",
        "' UNION SELECT NULL, NULL, NULL--",
        "1' AND '1'='1",
        "'; EXEC xp_cmdshell('dir'); --",
        "' OR 1=1--",
        "admin' OR 1=1#",
        "' OR 'x'='x",
        "1'; DROP TABLE funcionarios--"
    ]


@pytest.fixture
def payloads_xss():
    """
    Payloads comunes de XSS para tests de seguridad
    """
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "';alert(String.fromCharCode(88,83,83))//'"
    ]


@pytest.fixture
def payloads_path_traversal():
    """
    Payloads de Path Traversal para tests de seguridad
    """
    return [
        "../../etc/passwd",
        "..\\..\\windows\\system32\\config\\sam",
        "....//....//....//etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "/etc/passwd",
        "C:\\Windows\\System32\\config\\SAM"
    ]


# ============================================================
# FIXTURES DE PERFORMANCE
# ============================================================

@pytest.fixture
def large_dataset_funcionarios():
    """
    Dataset grande para tests de performance
    1000 funcionarios simulados
    """
    funcionarios = []
    for i in range(1, 1001):
        funcionarios.append({
            "cedula": f"{10000000 + i}",
            "nombre": f"Funcionario{i}",
            "apellidos": f"Apellido{i}",
            "direccion_grupo": "Dirección Test",
            "cargo": "Asesor" if i % 3 != 0 else "Coordinador",
            "celular": f"300{str(i).zfill(7)}",
            "tarjeta": str(i),
            "permite_compartir": i % 2 == 0
        })
    return funcionarios


@pytest.fixture
def large_dataset_vehiculos():
    """Dataset grande de vehículos"""
    vehiculos = []
    for i in range(1, 1001):
        vehiculos.append({
            "placa": f"TST{str(i).zfill(3)}",
            "tipo_vehiculo": "Carro",
            "tipo_circulacion": "PAR" if i % 2 == 0 else "IMPAR",
            "funcionario_id": (i % 100) + 1  # Distribuir entre 100 funcionarios
        })
    return vehiculos


# ============================================================
# FIXTURES DE ENTORNO
# ============================================================

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """
    Configurar variables de entorno para tests
    Autouse=True: Se ejecuta automáticamente para todos los tests
    """
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_PORT", "3306")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.setenv("DB_NAME", "parking_management_test")


@pytest.fixture
def temp_test_dir(tmp_path):
    """
    Directorio temporal para tests que requieren I/O
    """
    test_dir = tmp_path / "parking_test"
    test_dir.mkdir()

    # Crear subdirectorios
    (test_dir / "logs").mkdir()
    (test_dir / "reports").mkdir()

    yield test_dir

    # Cleanup automático por pytest


# ============================================================
# UTILIDADES DE TESTING
# ============================================================

@pytest.fixture
def assert_sql_safe():
    """
    Función helper para verificar que un string es seguro contra SQL injection
    """
    def _assert(value: str):
        dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'EXEC', 'UNION',
            'INSERT', 'UPDATE', 'SELECT', '--', ';', 'xp_'
        ]
        value_upper = value.upper()
        for keyword in dangerous_keywords:
            assert keyword not in value_upper, f"SQL keyword '{keyword}' detectado en: {value}"
    return _assert


@pytest.fixture
def assert_no_xss():
    """
    Función helper para verificar que un string está sanitizado contra XSS
    """
    def _assert(value: str):
        dangerous_tags = ['<script', '<iframe', '<img', '<svg', 'javascript:', 'onerror=', 'onload=']
        value_lower = value.lower()
        for tag in dangerous_tags:
            assert tag not in value_lower, f"XSS tag '{tag}' detectado en: {value}"
    return _assert


# ============================================================
# HOOKS DE PYTEST
# ============================================================

def pytest_configure(config):
    """
    Hook ejecutado al inicio de la sesión de pytest
    """
    import io
    import codecs

    # Forzar UTF-8 en stdout para Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("\n" + "="*70)
    print("PARKING MANAGEMENT SYSTEM - SUITE DE PRUEBAS")
    print("="*70)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Coverage: Habilitado")
    print("="*70 + "\n")


def pytest_collection_modifyitems(config, items):
    """
    Hook para modificar items de test después de la colección
    Agregar markers automáticamente según el path
    """
    for item in items:
        # Agregar marker según path del archivo
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Hook ejecutado al final de la sesión para mostrar resumen personalizado
    """
    print("\n" + "="*70)
    print("RESUMEN DE TESTING")
    print("="*70)

    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    errors = len(terminalreporter.stats.get('error', []))

    total = passed + failed + skipped + errors

    if total > 0:
        coverage_percentage = (passed / total) * 100
        print(f"[OK] Pasados: {passed}")
        print(f"[FAIL] Fallidos: {failed}")
        print(f"[SKIP] Omitidos: {skipped}")
        print(f"[ERROR] Errores: {errors}")
        print(f"Cobertura: {coverage_percentage:.2f}%")

    print("="*70 + "\n")
