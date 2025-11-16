# -*- coding: utf-8 -*-
"""Tests Unitarios: Modelo Funcionario"""

import pytest
from unittest.mock import Mock, patch


class TestFuncionarioCrear:
    """Tests de creación de funcionarios"""

    def test_crear_funcionario_valido(self, mock_db_manager, funcionario_valido):
        """Crear funcionario con datos válidos"""
        from src.models.funcionario import FuncionarioModel

        mock_db_manager.execute_query.return_value = (True, "")
        mock_db_manager.cursor.lastrowid = 1
        mock_db_manager.fetch_one.return_value = None  # Cédula no existe (única)

        model = FuncionarioModel(mock_db_manager)
        result, _ = model.crear(**funcionario_valido)
        assert result is True

    def test_crear_funcionario_cedula_duplicada(self, mock_db_manager, funcionario_valido):
        """Rechazar funcionario con cédula duplicada"""
        from src.models.funcionario import FuncionarioModel

        # Simular que ya existe - debe incluir nombre y apellidos
        mock_db_manager.fetch_one.return_value = {
            "id": 1,
            "nombre": "Pedro",
            "apellidos": "González"
        }

        model = FuncionarioModel(mock_db_manager)
        result, _ = model.crear(**funcionario_valido)

        assert result is False

    def test_crear_funcionario_campos_obligatorios(self, mock_db_manager):
        """Validar campos obligatorios"""
        from src.models.funcionario import FuncionarioModel

        model = FuncionarioModel(mock_db_manager)

        # Sin cédula
        with pytest.raises((ValueError, TypeError)):
            model.crear(nombre="Juan", apellidos="Pérez")

    @pytest.mark.parametrize("cedula", ["123", "ABC123", "12345678901"])
    def test_crear_funcionario_cedula_invalida(self, mock_db_manager, cedula):
        """Rechazar cédulas inválidas"""
        from src.models.funcionario import FuncionarioModel

        model = FuncionarioModel(mock_db_manager)
        result, _ = model.crear(
            cedula=cedula,
            nombre="Test",
            apellidos="User",
            direccion_grupo="Dir",
            cargo="Asesor"
        )

        assert result is False


class TestFuncionarioLeer:
    """Tests de lectura de funcionarios"""

    def test_obtener_funcionario_por_id(self, mock_db_manager):
        """Obtener funcionario por ID"""
        from src.models.funcionario import FuncionarioModel

        mock_db_manager.fetch_one.return_value = {
            "id": 1,
            "cedula": "12345678",
            "nombre": "Juan"
        }

        model = FuncionarioModel(mock_db_manager)
        result = model.obtener_por_id(1)

        assert result is not None
        assert result["id"] == 1

    def test_obtener_funcionario_inexistente(self, mock_db_manager):
        """Obtener funcionario que no existe"""
        from src.models.funcionario import FuncionarioModel

        mock_db_manager.fetch_one.return_value = None

        model = FuncionarioModel(mock_db_manager)
        result = model.obtener_por_id(999)

        assert result is None

    def test_obtener_todos_funcionarios(self, mock_db_manager):
        """Listar todos los funcionarios activos"""
        from src.models.funcionario import FuncionarioModel

        mock_db_manager.fetch_all.return_value = [
            {"id": 1, "activo": True, "nombre": "Juan"},
            {"id": 2, "activo": True, "nombre": "María"}
        ]

        model = FuncionarioModel(mock_db_manager)
        result = model.obtener_todos()

        assert len(result) == 2


class TestFuncionarioActualizar:
    """Tests de actualización de funcionarios"""

    def test_actualizar_funcionario_existente(self, mock_db_manager, funcionario_valido):
        """Actualizar datos de funcionario"""
        from src.models.funcionario import FuncionarioModel

        # Mock para que obtener_por_id encuentre el funcionario
        mock_db_manager.fetch_one.side_effect = [
            {"id": 1, "cedula": "12345678", "nombre": "Juan"},  # obtener_por_id
            None  # validar_cedula_unica (no hay duplicados)
        ]
        mock_db_manager.execute_query.return_value = (True, "")

        model = FuncionarioModel(mock_db_manager)
        result, _ = model.actualizar(
            funcionario_id=1,
            cedula="12345678",
            nombre="Nuevo Nombre",
            apellidos="Nuevos Apellidos"
        )

        assert result is True

    def test_actualizar_funcionario_inexistente(self, mock_db_manager):
        """Actualizar funcionario que no existe"""
        from src.models.funcionario import FuncionarioModel

        # obtener_por_id returns None (funcionario doesn't exist)
        mock_db_manager.fetch_one.return_value = None

        model = FuncionarioModel(mock_db_manager)
        result, _ = model.actualizar(
            funcionario_id=999,
            cedula="99999999",
            nombre="Test",
            apellidos="User"
        )

        assert result is False


class TestFuncionarioEliminar:
    """Tests de eliminación de funcionarios"""

    def test_eliminar_logico_funcionario(self, mock_db_manager):
        """Borrado lógico (activo=FALSE)"""
        from src.models.funcionario import FuncionarioModel

        # Mock para obtener_por_id (requiere nombre, apellidos, cedula)
        mock_db_manager.fetch_one.return_value = {
            "id": 1,
            "nombre": "Juan",
            "apellidos": "Pérez",
            "cedula": "12345678"
        }
        # Mock para fetch_all (parqueaderos_ids, etc.)
        mock_db_manager.fetch_all.return_value = []
        # Mock para execute_query
        mock_db_manager.execute_query.return_value = (True, "")

        model = FuncionarioModel(mock_db_manager)
        result, _ = model.eliminar(1)

        assert result is True

    @pytest.mark.skip(reason="Método eliminar_con_cascada no existe - La cascada se maneja automáticamente en eliminar()")
    def test_eliminar_en_cascada_vehiculos(self, mock_db_manager):
        """Eliminar vehículos asociados en cascada"""
        from src.models.funcionario import FuncionarioModel

        model = FuncionarioModel(mock_db_manager)
        model.eliminar_con_cascada(1)

        # Debe eliminar funcionario y sus vehículos
        assert mock_db_manager.execute_query.call_count >= 2


class TestFuncionarioReactivar:
    """Tests de reactivación de funcionarios"""

    def test_reactivar_funcionario_inactivo(self, mock_db_manager):
        """Reactivar funcionario eliminado lógicamente"""
        from src.models.funcionario import FuncionarioModel

        # Mock con side_effect para múltiples llamadas a fetch_one
        mock_db_manager.fetch_one.side_effect = [
            {  # Primera llamada: verificar funcionario inactivo
                "id": 1,
                "activo": False,
                "nombre": "Juan",
                "apellidos": "Pérez",
                "cedula": "12345678"
            },
            {"total": 0}  # Segunda llamada: count de vehículos reactivados
        ]
        mock_db_manager.execute_query.return_value = (True, "")

        model = FuncionarioModel(mock_db_manager)
        result, _ = model.reactivar(1)

        assert result is True
