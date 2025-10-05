# -*- coding: utf-8 -*-
"""
Modelo para operaciones CRUD de vehículos
"""

from typing import List, Dict, Tuple
from ..database.manager import DatabaseManager
from ..utils.validaciones_vehiculos import ValidadorVehiculos
from ..utils.validaciones import ValidadorCampos


class VehiculoModel:
    """Modelo para operaciones CRUD de vehículos"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.validador = ValidadorVehiculos()

    def validar_placa_unica(self, placa: str, vehiculo_id: int = None) -> Tuple[bool, str]:
        """Valida que la placa no exista en el sistema

        Args:
            placa (str): Placa a validar
            vehiculo_id (int, optional): ID del vehículo a excluir (para actualizaciones)

        Returns:
            Tuple[bool, str]: (es_única, mensaje_error)
        """
        # Validar formato usando validador centralizado
        es_valida, mensaje = ValidadorCampos.validar_placa(placa, requerido=True)
        if not es_valida:
            return False, mensaje

        query = "SELECT id, tipo_vehiculo FROM vehiculos WHERE UPPER(placa) = UPPER(%s) AND activo = TRUE"
        params = [placa.strip()]

        if vehiculo_id:
            query += " AND id != %s"
            params.append(vehiculo_id)

        existing = self.db.fetch_one(query, params)
        if existing:
            return False, f"🚫 Placa duplicada detectada\n\n" \
                         f"❌ La placa '{placa.upper()}' ya está registrada en el sistema.\n" \
                         f"🚗 Tipo de vehículo: {existing['tipo_vehiculo']}\n\n" \
                         f"💡 Solución: Use una placa diferente o verifique si ya está registrada."

        return True, ""

    def crear(self, funcionario_id: int, tipo_vehiculo: str, placa: str) -> Tuple[bool, str]:
        """Crea un nuevo vehículo con validaciones de reglas de negocio

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        # Validación 1: Placa única en el sistema (solo si se proporciona)
        # Para Bicicletas, la placa es opcional
        if placa and placa.strip():
            es_unica, mensaje_placa = self.validar_placa_unica(placa)
            if not es_unica:
                return False, mensaje_placa

        # Obtener vehículos actuales del funcionario
        vehiculos_actuales = self.obtener_por_funcionario(funcionario_id)

        # Validación 2: Reglas de negocio del funcionario
        es_valido, mensaje_validacion = self.validador.validar_registro_vehiculo(
            vehiculos_actuales, tipo_vehiculo, placa
        )

        if not es_valido:
            return False, mensaje_validacion

        # Si las validaciones pasan, crear el vehículo
        # Para Bicicletas sin placa, guardar NULL en lugar de cadena vacía
        placa_final = placa.upper() if placa and placa.strip() else None

        query = """
            INSERT INTO vehiculos (funcionario_id, tipo_vehiculo, placa)
            VALUES (%s, %s, %s)
        """
        exito, error = self.db.execute_query(query, (funcionario_id, tipo_vehiculo, placa_final))

        if exito:
            # Mensaje de éxito personalizado según si tiene placa o no
            if placa_final:
                mensaje_placa = f"🏷️ Placa: {placa_final}\n"
            else:
                mensaje_placa = f"🏷️ Placa: Sin placa (Bicicleta)\n"

            return True, f"✅ Vehículo registrado exitosamente\n\n" \
                        f"🚗 Tipo: {tipo_vehiculo}\n" \
                        f"{mensaje_placa}" \
                        f"👤 Funcionario ID: {funcionario_id}"
        else:
            # Manejo de errores específicos de BD
            if "Duplicate entry" in str(error):
                return False, f"🚫 Error: La placa '{placa.upper()}' ya existe en el sistema"
            elif "foreign key constraint" in str(error).lower():
                return False, f"🚫 Error: El funcionario con ID {funcionario_id} no existe"
            else:
                return False, f"🚫 Error al registrar el vehículo: {error}"

    def obtener_por_funcionario(self, funcionario_id: int) -> List[Dict]:
        """Obtiene todos los vehículos de un funcionario"""
        query = """
            SELECT v.*, p.numero_parqueadero
            FROM vehiculos v
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
            WHERE v.funcionario_id = %s AND v.activo = TRUE
        """
        return self.db.fetch_all(query, (funcionario_id,))

    def obtener_sin_asignar(self, tipo_circulacion: str = None) -> List[Dict]:
        """Obtiene vehículos sin parqueadero asignado"""
        query = """
            SELECT v.*, f.nombre, f.apellidos, f.cedula
            FROM vehiculos v
            JOIN funcionarios f ON v.funcionario_id = f.id
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            WHERE v.activo = TRUE AND a.id IS NULL AND v.tipo_vehiculo = 'Carro'
        """

        if tipo_circulacion:
            query += f" AND v.tipo_circulacion = '{tipo_circulacion}'"

        query += " ORDER BY f.apellidos, f.nombre"
        return self.db.fetch_all(query)

    def obtener_todos(self) -> List[Dict]:
        """Obtiene todos los vehículos con información de funcionario y parqueadero"""
        query = """
            SELECT
                v.id,
                CONCAT(f.nombre, ' ', f.apellidos) as funcionario,
                v.tipo_vehiculo,
                v.placa,
                v.ultimo_digito,
                v.tipo_circulacion,
                p.numero_parqueadero
            FROM vehiculos v
            JOIN funcionarios f ON v.funcionario_id = f.id
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
            WHERE v.activo = TRUE
            ORDER BY f.apellidos, f.nombre
        """
        return self.db.fetch_all(query)

    def obtener_sugerencias_vehiculo(self, funcionario_id: int) -> List[str]:
        """Obtiene sugerencias sobre qué vehículos puede registrar el funcionario

        Args:
            funcionario_id (int): ID del funcionario

        Returns:
            List[str]: Lista de sugerencias
        """
        vehiculos_actuales = self.obtener_por_funcionario(funcionario_id)
        return self.validador.obtener_sugerencias_vehiculo(vehiculos_actuales)

    def validar_vehiculo_antes_registro(self, funcionario_id: int, tipo_vehiculo: str, placa: str = "") -> Tuple[bool, str]:
        """Valida un vehículo antes del registro sin crearlo

        Args:
            funcionario_id (int): ID del funcionario
            tipo_vehiculo (str): Tipo de vehículo
            placa (str): Placa del vehículo

        Returns:
            Tuple[bool, str]: (es_válido, mensaje)
        """
        vehiculos_actuales = self.obtener_por_funcionario(funcionario_id)
        return self.validador.validar_registro_vehiculo(vehiculos_actuales, tipo_vehiculo, placa)

    def obtener_por_id(self, vehiculo_id: int) -> Dict:
        """Obtiene un vehículo específico por su ID

        Args:
            vehiculo_id (int): ID del vehículo

        Returns:
            Dict: Información del vehículo
        """
        query = """
            SELECT v.*, f.nombre, f.apellidos, f.cedula,
                   p.numero_parqueadero
            FROM vehiculos v
            JOIN funcionarios f ON v.funcionario_id = f.id
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
            WHERE v.id = %s AND v.activo = TRUE
        """
        return self.db.fetch_one(query, (vehiculo_id,))

    def actualizar(self, vehiculo_id: int, funcionario_id: int, tipo_vehiculo: str, placa: str) -> Tuple[bool, str]:
        """Actualiza un vehículo existente con validaciones

        Args:
            vehiculo_id (int): ID del vehículo a actualizar
            funcionario_id (int): ID del funcionario propietario
            tipo_vehiculo (str): Tipo de vehículo
            placa (str): Nueva placa del vehículo

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Obtener vehículo actual
            vehiculo_actual = self.obtener_por_id(vehiculo_id)
            if not vehiculo_actual:
                return False, "Vehículo no encontrado"

            # Validación 1: Placa única (solo si se proporciona)
            if placa and placa.strip():
                es_unica, mensaje_placa = self.validar_placa_unica(placa, vehiculo_id)
                if not es_unica:
                    return False, mensaje_placa

            # Obtener otros vehículos del funcionario (excluyendo el actual)
            vehiculos_funcionario = self.obtener_por_funcionario(funcionario_id)
            otros_vehiculos = [v for v in vehiculos_funcionario if v['id'] != vehiculo_id]

            # Validación 2: Reglas de negocio del funcionario
            es_valido, mensaje_validacion = self.validador.validar_registro_vehiculo(
                otros_vehiculos, tipo_vehiculo, placa
            )

            if not es_valido:
                return False, mensaje_validacion

            # Actualizar el vehículo
            placa_final = placa.upper() if placa and placa.strip() else None

            query = """
                UPDATE vehiculos
                SET funcionario_id = %s, tipo_vehiculo = %s, placa = %s
                WHERE id = %s AND activo = TRUE
            """
            exito, error = self.db.execute_query(query, (funcionario_id, tipo_vehiculo, placa_final, vehiculo_id))

            if exito:
                # Mensaje personalizado según si tiene placa o no
                if placa_final:
                    mensaje_placa = f"🏷️ Placa: {placa_final}\n"
                else:
                    mensaje_placa = f"🏷️ Placa: Sin placa (Bicicleta)\n"

                return True, f"✅ Vehículo actualizado exitosamente\n\n" \
                            f"🚗 Tipo: {tipo_vehiculo}\n" \
                            f"{mensaje_placa}" \
                            f"👤 Funcionario ID: {funcionario_id}"
            else:
                return False, f"🚫 Error al actualizar el vehículo: {error}"

        except Exception as e:
            return False, f"🚫 Error inesperado: {str(e)}"

    def eliminar(self, vehiculo_id: int) -> Tuple[bool, str]:
        """Elimina un vehículo (desactivación lógica) y libera asignaciones

        Args:
            vehiculo_id (int): ID del vehículo a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar que el vehículo existe
            vehiculo = self.obtener_por_id(vehiculo_id)
            if not vehiculo:
                return False, f"🔍 Vehículo no encontrado\n\n" \
                             f"❌ No existe un vehículo con ID: {vehiculo_id}\n" \
                             f"💡 Verifique que el vehículo no haya sido eliminado previamente"

            # Iniciar transacción
            self.db.connection.autocommit = False

            # 1. Liberar asignaciones activas
            query_liberar = """
                UPDATE asignaciones
                SET activo = NULL, fecha_fin_asignacion = NOW()
                WHERE vehiculo_id = %s AND activo = TRUE
            """
            exito, error = self.db.execute_query(query_liberar, (vehiculo_id,))
            if not exito:
                self.db.connection.rollback()
                return False, f"🚫 Error liberando asignaciones: {error}"

            # 2. Desactivar el vehículo
            query_eliminar = """
                UPDATE vehiculos
                SET activo = FALSE
                WHERE id = %s AND activo = TRUE
            """
            exito, error = self.db.execute_query(query_eliminar, (vehiculo_id,))
            if not exito:
                self.db.connection.rollback()
                return False, f"🚫 Error eliminando vehículo: {error}"

            # Confirmar transacción
            self.db.connection.commit()

            return True, f"✅ Vehículo eliminado exitosamente\n\n" \
                        f"🚗 Placa: {vehiculo['placa']}\n" \
                        f"👤 Propietario: {vehiculo['nombre']} {vehiculo['apellidos']}\n" \
                        f"🌐 El espacio de parqueadero ha sido liberado automáticamente"

        except Exception as e:
            if hasattr(self.db, 'connection'):
                self.db.connection.rollback()
            return False, f"🚫 Error inesperado: {str(e)}"
        finally:
            # Restaurar autocommit
            if hasattr(self.db, 'connection'):
                self.db.connection.autocommit = True

    def eliminar_fisico(self, vehiculo_id: int) -> Tuple[bool, str]:
        """Elimina un vehículo físicamente de la base de datos

        Args:
            vehiculo_id (int): ID del vehículo a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar que el vehículo existe
            vehiculo = self.obtener_por_id(vehiculo_id)
            if not vehiculo:
                return False, "Vehículo no encontrado"

            # Iniciar transacción
            self.db.connection.autocommit = False

            # 1. Eliminar asignaciones
            query_eliminar_asignaciones = """
                DELETE FROM asignaciones WHERE vehiculo_id = %s
            """
            exito, error = self.db.execute_query(query_eliminar_asignaciones, (vehiculo_id,))
            if not exito:
                self.db.connection.rollback()
                return False, f"Error eliminando asignaciones: {error}"

            # 2. Eliminar el vehículo
            query_eliminar = """
                DELETE FROM vehiculos WHERE id = %s
            """
            exito, error = self.db.execute_query(query_eliminar, (vehiculo_id,))
            if not exito:
                self.db.connection.rollback()
                return False, f"🚫 Error eliminando vehículo: {error}"

            # Confirmar transacción
            self.db.connection.commit()

            return True, f"Vehículo {vehiculo['placa']} eliminado permanentemente"

        except Exception as e:
            if hasattr(self.db, 'connection'):
                self.db.connection.rollback()
            return False, f"🚫 Error inesperado: {str(e)}"
        finally:
            # Restaurar autocommit
            if hasattr(self.db, 'connection'):
                self.db.connection.autocommit = True