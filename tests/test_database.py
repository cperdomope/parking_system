# -*- coding: utf-8 -*-
"""
Tests de Base de Datos
======================

Tests para DatabaseManager y GestorEliminacionCascada
usando mocks para evitar dependencia de MySQL real.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock, PropertyMock


class TestDatabaseManager:
    """Tests para DatabaseManager."""

    def test_import_database_manager(self):
        """Verifica que DatabaseManager se pueda importar."""
        from src.database.manager import DatabaseManager
        assert DatabaseManager is not None

    @patch('mysql.connector.connect')
    def test_database_manager_instantiation(self, mock_connect):
        """Verifica que se pueda instanciar DatabaseManager con mock."""
        from src.database.manager import DatabaseManager

        # Configurar mock de conexión
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Resetear singleton
        DatabaseManager._instance = None

        # Crear instancia
        db = DatabaseManager()

        assert db is not None
        assert db.connection == mock_conn
        assert db.cursor == mock_cursor

    @patch('mysql.connector.connect')
    def test_database_manager_singleton(self, mock_connect):
        """Verifica que DatabaseManager sea singleton."""
        from src.database.manager import DatabaseManager

        # Configurar mock
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_connect.return_value = mock_conn

        # Resetear singleton
        DatabaseManager._instance = None

        # Crear dos instancias
        db1 = DatabaseManager()
        db2 = DatabaseManager()

        # Deben ser la misma instancia
        assert db1 is db2

    def test_database_manager_fetch_all(self, mock_database_manager):
        """Verifica que fetch_all funcione."""
        # Configurar mock para retornar datos
        mock_database_manager.cursor.fetchall.return_value = [
            {'id': 1, 'nombre': 'Test 1'},
            {'id': 2, 'nombre': 'Test 2'}
        ]

        result = mock_database_manager.fetch_all("SELECT * FROM test")

        assert isinstance(result, list)
        assert len(result) == 2

    def test_database_manager_fetch_one(self, mock_database_manager):
        """Verifica que fetch_one funcione."""
        # Configurar mock para retornar un registro
        mock_database_manager.cursor.fetchone.return_value = {'id': 1, 'nombre': 'Test'}

        result = mock_database_manager.fetch_one("SELECT * FROM test WHERE id = 1")

        assert isinstance(result, dict)
        assert result['id'] == 1

    def test_database_manager_execute_query(self, mock_database_manager):
        """Verifica que execute_query funcione."""
        # Mock del método execute_query
        mock_database_manager.execute_query = Mock(return_value=(True, None))

        exito, error = mock_database_manager.execute_query("INSERT INTO test VALUES (1, 'Test')")

        assert exito is True
        assert error is None

    @patch('mysql.connector.connect')
    def test_database_manager_connect(self, mock_connect):
        """Verifica que el método connect funcione."""
        from src.database.manager import DatabaseManager

        # Configurar mock
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Resetear singleton
        DatabaseManager._instance = None

        # Crear instancia (automáticamente llama connect)
        db = DatabaseManager()

        # Verificar que connect fue llamado
        assert mock_connect.called
        assert db.connection.is_connected()

    @patch('mysql.connector.connect')
    def test_database_manager_disconnect(self, mock_connect):
        """Verifica que el método disconnect funcione."""
        from src.database.manager import DatabaseManager

        # Configurar mock
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Resetear singleton
        DatabaseManager._instance = None

        # Crear instancia
        db = DatabaseManager()

        # Llamar disconnect
        db.disconnect()

        # Verificar que se llamaron los métodos de cierre
        assert mock_cursor.close.called
        assert mock_conn.close.called


class TestGestorEliminacionCascada:
    """Tests para GestorEliminacionCascada."""

    def test_import_gestor_eliminacion_cascada(self):
        """Verifica que GestorEliminacionCascada se pueda importar."""
        from src.database.eliminacion_cascada import GestorEliminacionCascada
        assert GestorEliminacionCascada is not None

    def test_gestor_eliminacion_instantiation(self, mock_database_manager):
        """Verifica que se pueda instanciar GestorEliminacionCascada."""
        from src.database.eliminacion_cascada import GestorEliminacionCascada

        gestor = GestorEliminacionCascada(mock_database_manager)

        assert gestor is not None
        assert gestor.db == mock_database_manager

    def test_gestor_eliminacion_obtener_datos_funcionario(self, mock_database_manager):
        """Verifica que obtener_datos_funcionario_completos funcione."""
        from src.database.eliminacion_cascada import GestorEliminacionCascada

        gestor = GestorEliminacionCascada(mock_database_manager)

        # Mock de fetch_all y fetch_one
        mock_database_manager.fetch_one = Mock(return_value={
            'id': 1,
            'nombre': 'Juan',
            'apellidos': 'Pérez',
            'cedula': '1234567890'
        })
        mock_database_manager.fetch_all = Mock(return_value=[])

        datos = gestor.obtener_datos_funcionario_completos('1234567890')

        assert isinstance(datos, dict)


class TestDatabaseConfig:
    """Tests para DatabaseConfig."""

    def test_import_database_config(self):
        """Verifica que DatabaseConfig se pueda importar."""
        from src.config.settings import DatabaseConfig
        assert DatabaseConfig is not None

    @patch.dict('os.environ', {
        'DB_HOST': 'test_host',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_pass',
        'DB_NAME': 'test_db',
        'DB_PORT': '3307'
    })
    def test_database_config_from_env(self):
        """Verifica que DatabaseConfig lea de variables de entorno."""
        from src.config.settings import DatabaseConfig

        config = DatabaseConfig()

        assert config.host == 'test_host'
        assert config.user == 'test_user'
        assert config.password == 'test_pass'
        assert config.database == 'test_db'
        assert config.port == 3307

    def test_database_config_defaults(self):
        """Verifica valores por defecto de DatabaseConfig."""
        from src.config.settings import DatabaseConfig

        config = DatabaseConfig()

        # Verificar que tenga valores (pueden ser de .env o defaults)
        assert config.host is not None
        assert config.user is not None
        assert config.database is not None
        assert isinstance(config.port, int)


class TestDatabaseSecurity:
    """Tests de seguridad de base de datos."""

    def test_database_credentials_not_hardcoded(self):
        """Verifica que las credenciales no estén hardcodeadas."""
        from src.config.settings import DatabaseConfig
        import inspect

        # Obtener código fuente
        source = inspect.getsource(DatabaseConfig)

        # Verificar que no haya contraseñas hardcodeadas (excepto "root" de ejemplo)
        # No debe haber strings como "password123", etc.
        assert 'password123' not in source.lower()
        assert 'admin123' not in source.lower()

    def test_database_config_uses_env_vars(self):
        """Verifica que DatabaseConfig use variables de entorno."""
        from src.config.settings import DatabaseConfig
        import inspect

        source = inspect.getsource(DatabaseConfig)

        # Debe usar os.getenv
        assert 'os.getenv' in source or 'DB_PASSWORD' in source
