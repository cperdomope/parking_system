# -*- coding: utf-8 -*-
"""
Modelo para operaciones CRUD de funcionarios
"""

from typing import List, Dict, Tuple
from ..database.manager import DatabaseManager
from ..database.eliminacion_cascada import GestorEliminacionCascada
from ..utils.validaciones_asignacion import ValidadorAsignacion
from ..utils.validaciones import ValidadorCampos, ValidadorReglasNegocio


class FuncionarioModel:
    """Modelo para operaciones CRUD de funcionarios"""

    def __init__(self, db: DatabaseManager):
        self.db = db
        self.gestor_eliminacion = GestorEliminacionCascada(self.db)

    def validar_cedula_unica(self, cedula: str, funcionario_id: int = None) -> Tuple[bool, str]:
        """Valida que la cédula no exista en el sistema

        Args:
            cedula (str): Cédula a validar
            funcionario_id (int, optional): ID del funcionario a excluir (para actualizaciones)

        Returns:
            Tuple[bool, str]: (es_única, mensaje_error)
        """
        # Validar formato usando validador centralizado
        es_valida, mensaje = ValidadorCampos.validar_cedula(cedula)
        if not es_valida:
            return False, mensaje

        cedula_clean = cedula.strip()

        query = "SELECT id, nombre, apellidos FROM funcionarios WHERE cedula = %s AND activo = TRUE"
        params = [cedula_clean]

        if funcionario_id:
            query += " AND id != %s"
            params.append(funcionario_id)

        existing = self.db.fetch_one(query, params)
        if existing:
            return False, f"🚫 Cédula duplicada detectada\n\n" \
                         f"❌ La cédula '{cedula_clean}' ya está registrada.\n" \
                         f"👤 Funcionario existente: {existing['nombre']} {existing['apellidos']}\n\n" \
                         f"💡 Solución: Use una cédula diferente o verifique si ya está registrado."

        return True, ""

    def crear(self, cedula: str, nombre: str, apellidos: str,
              direccion_grupo: str = "", cargo: str = "",
              celular: str = "", tarjeta: str = "",
              permite_compartir: bool = True,
              pico_placa_solidario: bool = False,
              discapacidad: bool = False) -> tuple:
        """Crea un nuevo funcionario en la base de datos

        Args:
            permite_compartir: Si el funcionario permite compartir parqueadero (default: True)
            pico_placa_solidario: Si puede usar parqueadero en días no correspondientes (default: False)
            discapacidad: Si el funcionario tiene condición de discapacidad (default: False)

        Returns:
            tuple: (bool: éxito, str: mensaje de error si existe)
        """
        # Validación 1: Cédula única
        es_unica, mensaje_cedula = self.validar_cedula_unica(cedula)
        if not es_unica:
            return False, mensaje_cedula

        # Validación 2: Nombre y apellidos
        es_valido, mensaje = ValidadorCampos.validar_nombre(nombre, "Nombre")
        if not es_valido:
            return False, mensaje

        es_valido, mensaje = ValidadorCampos.validar_nombre(apellidos, "Apellidos")
        if not es_valido:
            return False, mensaje

        # Validación 3: Lógica de permite_compartir según cargo
        permite_compartir = ValidadorReglasNegocio.validar_cargo_permite_compartir(
            cargo.strip(), permite_compartir
        )

        query = """
            INSERT INTO funcionarios
            (cedula, nombre, apellidos, direccion_grupo, cargo, celular, no_tarjeta_proximidad,
             permite_compartir, pico_placa_solidario, discapacidad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (cedula.strip(), nombre.strip(), apellidos.strip(),
                 direccion_grupo.strip(), cargo.strip(), celular.strip(), tarjeta.strip(),
                 permite_compartir, pico_placa_solidario, discapacidad)

        exito, error = self.db.execute_query(query, params)

        if exito:
            msg_extra = []
            if not permite_compartir:
                msg_extra.append("🚫 No permite compartir parqueadero (exclusivo)")
            if pico_placa_solidario:
                msg_extra.append("🔄 Pico y placa solidario activado")
            if discapacidad:
                msg_extra.append("♿ Condición de discapacidad registrada")

            return True, f"✅ Funcionario registrado exitosamente\n\n" \
                        f"👤 Nombre: {nombre.strip()} {apellidos.strip()}\n" \
                        f"🏷️ Cédula: {cedula.strip()}\n" \
                        f"🏢 Dirección: {direccion_grupo.strip() or 'No especificada'}\n" \
                        f"💼 Cargo: {cargo.strip() or 'No especificado'}" + \
                        (f"\n\n{chr(10).join(msg_extra)}" if msg_extra else "")
        else:
            # Manejo de errores específicos de BD
            if "Duplicate entry" in str(error) and "cedula" in str(error):
                return False, f"🚫 Error: La cédula '{cedula.strip()}' ya existe en el sistema"
            else:
                return False, f"🚫 Error al registrar el funcionario: {error}"

    def obtener_todos(self) -> List[Dict]:
        """Obtiene todos los funcionarios activos"""
        query = """
            SELECT f.*, COUNT(v.id) as total_vehiculos
            FROM funcionarios f
            LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
            WHERE f.activo = TRUE
            GROUP BY f.id
            ORDER BY f.apellidos, f.nombre
        """
        return self.db.fetch_all(query)

    def obtener_por_id(self, funcionario_id: int) -> Dict:
        """Obtiene un funcionario por su ID"""
        query = """
            SELECT * FROM funcionarios
            WHERE id = %s AND activo = TRUE
        """
        return self.db.fetch_one(query, (funcionario_id,))

    def obtener_datos_relacionados(self, funcionario_id: int) -> Dict:
        """Obtiene información detallada de todos los datos que serían eliminados"""
        # Obtener vehículos del funcionario
        query_vehiculos = """
            SELECT v.id, v.tipo_vehiculo, v.placa, v.tipo_circulacion,
                   CASE WHEN a.id IS NOT NULL THEN TRUE ELSE FALSE END as tiene_asignacion,
                   p.numero_parqueadero
            FROM vehiculos v
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
            WHERE v.funcionario_id = %s AND v.activo = TRUE
        """
        vehiculos = self.db.fetch_all(query_vehiculos, (funcionario_id,))

        # Obtener parqueaderos que quedarán disponibles
        query_parqueaderos = """
            SELECT DISTINCT p.numero_parqueadero, p.estado
            FROM parqueaderos p
            JOIN asignaciones a ON p.id = a.parqueadero_id
            JOIN vehiculos v ON a.vehiculo_id = v.id
            WHERE v.funcionario_id = %s AND a.activo = TRUE
        """
        parqueaderos_afectados = self.db.fetch_all(query_parqueaderos, (funcionario_id,))

        return {
            'vehiculos': vehiculos,
            'parqueaderos_afectados': parqueaderos_afectados
        }

    def buscar(self, termino: str) -> List[Dict]:
        """Busca funcionarios por cédula, nombre o apellido"""
        query = """
            SELECT * FROM funcionarios
            WHERE activo = TRUE AND (
                cedula LIKE %s OR
                nombre LIKE %s OR
                apellidos LIKE %s
            )
            ORDER BY apellidos, nombre
        """
        termino_like = f"%{termino}%"
        return self.db.fetch_all(query, (termino_like, termino_like, termino_like))

    def actualizar(self, funcionario_id: int, cedula: str, nombre: str, apellidos: str,
                  direccion_grupo: str = "", cargo: str = "", celular: str = "", tarjeta: str = "",
                  permite_compartir: bool = True,
                  pico_placa_solidario: bool = False,
                  discapacidad: bool = False) -> tuple:
        """
        Actualiza los datos de un funcionario

        Args:
            permite_compartir: Si el funcionario permite compartir parqueadero (default: True)
            pico_placa_solidario: Si puede usar parqueadero en días no correspondientes (default: False)
            discapacidad: Si el funcionario tiene condición de discapacidad (default: False)

        Returns:
            tuple: (bool: éxito, str: mensaje de error si existe)
        """
        # Validación 1: Funcionario existe
        funcionario_actual = self.obtener_por_id(funcionario_id)
        if not funcionario_actual:
            return False, f"🔍 Funcionario no encontrado\n\n" \
                         f"❌ No existe un funcionario con ID: {funcionario_id}\n" \
                         f"💡 Verifique que el funcionario no haya sido eliminado"

        # Validación 2: Cédula única (excluyendo el funcionario actual)
        es_unica, mensaje_cedula = self.validar_cedula_unica(cedula, funcionario_id)
        if not es_unica:
            return False, mensaje_cedula

        # Validación 3: Nombre y apellidos
        es_valido, mensaje = ValidadorCampos.validar_nombre(nombre, "Nombre")
        if not es_valido:
            return False, mensaje

        es_valido, mensaje = ValidadorCampos.validar_nombre(apellidos, "Apellidos")
        if not es_valido:
            return False, mensaje

        # Validación 4: Si cambia a "no permite compartir", verificar asignaciones existentes
        es_valido, mensaje = ValidadorAsignacion.validar_cambio_permite_compartir(
            funcionario_id,
            permite_compartir,
            funcionario_actual.get('permite_compartir', True),
            self.db
        )
        if not es_valido:
            return False, mensaje

        query = """
            UPDATE funcionarios
            SET cedula = %s, nombre = %s, apellidos = %s, direccion_grupo = %s,
                cargo = %s, celular = %s, no_tarjeta_proximidad = %s,
                permite_compartir = %s, pico_placa_solidario = %s, discapacidad = %s
            WHERE id = %s
        """
        params = (cedula.strip(), nombre.strip(), apellidos.strip(),
                 direccion_grupo.strip(), cargo.strip(), celular.strip(), tarjeta.strip(),
                 permite_compartir, pico_placa_solidario, discapacidad, funcionario_id)

        exito, error = self.db.execute_query(query, params)

        if exito:
            msg_extra = []
            if not permite_compartir:
                msg_extra.append("🚫 No permite compartir parqueadero (exclusivo)")
            if pico_placa_solidario:
                msg_extra.append("🔄 Pico y placa solidario activado")
            if discapacidad:
                msg_extra.append("♿ Condición de discapacidad registrada")

            return True, f"✅ Funcionario actualizado exitosamente\n\n" \
                        f"👤 Nombre: {nombre.strip()} {apellidos.strip()}\n" \
                        f"🏷️ Cédula: {cedula.strip()}\n" \
                        f"🏢 Dirección: {direccion_grupo.strip() or 'No especificada'}\n" \
                        f"💼 Cargo: {cargo.strip() or 'No especificado'}" + \
                        (f"\n\n{chr(10).join(msg_extra)}" if msg_extra else "")
        else:
            return False, f"🚫 Error al actualizar el funcionario: {error}"

    def eliminar(self, funcionario_id: int) -> Tuple[bool, str]:
        """
        Elimina un funcionario y TODOS sus datos relacionados de forma COMPLETA
        Nueva implementación que garantiza eliminación total, no solo desactivación

        Args:
            funcionario_id (int): ID del funcionario a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje detallado)
        """
        # Verificar que el funcionario existe antes de intentar eliminar
        funcionario = self.obtener_por_id(funcionario_id)
        if not funcionario:
            return False, f"🔍 Funcionario no encontrado\n\n" \
                         f"❌ No existe un funcionario con ID: {funcionario_id}\n" \
                         f"💡 Verifique que el funcionario no haya sido eliminado previamente"

        # Obtener datos relacionados para mostrar resumen
        datos_relacionados = self.obtener_datos_relacionados(funcionario_id)
        vehiculos_count = len(datos_relacionados.get('vehiculos', []))
        parqueaderos_count = len(datos_relacionados.get('parqueaderos_afectados', []))

        exito, mensaje, detalles = self.gestor_eliminacion.eliminar_funcionario_completo(str(funcionario_id))

        if exito:
            return True, f"✅ Funcionario eliminado exitosamente\n\n" \
                        f"👤 Funcionario: {funcionario['nombre']} {funcionario['apellidos']}\n" \
                        f"🏷️ Cédula: {funcionario['cedula']}\n" \
                        f"🚗 Vehículos eliminados: {vehiculos_count}\n" \
                        f"🌐 Espacios liberados: {parqueaderos_count}\n\n" \
                        f"📝 Eliminación en cascada completada"
        else:
            return False, f"🚫 Error en eliminación: {mensaje}"

    def eliminar_por_cedula(self, cedula: str) -> Tuple[bool, str]:
        """
        Elimina un funcionario por su cédula y TODOS sus datos relacionados

        Args:
            cedula (str): Cédula del funcionario a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje detallado)
        """
        exito, mensaje, detalles = self.gestor_eliminacion.eliminar_funcionario_completo(cedula)
        return exito, mensaje

    def obtener_reporte_previa_eliminacion(self, funcionario_id: int) -> str:
        """
        Genera un reporte detallado de lo que se eliminará antes de proceder

        Args:
            funcionario_id (int): ID del funcionario

        Returns:
            str: Reporte detallado de eliminación prevista
        """
        return self.gestor_eliminacion.generar_reporte_previa_eliminacion(str(funcionario_id))

    def verificar_datos_asociados(self, funcionario_id: int) -> Dict:
        """
        Obtiene información completa de todos los datos asociados a un funcionario

        Args:
            funcionario_id (int): ID del funcionario

        Returns:
            Dict: Datos completos del funcionario y elementos asociados
        """
        return self.gestor_eliminacion.obtener_datos_funcionario_completos(str(funcionario_id))