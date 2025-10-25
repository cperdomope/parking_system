# -*- coding: utf-8 -*-
"""
Validaciones para asignación de parqueaderos según reglas de negocio
"""

from typing import Dict, Optional, Tuple


class ValidadorAsignacion:
    """Validador para reglas de asignación de parqueaderos"""

    @staticmethod
    def validar_permite_compartir(funcionario_data: Dict, asignaciones_existentes: int) -> Tuple[bool, str]:
        """
        Valida si un funcionario puede compartir parqueadero

        Args:
            funcionario_data: Datos del funcionario (debe incluir 'permite_compartir', 'pico_placa_solidario',
                             'discapacidad', 'nombre', 'apellidos', 'cargo')
            asignaciones_existentes: Número de asignaciones activas en el parqueadero

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Verificar si tiene Pico y Placa Solidario activo
        if funcionario_data.get("pico_placa_solidario", False) and asignaciones_existentes > 0:
            return False, (
                f"🚫 Asignación bloqueada por Pico y Placa Solidario\n\n"
                f"👤 {funcionario_data.get('nombre', 'N/A')} {funcionario_data.get('apellidos', 'N/A')}\n"
                f"💼 Cargo: {funcionario_data.get('cargo', 'N/A')}\n"
                f"🔄 Este funcionario tiene Pico y Placa Solidario activo\n"
                f"⚠️ El parqueadero será exclusivo y se marcará como COMPLETO\n\n"
                f"💡 Seleccione un parqueadero completamente disponible"
            )

        # Verificar si tiene Discapacidad
        if funcionario_data.get("discapacidad", False) and asignaciones_existentes > 0:
            return False, (
                f"🚫 Asignación bloqueada por condición de discapacidad\n\n"
                f"👤 {funcionario_data.get('nombre', 'N/A')} {funcionario_data.get('apellidos', 'N/A')}\n"
                f"💼 Cargo: {funcionario_data.get('cargo', 'N/A')}\n"
                f"♿ Este funcionario tiene condición de discapacidad\n"
                f"⚠️ El parqueadero será exclusivo y se marcará como COMPLETO\n\n"
                f"💡 Seleccione un parqueadero completamente disponible"
            )

        return True, ""

    @staticmethod
    def validar_ocupante_permite_compartir(ocupante_data: Optional[Dict]) -> Tuple[bool, str]:
        """
        Valida si el ocupante actual del parqueadero permite compartir

        Args:
            ocupante_data: Datos del ocupante actual (puede ser None si está vacío)

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if ocupante_data:
            # Verificar si tiene Pico y Placa Solidario
            if ocupante_data.get("pico_placa_solidario", False):
                return False, (
                    f"🚫 Parqueadero ocupado por funcionario con Pico y Placa Solidario\n\n"
                    f"👤 Ocupante: {ocupante_data.get('nombre', 'N/A')} {ocupante_data.get('apellidos', 'N/A')}\n"
                    f"💼 Cargo: {ocupante_data.get('cargo', 'N/A')}\n"
                    f"🔄 Este funcionario tiene Pico y Placa Solidario activo\n"
                    f"⚠️ El parqueadero es exclusivo\n\n"
                    f"💡 Seleccione otro parqueadero disponible"
                )

            # Verificar si tiene Discapacidad
            if ocupante_data.get("discapacidad", False):
                return False, (
                    f"🚫 Parqueadero ocupado por funcionario con discapacidad\n\n"
                    f"👤 Ocupante: {ocupante_data.get('nombre', 'N/A')} {ocupante_data.get('apellidos', 'N/A')}\n"
                    f"💼 Cargo: {ocupante_data.get('cargo', 'N/A')}\n"
                    f"♿ Este funcionario tiene condición de discapacidad\n"
                    f"⚠️ El parqueadero es exclusivo\n\n"
                    f"💡 Seleccione otro parqueadero disponible"
                )

        return True, ""

    @staticmethod
    def validar_compatibilidad_cargos(cargo_nuevo: str, cargo_existente: Optional[str]) -> Tuple[bool, str]:
        """
        Valida si dos cargos pueden compartir parqueadero

        Reglas:
        - Director: NO comparte con nadie (exclusivo)
        - Coordinador: Solo con Asesores
        - Asesor: Entre ellos y con Coordinadores

        Args:
            cargo_nuevo: Cargo del funcionario que intenta asignar
            cargo_existente: Cargo del funcionario ya asignado (None si está vacío)

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not cargo_existente:
            return True, ""

        # Director NO comparte con nadie
        if cargo_nuevo == "Director" or cargo_existente == "Director":
            return False, (
                "🚫 Restricción de jerarquía - Director\n\n"
                "⚠️ Los Directores tienen parqueaderos exclusivos\n"
                "💡 Seleccione un parqueadero disponible"
            )

        # Coordinador solo con Asesor
        if cargo_nuevo == "Coordinador" and cargo_existente != "Asesor":
            return False, (
                f"🚫 Restricción de jerarquía - Coordinador\n\n"
                f"⚠️ Coordinadores solo pueden compartir con Asesores\n"
                f"👤 El parqueadero está ocupado por: {cargo_existente}\n"
                f"💡 Seleccione otro parqueadero"
            )

        if cargo_existente == "Coordinador" and cargo_nuevo != "Asesor":
            return False, (
                "🚫 Restricción de jerarquía\n\n"
                "⚠️ Este parqueadero tiene un Coordinador\n"
                "👤 Solo Asesores pueden compartir con Coordinadores\n"
                "💡 Seleccione otro parqueadero"
            )

        return True, ""

    @staticmethod
    def validar_pico_placa(
        vehiculo_tipo: str, tipo_circulacion: str, tiene_pico_placa_solidario: bool, mismo_tipo_count: int,
        tiene_parqueadero_exclusivo: bool = False, cargo: str = ""
    ) -> Tuple[bool, str]:
        """
        Valida las reglas de pico y placa

        Args:
            vehiculo_tipo: Tipo de vehículo ('Carro', 'Moto', 'Bicicleta')
            tipo_circulacion: 'PAR', 'IMPAR', 'N/A'
            tiene_pico_placa_solidario: Si el funcionario tiene pico placa solidario
            mismo_tipo_count: Cantidad de vehículos del mismo tipo circulación ya asignados
            tiene_parqueadero_exclusivo: Si es directivo con parqueadero exclusivo
            cargo: Cargo del funcionario

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Solo aplica para carros con tipo de circulación definido
        if vehiculo_tipo != "Carro" or tipo_circulacion == "N/A":
            return True, ""

        # Si tiene pico_placa_solidario, permitir
        if tiene_pico_placa_solidario:
            return True, ""

        # Si es directivo con parqueadero exclusivo, ignorar restricción PAR/IMPAR
        from ..config.settings import CARGOS_DIRECTIVOS
        if tiene_parqueadero_exclusivo and cargo in CARGOS_DIRECTIVOS:
            return True, ""

        # Si hay vehículos del mismo tipo, denegar
        if mismo_tipo_count > 0:
            return False, (
                f"🚫 Conflicto de pico y placa\n\n"
                f"❌ Ya existe un vehículo {tipo_circulacion} asignado\n\n"
                f"💡 Soluciones:\n"
                f"   • Active 'Pico y placa solidario' para este funcionario\n"
                f"   • Seleccione un parqueadero con complemento {tipo_circulacion}"
            )

        return True, ""

    @staticmethod
    def puede_acceder_parqueadero_exclusivo_discapacidad(
        tiene_discapacidad: bool, parqueadero_exclusivo: bool
    ) -> Tuple[bool, str]:
        """
        Valida si un funcionario puede acceder a un parqueadero exclusivo para discapacidad

        Args:
            tiene_discapacidad: Si el funcionario tiene discapacidad
            parqueadero_exclusivo: Si el parqueadero es exclusivo para discapacidad

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if parqueadero_exclusivo and not tiene_discapacidad:
            return False, (
                "♿ Parqueadero reservado para personas con discapacidad\n\n"
                "⚠️ Este espacio está reservado exclusivamente\n"
                "💡 Seleccione otro parqueadero disponible"
            )

        return True, ""

    @staticmethod
    def obtener_mensajes_informativos(funcionario_data: Dict) -> list:
        """
        Genera mensajes informativos sobre características especiales del funcionario

        Args:
            funcionario_data: Datos del funcionario

        Returns:
            list: Lista de mensajes informativos
        """
        mensajes = []

        if funcionario_data.get("pico_placa_solidario"):
            mensajes.append("🔄 Pico y placa solidario activo - Sin restricción PAR/IMPAR")

        if funcionario_data.get("discapacidad"):
            mensajes.append("♿ Funcionario con discapacidad - Prioridad especial")

        if funcionario_data.get("cargo") in ["Director", "Coordinador"]:
            mensajes.append(f"💼 {funcionario_data['cargo']} - Restricciones de jerarquía aplicadas")

        return mensajes

    @staticmethod
    def obtener_indicadores_visuales(funcionario_data: Dict) -> str:
        """
        Genera una cadena con indicadores visuales para mostrar en UI

        Args:
            funcionario_data: Datos del funcionario

        Returns:
            str: Cadena con indicadores tipo '[🚫EXCLUSIVO] [🔄SOL]'
        """
        indicadores = []

        if funcionario_data.get("pico_placa_solidario"):
            indicadores.append("🔄SOL")

        if funcionario_data.get("discapacidad"):
            indicadores.append("♿DISC")

        return " ".join(f"[{ind}]" for ind in indicadores) if indicadores else ""

    @staticmethod
    def obtener_indicadores_badges(funcionario_data: Dict) -> str:
        """
        Genera emojis badges para agregar al nombre del funcionario

        Args:
            funcionario_data: Datos del funcionario

        Returns:
            str: Cadena con badges tipo '🚫 🔄 ♿'
        """
        badges = []

        if funcionario_data.get("pico_placa_solidario"):
            badges.append("🔄")

        if funcionario_data.get("discapacidad"):
            badges.append("♿")

        return " ".join(badges) if badges else ""

