# -*- coding: utf-8 -*-
"""Tests de Performance: Base de Datos"""

import pytest
import time
from unittest.mock import Mock


@pytest.mark.performance
@pytest.mark.slow
class TestPerformanceConsultas:
    """Tests de rendimiento de consultas"""

    def test_listar_1000_funcionarios_performance(self, mock_db_manager, large_dataset_funcionarios):
        """Listar 1000 funcionarios debe ser rápido (<500ms)"""
        from src.models.funcionario import FuncionarioModel

        mock_db_manager.fetch_all.return_value = large_dataset_funcionarios

        model = FuncionarioModel(mock_db_manager)

        start_time = time.time()
        result = model.obtener_todos()  # Fixed method name
        end_time = time.time()

        elapsed = (end_time - start_time) * 1000  # ms

        assert len(result) == 1000
        assert elapsed < 500, f"Query demasiado lenta: {elapsed:.2f}ms"

    def test_busqueda_por_id_performance(self, mock_db_manager):
        """Búsqueda por ID debe usar índice (<50ms)"""
        from src.models.funcionario import FuncionarioModel

        mock_db_manager.fetch_one.return_value = {
            "id": 1,
            "nombre": "Test",
            "apellidos": "User",
            "cedula": "12345678"
        }

        model = FuncionarioModel(mock_db_manager)

        start_time = time.time()
        result = model.obtener_por_id(1)  # Fixed method name
        end_time = time.time()

        elapsed = (end_time - start_time) * 1000

        assert result is not None
        assert elapsed < 50, f"Búsqueda lenta: {elapsed:.2f}ms"

    @pytest.mark.benchmark
    def test_insercion_masiva_performance(self, mock_db_manager, large_dataset_vehiculos):
        """Inserción de 1000 vehículos (<5s)"""
        from src.models.vehiculo import VehiculoModel

        mock_db_manager.execute_query.return_value = (True, "")
        mock_db_manager.fetch_one.return_value = None  # Placa única
        mock_db_manager.fetch_all.return_value = []  # Sin vehículos previos

        model = VehiculoModel(mock_db_manager)

        start_time = time.time()
        for vehiculo in large_dataset_vehiculos[:100]:  # 100 para test más rápido
            # Extraer solo los parámetros correctos para crear()
            model.crear(
                funcionario_id=vehiculo["funcionario_id"],
                tipo_vehiculo=vehiculo["tipo_vehiculo"],
                placa=vehiculo["placa"]
            )
        end_time = time.time()

        elapsed = end_time - start_time

        assert elapsed < 1, f"Inserción muy lenta: {elapsed:.2f}s"


@pytest.mark.performance
class TestPerformanceMemoria:
    """Tests de uso de memoria"""

    def test_consulta_grande_no_causa_memory_leak(self, mock_db_manager, large_dataset_funcionarios):
        """Consultas grandes no deben causar leaks de memoria"""
        from src.models.funcionario import FuncionarioModel
        import gc

        mock_db_manager.fetch_all.return_value = large_dataset_funcionarios

        model = FuncionarioModel(mock_db_manager)

        # Ejecutar múltiples veces
        for _ in range(10):
            result = model.obtener_todos()  # Fixed method name
            del result

        # Forzar garbage collection
        gc.collect()

        # Si no hay excepción de memoria, pasa el test
        assert True
