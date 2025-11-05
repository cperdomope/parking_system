# -*- coding: utf-8 -*-
"""
Módulo de validaciones para el registro de vehículos de funcionarios
Implementa las reglas de negocio para cantidad máxima y combinaciones permitidas
"""

from typing import Dict, List, Tuple

from ..config.settings import TipoCirculacion, TipoVehiculo
from .validaciones import ValidadorCampos, ValidadorPicoPlaca


class ValidadorVehiculos:
    """Clase para validar el registro de vehículos según reglas de negocio

    IMPORTANTE: Solo los carros ocupan espacios de parqueadero.
    Motos y bicicletas no afectan los estados de parqueaderos.

    REGLA ESPECIAL: Directivos (Director, Coordinador, Asesor) con parqueadero exclusivo
    pueden registrar hasta 6 vehículos total:
    - Hasta 4 carros (sin restricción PAR/IMPAR)
    - Hasta 1 moto
    - Hasta 1 bicicleta
    """

    # Cantidad máxima de vehículos por funcionario
    MAX_VEHICULOS_POR_FUNCIONARIO = 3  # Máximo 3 vehículos en total (combinaciones específicas)
    MAX_VEHICULOS_DIRECTIVO_EXCLUSIVO = 6  # 4 carros + 1 moto + 1 bicicleta
    MAX_CARROS_DIRECTIVO_EXCLUSIVO = 4
    MAX_CARROS_REGULAR = 2  # Máximo 2 carros para regulares
    MAX_MOTOS_DIRECTIVO_EXCLUSIVO = 1
    MAX_BICICLETAS_DIRECTIVO_EXCLUSIVO = 1

    def __init__(self, db_manager=None):
        self.db = db_manager

    def obtener_tipo_placa(self, placa: str) -> TipoCirculacion:
        """
        Determina el tipo de placa (PAR/IMPAR) según el último dígito
        Usa validador centralizado.

        Args:
            placa (str): Placa del vehículo

        Returns:
            TipoCirculacion: PAR, IMPAR o N/A
        """
        return ValidadorPicoPlaca.obtener_tipo_circulacion(placa)

    def contar_vehiculos_por_tipo(self, vehiculos: List[Dict]) -> Dict[str, int]:
        """
        Cuenta la cantidad de vehículos por tipo

        Args:
            vehiculos (List[Dict]): Lista de vehículos actuales del funcionario

        Returns:
            Dict[str, int]: Diccionario con el conteo por tipo
        """
        conteo = {TipoVehiculo.CARRO.value: 0, TipoVehiculo.MOTO.value: 0, TipoVehiculo.BICICLETA.value: 0}

        for vehiculo in vehiculos:
            tipo = vehiculo.get("tipo_vehiculo", "")
            if tipo in conteo:
                conteo[tipo] += 1

        return conteo

    def validar_cantidad_maxima(self, vehiculos_actuales: List[Dict], nuevo_tipo: str, funcionario_id: int = None) -> Tuple[bool, str]:
        """
        Valida que no se exceda la cantidad máxima de vehículos

        Args:
            vehiculos_actuales (List[Dict]): Vehículos actuales del funcionario
            nuevo_tipo (str): Tipo del nuevo vehículo a registrar
            funcionario_id (int): ID del funcionario para verificar si es directivo con exclusivo

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        total_actual = len(vehiculos_actuales)

        # Verificar si es directivo con parqueadero exclusivo
        max_vehiculos = self.MAX_VEHICULOS_POR_FUNCIONARIO
        if funcionario_id and self.db:
            query = """
                SELECT tiene_parqueadero_exclusivo
                FROM funcionarios
                WHERE id = %s AND activo = TRUE
            """
            funcionario_data = self.db.fetch_one(query, (funcionario_id,))
            if funcionario_data:
                tiene_exclusivo = funcionario_data.get("tiene_parqueadero_exclusivo", False)

                # Si tiene parqueadero exclusivo, permite hasta 4 vehículos (sin restricción de cargo)
                if tiene_exclusivo:
                    max_vehiculos = self.MAX_VEHICULOS_DIRECTIVO_EXCLUSIVO

        if total_actual >= max_vehiculos:
            return (
                False,
                f"💔 No se puede registrar más vehículos.\n\n"
                f"📊 Estado actual: {total_actual} de {max_vehiculos} vehículos permitidos.\n"
                f"💡 Para agregar un nuevo vehículo, primero debe eliminar uno existente.",
            )

        return True, ""

    def validar_pico_y_placa_carros(self, vehiculos_actuales: List[Dict], nueva_placa: str, funcionario_id: int = None) -> Tuple[bool, str]:
        """
        Valida la regla de pico y placa para carros
        Si ya tiene un carro, el nuevo debe tener placa diferente (par/impar)

        EXCEPCIÓN: Directivos con parqueadero exclusivo NO tienen restricción PAR/IMPAR

        Args:
            vehiculos_actuales (List[Dict]): Vehículos actuales del funcionario
            nueva_placa (str): Placa del nuevo carro
            funcionario_id (int): ID del funcionario para verificar si es directivo con exclusivo

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Validar formato de placa usando validador centralizado
        es_valida, mensaje = ValidadorCampos.validar_placa(nueva_placa, requerido=True)
        if not es_valida:
            return False, mensaje

        # Verificar si tiene parqueadero exclusivo (exento de restricción PAR/IMPAR)
        if funcionario_id and self.db:
            query = """
                SELECT tiene_parqueadero_exclusivo
                FROM funcionarios
                WHERE id = %s AND activo = TRUE
            """
            funcionario_data = self.db.fetch_one(query, (funcionario_id,))
            if funcionario_data:
                tiene_exclusivo = funcionario_data.get("tiene_parqueadero_exclusivo", False)

                # Si tiene parqueadero exclusivo: NO validar PAR/IMPAR (sin restricción de cargo)
                if tiene_exclusivo:
                    return True, ""

        carros_actuales = [v for v in vehiculos_actuales if v.get("tipo_vehiculo") == TipoVehiculo.CARRO.value]

        if len(carros_actuales) == 0:
            # Si no tiene carros, puede registrar cualquiera
            return True, ""

        if len(carros_actuales) >= 1:
            # Ya tiene un carro, verificar pico y placa
            carro_existente = carros_actuales[0]
            placa_existente = carro_existente.get("placa", "")

            tipo_placa_existente = self.obtener_tipo_placa(placa_existente)
            tipo_placa_nueva = self.obtener_tipo_placa(nueva_placa)

            if tipo_placa_existente == tipo_placa_nueva and tipo_placa_nueva != TipoCirculacion.NA:
                tipo_requerido = "PAR" if tipo_placa_existente == TipoCirculacion.IMPAR else "IMPAR"
                digitos_requeridos = "6, 7, 8, 9, 0" if tipo_requerido == "PAR" else "1, 2, 3, 4, 5"

                return (
                    False,
                    f"🚗 Conflicto de pico y placa detectado\n\n"
                    f"❌ Carro actual: {placa_existente} (placa {tipo_placa_existente.value})\n"
                    f"❌ Placa nueva: {nueva_placa} (placa {tipo_placa_nueva.value})\n\n"
                    f"💡 Solución: Para cumplir el pico y placa, el segundo carro debe terminar en dígito {tipo_requerido}\n"
                    f"   Dígitos válidos: {digitos_requeridos}",
                )

        return True, ""

    def validar_combinaciones_permitidas(self, vehiculos_actuales: List[Dict], nuevo_tipo: str, funcionario_id: int = None) -> Tuple[bool, str]:
        """
        Valida las combinaciones permitidas de vehículos

        Combinaciones válidas (funcionarios regulares - MÁXIMO 3 VEHÍCULOS):
        1. 1 Carro + 1 Moto + 1 Bicicleta
        2. 2 Carros + 1 Bicicleta (carros con placas PAR/IMPAR diferentes)
        3. 2 Carros + 1 Moto (carros con placas PAR/IMPAR diferentes)

        Combinaciones válidas (directivos con parqueadero exclusivo):
        - Hasta 4 carros sin restricción PAR/IMPAR + 1 moto + 1 bicicleta (6 total)

        Args:
            vehiculos_actuales (List[Dict]): Vehículos actuales del funcionario
            nuevo_tipo (str): Tipo del nuevo vehículo
            funcionario_id (int): ID del funcionario para verificar si es directivo con exclusivo

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        conteo = self.contar_vehiculos_por_tipo(vehiculos_actuales)
        total_actual = sum(conteo.values())

        # Verificar si es directivo con parqueadero exclusivo
        max_vehiculos = self.MAX_VEHICULOS_POR_FUNCIONARIO
        es_directivo_exclusivo = False
        if funcionario_id and self.db:
            query = """
                SELECT tiene_parqueadero_exclusivo
                FROM funcionarios
                WHERE id = %s AND activo = TRUE
            """
            funcionario_data = self.db.fetch_one(query, (funcionario_id,))
            if funcionario_data:
                tiene_exclusivo = funcionario_data.get("tiene_parqueadero_exclusivo", False)

                # Si tiene parqueadero exclusivo, permite hasta 4 vehículos (sin restricción de cargo)
                if tiene_exclusivo:
                    max_vehiculos = self.MAX_VEHICULOS_DIRECTIVO_EXCLUSIVO
                    es_directivo_exclusivo = True

        # Si ya tiene el máximo de vehículos, no puede agregar más
        if total_actual >= max_vehiculos:
            vehiculos_str = ", ".join([f"{count} {tipo}" for tipo, count in conteo.items() if count > 0])
            return (
                False,
                f"🚫 Límite de vehículos alcanzado\n\n"
                f"📊 Vehículos actuales: {vehiculos_str}\n"
                f"🔒 Máximo permitido: {max_vehiculos} vehículos por funcionario",
            )

        # Si es el primer vehículo, siempre es válido
        if total_actual == 0:
            return True, ""

        # Si es directivo con exclusivo, validar límites por tipo de vehículo
        if es_directivo_exclusivo:
            if nuevo_tipo == TipoVehiculo.CARRO.value:
                if conteo[TipoVehiculo.CARRO.value] >= self.MAX_CARROS_DIRECTIVO_EXCLUSIVO:
                    return (
                        False,
                        f"🚗 Límite de carros alcanzado para Directivo Exclusivo\n\n"
                        f"📊 Carros actuales: {conteo[TipoVehiculo.CARRO.value]}\n"
                        f"🔒 Máximo permitido: {self.MAX_CARROS_DIRECTIVO_EXCLUSIVO} carros\n\n"
                        f"💡 Puede registrar hasta 1 moto y 1 bicicleta adicional."
                    )
                return True, ""
            elif nuevo_tipo == TipoVehiculo.MOTO.value:
                if conteo[TipoVehiculo.MOTO.value] >= self.MAX_MOTOS_DIRECTIVO_EXCLUSIVO:
                    return (
                        False,
                        f"🏍️ Límite de motos alcanzado para Directivo Exclusivo\n\n"
                        f"📊 Motos actuales: {conteo[TipoVehiculo.MOTO.value]}\n"
                        f"🔒 Máximo permitido: {self.MAX_MOTOS_DIRECTIVO_EXCLUSIVO} moto\n\n"
                        f"💡 Puede registrar carros (hasta {self.MAX_CARROS_DIRECTIVO_EXCLUSIVO}) o 1 bicicleta."
                    )
                return True, ""
            elif nuevo_tipo == TipoVehiculo.BICICLETA.value:
                if conteo[TipoVehiculo.BICICLETA.value] >= self.MAX_BICICLETAS_DIRECTIVO_EXCLUSIVO:
                    return (
                        False,
                        f"🚲 Límite de bicicletas alcanzado para Directivo Exclusivo\n\n"
                        f"📊 Bicicletas actuales: {conteo[TipoVehiculo.BICICLETA.value]}\n"
                        f"🔒 Máximo permitido: {self.MAX_BICICLETAS_DIRECTIVO_EXCLUSIVO} bicicleta\n\n"
                        f"💡 Puede registrar carros (hasta {self.MAX_CARROS_DIRECTIVO_EXCLUSIVO}) o 1 moto."
                    )
                return True, ""

        # ====================================================================================
        # VALIDACIONES PARA FUNCIONARIOS REGULARES
        # ====================================================================================
        # Combinaciones válidas permitidas:
        # 1. 1 Carro + 1 Moto + 1 Bicicleta
        # 2. 2 Carros + 1 Bicicleta
        # 3. 2 Carros + 1 Moto
        # ====================================================================================

        cant_carros = conteo[TipoVehiculo.CARRO.value]
        cant_motos = conteo[TipoVehiculo.MOTO.value]
        cant_bicis = conteo[TipoVehiculo.BICICLETA.value]

        # Validar límite de 2 carros para regulares
        if nuevo_tipo == TipoVehiculo.CARRO.value and cant_carros >= self.MAX_CARROS_REGULAR:
            return (
                False,
                f"🚗 Límite de carros alcanzado\n\n"
                f"📊 Carros actuales: {cant_carros}\n"
                f"🔒 Máximo permitido: {self.MAX_CARROS_REGULAR} carros para funcionarios regulares\n\n"
                f"💡 Puede registrar moto o bicicleta si aún no tiene una."
            )

        # Validar que solo puede tener 1 moto
        if nuevo_tipo == TipoVehiculo.MOTO.value and cant_motos >= 1:
            return (
                False,
                "🏍️ No se puede registrar otra moto\n\n"
                "📋 Ya tiene una moto registrada.\n"
                "🔒 Límite: 1 moto por funcionario regular.\n\n"
                "💡 Combinaciones válidas:\n"
                "   • 1 Carro + 1 Moto + 1 Bicicleta\n"
                "   • 2 Carros + 1 Moto (carros con placas PAR/IMPAR)"
            )

        # Validar que solo puede tener 1 bicicleta
        if nuevo_tipo == TipoVehiculo.BICICLETA.value and cant_bicis >= 1:
            return (
                False,
                "🚲 No se puede registrar otra bicicleta\n\n"
                "📋 Ya tiene una bicicleta registrada.\n"
                "🔒 Límite: 1 bicicleta por funcionario regular.\n\n"
                "💡 Combinaciones válidas:\n"
                "   • 1 Carro + 1 Moto + 1 Bicicleta\n"
                "   • 2 Carros + 1 Bicicleta (carros con placas PAR/IMPAR)"
            )

        # Verificar que la combinación resultante sea válida
        cant_carros_nuevo = cant_carros + (1 if nuevo_tipo == TipoVehiculo.CARRO.value else 0)
        cant_motos_nuevo = cant_motos + (1 if nuevo_tipo == TipoVehiculo.MOTO.value else 0)
        cant_bicis_nuevo = cant_bicis + (1 if nuevo_tipo == TipoVehiculo.BICICLETA.value else 0)

        # Combinación 1: 1 Carro + 1 Moto + 1 Bicicleta
        combinacion1 = (cant_carros_nuevo == 1 and cant_motos_nuevo == 1 and cant_bicis_nuevo == 1)

        # Combinación 2: 2 Carros + 1 Bicicleta
        combinacion2 = (cant_carros_nuevo == 2 and cant_bicis_nuevo == 1 and cant_motos_nuevo == 0)

        # Combinación 3: 2 Carros + 1 Moto
        combinacion3 = (cant_carros_nuevo == 2 and cant_motos_nuevo == 1 and cant_bicis_nuevo == 0)

        # Combinaciones parciales válidas (1 o 2 vehículos)
        combinacion_parcial_valida = (
            # Solo 1 vehículo
            (cant_carros_nuevo + cant_motos_nuevo + cant_bicis_nuevo == 1) or
            # 2 vehículos: cualquier combinación de 2 elementos
            (cant_carros_nuevo == 1 and cant_motos_nuevo == 1 and cant_bicis_nuevo == 0) or
            (cant_carros_nuevo == 1 and cant_bicis_nuevo == 1 and cant_motos_nuevo == 0) or
            (cant_carros_nuevo == 2 and cant_motos_nuevo == 0 and cant_bicis_nuevo == 0) or
            (cant_motos_nuevo == 1 and cant_bicis_nuevo == 1 and cant_carros_nuevo == 0)
        )

        # Validar que la combinación sea válida
        if combinacion1 or combinacion2 or combinacion3 or combinacion_parcial_valida:
            return True, ""

        # Si no es ninguna combinación válida, rechazar
        return (
            False,
            f"🚫 Combinación de vehículos no permitida\n\n"
            f"📊 Vehículos actuales: {cant_carros} Carro(s), {cant_motos} Moto(s), {cant_bicis} Bicicleta(s)\n"
            f"➕ Intentando agregar: {nuevo_tipo}\n\n"
            f"✅ Combinaciones válidas para funcionarios regulares:\n"
            f"   1. 1 Carro + 1 Moto + 1 Bicicleta\n"
            f"   2. 2 Carros + 1 Bicicleta (placas PAR/IMPAR)\n"
            f"   3. 2 Carros + 1 Moto (placas PAR/IMPAR)"
        )

    def validar_registro_vehiculo(
        self, vehiculos_actuales: List[Dict], nuevo_tipo: str, nueva_placa: str = "", funcionario_id: int = None
    ) -> Tuple[bool, str]:
        """
        Función principal que ejecuta todas las validaciones

        Args:
            vehiculos_actuales (List[Dict]): Lista de vehículos actuales del funcionario
            nuevo_tipo (str): Tipo del nuevo vehículo
            nueva_placa (str): Placa del nuevo vehículo (requerida solo para carros)
            funcionario_id (int): ID del funcionario (para validar límites de directivos)

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Validación 1: Cantidad máxima
        es_valido, mensaje = self.validar_cantidad_maxima(vehiculos_actuales, nuevo_tipo, funcionario_id)
        if not es_valido:
            return False, mensaje

        # Validación 2: Combinaciones permitidas
        es_valido, mensaje = self.validar_combinaciones_permitidas(vehiculos_actuales, nuevo_tipo, funcionario_id)
        if not es_valido:
            return False, mensaje

        # Validación 3: Pico y placa para carros
        if nuevo_tipo == TipoVehiculo.CARRO.value:
            es_valido, mensaje = self.validar_pico_y_placa_carros(vehiculos_actuales, nueva_placa, funcionario_id)
            if not es_valido:
                return False, mensaje

        return True, "✅ Validación exitosa. El vehículo cumple todas las reglas y puede ser registrado."

    def obtener_sugerencias_vehiculo(self, vehiculos_actuales: List[Dict]) -> List[str]:
        """
        Proporciona sugerencias sobre qué vehículos puede registrar el funcionario

        NOTA: Solo los carros requieren asignación de parqueadero.
        Motos y bicicletas no ocupan espacios de parqueadero.

        Args:
            vehiculos_actuales (List[Dict]): Vehículos actuales del funcionario

        Returns:
            List[str]: Lista de sugerencias
        """
        total_actual = len(vehiculos_actuales)

        if total_actual >= self.MAX_VEHICULOS_POR_FUNCIONARIO:
            return [
                "🔒 El funcionario ya alcanzó el máximo de vehículos permitidos (2).",
                "💡 Para registrar un nuevo vehículo, debe eliminar uno existente.",
            ]

        if total_actual == 0:
            return [
                "✅ El funcionario puede registrar cualquier tipo de vehículo.",
                "📋 Tipos disponibles: Carro, Moto, Bicicleta",
                "📝 Nota: Los carros requieren placa válida para pico y placa",
            ]

        # Tiene 1 vehículo, analizar qué puede agregar
        conteo = self.contar_vehiculos_por_tipo(vehiculos_actuales)
        sugerencias = []

        if conteo[TipoVehiculo.CARRO.value] == 1:
            # Ya tiene un carro
            carro_actual = next(v for v in vehiculos_actuales if v.get("tipo_vehiculo") == TipoVehiculo.CARRO.value)
            placa_actual = carro_actual.get("placa", "")
            tipo_placa_actual = self.obtener_tipo_placa(placa_actual)

            tipo_contrario = "PAR" if tipo_placa_actual == TipoCirculacion.IMPAR else "IMPAR"
            digitos_contrarios = "6, 7, 8, 9, 0" if tipo_contrario == "PAR" else "1, 2, 3, 4, 5"
            sugerencias.extend(
                [
                    f"🚗 Segundo carro: placa {tipo_contrario} (termina en {digitos_contrarios}) - Requerirá espacio de parqueadero",
                    "🏍️ Una moto (cualquier placa) - No requiere espacio de parqueadero",
                    "🚲 Una bicicleta - No requiere espacio de parqueadero",
                ]
            )
        elif conteo[TipoVehiculo.MOTO.value] == 1:
            # Ya tiene una moto
            sugerencias.extend(
                [
                    "🚗 Un carro (cualquier placa) - Requerirá espacio de parqueadero",
                    "🚲 Una bicicleta - No requiere espacio de parqueadero",
                ]
            )
        elif conteo[TipoVehiculo.BICICLETA.value] == 1:
            # Ya tiene una bicicleta
            sugerencias.extend(
                [
                    "🚗 Un carro (cualquier placa) - Requerirá espacio de parqueadero",
                    "🏍️ Una moto (cualquier placa) - No requiere espacio de parqueadero",
                ]
            )

        return sugerencias
