# -*- coding: utf-8 -*-
"""
Módulo central de validaciones para el sistema de gestión de parqueadero.
Centraliza validaciones comunes para evitar duplicación de código.
"""

import re
from typing import Tuple
from ..config.settings import TipoCirculacion


class ValidadorCampos:
    """Validador central para campos comunes del sistema"""

    # Expresiones regulares para validaciones
    REGEX_CEDULA = r'^[0-9]{7,10}$'
    REGEX_CELULAR = r'^[0-9]{10}$'
    REGEX_TARJETA = r'^[a-zA-Z0-9]{1,15}$'
    REGEX_NOMBRE = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$'
    REGEX_PLACA = r'^[A-Z0-9]{5,7}$'

    @staticmethod
    def validar_cedula(cedula: str) -> Tuple[bool, str]:
        """
        Valida formato de cédula colombiana

        Args:
            cedula: Cédula a validar

        Returns:
            Tuple[bool, str]: (es_válida, mensaje_error)
        """
        if not cedula or not cedula.strip():
            return False, "🚫 La cédula es obligatoria"

        cedula_clean = cedula.strip()

        if not cedula_clean.isdigit():
            return False, (
                f"🚫 Formato de cédula inválido\n\n"
                f"❌ La cédula debe contener solo números\n"
                f"📋 Cédula ingresada: '{cedula}'\n"
                f"💡 Ejemplo válido: 1234567890"
            )

        if len(cedula_clean) < 7 or len(cedula_clean) > 10:
            return False, (
                f"🚫 Longitud de cédula inválida\n\n"
                f"❌ Cédula ingresada: '{cedula}' ({len(cedula_clean)} dígitos)\n"
                f"📋 Longitud válida: Entre 7 y 10 dígitos\n"
                f"💡 Ejemplo: 1234567, 12345678 o 1234567890"
            )

        return True, ""

    @staticmethod
    def validar_celular(celular: str, requerido: bool = False) -> Tuple[bool, str]:
        """
        Valida formato de celular colombiano

        Args:
            celular: Número de celular a validar
            requerido: Si el campo es obligatorio

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not celular or not celular.strip():
            if requerido:
                return False, "🚫 El número de celular es obligatorio"
            return True, ""

        celular_clean = celular.strip()

        if not re.match(ValidadorCampos.REGEX_CELULAR, celular_clean):
            return False, (
                f"🚫 Formato de celular inválido\n\n"
                f"❌ Celular ingresado: '{celular}'\n"
                f"📋 Formato válido: Exactamente 10 dígitos numéricos\n"
                f"💡 Ejemplo: 3001234567"
            )

        return True, ""

    @staticmethod
    def validar_placa(placa: str, requerido: bool = True) -> Tuple[bool, str]:
        """
        Valida formato de placa vehicular

        Args:
            placa: Placa a validar
            requerido: Si el campo es obligatorio

        Returns:
            Tuple[bool, str]: (es_válida, mensaje_error)
        """
        if not placa or not placa.strip():
            if requerido:
                return False, (
                    "🚫 La placa es obligatoria\n\n"
                    "📝 Por favor ingrese una placa válida\n"
                    "💡 Ejemplo: ABC123, XYZ789"
                )
            return True, ""

        placa_clean = placa.strip().upper()

        if not re.match(ValidadorCampos.REGEX_PLACA, placa_clean):
            return False, (
                f"🚫 Formato de placa inválido\n\n"
                f"❌ Placa ingresada: '{placa}'\n"
                f"📋 Formato válido: 5-7 caracteres alfanuméricos\n"
                f"💡 Ejemplos: ABC123, XYZ789, MNO12"
            )

        return True, ""

    @staticmethod
    def validar_nombre(nombre: str, campo: str = "Nombre") -> Tuple[bool, str]:
        """
        Valida formato de nombre o apellido

        Args:
            nombre: Nombre a validar
            campo: Nombre del campo para mensajes personalizados

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not nombre or not nombre.strip():
            return False, f"🚫 {campo} es obligatorio"

        nombre_clean = nombre.strip()

        if not re.match(ValidadorCampos.REGEX_NOMBRE, nombre_clean):
            return False, (
                f"🚫 Formato de {campo.lower()} inválido\n\n"
                f"❌ Solo se permiten letras, espacios y tildes\n"
                f"💡 Ejemplo: Juan Carlos, María José"
            )

        return True, ""

    @staticmethod
    def validar_tarjeta_proximidad(tarjeta: str, requerido: bool = False) -> Tuple[bool, str]:
        """
        Valida formato de tarjeta de proximidad

        Args:
            tarjeta: Número de tarjeta a validar
            requerido: Si el campo es obligatorio

        Returns:
            Tuple[bool, str]: (es_válida, mensaje_error)
        """
        if not tarjeta or not tarjeta.strip():
            if requerido:
                return False, "🚫 El número de tarjeta es obligatorio"
            return True, ""

        tarjeta_clean = tarjeta.strip()

        if not re.match(ValidadorCampos.REGEX_TARJETA, tarjeta_clean):
            return False, (
                f"🚫 Formato de tarjeta inválido\n\n"
                f"❌ Tarjeta ingresada: '{tarjeta}'\n"
                f"📋 Formato válido: Alfanumérico, máximo 15 caracteres\n"
                f"💡 Ejemplo: ABC123XYZ, 12345"
            )

        return True, ""


class ValidadorPicoPlaca:
    """Validador para lógica de pico y placa"""

    @staticmethod
    def obtener_tipo_circulacion(placa: str) -> TipoCirculacion:
        """
        Determina el tipo de circulación (PAR/IMPAR) según el último dígito de la placa

        Reglas:
        - Dígitos 1-5: IMPAR
        - Dígitos 6-9, 0: PAR
        - Sin dígito final: N/A

        Args:
            placa: Placa del vehículo

        Returns:
            TipoCirculacion: PAR, IMPAR o N/A
        """
        if not placa or not placa.strip():
            return TipoCirculacion.NA

        ultimo_caracter = placa.strip()[-1]

        if not ultimo_caracter.isdigit():
            return TipoCirculacion.NA

        digito = int(ultimo_caracter)

        if digito in [1, 2, 3, 4, 5]:
            return TipoCirculacion.IMPAR
        else:  # 6, 7, 8, 9, 0
            return TipoCirculacion.PAR

    @staticmethod
    def obtener_ultimo_digito(placa: str) -> str:
        """
        Obtiene el último dígito de una placa

        Args:
            placa: Placa del vehículo

        Returns:
            str: Último dígito o cadena vacía si no tiene
        """
        if not placa or not placa.strip():
            return ""

        ultimo_caracter = placa.strip()[-1]

        if ultimo_caracter.isdigit():
            return ultimo_caracter

        return ""

    @staticmethod
    def son_placas_compatibles(placa1: str, placa2: str) -> bool:
        """
        Verifica si dos placas son compatibles para compartir parqueadero
        (deben tener diferentes tipos de circulación: PAR/IMPAR)

        Args:
            placa1: Primera placa
            placa2: Segunda placa

        Returns:
            bool: True si son compatibles (PAR/IMPAR diferentes)
        """
        tipo1 = ValidadorPicoPlaca.obtener_tipo_circulacion(placa1)
        tipo2 = ValidadorPicoPlaca.obtener_tipo_circulacion(placa2)

        # Si alguna es N/A, no son compatibles
        if tipo1 == TipoCirculacion.NA or tipo2 == TipoCirculacion.NA:
            return False

        # Deben ser diferentes
        return tipo1 != tipo2


class ValidadorReglasNegocio:
    """Validador para reglas de negocio específicas del sistema"""

    @staticmethod
    def validar_campos_requeridos(**campos) -> Tuple[bool, str]:
        """
        Valida que campos requeridos no estén vacíos

        Args:
            **campos: Diccionario de nombre_campo: valor

        Returns:
            Tuple[bool, str]: (son_válidos, mensaje_error)

        Example:
            validar_campos_requeridos(Nombre="Juan", Apellidos="", Cedula="123")
            # Returns: (False, "🚫 Campos obligatorios faltantes\n\n❌ Apellidos")
        """
        campos_vacios = []

        for nombre_campo, valor in campos.items():
            if not valor or not str(valor).strip():
                campos_vacios.append(nombre_campo)

        if campos_vacios:
            lista_campos = "\n❌ ".join(campos_vacios)
            return False, (
                f"🚫 Campos obligatorios faltantes\n\n"
                f"❌ {lista_campos}\n\n"
                f"💡 Por favor complete todos los campos requeridos"
            )

        return True, ""

    @staticmethod
    def validar_cargo_permite_compartir(cargo: str, permite_compartir: bool) -> bool:
        """
        Valida lógica de negocio: Directores no deberían compartir por defecto

        Args:
            cargo: Cargo del funcionario
            permite_compartir: Valor actual de permite_compartir

        Returns:
            bool: Valor ajustado de permite_compartir según cargo
        """
        if cargo == "Director":
            return False
        return permite_compartir


# Exportar clases principales
__all__ = [
    'ValidadorCampos',
    'ValidadorPicoPlaca',
    'ValidadorReglasNegocio'
]
