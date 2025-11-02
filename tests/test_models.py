# -*- coding: utf-8 -*-
"""
Tests de Modelos
================

Tests para los modelos principales (Funcionario, Vehiculo, Parqueadero)
usando mocks para evitar dependencia de MySQL real.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock


class TestFuncionarioModel:
    """Tests para FuncionarioModel."""

    def test_import_funcionario_model(self):
        """Verifica que FuncionarioModel se pueda importar."""
        from src.models.funcionario import FuncionarioModel
        assert FuncionarioModel is not None

    def test_funcionario_model_instantiation(self, mock_database_manager):
        """Verifica que se pueda instanciar FuncionarioModel con mock DB."""
        from src.models.funcionario import FuncionarioModel

        model = FuncionarioModel(mock_database_manager)
        assert model is not None
        assert model.db == mock_database_manager

    def test_funcionario_crear_validation(self, mock_database_manager):
        """Verifica que el método crear valide correctamente los datos."""
        from src.models.funcionario import FuncionarioModel

        model = FuncionarioModel(mock_database_manager)

        # Mock de execute_query para simular inserción exitosa
        mock_database_manager.execute_query = Mock(return_value=(True, None))

        # Crear funcionario
        exito, mensaje = model.crear(
            cedula='1234567890',
            nombre='Juan',
            apellidos='Pérez',
            direccion_grupo='Administrativa',
            cargo='Asesor',
            celular='3001234567'
        )

        assert exito is True
        assert 'exitosamente' in mensaje.lower()

    def test_funcionario_obtener_todos(self, mock_database_manager, sample_funcionario_data):
        """Verifica que obtener_todos retorne lista de funcionarios."""
        from src.models.funcionario import FuncionarioModel

        model = FuncionarioModel(mock_database_manager)

        # Mock de fetch_all
        mock_database_manager.fetch_all = Mock(return_value=[sample_funcionario_data])

        funcionarios = model.obtener_todos()

        assert isinstance(funcionarios, list)
        assert len(funcionarios) == 1
        assert funcionarios[0]['nombre'] == 'Juan'

    def test_funcionario_validar_cedula_unica(self, mock_database_manager):
        """Verifica validación de cédula única."""
        from src.models.funcionario import FuncionarioModel

        model = FuncionarioModel(mock_database_manager)

        # Mock de fetch_one (no existe cédula)
        mock_database_manager.fetch_one = Mock(return_value=None)

        es_unica, mensaje = model.validar_cedula_unica('1234567890')

        assert es_unica is True


class TestVehiculoModel:
    """Tests para VehiculoModel."""

    def test_import_vehiculo_model(self):
        """Verifica que VehiculoModel se pueda importar."""
        from src.models.vehiculo import VehiculoModel
        assert VehiculoModel is not None

    def test_vehiculo_model_instantiation(self, mock_database_manager):
        """Verifica que se pueda instanciar VehiculoModel con mock DB."""
        from src.models.vehiculo import VehiculoModel

        model = VehiculoModel(mock_database_manager)
        assert model is not None
        assert model.db == mock_database_manager

    def test_vehiculo_crear(self, mock_database_manager):
        """Verifica que el método crear funcione con mock DB."""
        from src.models.vehiculo import VehiculoModel

        model = VehiculoModel(mock_database_manager)

        # Mock de execute_query
        mock_database_manager.execute_query = Mock(return_value=(True, None))
        mock_database_manager.fetch_one = Mock(return_value=None)  # No existe placa

        exito, mensaje = model.crear(
            funcionario_id=1,
            tipo_vehiculo='Carro',
            placa='ABC123',
            tipo_circulacion='PAR'
        )

        assert exito is True
        assert 'exitosamente' in mensaje.lower()

    def test_vehiculo_obtener_por_funcionario(self, mock_database_manager, sample_vehiculo_data):
        """Verifica que obtener_por_funcionario retorne vehículos."""
        from src.models.vehiculo import VehiculoModel

        model = VehiculoModel(mock_database_manager)

        # Mock de fetch_all
        mock_database_manager.fetch_all = Mock(return_value=[sample_vehiculo_data])

        vehiculos = model.obtener_por_funcionario(1)

        assert isinstance(vehiculos, list)
        assert len(vehiculos) == 1
        assert vehiculos[0]['placa'] == 'ABC123'

    def test_vehiculo_validar_placa_unica(self, mock_database_manager):
        """Verifica validación de placa única."""
        from src.models.vehiculo import VehiculoModel

        model = VehiculoModel(mock_database_manager)

        # Mock de fetch_one (no existe placa)
        mock_database_manager.fetch_one = Mock(return_value=None)

        es_unica, mensaje = model.validar_placa_unica('XYZ789')

        assert es_unica is True


class TestParqueaderoModel:
    """Tests para ParqueaderoModel."""

    def test_import_parqueadero_model(self):
        """Verifica que ParqueaderoModel se pueda importar."""
        from src.models.parqueadero import ParqueaderoModel
        assert ParqueaderoModel is not None

    def test_parqueadero_model_instantiation(self, mock_database_manager):
        """Verifica que se pueda instanciar ParqueaderoModel con mock DB."""
        from src.models.parqueadero import ParqueaderoModel

        model = ParqueaderoModel(mock_database_manager)
        assert model is not None
        assert model.db == mock_database_manager

    def test_parqueadero_obtener_todos(self, mock_database_manager, sample_parqueadero_data):
        """Verifica que obtener_todos retorne lista de parqueaderos."""
        from src.models.parqueadero import ParqueaderoModel

        model = ParqueaderoModel(mock_database_manager)

        # Mock de fetch_all y fetch_one
        mock_database_manager.fetch_all = Mock(return_value=[sample_parqueadero_data])
        mock_database_manager.fetch_one = Mock(return_value={'sotano': 'Sótano-1'})

        parqueaderos = model.obtener_todos()

        assert isinstance(parqueaderos, list)
        assert len(parqueaderos) >= 1

    def test_parqueadero_obtener_disponibles(self, mock_database_manager, sample_parqueadero_data):
        """Verifica que obtener_disponibles funcione."""
        from src.models.parqueadero import ParqueaderoModel

        model = ParqueaderoModel(mock_database_manager)

        # Mock de fetch_all
        disponible = {**sample_parqueadero_data, 'estado': 'Disponible'}
        mock_database_manager.fetch_all = Mock(return_value=[disponible])

        parqueaderos = model.obtener_disponibles()

        assert isinstance(parqueaderos, list)

    def test_parqueadero_obtener_estadisticas(self, mock_database_manager):
        """Verifica que obtener_estadisticas retorne datos."""
        from src.models.parqueadero import ParqueaderoModel

        model = ParqueaderoModel(mock_database_manager)

        # Mock de fetch_one y call_procedure
        stats_data = {
            'total_parqueaderos': 100,
            'disponibles': 50,
            'parcialmente_asignados': 30,
            'completos': 20
        }
        mock_database_manager.fetch_one = Mock(return_value=stats_data)
        mock_database_manager.call_procedure = Mock(return_value=[stats_data])

        stats = model.obtener_estadisticas()

        assert isinstance(stats, dict)
        assert 'total_parqueaderos' in stats or stats is not None


class TestModelsValidators:
    """Tests para validadores de modelos."""

    def test_validador_asignacion_import(self):
        """Verifica que ValidadorAsignacion se pueda importar."""
        from src.utils.validaciones_asignaciones import ValidadorAsignacion
        assert ValidadorAsignacion is not None

    def test_validador_asignacion_validar_pico_placa(self):
        """Verifica validación de pico y placa."""
        from src.utils.validaciones_asignaciones import ValidadorAsignacion

        # Caso 1: Sin pico placa solidario, sin conflicto
        es_valido, mensaje = ValidadorAsignacion.validar_pico_placa(
            vehiculo_tipo='Carro',
            tipo_circulacion='PAR',
            tiene_pico_placa_solidario=False,
            mismo_tipo_count=0,
            tiene_parqueadero_exclusivo=False,
            cargo='Asesor'
        )

        assert es_valido is True

        # Caso 2: Con pico placa solidario (siempre válido)
        es_valido, mensaje = ValidadorAsignacion.validar_pico_placa(
            vehiculo_tipo='Carro',
            tipo_circulacion='PAR',
            tiene_pico_placa_solidario=True,
            mismo_tipo_count=1,
            tiene_parqueadero_exclusivo=False,
            cargo='Asesor'
        )

        assert es_valido is True

    def test_validador_campos_import(self):
        """Verifica que ValidadorCampos se pueda importar."""
        from src.utils.validaciones import ValidadorCampos
        assert ValidadorCampos is not None

    def test_validador_campos_validar_cedula(self):
        """Verifica validación de cédula."""
        from src.utils.validaciones import ValidadorCampos

        # Cédula válida
        es_valida, mensaje = ValidadorCampos.validar_cedula('1234567890')
        assert es_valida is True

        # Cédula vacía
        es_valida, mensaje = ValidadorCampos.validar_cedula('')
        assert es_valida is False

    def test_formatter_numero_parqueadero(self):
        """Verifica formateador de número de parqueadero."""
        from src.utils.formatters import format_numero_parqueadero

        # Casos de prueba
        assert format_numero_parqueadero(1) == 'P-001'
        assert format_numero_parqueadero(42) == 'P-042'
        assert format_numero_parqueadero('P-123') == 'P-123'
        assert format_numero_parqueadero('25') == 'P-025'
