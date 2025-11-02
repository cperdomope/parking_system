# -*- coding: utf-8 -*-
"""
Tests para el Sistema de Gestión de Parqueaderos
=================================================

Suite de tests que verifican la correcta importación y funcionamiento
de los módulos principales sin depender de MySQL real.

Estructura:
    - test_imports.py: Verifica que todos los módulos se importen correctamente
    - test_models.py: Tests de modelos (Funcionario, Vehiculo, Parqueadero) con mocks
    - test_database.py: Tests de DatabaseManager con mocks
    - test_auth.py: Tests de autenticación con mocks
    - conftest.py: Fixtures compartidas y configuración de pytest

Ejecución:
    pytest -v                    # Verbose
    pytest -q                    # Quiet
    pytest tests/test_imports.py # Solo tests de imports
    pytest --cov=src             # Con cobertura
"""

__version__ = "1.0.0"
