# -*- coding: utf-8 -*-
"""
Input Validators
Centralized QRegExpValidator instances to avoid duplication
"""

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator


class InputValidators:
    """Reusable input validators for common field types"""

    # Cedula: 7-10 digits
    CEDULA = QRegExpValidator(QRegExp("^[0-9]{7,10}$"))

    # Nombre/Apellidos: Only letters, accents, and spaces
    NOMBRE = QRegExpValidator(QRegExp("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$"))
    APELLIDOS = QRegExpValidator(QRegExp("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$"))

    # Celular: Exactly 10 digits
    CELULAR = QRegExpValidator(QRegExp("^[0-9]{10}$"))

    # Telefono: 7-10 digits
    TELEFONO = QRegExpValidator(QRegExp("^[0-9]{7,10}$"))

    # Tarjeta CLARO: Alphanumeric, 1-15 characters
    TARJETA_CLARO = QRegExpValidator(QRegExp("^[a-zA-Z0-9]{1,15}$"))

    # Placa: 6 alphanumeric characters (ABC123 or ABC12D)
    PLACA = QRegExpValidator(QRegExp("^[A-Z0-9]{6}$"))

    # Email: Basic email validation
    EMAIL = QRegExpValidator(QRegExp("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"))

    # Numero parqueadero: P-XXX format
    NUMERO_PARQUEADERO = QRegExpValidator(QRegExp("^P-[0-9]{3}$"))

    # Solo numeros
    SOLO_NUMEROS = QRegExpValidator(QRegExp("^[0-9]+$"))

    # Solo letras
    SOLO_LETRAS = QRegExpValidator(QRegExp("^[a-zA-ZáéíóúÁÉÍÓÚñÑ]+$"))

    # Alfanumerico
    ALFANUMERICO = QRegExpValidator(QRegExp("^[a-zA-Z0-9]+$"))
