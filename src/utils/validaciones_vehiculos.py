# -*- coding: utf-8 -*-
"""
Módulo de validaciones para el registro de vehículos de funcionarios
Implementa las reglas de negocio para cantidad máxima y combinaciones permitidas
"""

from typing import List, Dict, Tuple
from ..config.settings import TipoVehiculo, TipoCirculacion
from .validaciones import ValidadorPicoPlaca, ValidadorCampos


class ValidadorVehiculos:
    """Clase para validar el registro de vehículos según reglas de negocio

    IMPORTANTE: Solo los carros ocupan espacios de parqueadero.
    Motos y bicicletas no afectan los estados de parqueaderos.
    """

    # Cantidad máxima de vehículos por funcionario
    MAX_VEHICULOS_POR_FUNCIONARIO = 2

    def __init__(self):
        pass

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
        conteo = {
            TipoVehiculo.CARRO.value: 0,
            TipoVehiculo.MOTO.value: 0,
            TipoVehiculo.BICICLETA.value: 0
        }

        for vehiculo in vehiculos:
            tipo = vehiculo.get('tipo_vehiculo', '')
            if tipo in conteo:
                conteo[tipo] += 1

        return conteo

    def validar_cantidad_maxima(self, vehiculos_actuales: List[Dict], nuevo_tipo: str) -> Tuple[bool, str]:
        """
        Valida que no se exceda la cantidad máxima de vehículos

        Args:
            vehiculos_actuales (List[Dict]): Vehículos actuales del funcionario
            nuevo_tipo (str): Tipo del nuevo vehículo a registrar

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        total_actual = len(vehiculos_actuales)

        if total_actual >= self.MAX_VEHICULOS_POR_FUNCIONARIO:
            return False, f"💔 No se puede registrar más vehículos.\n\n" \
                         f"📊 Estado actual: {total_actual} de {self.MAX_VEHICULOS_POR_FUNCIONARIO} vehículos permitidos.\n" \
                         f"💡 Para agregar un nuevo vehículo, primero debe eliminar uno existente."

        return True, ""

    def validar_pico_y_placa_carros(self, vehiculos_actuales: List[Dict], nueva_placa: str) -> Tuple[bool, str]:
        """
        Valida la regla de pico y placa para carros
        Si ya tiene un carro, el nuevo debe tener placa diferente (par/impar)

        Args:
            vehiculos_actuales (List[Dict]): Vehículos actuales del funcionario
            nueva_placa (str): Placa del nuevo carro

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Validar formato de placa usando validador centralizado
        es_valida, mensaje = ValidadorCampos.validar_placa(nueva_placa, requerido=True)
        if not es_valida:
            return False, mensaje

        carros_actuales = [v for v in vehiculos_actuales if v.get('tipo_vehiculo') == TipoVehiculo.CARRO.value]

        if len(carros_actuales) == 0:
            # Si no tiene carros, puede registrar cualquiera
            return True, ""

        if len(carros_actuales) >= 1:
            # Ya tiene un carro, verificar pico y placa
            carro_existente = carros_actuales[0]
            placa_existente = carro_existente.get('placa', '')

            tipo_placa_existente = self.obtener_tipo_placa(placa_existente)
            tipo_placa_nueva = self.obtener_tipo_placa(nueva_placa)

            if tipo_placa_existente == tipo_placa_nueva and tipo_placa_nueva != TipoCirculacion.NA:
                tipo_requerido = 'PAR' if tipo_placa_existente == TipoCirculacion.IMPAR else 'IMPAR'
                digitos_requeridos = '6, 7, 8, 9, 0' if tipo_requerido == 'PAR' else '1, 2, 3, 4, 5'

                return False, f"🚗 Conflicto de pico y placa detectado\n\n" \
                             f"❌ Carro actual: {placa_existente} (placa {tipo_placa_existente.value})\n" \
                             f"❌ Placa nueva: {nueva_placa} (placa {tipo_placa_nueva.value})\n\n" \
                             f"💡 Solución: Para cumplir el pico y placa, el segundo carro debe terminar en dígito {tipo_requerido}\n" \
                             f"   Dígitos válidos: {digitos_requeridos}"

        return True, ""

    def validar_combinaciones_permitidas(self, vehiculos_actuales: List[Dict], nuevo_tipo: str) -> Tuple[bool, str]:
        """
        Valida las combinaciones permitidas de vehículos

        Combinaciones válidas:
        - 1 carro + 1 moto
        - 1 carro + 1 bicicleta
        - 1 moto + 1 bicicleta
        - 2 carros (con placas par/impar diferentes)

        Args:
            vehiculos_actuales (List[Dict]): Vehículos actuales del funcionario
            nuevo_tipo (str): Tipo del nuevo vehículo

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        conteo = self.contar_vehiculos_por_tipo(vehiculos_actuales)

        # Si ya tiene 2 vehículos, no puede agregar más
        total_actual = sum(conteo.values())
        if total_actual >= self.MAX_VEHICULOS_POR_FUNCIONARIO:
            vehiculos_str = ", ".join([f"{count} {tipo}" for tipo, count in conteo.items() if count > 0])
            return False, f"🚫 Límite de vehículos alcanzado\n\n" \
                         f"📊 Vehículos actuales: {vehiculos_str}\n" \
                         f"🔒 Máximo permitido: {self.MAX_VEHICULOS_POR_FUNCIONARIO} vehículos por funcionario"

        # Si es el primer vehículo, siempre es válido
        if total_actual == 0:
            return True, ""

        # Si es el segundo vehículo, validar combinaciones
        if nuevo_tipo == TipoVehiculo.CARRO.value:
            if conteo[TipoVehiculo.CARRO.value] >= 1:
                # Ya tiene un carro, validar que sea diferente tipo de placa
                # Esta validación se hace en validar_pico_y_placa_carros
                return True, ""
            elif conteo[TipoVehiculo.MOTO.value] >= 1 or conteo[TipoVehiculo.BICICLETA.value] >= 1:
                # Combinación válida: carro + moto/bicicleta
                return True, ""

        elif nuevo_tipo == TipoVehiculo.MOTO.value:
            if conteo[TipoVehiculo.MOTO.value] >= 1:
                return False, "🏍️ No se puede registrar otra moto\n\n" \
                             "📋 Ya tiene una moto registrada.\n" \
                             "🔒 Límite: 1 moto por funcionario.\n\n" \
                             "💡 Puede registrar un carro o bicicleta como segundo vehículo."
            elif conteo[TipoVehiculo.CARRO.value] >= 1 or conteo[TipoVehiculo.BICICLETA.value] >= 1:
                # Combinación válida: moto + carro/bicicleta
                return True, ""

        elif nuevo_tipo == TipoVehiculo.BICICLETA.value:
            if conteo[TipoVehiculo.BICICLETA.value] >= 1:
                return False, "🚲 No se puede registrar otra bicicleta\n\n" \
                             "📋 Ya tiene una bicicleta registrada.\n" \
                             "🔒 Límite: 1 bicicleta por funcionario.\n\n" \
                             "💡 Puede registrar un carro o moto como segundo vehículo."
            elif conteo[TipoVehiculo.CARRO.value] >= 1 or conteo[TipoVehiculo.MOTO.value] >= 1:
                # Combinación válida: bicicleta + carro/moto
                return True, ""

        return True, ""

    def validar_registro_vehiculo(self, vehiculos_actuales: List[Dict], nuevo_tipo: str, nueva_placa: str = "") -> Tuple[bool, str]:
        """
        Función principal que ejecuta todas las validaciones

        Args:
            vehiculos_actuales (List[Dict]): Lista de vehículos actuales del funcionario
            nuevo_tipo (str): Tipo del nuevo vehículo
            nueva_placa (str): Placa del nuevo vehículo (requerida solo para carros)

        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        # Validación 1: Cantidad máxima
        es_valido, mensaje = self.validar_cantidad_maxima(vehiculos_actuales, nuevo_tipo)
        if not es_valido:
            return False, mensaje

        # Validación 2: Combinaciones permitidas
        es_valido, mensaje = self.validar_combinaciones_permitidas(vehiculos_actuales, nuevo_tipo)
        if not es_valido:
            return False, mensaje

        # Validación 3: Pico y placa para carros
        if nuevo_tipo == TipoVehiculo.CARRO.value:
            es_valido, mensaje = self.validar_pico_y_placa_carros(vehiculos_actuales, nueva_placa)
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
            return ["🔒 El funcionario ya alcanzó el máximo de vehículos permitidos (2).",
                   "💡 Para registrar un nuevo vehículo, debe eliminar uno existente."]

        if total_actual == 0:
            return [
                "✅ El funcionario puede registrar cualquier tipo de vehículo.",
                "📋 Tipos disponibles: Carro, Moto, Bicicleta",
                "📝 Nota: Los carros requieren placa válida para pico y placa"
            ]

        # Tiene 1 vehículo, analizar qué puede agregar
        conteo = self.contar_vehiculos_por_tipo(vehiculos_actuales)
        sugerencias = []

        if conteo[TipoVehiculo.CARRO.value] == 1:
            # Ya tiene un carro
            carro_actual = next(v for v in vehiculos_actuales if v.get('tipo_vehiculo') == TipoVehiculo.CARRO.value)
            placa_actual = carro_actual.get('placa', '')
            tipo_placa_actual = self.obtener_tipo_placa(placa_actual)

            tipo_contrario = "PAR" if tipo_placa_actual == TipoCirculacion.IMPAR else "IMPAR"
            digitos_contrarios = "6, 7, 8, 9, 0" if tipo_contrario == "PAR" else "1, 2, 3, 4, 5"
            sugerencias.extend([
                f"🚗 Segundo carro: placa {tipo_contrario} (termina en {digitos_contrarios}) - Requerirá espacio de parqueadero",
                "🏍️ Una moto (cualquier placa) - No requiere espacio de parqueadero",
                "🚲 Una bicicleta - No requiere espacio de parqueadero"
            ])
        elif conteo[TipoVehiculo.MOTO.value] == 1:
            # Ya tiene una moto
            sugerencias.extend([
                "🚗 Un carro (cualquier placa) - Requerirá espacio de parqueadero",
                "🚲 Una bicicleta - No requiere espacio de parqueadero"
            ])
        elif conteo[TipoVehiculo.BICICLETA.value] == 1:
            # Ya tiene una bicicleta
            sugerencias.extend([
                "🚗 Un carro (cualquier placa) - Requerirá espacio de parqueadero",
                "🏍️ Una moto (cualquier placa) - No requiere espacio de parqueadero"
            ])

        return sugerencias