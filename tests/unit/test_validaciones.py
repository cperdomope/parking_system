# -*- coding: utf-8 -*-
"""Tests Unitarios: Validaciones"""

import pytest


class TestValidadorCedula:
    """Tests de validación de cédula"""

    @pytest.mark.parametrize("cedula_valida", [
        "1234567", "12345678", "123456789", "1234567890"
    ])
    def test_cedulas_validas(self, cedula_valida):
        from src.utils.validaciones import ValidadorCampos

        result, _ = ValidadorCampos.validar_cedula(cedula_valida)
        assert result is True

    @pytest.mark.parametrize("cedula_invalida", [
        "123", "12345678901", "ABC123", "1234-567", ""
    ])
    def test_cedulas_invalidas(self, cedula_invalida):
        from src.utils.validaciones import ValidadorCampos

        result, _ = ValidadorCampos.validar_cedula(cedula_invalida)
        assert result is False


class TestValidadorPlaca:
    """Tests de validación de placa"""

    @pytest.mark.parametrize("placa_valida", [
        "ABC123", "XYZ890", "DEF45"
    ])
    def test_placas_validas(self, placa_valida):
        from src.utils.validaciones import ValidadorCampos

        result, _ = ValidadorCampos.validar_placa(placa_valida)
        assert result is True

    @pytest.mark.parametrize("placa_invalida", [
        "AB", "ABC123456", "AB@123", ""
    ])
    def test_placas_invalidas(self, placa_invalida):
        from src.utils.validaciones import ValidadorCampos

        result, _ = ValidadorCampos.validar_placa(placa_invalida)
        assert result is False


class TestValidadorNombre:
    """Tests de validación de nombres"""

    @pytest.mark.parametrize("nombre_valido", [
        "Juan", "María José", "José Andrés", "Ángel"
    ])
    def test_nombres_validos(self, nombre_valido):
        from src.utils.validaciones import ValidadorCampos

        result, _ = ValidadorCampos.validar_nombre(nombre_valido)
        assert result is True

    @pytest.mark.parametrize("nombre_invalido", [
        "Juan123", "Test@", "<script>", "123"
    ])
    def test_nombres_invalidos(self, nombre_invalido):
        from src.utils.validaciones import ValidadorCampos

        result, _ = ValidadorCampos.validar_nombre(nombre_invalido)
        assert result is False


class TestValidadorPicoPlaca:
    """Tests de validación pico y placa"""

    @pytest.mark.parametrize("placa,esperado", [
        ("ABC121", "IMPAR"),  # 1: 1-5 = IMPAR
        ("ABC122", "IMPAR"),  # 2: 1-5 = IMPAR
        ("ABC123", "IMPAR"),  # 3: 1-5 = IMPAR
        ("ABC124", "IMPAR"),  # 4: 1-5 = IMPAR
        ("ABC125", "IMPAR"),  # 5: 1-5 = IMPAR
        ("ABC126", "PAR"),    # 6: 6-9/0 = PAR
        ("ABC127", "PAR"),    # 7: 6-9/0 = PAR
        ("ABC128", "PAR"),    # 8: 6-9/0 = PAR
        ("ABC129", "PAR"),    # 9: 6-9/0 = PAR
        ("ABC120", "PAR")     # 0: 6-9/0 = PAR
    ])
    def test_calcular_circulacion_correcta(self, placa, esperado):
        from src.utils.validaciones import ValidadorPicoPlaca
        from src.config.settings import TipoCirculacion

        result = ValidadorPicoPlaca.obtener_tipo_circulacion(placa)
        assert result.value == esperado

    def test_compatibilidad_par_impar(self):
        from src.utils.validaciones import ValidadorPicoPlaca

        # IMPAR (1) + PAR (6) = Compatible
        assert ValidadorPicoPlaca.son_placas_compatibles("ABC121", "ABC126") is True

        # IMPAR (2) + IMPAR (3) = Incompatible
        assert ValidadorPicoPlaca.son_placas_compatibles("ABC122", "ABC123") is False

        # PAR (7) + PAR (8) = Incompatible
        assert ValidadorPicoPlaca.son_placas_compatibles("ABC127", "ABC128") is False
