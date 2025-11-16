# -*- coding: utf-8 -*-
"""Tests Unitarios: Sanitización"""

import pytest


class TestSanitizacionSQL:
    """Tests de sanitización contra SQL injection"""

    def test_sanitize_sql_input(self, payloads_sql_injection):
        from src.utils.sanitizacion import sanitize_sql_input

        for payload in payloads_sql_injection:
            result = sanitize_sql_input(payload)
            assert result != payload or result is None

    def test_check_sql_injection_detecta_peligros(self):
        from src.utils.sanitizacion import check_sql_injection

        dangerous = [
            "SELECT * FROM usuarios",
            "DROP TABLE funcionarios",
            "'; DELETE FROM --"
        ]

        for payload in dangerous:
            assert check_sql_injection(payload) is True


class TestSanitizacionHTML:
    """Tests de escape HTML"""

    def test_escape_html(self, payloads_xss):
        from src.utils.sanitizacion import escape_html

        for payload in payloads_xss:
            result = escape_html(payload)
            assert '<script' not in result.lower()
            assert '<img' not in result.lower()


class TestSanitizacionArchivos:
    """Tests de sanitización de paths"""

    def test_sanitize_file_path(self, payloads_path_traversal):
        from src.utils.sanitizacion import sanitize_file_path

        for payload in payloads_path_traversal:
            result = sanitize_file_path(payload)
            assert result is None or '..' not in result


class TestSanitizacionCampos:
    """Tests de sanitización de campos específicos"""

    def test_sanitize_cedula(self):
        from src.utils.sanitizacion import sanitize_cedula

        assert sanitize_cedula("12345678") == "12345678"
        assert sanitize_cedula("ABC123") is None
        assert sanitize_cedula("1234'; DROP--") is None

    def test_sanitize_nombre(self):
        from src.utils.sanitizacion import sanitize_nombre

        assert sanitize_nombre("Juan Carlos") == "Juan Carlos"
        assert sanitize_nombre("Juan<script>") != "Juan<script>"
        assert sanitize_nombre("Test123") is None
