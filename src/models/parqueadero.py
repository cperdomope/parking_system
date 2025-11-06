# -*- coding: utf-8 -*-
"""
Modelo para operaciones con parqueaderos
"""

from typing import Dict, List, Tuple

from mysql.connector import Error

from ..database.manager import DatabaseManager
from ..utils.validaciones_asignaciones import ValidadorAsignacion
from ..utils.formatters import format_numero_parqueadero


class ParqueaderoModel:
    """Modelo para operaciones con parqueaderos"""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def _obtener_vehiculos_detalle(self, parqueadero_id: int) -> List[Dict]:
        """
        Obtiene información detallada de todos los vehículos asignados a un parqueadero

        Returns:
            Lista de diccionarios con información de vehículos y funcionarios
        """
        query = """
            SELECT
                v.id as vehiculo_id,
                v.placa,
                v.tipo_vehiculo,
                v.tipo_circulacion,
                f.id as funcionario_id,
                CONCAT(f.nombre, ' ', f.apellidos) as funcionario_nombre,
                f.cargo,
                f.permite_compartir,
                f.pico_placa_solidario,
                f.discapacidad,
                f.tiene_parqueadero_exclusivo,
                f.tiene_carro_hibrido
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE a.parqueadero_id = %s
            AND a.activo = TRUE
            ORDER BY a.fecha_asignacion
        """
        results = self.db.fetch_all(query, (parqueadero_id,))
        return results if results else []

    def obtener_todos(self, sotano: str = None, tipo_vehiculo: str = None, estado: str = None) -> List[Dict]:
        """Obtiene información de todos los parqueaderos con filtros opcionales
        Solo muestra carros asignados, ya que motos y bicicletas no ocupan espacios de parqueadero

        Args:
            sotano: Filtro por sótano (ej: 'Sótano-1', 'Sótano-2', 'Sótano-3')
            tipo_vehiculo: Filtro por tipo de espacio ('Carro', 'Moto', 'Bicicleta')
            estado: Filtro por estado ('Disponible', 'Parcialmente_Asignado', 'Completo')
        """
        # Verificar si la columna 'sotano' existe
        try:
            # Intentar consultar la estructura de la tabla
            check_query = "SHOW COLUMNS FROM parqueaderos LIKE 'sotano'"
            column_exists = self.db.fetch_one(check_query) is not None
        except Exception as e:
            print(f"Advertencia al verificar columna 'sotano': {e}")
            column_exists = False

        # Query base adaptable según estructura de DB
        if column_exists:
            # Nueva estructura con sótanos
            query = """
                SELECT
                    p.id,
                    p.numero_parqueadero,
                    p.estado,
                    p.tipo_espacio,
                    COALESCE(p.sotano, 'Sótano-1') as sotano,
                    GROUP_CONCAT(
                        CONCAT(f.nombre, ' ', f.apellidos, ' (', v.placa, '-', v.tipo_circulacion, ')')
                        SEPARATOR ' | '
                    ) AS asignados,
                    (
                        SELECT COUNT(*)
                        FROM asignaciones a2
                        WHERE a2.parqueadero_id = p.id AND a2.activo = TRUE
                    ) AS total_asignaciones,
                    (
                        SELECT MIN(f2.permite_compartir)
                        FROM asignaciones a2
                        JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
                        JOIN funcionarios f2 ON v2.funcionario_id = f2.id
                        WHERE a2.parqueadero_id = p.id AND a2.activo = TRUE
                    ) AS permite_compartir_ocupante,
                    (
                        SELECT MAX(f2.pico_placa_solidario)
                        FROM asignaciones a2
                        JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
                        JOIN funcionarios f2 ON v2.funcionario_id = f2.id
                        WHERE a2.parqueadero_id = p.id AND a2.activo = TRUE
                    ) AS pico_placa_solidario_ocupante,
                    (
                        SELECT MAX(f2.discapacidad)
                        FROM asignaciones a2
                        JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
                        JOIN funcionarios f2 ON v2.funcionario_id = f2.id
                        WHERE a2.parqueadero_id = p.id AND a2.activo = TRUE
                    ) AS discapacidad_ocupante
                FROM parqueaderos p
                LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
                LEFT JOIN vehiculos v ON a.vehiculo_id = v.id
                    AND (v.tipo_vehiculo = 'Carro' OR p.tipo_espacio IN ('Moto', 'Bicicleta'))
                LEFT JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE p.activo = TRUE
            """
        else:
            # Estructura original sin sótanos (compatibilidad hacia atrás)
            query = """
                SELECT
                    p.id,
                    p.numero_parqueadero,
                    p.estado,
                    p.tipo_espacio,
                    'Sótano-1' as sotano,
                    GROUP_CONCAT(
                        CONCAT(f.nombre, ' ', f.apellidos, ' (', v.placa, '-', v.tipo_circulacion, ')')
                        SEPARATOR ' | '
                    ) AS asignados,
                    (
                        SELECT COUNT(*)
                        FROM asignaciones a2
                        WHERE a2.parqueadero_id = p.id AND a2.activo = TRUE
                    ) AS total_asignaciones,
                    (
                        SELECT MIN(f2.permite_compartir)
                        FROM asignaciones a2
                        JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
                        JOIN funcionarios f2 ON v2.funcionario_id = f2.id
                        WHERE a2.parqueadero_id = p.id AND a2.activo = TRUE
                    ) AS permite_compartir_ocupante,
                    (
                        SELECT MAX(f2.pico_placa_solidario)
                        FROM asignaciones a2
                        JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
                        JOIN funcionarios f2 ON v2.funcionario_id = f2.id
                        WHERE a2.parqueadero_id = p.id AND a2.activo = TRUE
                    ) AS pico_placa_solidario_ocupante,
                    (
                        SELECT MAX(f2.discapacidad)
                        FROM asignaciones a2
                        JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
                        JOIN funcionarios f2 ON v2.funcionario_id = f2.id
                        WHERE a2.parqueadero_id = p.id AND a2.activo = TRUE
                    ) AS discapacidad_ocupante
                FROM parqueaderos p
                LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
                LEFT JOIN vehiculos v ON a.vehiculo_id = v.id AND v.tipo_vehiculo = 'Carro'
                LEFT JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE p.activo = TRUE
            """

        # Aplicar filtros dinámicamente
        params = []
        if sotano and column_exists:
            query += " AND COALESCE(p.sotano, 'Sótano-1') = %s"
            params.append(sotano)

        if tipo_vehiculo and column_exists:
            query += " AND p.tipo_espacio = %s"
            params.append(tipo_vehiculo)

        # NO aplicar filtro por estado aquí - se aplicará post-procesamiento
        # para considerar la lógica de permite_compartir

        if column_exists:
            query += """
                GROUP BY p.id
                ORDER BY COALESCE(p.sotano, 'Sótano-1'), p.numero_parqueadero
            """
        else:
            query += """
                GROUP BY p.id
                ORDER BY p.numero_parqueadero
            """

        results = self.db.fetch_all(query, tuple(params) if params else None)

        # Post-procesamiento: calcular estado "display" considerando permite_compartir, pico_placa_solidario, discapacidad
        # y tipo de espacio (Motos y Bicicletas solo permiten 1 vehículo)
        # NUEVO: También agregamos información detallada de ocupación para tooltips y visualización mejorada
        if results:
            for park in results:
                estado_display = park["estado"]
                total_asigs = park.get("total_asignaciones", 0)
                permite_compartir = park.get("permite_compartir_ocupante")
                pico_placa_solidario = park.get("pico_placa_solidario_ocupante")
                discapacidad = park.get("discapacidad_ocupante")
                tipo_espacio = park.get("tipo_espacio", "Carro")

                # Obtener información detallada de vehículos asignados
                vehiculos_detalle = self._obtener_vehiculos_detalle(park["id"])

                # Determinar capacidad total y tipo de ocupación
                capacidad_total = 1  # Por defecto
                tipo_ocupacion = "Regular"

                if tipo_espacio in ["Moto", "Bicicleta"]:
                    capacidad_total = 1
                    tipo_ocupacion = "Individual"
                elif tipo_espacio == "Carro":
                    # Verificar si es directivo exclusivo
                    if vehiculos_detalle and vehiculos_detalle[0].get("tiene_parqueadero_exclusivo"):
                        capacidad_total = 4
                        tipo_ocupacion = "Exclusivo Directivo"
                    # Verificar si tiene carro híbrido
                    elif vehiculos_detalle and vehiculos_detalle[0].get("tiene_carro_hibrido"):
                        capacidad_total = 1
                        tipo_ocupacion = "Híbrido Ecológico"
                    # Verificar si no permite compartir
                    elif permite_compartir == 0:
                        capacidad_total = 1
                        tipo_ocupacion = "Exclusivo"
                    # Verificar pico y placa solidario
                    elif pico_placa_solidario == 1:
                        capacidad_total = 1
                        tipo_ocupacion = "Pico y Placa Solidario"
                    # Verificar discapacidad
                    elif discapacidad == 1:
                        capacidad_total = 1
                        tipo_ocupacion = "Prioritario (Discapacidad)"
                    else:
                        capacidad_total = 2
                        tipo_ocupacion = "Regular (PAR/IMPAR)"

                # REGLA 1: Motos y Bicicletas SIEMPRE se marcan como Completo con 1 asignación
                if tipo_espacio in ["Moto", "Bicicleta"] and total_asigs >= 1:
                    estado_display = "Completo"

                # REGLA 2: Exclusivo Directivo (4 carros) - Parcialmente Asignado hasta 4/4
                elif tipo_espacio == "Carro" and vehiculos_detalle and vehiculos_detalle[0].get("tiene_parqueadero_exclusivo"):
                    if total_asigs < 4:
                        estado_display = "Parcialmente_Asignado"
                    else:
                        estado_display = "Completo"

                # REGLA 3: Carros con condiciones especiales (1 asignación → Completo)
                elif tipo_espacio == "Carro" and total_asigs == 1:
                    if (
                        pico_placa_solidario == 1  # Tiene Pico y Placa Solidario
                        or discapacidad == 1  # Tiene Discapacidad
                        or (vehiculos_detalle and vehiculos_detalle[0].get("tiene_carro_hibrido"))  # Carro Híbrido
                    ):
                        estado_display = "Completo"
                    else:
                        # Funcionario regular con 1 carro → Parcialmente Asignado
                        estado_display = "Parcialmente_Asignado"

                # REGLA 4: Carros con 2 asignaciones (funcionarios regulares) → Completo
                elif tipo_espacio == "Carro" and total_asigs >= 2:
                    estado_display = "Completo"

                # Agregar información adicional para visualización mejorada
                park["estado_display"] = estado_display
                park["vehiculos_actuales"] = total_asigs
                park["capacidad_total"] = capacidad_total
                park["tipo_ocupacion"] = tipo_ocupacion
                park["vehiculos_detalle"] = vehiculos_detalle

            # Aplicar filtro de estado después del cálculo
            if estado:
                results = [p for p in results if p["estado_display"] == estado]

        return results

    def obtener_disponibles(self, tipo_complemento: str = None) -> List[Dict]:
        """
        Obtiene parqueaderos disponibles o que necesitan un complemento específico
        Solo considera carros para determinar disponibilidad
        Args:
            tipo_complemento: 'PAR' o 'IMPAR' para buscar espacios que necesiten ese tipo
        """
        if tipo_complemento:
            # Buscar parqueaderos parcialmente asignados que necesiten el complemento
            # VALIDACIÓN CRÍTICA: Solo devolver parqueaderos que:
            # 1. Tengan EXACTAMENTE 1 carro asignado
            # 2. El carro existente sea del tipo complementario (PAR vs IMPAR)
            # 3. El funcionario del carro existente NO tenga condiciones especiales que impidan compartir
            query = """
                SELECT DISTINCT p.id, p.numero_parqueadero, p.estado, p.tipo_espacio,
                       COALESCE(p.sotano, 'Sótano-1') as sotano
                FROM parqueaderos p
                WHERE p.estado = 'Parcialmente_Asignado'
                AND p.tipo_espacio = 'Carro'
                AND p.activo = TRUE
                AND (
                    -- Verificar que tiene EXACTAMENTE 1 carro
                    SELECT COUNT(*)
                    FROM asignaciones a2
                    JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
                    WHERE a2.parqueadero_id = p.id
                    AND a2.activo = TRUE
                    AND v2.tipo_vehiculo = 'Carro'
                ) = 1
                AND (
                    -- Verificar que el carro existente tiene tipo de circulación complementario
                    SELECT v.tipo_circulacion
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    WHERE a.parqueadero_id = p.id
                    AND a.activo = TRUE
                    AND v.tipo_vehiculo = 'Carro'
                    LIMIT 1
                ) != %s
                -- ✅ CORRECCIÓN v2.0.2: Eliminada validación de 'permite_compartir' (campo obsoleto)
                -- La lógica de compartir se valida únicamente con los 4 checkboxes siguientes
                AND (
                    -- Verificar que NO tiene pico y placa solidario
                    SELECT f.pico_placa_solidario
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    JOIN funcionarios f ON v.funcionario_id = f.id
                    WHERE a.parqueadero_id = p.id
                    AND a.activo = TRUE
                    AND v.tipo_vehiculo = 'Carro'
                    LIMIT 1
                ) = FALSE
                AND (
                    -- Verificar que NO tiene discapacidad
                    SELECT f.discapacidad
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    JOIN funcionarios f ON v.funcionario_id = f.id
                    WHERE a.parqueadero_id = p.id
                    AND a.activo = TRUE
                    AND v.tipo_vehiculo = 'Carro'
                    LIMIT 1
                ) = FALSE
                AND (
                    -- Verificar que NO tiene parqueadero exclusivo
                    SELECT f.tiene_parqueadero_exclusivo
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    JOIN funcionarios f ON v.funcionario_id = f.id
                    WHERE a.parqueadero_id = p.id
                    AND a.activo = TRUE
                    AND v.tipo_vehiculo = 'Carro'
                    LIMIT 1
                ) = FALSE
                AND (
                    -- Verificar que NO tiene carro híbrido
                    SELECT f.tiene_carro_hibrido
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    JOIN funcionarios f ON v.funcionario_id = f.id
                    WHERE a.parqueadero_id = p.id
                    AND a.activo = TRUE
                    AND v.tipo_vehiculo = 'Carro'
                    LIMIT 1
                ) = FALSE
                ORDER BY p.numero_parqueadero
            """
            return self.db.fetch_all(query, (tipo_complemento,))
        else:
            # Buscar parqueaderos completamente disponibles
            query = """
                SELECT * FROM parqueaderos
                WHERE estado = 'Disponible' AND activo = TRUE
                ORDER BY numero_parqueadero
            """
            return self.db.fetch_all(query)

    def asignar_vehiculo(self, vehiculo_id: int, parqueadero_id: int, observaciones: str = "") -> Tuple[bool, str]:
        """
        Asigna un vehículo a un parqueadero con validaciones previas de reglas de negocio

        Args:
            vehiculo_id: ID del vehículo a asignar
            parqueadero_id: ID del parqueadero
            observaciones: Observaciones adicionales sobre la asignación

        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            # ==================== VALIDACIONES PREVIAS ====================

            # 1. Obtener información completa del vehículo y funcionario
            query_vehiculo = """
                SELECT
                    v.id, v.tipo_vehiculo, v.placa, v.tipo_circulacion,
                    v.funcionario_id,
                    f.nombre, f.apellidos, f.cargo,
                    f.permite_compartir, f.pico_placa_solidario, f.discapacidad,
                    f.tiene_parqueadero_exclusivo
                FROM vehiculos v
                JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE v.id = %s AND v.activo = TRUE
            """
            vehiculo_data = self.db.fetch_one(query_vehiculo, (vehiculo_id,))

            if not vehiculo_data:
                return (False, "🚫 Vehículo no encontrado o inactivo")

            # 2. Verificar si el parqueadero existe
            query_parqueadero = """
                SELECT id, numero_parqueadero, estado, tipo_espacio
                FROM parqueaderos
                WHERE id = %s AND activo = TRUE
            """
            parqueadero_data = self.db.fetch_one(query_parqueadero, (parqueadero_id,))

            if not parqueadero_data:
                return (False, "🚫 Parqueadero no encontrado o inactivo")

            # 3. Contar asignaciones activas en el parqueadero
            query_count = """
                SELECT COUNT(*) as total
                FROM asignaciones
                WHERE parqueadero_id = %s AND activo = TRUE
            """
            count_result = self.db.fetch_one(query_count, (parqueadero_id,))
            asignaciones_existentes = count_result.get("total", 0) if count_result else 0

            # 4. VALIDACIÓN: Pico y placa (solo si NO tiene pico_placa_solidario)
            mismo_tipo_count = 0
            if vehiculo_data["tipo_vehiculo"] == "Carro" and vehiculo_data["tipo_circulacion"] != "N/A":
                query_mismo_tipo = """
                    SELECT COUNT(*) as total
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    WHERE a.parqueadero_id = %s
                    AND a.activo = TRUE
                    AND v.tipo_circulacion = %s
                """
                mismo_tipo_result = self.db.fetch_one(
                    query_mismo_tipo, (parqueadero_id, vehiculo_data["tipo_circulacion"])
                )
                mismo_tipo_count = mismo_tipo_result.get("total", 0) if mismo_tipo_result else 0

            es_valido, mensaje = ValidadorAsignacion.validar_pico_placa(
                vehiculo_data["tipo_vehiculo"],
                vehiculo_data["tipo_circulacion"],
                vehiculo_data.get("pico_placa_solidario", False),
                mismo_tipo_count,
                vehiculo_data.get("tiene_parqueadero_exclusivo", False),
                vehiculo_data.get("cargo", ""),
            )
            if not es_valido:
                return (False, mensaje)

            # 5. VALIDACIÓN CRÍTICA: Vehículos con excepción de pico y placa NO pueden compartir parqueadero
            # Excepciones: Pico y Placa Solidario, Discapacidad, Híbrido, Directivo Exclusivo
            pico_placa_solidario = vehiculo_data.get("pico_placa_solidario", False)
            discapacidad = vehiculo_data.get("discapacidad", False)
            es_hibrido = vehiculo_data.get("tipo_circulacion", "") == "HÍBRIDO"
            es_directivo_exclusivo = vehiculo_data.get("tiene_parqueadero_exclusivo", False)

            tiene_excepcion = (
                pico_placa_solidario or
                discapacidad or
                es_hibrido or
                es_directivo_exclusivo
            )

            if tiene_excepcion and asignaciones_existentes > 0:
                # Verificar si NO es directivo con sus propios vehículos
                if es_directivo_exclusivo:
                    # Permitir solo si TODOS los vehículos en el parqueadero son del MISMO funcionario
                    query_check_mismo_funcionario = """
                        SELECT COUNT(DISTINCT v.funcionario_id) as total_funcionarios
                        FROM asignaciones a
                        JOIN vehiculos v ON a.vehiculo_id = v.id
                        WHERE a.parqueadero_id = %s AND a.activo = TRUE
                    """
                    check_result = self.db.fetch_one(query_check_mismo_funcionario, (parqueadero_id,))
                    total_funcionarios = check_result.get("total_funcionarios", 0) if check_result else 0

                    if total_funcionarios > 0:
                        # Verificar que sea el MISMO funcionario
                        query_check_owner = """
                            SELECT v.funcionario_id
                            FROM asignaciones a
                            JOIN vehiculos v ON a.vehiculo_id = v.id
                            WHERE a.parqueadero_id = %s AND a.activo = TRUE
                            LIMIT 1
                        """
                        owner_result = self.db.fetch_one(query_check_owner, (parqueadero_id,))
                        funcionario_en_parqueadero = owner_result.get("funcionario_id") if owner_result else None

                        if funcionario_en_parqueadero != vehiculo_data["funcionario_id"]:
                            return (
                                False,
                                f"🚫 Este parqueadero ya está asignado a otro directivo.\n\n"
                                f"Los directivos exclusivos solo pueden compartir parqueaderos con sus propios vehículos."
                            )
                else:
                    # Para otras excepciones (Híbrido, Discapacidad, Pico y Placa Solidario)
                    # NO pueden usar parqueaderos parcialmente asignados
                    excepciones_str = []
                    if pico_placa_solidario:
                        excepciones_str.append("Pico y Placa Solidario")
                    if discapacidad:
                        excepciones_str.append("Funcionario con Discapacidad")
                    if es_hibrido:
                        excepciones_str.append("Vehículo Híbrido")

                    return (
                        False,
                        f"🚫 Este vehículo tiene excepción de pico y placa ({', '.join(excepciones_str)}).\n\n"
                        f"⚠️ Los vehículos con excepciones SOLO pueden asignarse a parqueaderos 100% DISPONIBLES.\n"
                        f"No pueden compartir con otros vehículos.\n\n"
                        f"Por favor, seleccione un parqueadero que esté completamente desocupado."
                    )

            # 6. Mensajes informativos para casos especiales
            msg_info = ValidadorAsignacion.obtener_mensajes_informativos(vehiculo_data)

            # ==================== LLAMAR AL PROCEDIMIENTO ALMACENADO ====================

            self.db.cursor.callproc("sp_asignar_vehiculo", (vehiculo_id, parqueadero_id))

            # Si hay observaciones, actualizar el registro
            if observaciones.strip():
                update_query = """
                    UPDATE asignaciones
                    SET observaciones = %s
                    WHERE vehiculo_id = %s AND activo = TRUE
                """
                self.db.cursor.execute(update_query, (observaciones.strip(), vehiculo_id))

            self.db.connection.commit()

            # Obtener el mensaje de resultado
            msg_base = "Asignación realizada correctamente"
            for result in self.db.cursor.stored_results():
                mensaje = result.fetchone()
                msg_base = mensaje.get("mensaje", msg_base) if mensaje else msg_base

            # Agregar información adicional
            msg_final = (
                f"✅ {msg_base}\n\n"
                f"🚗 Vehículo: {vehiculo_data['placa']}\n"
                f"👤 Funcionario: {vehiculo_data['nombre']} {vehiculo_data['apellidos']}\n"
                f"📍 Parqueadero: {format_numero_parqueadero(parqueadero_data['numero_parqueadero'])}"
            )

            if msg_info:
                msg_final += "\n\nℹ️ Información:\n" + "\n".join(f"   • {info}" for info in msg_info)

            return (True, msg_final)

        except Error as e:
            self.db.connection.rollback()
            error_msg = str(e)

            # Mejorar mensajes de error del procedimiento almacenado
            if "no permite compartir" in error_msg.lower():
                return (False, f"🚫 {error_msg}")
            elif "mismo tipo" in error_msg.lower() or "pico" in error_msg.lower():
                return (False, f"🚫 {error_msg}")
            else:
                return (False, f"🚫 Error en asignación: {error_msg}")

    def liberar_asignacion(self, vehiculo_id: int) -> bool:
        """Libera la asignación de un vehículo y actualiza el estado del parqueadero"""
        try:
            # Primero obtener el parqueadero_id antes de liberar
            query_get_park = """
                SELECT parqueadero_id
                FROM asignaciones
                WHERE vehiculo_id = %s AND activo = TRUE
            """
            resultado = self.db.fetch_one(query_get_park, (vehiculo_id,))

            if not resultado:
                return False

            parqueadero_id = resultado["parqueadero_id"]

            # Eliminar la asignación físicamente
            query_liberar = """
                DELETE FROM asignaciones
                WHERE vehiculo_id = %s AND activo = TRUE
            """
            exito, _ = self.db.execute_query(query_liberar, (vehiculo_id,))

            if not exito:
                return False

            # Recalcular el estado del parqueadero
            query_update_estado = """
                UPDATE parqueaderos p
                SET estado = CASE
                    WHEN (SELECT COUNT(*) FROM asignaciones WHERE parqueadero_id = p.id AND activo = TRUE) = 0
                        THEN 'Disponible'
                    WHEN p.tipo_espacio IN ('Moto', 'Bicicleta')
                        THEN 'Completo'
                    WHEN p.tipo_espacio = 'Carro' AND (SELECT COUNT(*) FROM asignaciones WHERE parqueadero_id = p.id AND activo = TRUE) = 1
                        THEN 'Parcialmente_Asignado'
                    ELSE 'Completo'
                END
                WHERE id = %s
            """
            self.db.execute_query(query_update_estado, (parqueadero_id,))

            return True

        except Exception as e:
            print(f"Error al liberar asignación: {e}")
            return False

    def obtener_estadisticas(self, sotano: str = None) -> Dict:
        """Obtiene estadísticas del parqueadero, opcionalmente filtradas por sótano"""
        # Verificar si existe la columna sotano
        try:
            check_query = "SHOW COLUMNS FROM parqueaderos LIKE 'sotano'"
            column_exists = self.db.fetch_one(check_query) is not None
        except Exception as e:
            print(f"Advertencia al verificar columna 'sotano': {e}")
            column_exists = False

        if sotano and column_exists:
            # Estadísticas específicas por sótano
            query = """
                SELECT
                    COUNT(*) as total_parqueaderos,
                    SUM(CASE WHEN estado = 'Disponible' THEN 1 ELSE 0 END) as disponibles,
                    SUM(CASE WHEN estado = 'Parcialmente_Asignado' THEN 1 ELSE 0 END) as parcialmente_asignados,
                    SUM(CASE WHEN estado = 'Completo' THEN 1 ELSE 0 END) as completos
                FROM parqueaderos
                WHERE activo = TRUE AND COALESCE(sotano, 'Sótano-1') = %s
            """
            result = self.db.fetch_one(query, (sotano,))
            return (
                result
                if result
                else {"total_parqueaderos": 0, "disponibles": 0, "parcialmente_asignados": 0, "completos": 0}
            )
        else:
            # Estadísticas generales (compatible con versión anterior)
            try:
                results = self.db.call_procedure("sp_obtener_estadisticas")
                if results:
                    return results[0]
            except Exception as e:
                # Fallback directo si el procedimiento no existe
                print(f"Procedimiento sp_obtener_estadisticas no disponible: {e}")
                query = """
                    SELECT
                        COUNT(*) as total_parqueaderos,
                        SUM(CASE WHEN estado = 'Disponible' THEN 1 ELSE 0 END) as disponibles,
                        SUM(CASE WHEN estado = 'Parcialmente_Asignado' THEN 1 ELSE 0 END) as parcialmente_asignados,
                        SUM(CASE WHEN estado = 'Completo' THEN 1 ELSE 0 END) as completos
                    FROM parqueaderos
                    WHERE activo = TRUE
                """
                result = self.db.fetch_one(query)
                if result:
                    return result

            return {"total_parqueaderos": 0, "disponibles": 0, "parcialmente_asignados": 0, "completos": 0}

    def obtener_sotanos_disponibles(self) -> List[str]:
        """Obtiene la lista de sótanos disponibles que tienen espacios para carros"""
        try:
            # Verificar si existe la columna sotano
            check_query = "SHOW COLUMNS FROM parqueaderos LIKE 'sotano'"
            column_exists = self.db.fetch_one(check_query) is not None

            if column_exists:
                # Obtener sótanos que tienen espacios para carros
                query = """
                    SELECT DISTINCT COALESCE(sotano, 'Sótano-1') as sotano
                    FROM parqueaderos
                    WHERE activo = TRUE
                    AND tipo_espacio = 'Carro'
                    ORDER BY sotano
                """
                results = self.db.fetch_all(query)
                sotanos_con_carros = [row["sotano"] for row in results] if results else []

                # Garantizar que aparezcan los 3 sótanos principales
                sotanos_principales = ["Sótano-1", "Sótano-2", "Sótano-3"]

                # Si la base de datos tiene los sótanos, usar esos; si no, usar los principales
                if len(sotanos_con_carros) >= 2:  # Al menos 2 sótanos con carros
                    return sotanos_con_carros
                else:
                    return sotanos_principales
            else:
                # Sin columna sotano, retornar solo el sótano por defecto
                return ["Sótano-1"]
        except Exception:
            # En caso de error, asegurar que aparezcan los 3 sótanos
            return ["Sótano-1", "Sótano-2", "Sótano-3"]

    def obtener_tipos_vehiculo_por_sotano(self, sotano: str = None) -> List[str]:
        """Obtiene los tipos de vehículo disponibles en un sótano específico"""
        try:
            # Verificar si existe la columna sotano
            check_query = "SHOW COLUMNS FROM parqueaderos LIKE 'sotano'"
            column_exists = self.db.fetch_one(check_query) is not None

            query = """
                SELECT DISTINCT tipo_espacio
                FROM parqueaderos
                WHERE activo = TRUE
            """
            params = []
            if sotano and column_exists:
                query += " AND COALESCE(sotano, 'Sótano-1') = %s"
                params.append(sotano)

            query += " ORDER BY tipo_espacio"

            results = self.db.fetch_all(query, tuple(params) if params else None)
            return [row["tipo_espacio"] for row in results] if results else ["Carro"]
        except Exception as e:
            print(f"Error al obtener tipos de vehículo: {e}")
            return ["Carro"]

    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales de ocupación para espacios de carros únicamente."""
        query = """
            SELECT
                (SELECT COUNT(*) FROM parqueaderos WHERE activo = TRUE AND tipo_espacio = 'Carro') AS total_espacios,
                (SELECT COUNT(DISTINCT a.parqueadero_id)
                 FROM asignaciones a
                 JOIN parqueaderos p ON a.parqueadero_id = p.id
                 WHERE a.activo = TRUE AND p.tipo_espacio = 'Carro') AS ocupados,
                (SELECT COUNT(*) FROM asignaciones WHERE activo = TRUE) AS vehiculos_estacionados
        """
        result = self.db.fetch_one(query)
        return result if result else {"total_espacios": 0, "ocupados": 0, "vehiculos_estacionados": 0}

    def obtener_ocupacion_por_sotano(self) -> Dict:
        """Obtiene la ocupación detallada por cada sótano contando solo parqueaderos de carros."""
        query = """
            SELECT
                COALESCE(TRIM(p.sotano), 'Sótano-1') as sotano,
                COUNT(DISTINCT p.id) AS total,
                COUNT(DISTINCT CASE WHEN a.parqueadero_id IS NOT NULL THEN a.parqueadero_id END) AS ocupados
            FROM parqueaderos p
            LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
            WHERE p.activo = TRUE AND p.tipo_espacio = 'Carro'
            GROUP BY COALESCE(TRIM(p.sotano), 'Sótano-1')
            ORDER BY COALESCE(TRIM(p.sotano), 'Sótano-1');
        """
        results = self.db.fetch_all(query)
        sotanos_data = {}
        if results:
            for row in results:
                sotanos_data[row["sotano"]] = {"total": row["total"], "ocupados": row["ocupados"]}
        return sotanos_data

    def obtener_ocupacion_por_tipo_vehiculo(self) -> Dict:
        """Obtiene la ocupación por tipo de vehículo de forma robusta."""

        # Get occupied spots
        query_ocupados = """
            SELECT v.tipo_vehiculo, COUNT(*) as ocupados
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            WHERE a.activo = TRUE
            GROUP BY v.tipo_vehiculo;
        """
        ocupados_results = self.db.fetch_all(query_ocupados)

        ocupados_data = {row["tipo_vehiculo"]: row["ocupados"] for row in ocupados_results} if ocupados_results else {}

        # Get total spots by specific type
        query_total = """
            SELECT tipo_espacio, COUNT(*) as total
            FROM parqueaderos
            WHERE activo = TRUE
            GROUP BY tipo_espacio;
        """
        total_results = self.db.fetch_all(query_total)

        total_data = {row["tipo_espacio"]: row["total"] for row in total_results} if total_results else {}

        # Calculate total spots for each vehicle type, considering 'Mixto'
        total_carros = total_data.get("Carro", 0) + total_data.get("Mixto", 0)
        total_motos = total_data.get("Moto", 0) + total_data.get("Mixto", 0)
        total_bicicletas = total_data.get("Bicicleta", 0)

        tipos_data = {
            "Carro": {"ocupados": ocupados_data.get("Carro", 0), "total": total_carros},
            "Moto": {"ocupados": ocupados_data.get("Moto", 0), "total": total_motos},
            "Bicicleta": {"ocupados": ocupados_data.get("Bicicleta", 0), "total": total_bicicletas},
        }

        return tipos_data
