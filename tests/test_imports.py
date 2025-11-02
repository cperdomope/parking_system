# -*- coding: utf-8 -*-
"""
Tests de Importación de Módulos
================================

Verifica que todos los módulos principales se puedan importar correctamente
sin errores de sintaxis o dependencias faltantes.
"""

import pytest


class TestPackageImports:
    """Tests de importación del paquete principal."""

    def test_import_package(self):
        """Verifica que el paquete principal se importe correctamente."""
        import src as parking_system
        assert parking_system.__version__ == "2.0.3"

    def test_package_metadata(self):
        """Verifica que los metadatos del paquete estén disponibles."""
        import src as parking_system
        assert hasattr(parking_system, '__version__')
        assert hasattr(parking_system, '__author__')
        assert hasattr(parking_system, '__license__')

    def test_public_exports(self):
        """Verifica que las exportaciones públicas estén disponibles."""
        import src as parking_system

        # Verificar enumeraciones
        assert hasattr(parking_system, 'TipoVehiculo')
        assert hasattr(parking_system, 'TipoCirculacion')

        # Verificar constantes
        assert hasattr(parking_system, 'CARGOS_DIRECTIVOS')

        # Verificar utilidades
        assert hasattr(parking_system, 'format_numero_parqueadero')


class TestConfigImports:
    """Tests de importación de módulos de configuración."""

    def test_import_settings(self):
        """Verifica que settings se importe correctamente."""
        from src.config import settings
        assert hasattr(settings, 'DatabaseConfig')

    def test_import_database_config(self):
        """Verifica que DatabaseConfig se importe correctamente."""
        from src.config.settings import DatabaseConfig
        assert DatabaseConfig is not None

    def test_import_enums(self):
        """Verifica que las enumeraciones se importen correctamente."""
        from src.config.settings import TipoVehiculo, TipoCirculacion
        assert TipoVehiculo is not None
        assert TipoCirculacion is not None


class TestDatabaseImports:
    """Tests de importación de módulos de base de datos."""

    def test_import_database_manager(self):
        """Verifica que DatabaseManager se importe correctamente."""
        from src.database.manager import DatabaseManager
        assert DatabaseManager is not None

    def test_import_eliminacion_cascada(self):
        """Verifica que GestorEliminacionCascada se importe correctamente."""
        from src.database.eliminacion_cascada import GestorEliminacionCascada
        assert GestorEliminacionCascada is not None


class TestModelsImports:
    """Tests de importación de modelos."""

    def test_import_funcionario_model(self):
        """Verifica que FuncionarioModel se importe correctamente."""
        from src.models.funcionario import FuncionarioModel
        assert FuncionarioModel is not None

    def test_import_vehiculo_model(self):
        """Verifica que VehiculoModel se importe correctamente."""
        from src.models.vehiculo import VehiculoModel
        assert VehiculoModel is not None

    def test_import_parqueadero_model(self):
        """Verifica que ParqueaderoModel se importe correctamente."""
        from src.models.parqueadero import ParqueaderoModel
        assert ParqueaderoModel is not None


class TestAuthImports:
    """Tests de importación de módulos de autenticación."""

    def test_import_auth_manager(self):
        """Verifica que AuthManager se importe correctamente."""
        from src.auth.auth_manager import AuthManager
        assert AuthManager is not None


class TestUtilsImports:
    """Tests de importación de utilidades."""

    def test_import_validaciones(self):
        """Verifica que los validadores se importen correctamente."""
        from src.utils.validaciones import ValidadorCampos, ValidadorReglasNegocio
        assert ValidadorCampos is not None
        assert ValidadorReglasNegocio is not None

    def test_import_validaciones_asignaciones(self):
        """Verifica que ValidadorAsignacion se importe correctamente."""
        from src.utils.validaciones_asignaciones import ValidadorAsignacion
        assert ValidadorAsignacion is not None

    def test_import_validaciones_vehiculos(self):
        """Verifica que ValidadorVehiculos se importe correctamente."""
        from src.utils.validaciones_vehiculos import ValidadorVehiculos
        assert ValidadorVehiculos is not None

    def test_import_formatters(self):
        """Verifica que format_numero_parqueadero se importe correctamente."""
        from src.utils.formatters import format_numero_parqueadero
        assert format_numero_parqueadero is not None

    def test_import_sanitizacion(self):
        """Verifica que el módulo de sanitización se importe correctamente."""
        from src.utils import sanitizacion
        assert sanitizacion is not None


class TestUIImports:
    """Tests de importación de módulos de UI (verificación básica)."""

    def test_import_ui_modules_exist(self):
        """Verifica que el módulo UI exista."""
        import src.ui
        assert src.ui is not None

    def test_import_widgets_module(self):
        """Verifica que el módulo de widgets exista."""
        import src.ui.widgets
        assert src.ui.widgets is not None
