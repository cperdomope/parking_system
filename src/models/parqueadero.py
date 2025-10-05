# -*- coding: utf-8 -*-
"""
Modelo para operaciones con parqueaderos
"""

from typing import List, Dict, Tuple
from mysql.connector import Error
from ..database.manager import DatabaseManager
from ..utils.validaciones_asignacion import ValidadorAsignacion


class ParqueaderoModel:
    """Modelo para operaciones con parqueaderos"""

    def __init__(self, db: DatabaseManager):
        self.db = db

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
        except:
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
                    ) AS permite_compartir_ocupante
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
                    ) AS permite_compartir_ocupante
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

        # Post-procesamiento: calcular estado "display" considerando permite_compartir
        if results:
            for park in results:
                estado_display = park['estado']
                total_asigs = park.get('total_asignaciones', 0)
                permite_compartir = park.get('permite_compartir_ocupante')

                # Si hay 1 asignación Y el funcionario NO permite compartir → mostrar como Completo
                if total_asigs == 1 and permite_compartir == 0:  # 0 = FALSE en MySQL
                    estado_display = 'Completo'

                # Agregar el estado calculado
                park['estado_display'] = estado_display

            # Aplicar filtro de estado después del cálculo
            if estado:
                results = [p for p in results if p['estado_display'] == estado]

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
            # Solo considera carros existentes para el complemento
            query = """
                SELECT DISTINCT p.*
                FROM parqueaderos p
                JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
                JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE p.estado = 'Parcialmente_Asignado'
                AND v.tipo_vehiculo = 'Carro'
                AND v.tipo_circulacion != %s
                AND p.activo = TRUE
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
                    f.permite_compartir, f.pico_placa_solidario, f.discapacidad
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
            asignaciones_existentes = count_result.get('total', 0) if count_result else 0

            # 4. VALIDACIÓN: Si el funcionario NO permite compartir y hay asignaciones
            es_valido, mensaje = ValidadorAsignacion.validar_permite_compartir(
                vehiculo_data, asignaciones_existentes
            )
            if not es_valido:
                return (False, mensaje)

            # 5. VALIDACIÓN: Si hay ocupantes, verificar si permiten compartir
            ocupante_data = None
            if asignaciones_existentes > 0:
                query_ocupante = """
                    SELECT f.nombre, f.apellidos, f.cargo, f.permite_compartir
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    JOIN funcionarios f ON v.funcionario_id = f.id
                    WHERE a.parqueadero_id = %s AND a.activo = TRUE
                    LIMIT 1
                """
                ocupante_data = self.db.fetch_one(query_ocupante, (parqueadero_id,))

            es_valido, mensaje = ValidadorAsignacion.validar_ocupante_permite_compartir(ocupante_data)
            if not es_valido:
                return (False, mensaje)

            # 6. VALIDACIÓN: Pico y placa (solo si NO tiene pico_placa_solidario)
            mismo_tipo_count = 0
            if vehiculo_data['tipo_vehiculo'] == 'Carro' and vehiculo_data['tipo_circulacion'] != 'N/A':
                query_mismo_tipo = """
                    SELECT COUNT(*) as total
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    WHERE a.parqueadero_id = %s
                    AND a.activo = TRUE
                    AND v.tipo_circulacion = %s
                """
                mismo_tipo_result = self.db.fetch_one(
                    query_mismo_tipo,
                    (parqueadero_id, vehiculo_data['tipo_circulacion'])
                )
                mismo_tipo_count = mismo_tipo_result.get('total', 0) if mismo_tipo_result else 0

            es_valido, mensaje = ValidadorAsignacion.validar_pico_placa(
                vehiculo_data['tipo_vehiculo'],
                vehiculo_data['tipo_circulacion'],
                vehiculo_data.get('pico_placa_solidario', False),
                mismo_tipo_count
            )
            if not es_valido:
                return (False, mensaje)

            # 7. Mensajes informativos para casos especiales
            msg_info = ValidadorAsignacion.obtener_mensajes_informativos(vehiculo_data)

            # ==================== LLAMAR AL PROCEDIMIENTO ALMACENADO ====================

            self.db.cursor.callproc('sp_asignar_vehiculo', (vehiculo_id, parqueadero_id))

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
                msg_base = mensaje.get('mensaje', msg_base) if mensaje else msg_base

            # Agregar información adicional
            msg_final = f"✅ {msg_base}\n\n" \
                       f"🚗 Vehículo: {vehiculo_data['placa']}\n" \
                       f"👤 Funcionario: {vehiculo_data['nombre']} {vehiculo_data['apellidos']}\n" \
                       f"📍 Parqueadero: P-{parqueadero_data['numero_parqueadero']:03d}"

            if msg_info:
                msg_final += f"\n\nℹ️ Información:\n" + "\n".join(f"   • {info}" for info in msg_info)

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
        """Libera la asignación de un vehículo"""
        query = """
            UPDATE asignaciones
            SET activo = NULL, fecha_fin_asignacion = NOW()
            WHERE vehiculo_id = %s AND activo = TRUE
        """
        exito, _ = self.db.execute_query(query, (vehiculo_id,))
        return exito

    def obtener_estadisticas(self, sotano: str = None) -> Dict:
        """Obtiene estadísticas del parqueadero, opcionalmente filtradas por sótano"""
        # Verificar si existe la columna sotano
        try:
            check_query = "SHOW COLUMNS FROM parqueaderos LIKE 'sotano'"
            column_exists = self.db.fetch_one(check_query) is not None
        except:
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
            return result if result else {
                'total_parqueaderos': 0,
                'disponibles': 0,
                'parcialmente_asignados': 0,
                'completos': 0
            }
        else:
            # Estadísticas generales (compatible con versión anterior)
            try:
                results = self.db.call_procedure('sp_obtener_estadisticas')
                if results:
                    return results[0]
            except:
                # Fallback directo si el procedimiento no existe
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

            return {
                'total_parqueaderos': 0,
                'disponibles': 0,
                'parcialmente_asignados': 0,
                'completos': 0
            }

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
                sotanos_con_carros = [row['sotano'] for row in results] if results else []

                # Garantizar que aparezcan los 3 sótanos principales
                sotanos_principales = ['Sótano-1', 'Sótano-2', 'Sótano-3']

                # Si la base de datos tiene los sótanos, usar esos; si no, usar los principales
                if len(sotanos_con_carros) >= 2:  # Al menos 2 sótanos con carros
                    return sotanos_con_carros
                else:
                    return sotanos_principales
            else:
                # Sin columna sotano, retornar solo el sótano por defecto
                return ['Sótano-1']
        except Exception:
            # En caso de error, asegurar que aparezcan los 3 sótanos
            return ['Sótano-1', 'Sótano-2', 'Sótano-3']

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
            return [row['tipo_espacio'] for row in results] if results else ['Carro']
        except:
            return ['Carro']

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
        return result if result else {'total_espacios': 0, 'ocupados': 0, 'vehiculos_estacionados': 0}

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
                sotanos_data[row['sotano']] = {'total': row['total'], 'ocupados': row['ocupados']}
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
        
        ocupados_data = {row['tipo_vehiculo']: row['ocupados'] for row in ocupados_results} if ocupados_results else {}

        # Get total spots by specific type
        query_total = """
            SELECT tipo_espacio, COUNT(*) as total
            FROM parqueaderos
            WHERE activo = TRUE
            GROUP BY tipo_espacio;
        """
        total_results = self.db.fetch_all(query_total)
        
        total_data = {row['tipo_espacio']: row['total'] for row in total_results} if total_results else {}
        
        # Calculate total spots for each vehicle type, considering 'Mixto'
        total_carros = total_data.get('Carro', 0) + total_data.get('Mixto', 0)
        total_motos = total_data.get('Moto', 0) + total_data.get('Mixto', 0)
        total_bicicletas = total_data.get('Bicicleta', 0)

        tipos_data = {
            "Carro": {
                "ocupados": ocupados_data.get("Carro", 0),
                "total": total_carros
            },
            "Moto": {
                "ocupados": ocupados_data.get("Moto", 0),
                "total": total_motos
            },
            "Bicicleta": {
                "ocupados": ocupados_data.get("Bicicleta", 0),
                "total": total_bicicletas
            }
        }
        
        return tipos_data