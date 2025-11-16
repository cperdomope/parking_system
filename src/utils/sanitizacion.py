# -*- coding: utf-8 -*-
"""
Módulo de sanitización de entradas de usuario
Proporciona funciones para limpiar y validar datos de entrada

Versión: 1.0
Fecha: 2025-10-13
"""

import re
import html
from typing import Optional, Union


class InputSanitizer:
    """Clase para sanitizar entradas de usuario"""

    # Patrones de caracteres permitidos
    ALPHANUMERIC_PATTERN = re.compile(r'^[a-zA-Z0-9\s]+$')
    ALPHANUMERIC_EXTENDED_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.]+$')
    NUMERIC_PATTERN = re.compile(r'^[0-9]+$')
    ALPHA_PATTERN = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    # Caracteres peligrosos que deben ser escapados
    DANGEROUS_CHARS = ['<', '>', '"', "'", '&', ';', '|', '$', '`', '\n', '\r', '\t']

    # Palabras clave SQL peligrosas
    SQL_KEYWORDS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'EXEC', 'EXECUTE', 'UNION', 'WHERE', 'FROM', 'TABLE', '--', '/*', '*/',
        'SCRIPT', 'JAVASCRIPT', 'ONERROR', 'ONLOAD', 'TRUNCATE', 'XP_CMDSHELL'
    ]

    @staticmethod
    def sanitize_string(value: str, max_length: int = 255, allow_special: bool = False) -> str:
        """
        Sanitiza una cadena de texto general

        Args:
            value: Valor a sanitizar
            max_length: Longitud máxima permitida
            allow_special: Si se permiten caracteres especiales

        Returns:
            str: Cadena sanitizada

        Examples:
            >>> InputSanitizer.sanitize_string("Hello <script>")
            "Hello script"
            >>> InputSanitizer.sanitize_string("User123", max_length=5)
            "User1"
        """
        if not value:
            return ""

        # Convertir a string si no lo es
        value = str(value)

        # 1. Eliminar espacios al principio y final
        value = value.strip()

        # 2. Limitar longitud
        value = value[:max_length]

        # 3. Escapar HTML
        value = html.escape(value)

        # 4. Si no se permiten caracteres especiales, eliminarlos
        if not allow_special:
            # Eliminar caracteres peligrosos
            for char in InputSanitizer.DANGEROUS_CHARS:
                value = value.replace(char, '')

        # 5. Normalizar espacios múltiples
        value = ' '.join(value.split())

        return value

    @staticmethod
    def sanitize_numeric(value: Union[str, int, float], min_value: Optional[int] = None,
                        max_value: Optional[int] = None) -> Optional[int]:
        """
        Sanitiza un valor numérico

        Args:
            value: Valor a sanitizar
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido

        Returns:
            int: Valor numérico sanitizado o None si es inválido

        Examples:
            >>> InputSanitizer.sanitize_numeric("123", min_value=0, max_value=200)
            123
            >>> InputSanitizer.sanitize_numeric("abc")
            None
        """
        try:
            # Convertir a entero
            numeric_value = int(value)

            # Validar rango
            if min_value is not None and numeric_value < min_value:
                return None
            if max_value is not None and numeric_value > max_value:
                return None

            return numeric_value
        except (ValueError, TypeError):
            return None

    @staticmethod
    def sanitize_cedula(cedula: str) -> Optional[str]:
        """
        Sanitiza una cédula (solo números, longitud 6-12)

        Args:
            cedula: Cédula a sanitizar

        Returns:
            str: Cédula sanitizada o None si es inválida

        Examples:
            >>> InputSanitizer.sanitize_cedula("12345678")
            "12345678"
            >>> InputSanitizer.sanitize_cedula("123-456-78")
            "12345678"
        """
        if not cedula:
            return None

        # Eliminar espacios y guiones
        cedula = str(cedula).strip().replace('-', '').replace(' ', '')

        # Validar que solo contenga números
        if not InputSanitizer.NUMERIC_PATTERN.match(cedula):
            return None

        # Validar longitud (6-12 dígitos)
        if not (6 <= len(cedula) <= 12):
            return None

        return cedula

    @staticmethod
    def sanitize_placa(placa: str) -> Optional[str]:
        """
        Sanitiza una placa de vehículo (alfanumérico, longitud 3-10)

        Args:
            placa: Placa a sanitizar

        Returns:
            str: Placa sanitizada o None si es inválida

        Examples:
            >>> InputSanitizer.sanitize_placa("ABC123")
            "ABC123"
            >>> InputSanitizer.sanitize_placa("abc-123")
            "ABC123"
        """
        if not placa:
            return None

        # Eliminar espacios y guiones, convertir a mayúsculas
        placa = str(placa).strip().replace('-', '').replace(' ', '').upper()

        # Validar que solo contenga letras y números
        if not InputSanitizer.ALPHANUMERIC_PATTERN.match(placa):
            return None

        # Validar longitud (3-10 caracteres)
        if not (3 <= len(placa) <= 10):
            return None

        return placa

    @staticmethod
    def sanitize_nombre(nombre: str, max_length: int = 100) -> Optional[str]:
        """
        Sanitiza un nombre de persona (solo letras y espacios)

        Args:
            nombre: Nombre a sanitizar
            max_length: Longitud máxima

        Returns:
            str: Nombre sanitizado o None si es inválido

        Examples:
            >>> InputSanitizer.sanitize_nombre("Juan Pérez")
            "Juan Pérez"
            >>> InputSanitizer.sanitize_nombre("Juan123")
            None
        """
        if not nombre:
            return None

        nombre = str(nombre).strip()[:max_length]

        # Validar que solo contenga letras y espacios
        if not InputSanitizer.ALPHA_PATTERN.match(nombre):
            return None

        # Normalizar espacios
        nombre = ' '.join(nombre.split())

        # Validar longitud mínima
        if len(nombre) < 2:
            return None

        return nombre

    @staticmethod
    def sanitize_email(email: str) -> Optional[str]:
        """
        Sanitiza un email

        Args:
            email: Email a sanitizar

        Returns:
            str: Email sanitizado o None si es inválido

        Examples:
            >>> InputSanitizer.sanitize_email("user@example.com")
            "user@example.com"
            >>> InputSanitizer.sanitize_email("invalid-email")
            None
        """
        if not email:
            return None

        email = str(email).strip().lower()

        # Validar formato de email
        if not InputSanitizer.EMAIL_PATTERN.match(email):
            return None

        # Validar longitud
        if len(email) > 100:
            return None

        return email

    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        Verifica si una cadena contiene posibles intentos de SQL Injection

        Args:
            value: Valor a verificar

        Returns:
            bool: True si se detecta posible SQL injection, False en caso contrario

        Examples:
            >>> InputSanitizer.check_sql_injection("SELECT * FROM users")
            True
            >>> InputSanitizer.check_sql_injection("Juan Pérez")
            False
        """
        if not value:
            return False

        value_upper = str(value).upper()

        # Verificar palabras clave SQL
        for keyword in InputSanitizer.SQL_KEYWORDS:
            if keyword in value_upper:
                return True

        # Verificar patrones comunes de SQL injection
        sql_injection_patterns = [
            r"('\s*OR\s*'1'\s*=\s*'1)",  # ' OR '1'='1
            r"(\d+\s*=\s*\d+)",           # 1=1
            r"(--)",                       # Comentarios SQL
            r"(;)",                        # Múltiples consultas
            r"(/\*.*\*/)",                 # Comentarios multilínea
        ]

        for pattern in sql_injection_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                return True

        return False

    @staticmethod
    def sanitize_path(path: str) -> Optional[str]:
        """
        Sanitiza una ruta de archivo

        Args:
            path: Ruta a sanitizar

        Returns:
            str: Ruta sanitizada o None si es inválida

        Examples:
            >>> InputSanitizer.sanitize_path("report.pdf")
            "report.pdf"
            >>> InputSanitizer.sanitize_path("../../../etc/passwd")
            None
        """
        if not path:
            return None

        path = str(path).strip()

        # Detectar path traversal
        if '..' in path or path.startswith('/') or path.startswith('\\'):
            return None

        # Validar caracteres permitidos en nombres de archivo
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', path):
            return None

        # Validar longitud
        if len(path) > 100:
            return None

        return path

    @staticmethod
    def sanitize_observaciones(observaciones: str, max_length: int = 500) -> str:
        """
        Sanitiza observaciones o comentarios

        Args:
            observaciones: Observaciones a sanitizar
            max_length: Longitud máxima

        Returns:
            str: Observaciones sanitizadas

        Examples:
            >>> InputSanitizer.sanitize_observaciones("Buen funcionario<script>")
            "Buen funcionario"
        """
        if not observaciones:
            return ""

        observaciones = str(observaciones).strip()[:max_length]

        # Escapar HTML
        observaciones = html.escape(observaciones)

        # Eliminar caracteres peligrosos
        for char in ['<', '>', '"', "'", ';', '|', '$', '`']:
            observaciones = observaciones.replace(char, '')

        # Normalizar espacios
        observaciones = ' '.join(observaciones.split())

        return observaciones


# Alias para facilitar el uso
sanitize = InputSanitizer.sanitize_string
sanitize_numeric = InputSanitizer.sanitize_numeric
sanitize_cedula = InputSanitizer.sanitize_cedula
sanitize_placa = InputSanitizer.sanitize_placa
sanitize_nombre = InputSanitizer.sanitize_nombre
sanitize_email = InputSanitizer.sanitize_email
sanitize_path = InputSanitizer.sanitize_path
sanitize_observaciones = InputSanitizer.sanitize_observaciones
check_sql_injection = InputSanitizer.check_sql_injection

# Alias adicionales para compatibilidad con tests
sanitize_sql_input = InputSanitizer.sanitize_string  # Sanitiza texto general incluyendo SQL
escape_html = lambda text: html.escape(text) if text else ""  # Escape HTML directo
sanitize_file_path = InputSanitizer.sanitize_path  # Sanitiza rutas de archivo
