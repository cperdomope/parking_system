# -*- coding: utf-8 -*-
"""
Módulo para gestión de eliminación en cascada completa
Garantiza que al eliminar un funcionario se borren TODOS sus datos asociados
"""

from typing import Dict, List, Tuple

from .manager import DatabaseManager


class GestorEliminacionCascada:
    """Gestiona la eliminación completa en cascada de funcionarios y sus datos"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def obtener_datos_funcionario_completos(self, identificador: str) -> Dict:
        """
        Obtiene TODOS los datos asociados a un funcionario por cédula o ID

        Args:
            identificador (str): Cédula o ID del funcionario

        Returns:
            Dict: Información completa del funcionario y datos asociados
        """
        try:
            # Determinar si es ID numérico o cédula
            if identificador.isdigit():
                condicion = f"f.id = {identificador}"
            else:
                condicion = f"f.cedula = '{identificador}'"

            # Obtener datos del funcionario
            query_funcionario = f"""
                SELECT id, cedula, nombre, apellidos, direccion_grupo, cargo, celular,
                       no_tarjeta_proximidad, fecha_registro, activo
                FROM funcionarios f
                WHERE {condicion} AND f.activo = TRUE
            """
            funcionario = self.db.fetch_one(query_funcionario)

            if not funcionario:
                return {
                    "existe": False,
                    "funcionario": None,
                    "vehiculos": [],
                    "asignaciones": [],
                    "historial_accesos": [],
                    "parqueaderos_afectados": [],
                }

            funcionario_id = funcionario["id"]

            # Obtener vehículos del funcionario
            query_vehiculos = """
                SELECT v.id, v.tipo_vehiculo, v.placa, v.ultimo_digito,
                       v.tipo_circulacion, v.fecha_registro, v.activo
                FROM vehiculos v
                WHERE v.funcionario_id = %s AND v.activo = TRUE
            """
            vehiculos = self.db.fetch_all(query_vehiculos, (funcionario_id,))

            # Obtener asignaciones activas de los vehículos
            query_asignaciones = """
                SELECT a.id, a.parqueadero_id, a.vehiculo_id, a.fecha_asignacion,
                       a.fecha_fin_asignacion, a.activo, p.numero_parqueadero,
                       v.placa, v.tipo_vehiculo
                FROM asignaciones a
                JOIN vehiculos v ON a.vehiculo_id = v.id
                JOIN parqueaderos p ON a.parqueadero_id = p.id
                WHERE v.funcionario_id = %s AND a.activo = TRUE
            """
            asignaciones = self.db.fetch_all(query_asignaciones, (funcionario_id,))

            # Obtener historial de accesos
            query_historial = """
                SELECT h.id, h.vehiculo_id, h.parqueadero_id, h.tipo_evento,
                       h.fecha_hora, h.observaciones, v.placa, p.numero_parqueadero
                FROM historial_accesos h
                JOIN vehiculos v ON h.vehiculo_id = v.id
                JOIN parqueaderos p ON h.parqueadero_id = p.id
                WHERE v.funcionario_id = %s
                ORDER BY h.fecha_hora DESC
            """
            historial_accesos = self.db.fetch_all(query_historial, (funcionario_id,))

            # Obtener parqueaderos que quedarán libres
            query_parqueaderos = """
                SELECT DISTINCT p.id, p.numero_parqueadero, p.estado, p.tipo_espacio
                FROM parqueaderos p
                JOIN asignaciones a ON p.id = a.parqueadero_id
                JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE v.funcionario_id = %s AND a.activo = TRUE
            """
            parqueaderos_afectados = self.db.fetch_all(query_parqueaderos, (funcionario_id,))

            return {
                "existe": True,
                "funcionario": funcionario,
                "vehiculos": vehiculos,
                "asignaciones": asignaciones,
                "historial_accesos": historial_accesos,
                "parqueaderos_afectados": parqueaderos_afectados,
            }

        except Exception as e:
            return {
                "existe": False,
                "error": f"Error obteniendo datos del funcionario: {str(e)}",
                "funcionario": None,
                "vehiculos": [],
                "asignaciones": [],
                "historial_accesos": [],
                "parqueaderos_afectados": [],
            }

    def eliminar_funcionario_completo(self, identificador: str) -> Tuple[bool, str, Dict]:
        """
        Elimina un funcionario y TODOS sus datos asociados de forma completa

        Args:
            identificador (str): Cédula o ID del funcionario

        Returns:
            Tuple[bool, str, Dict]: (éxito, mensaje, detalles_eliminacion)
        """
        try:
            # Primero obtener todos los datos antes de eliminar
            datos_completos = self.obtener_datos_funcionario_completos(identificador)

            if not datos_completos["existe"]:
                return False, f"Funcionario con identificador '{identificador}' no encontrado", {}

            funcionario = datos_completos["funcionario"]
            funcionario_id = funcionario["id"]

            # Iniciar transacción
            self.db.connection.autocommit = False

            detalles_eliminacion = {
                "funcionario_eliminado": funcionario,
                "vehiculos_eliminados": datos_completos["vehiculos"],
                "asignaciones_liberadas": datos_completos["asignaciones"],
                "historial_borrado": len(datos_completos["historial_accesos"]),
                "parqueaderos_liberados": datos_completos["parqueaderos_afectados"],
            }

            # PASO 1: Eliminar historial de accesos
            if datos_completos["historial_accesos"]:
                query_historial = """
                    DELETE h FROM historial_accesos h
                    JOIN vehiculos v ON h.vehiculo_id = v.id
                    WHERE v.funcionario_id = %s
                """
                exito, error = self.db.execute_query(query_historial, (funcionario_id,))
                if not exito:
                    self.db.connection.rollback()
                    return False, f"Error eliminando historial: {error}", detalles_eliminacion

            # PASO 2: Eliminar TODOS los registros de asignaciones directamente
            query_eliminar_asignaciones = """
                DELETE a FROM asignaciones a
                JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE v.funcionario_id = %s
            """
            exito, error = self.db.execute_query(query_eliminar_asignaciones, (funcionario_id,))
            if not exito:
                self.db.connection.rollback()
                return False, f"Error eliminando asignaciones: {error}", detalles_eliminacion

            # PASO 3: Eliminar TODOS los vehículos (activos e inactivos)
            query_vehiculos = """
                DELETE FROM vehiculos
                WHERE funcionario_id = %s
            """
            exito, error = self.db.execute_query(query_vehiculos, (funcionario_id,))
            if not exito:
                self.db.connection.rollback()
                return False, f"Error eliminando vehículos: {error}", detalles_eliminacion

            # PASO 4: Eliminar el funcionario completamente
            query_funcionario = """
                DELETE FROM funcionarios
                WHERE id = %s
            """
            exito, error = self.db.execute_query(query_funcionario, (funcionario_id,))
            if not exito:
                self.db.connection.rollback()
                return False, f"Error eliminando funcionario: {error}", detalles_eliminacion

            # PASO 5: Actualizar estado de parqueaderos liberados
            for parqueadero in datos_completos["parqueaderos_afectados"]:
                query_actualizar_parqueadero = """
                    UPDATE parqueaderos
                    SET estado = 'Disponible'
                    WHERE id = %s
                """
                exito, error = self.db.execute_query(query_actualizar_parqueadero, (parqueadero["id"],))
                if not exito:
                    # No es crítico, solo advertencia
                    print(f"Advertencia: No se pudo actualizar parqueadero {parqueadero['numero_parqueadero']}")

            # Confirmar transacción
            self.db.connection.commit()

            # Verificar eliminación
            verificacion = self.verificar_eliminacion_completa(funcionario_id)

            if verificacion["eliminado_completamente"]:
                mensaje = f"""
ELIMINACION COMPLETA EXITOSA

Funcionario: {funcionario['nombre']} {funcionario['apellidos']} (Cedula: {funcionario['cedula']})

Datos eliminados:
- Vehiculos: {len(datos_completos['vehiculos'])}
- Asignaciones: {len(datos_completos['asignaciones'])}
- Registros de historial: {len(datos_completos['historial_accesos'])}
- Parqueaderos liberados: {len(datos_completos['parqueaderos_afectados'])}

Verificacion: Todos los datos fueron eliminados exitosamente
                """
                return True, mensaje, detalles_eliminacion
            else:
                return False, f"Eliminación parcial. Datos restantes: {verificacion}", detalles_eliminacion

        except Exception as e:
            if hasattr(self.db, "connection"):
                self.db.connection.rollback()
            return False, f"Error crítico en eliminación: {str(e)}", {}
        finally:
            # Restaurar autocommit
            if hasattr(self.db, "connection"):
                self.db.connection.autocommit = True

    def verificar_eliminacion_completa(self, funcionario_id: int) -> Dict:
        """Verifica que la eliminación haya sido completa"""
        verificacion = {
            "funcionario_existe": 0,
            "vehiculos_restantes": 0,
            "asignaciones_restantes": 0,
            "historial_restante": 0,
            "eliminado_completamente": True,
        }

        try:
            # Verificar funcionario
            query = "SELECT COUNT(*) as total FROM funcionarios WHERE id = %s"
            resultado = self.db.fetch_one(query, (funcionario_id,))
            verificacion["funcionario_existe"] = resultado["total"] if resultado else 0

            # Verificar vehículos
            query = "SELECT COUNT(*) as total FROM vehiculos WHERE funcionario_id = %s"
            resultado = self.db.fetch_one(query, (funcionario_id,))
            verificacion["vehiculos_restantes"] = resultado["total"] if resultado else 0

            # Verificar asignaciones
            query = """
                SELECT COUNT(*) as total FROM asignaciones a
                JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE v.funcionario_id = %s
            """
            resultado = self.db.fetch_one(query, (funcionario_id,))
            verificacion["asignaciones_restantes"] = resultado["total"] if resultado else 0

            # Verificar historial
            query = """
                SELECT COUNT(*) as total FROM historial_accesos h
                JOIN vehiculos v ON h.vehiculo_id = v.id
                WHERE v.funcionario_id = %s
            """
            resultado = self.db.fetch_one(query, (funcionario_id,))
            verificacion["historial_restante"] = resultado["total"] if resultado else 0

            # Determinar si fue completa
            verificacion["eliminado_completamente"] = (
                verificacion["funcionario_existe"] == 0
                and verificacion["vehiculos_restantes"] == 0
                and verificacion["asignaciones_restantes"] == 0
                and verificacion["historial_restante"] == 0
            )

        except Exception as e:
            verificacion["error"] = str(e)
            verificacion["eliminado_completamente"] = False

        return verificacion

    def buscar_funcionarios_por_criterio(self, criterio: str) -> List[Dict]:
        """Busca funcionarios por cédula, nombre o apellido para eliminación"""
        try:
            query = """
                SELECT f.id, f.cedula, f.nombre, f.apellidos, f.cargo,
                       COUNT(v.id) as total_vehiculos,
                       COUNT(a.id) as asignaciones_activas
                FROM funcionarios f
                LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
                LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
                WHERE f.activo = TRUE AND (
                    f.cedula LIKE %s OR
                    f.nombre LIKE %s OR
                    f.apellidos LIKE %s
                )
                GROUP BY f.id
                ORDER BY f.apellidos, f.nombre
            """
            criterio_like = f"%{criterio}%"
            return self.db.fetch_all(query, (criterio_like, criterio_like, criterio_like))

        except Exception as e:
            print(f"Error buscando funcionarios: {str(e)}")
            return []

    def generar_reporte_previa_eliminacion(self, identificador: str) -> str:
        """Genera un reporte detallado antes de eliminar un funcionario"""
        datos = self.obtener_datos_funcionario_completos(identificador)

        if not datos["existe"]:
            return f"ERROR Funcionario con identificador '{identificador}' no encontrado"

        funcionario = datos["funcionario"]
        reporte = [
            "REPORTE DE ELIMINACION PREVISTA",
            "=" * 50,
            "",
            "FUNCIONARIO A ELIMINAR:",
            f"   - Nombre: {funcionario['nombre']} {funcionario['apellidos']}",
            f"   - Cedula: {funcionario['cedula']}",
            f"   - Cargo: {funcionario['cargo']}",
            f"   - Registro: {funcionario['fecha_registro']}",
            "",
            f"VEHICULOS A ELIMINAR ({len(datos['vehiculos'])}):",
        ]

        for vehiculo in datos["vehiculos"]:
            reporte.append(f"   - {vehiculo['tipo_vehiculo']} - {vehiculo['placa']} ({vehiculo['tipo_circulacion']})")

        reporte.extend(["", f"ASIGNACIONES A LIBERAR ({len(datos['asignaciones'])}):"])

        for asignacion in datos["asignaciones"]:
            reporte.append(f"   - Parqueadero {asignacion['numero_parqueadero']} - {asignacion['placa']}")

        reporte.extend(
            [
                "",
                f"HISTORIAL A ELIMINAR: {len(datos['historial_accesos'])} registros",
                "",
                f"PARQUEADEROS A LIBERAR ({len(datos['parqueaderos_afectados'])}):",
            ]
        )

        for parqueadero in datos["parqueaderos_afectados"]:
            reporte.append(f"   - Parqueadero {parqueadero['numero_parqueadero']} (estado: {parqueadero['estado']})")

        reporte.extend(
            [
                "",
                "ADVERTENCIA: Esta accion es IRREVERSIBLE",
                "   Todos los datos asociados seran eliminados permanentemente.",
            ]
        )

        return "\n".join(reporte)
