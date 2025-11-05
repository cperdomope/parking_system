# -*- coding: utf-8 -*-
"""
Modelo para operaciones CRUD de funcionarios
"""

from typing import Dict, List, Tuple

from ..database.eliminacion_cascada import GestorEliminacionCascada
from ..database.manager import DatabaseManager
from ..utils.validaciones import ValidadorCampos, ValidadorReglasNegocio
from ..utils.validaciones_asignaciones import ValidadorAsignacion


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
            return (
                False,
                f"🚫 Cédula duplicada detectada\n\n"
                f"❌ La cédula '{cedula_clean}' ya está registrada.\n"
                f"👤 Funcionario existente: {existing['nombre']} {existing['apellidos']}\n\n"
                f"💡 Solución: Use una cédula diferente o verifique si ya está registrado.",
            )

        return True, ""

    def crear(
        self,
        cedula: str,
        nombre: str,
        apellidos: str,
        direccion_grupo: str = "",
        cargo: str = "",
        celular: str = "",
        tarjeta: str = "",
        permite_compartir: bool = True,
        pico_placa_solidario: bool = False,
        discapacidad: bool = False,
        tiene_parqueadero_exclusivo: bool = False,
        tiene_carro_hibrido: bool = False,
    ) -> tuple:
        """Crea un nuevo funcionario en la base de datos

        Args:
            permite_compartir: Si el funcionario permite compartir parqueadero (default: True)
            pico_placa_solidario: Si puede usar parqueadero en días no correspondientes (default: False)
            discapacidad: Si el funcionario tiene condición de discapacidad (default: False)
            tiene_parqueadero_exclusivo: Si es directivo con parqueadero exclusivo (hasta 4 vehículos) (default: False)
            tiene_carro_hibrido: Si tiene carro híbrido - uso diario, parqueadero exclusivo (default: False)

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
        permite_compartir = ValidadorReglasNegocio.validar_cargo_permite_compartir(cargo.strip(), permite_compartir)

        # Validación 4: tiene_parqueadero_exclusivo - ELIMINADA LA RESTRICCIÓN DE CARGO
        # Ahora cualquier cargo puede tener parqueadero exclusivo si el usuario lo marca

        query = """
            INSERT INTO funcionarios
            (cedula, nombre, apellidos, direccion_grupo, cargo, celular, no_tarjeta_proximidad,
             permite_compartir, pico_placa_solidario, discapacidad, tiene_parqueadero_exclusivo, tiene_carro_hibrido)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            cedula.strip(),
            nombre.strip(),
            apellidos.strip(),
            direccion_grupo.strip(),
            cargo.strip(),
            celular.strip(),
            tarjeta.strip(),
            permite_compartir,
            pico_placa_solidario,
            discapacidad,
            tiene_parqueadero_exclusivo,
            tiene_carro_hibrido,
        )

        exito, error = self.db.execute_query(query, params)

        if exito:
            msg_extra = []
            if tiene_carro_hibrido:
                msg_extra.append("🌿 Carro híbrido registrado (uso diario, parqueadero exclusivo - incentivo ambiental)")
            elif tiene_parqueadero_exclusivo:
                msg_extra.append("🏢 Parqueadero exclusivo activado (hasta 4 vehículos, sin restricción PAR/IMPAR)")
            elif not permite_compartir:
                msg_extra.append("🚫 No permite compartir parqueadero (exclusivo)")
            if pico_placa_solidario:
                msg_extra.append("🔄 Pico y placa solidario activado")
            if discapacidad:
                msg_extra.append("♿ Condición de discapacidad registrada")

            return (
                True,
                f"✅ Funcionario registrado exitosamente\n\n"
                f"👤 Nombre: {nombre.strip()} {apellidos.strip()}\n"
                f"🏷️ Cédula: {cedula.strip()}\n"
                f"🏢 Dirección: {direccion_grupo.strip() or 'No especificada'}\n"
                f"💼 Cargo: {cargo.strip() or 'No especificado'}"
                + (f"\n\n{chr(10).join(msg_extra)}" if msg_extra else ""),
            )
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

    def obtener_todos_incluyendo_inactivos(self) -> List[Dict]:
        """Obtiene TODOS los funcionarios (activos e inactivos)"""
        query = """
            SELECT f.*, COUNT(v.id) as total_vehiculos
            FROM funcionarios f
            LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
            GROUP BY f.id
            ORDER BY f.activo DESC, f.apellidos, f.nombre
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

        return {"vehiculos": vehiculos, "parqueaderos_afectados": parqueaderos_afectados}

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

    def actualizar(
        self,
        funcionario_id: int,
        cedula: str,
        nombre: str,
        apellidos: str,
        direccion_grupo: str = "",
        cargo: str = "",
        celular: str = "",
        tarjeta: str = "",
        permite_compartir: bool = True,
        pico_placa_solidario: bool = False,
        discapacidad: bool = False,
        tiene_parqueadero_exclusivo: bool = False,
        tiene_carro_hibrido: bool = False,
    ) -> tuple:
        """
        Actualiza los datos de un funcionario

        Args:
            permite_compartir: Si el funcionario permite compartir parqueadero (default: True)
            pico_placa_solidario: Si puede usar parqueadero en días no correspondientes (default: False)
            discapacidad: Si el funcionario tiene condición de discapacidad (default: False)
            tiene_parqueadero_exclusivo: Si es directivo con parqueadero exclusivo (hasta 4 vehículos) (default: False)
            tiene_carro_hibrido: Si tiene carro híbrido - uso diario, parqueadero exclusivo (default: False)

        Returns:
            tuple: (bool: éxito, str: mensaje de error si existe)
        """
        # Validación 1: Funcionario existe
        funcionario_actual = self.obtener_por_id(funcionario_id)
        if not funcionario_actual:
            return (
                False,
                f"🔍 Funcionario no encontrado\n\n"
                f"❌ No existe un funcionario con ID: {funcionario_id}\n"
                f"💡 Verifique que el funcionario no haya sido eliminado",
            )

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
        # NOTA: Esta validación está comentada porque el campo permite_compartir
        # ahora se gestiona automáticamente según los checkboxes activos
        # es_valido, mensaje = ValidadorAsignacion.validar_cambio_permite_compartir(
        #     funcionario_id, permite_compartir, funcionario_actual.get("permite_compartir", True), self.db
        # )
        # if not es_valido:
        #     return False, mensaje

        # Validación 5: tiene_parqueadero_exclusivo solo para directivos
        from ..config.settings import CARGOS_DIRECTIVOS
        cargo_actual = cargo.strip()
        cargo_anterior = funcionario_actual.get("cargo", "")

        # ELIMINADA LA RESTRICCIÓN DE CARGO PARA PARQUEADERO EXCLUSIVO
        # Ahora cualquier cargo puede tener parqueadero exclusivo si está marcado

        query = """
            UPDATE funcionarios
            SET cedula = %s, nombre = %s, apellidos = %s, direccion_grupo = %s,
                cargo = %s, celular = %s, no_tarjeta_proximidad = %s,
                permite_compartir = %s, pico_placa_solidario = %s, discapacidad = %s,
                tiene_parqueadero_exclusivo = %s, tiene_carro_hibrido = %s
            WHERE id = %s
        """
        params = (
            cedula.strip(),
            nombre.strip(),
            apellidos.strip(),
            direccion_grupo.strip(),
            cargo.strip(),
            celular.strip(),
            tarjeta.strip(),
            permite_compartir,
            pico_placa_solidario,
            discapacidad,
            tiene_parqueadero_exclusivo,
            tiene_carro_hibrido,
            funcionario_id,
        )

        exito, error = self.db.execute_query(query, params)

        if exito:
            msg_extra = []
            if tiene_carro_hibrido:
                msg_extra.append("🌿 Carro híbrido registrado (uso diario, parqueadero exclusivo - incentivo ambiental)")
            elif tiene_parqueadero_exclusivo:
                msg_extra.append("🏢 Parqueadero exclusivo activado (hasta 4 vehículos, sin restricción PAR/IMPAR)")
            elif not permite_compartir:
                msg_extra.append("🚫 No permite compartir parqueadero (exclusivo)")
            if pico_placa_solidario:
                msg_extra.append("🔄 Pico y placa solidario activado")
            if discapacidad:
                msg_extra.append("♿ Condición de discapacidad registrada")

            return (
                True,
                f"✅ Funcionario actualizado exitosamente\n\n"
                f"👤 Nombre: {nombre.strip()} {apellidos.strip()}\n"
                f"🏷️ Cédula: {cedula.strip()}\n"
                f"🏢 Dirección: {direccion_grupo.strip() or 'No especificada'}\n"
                f"💼 Cargo: {cargo.strip() or 'No especificado'}"
                + (f"\n\n{chr(10).join(msg_extra)}" if msg_extra else ""),
            )
        else:
            return False, f"🚫 Error al actualizar el funcionario: {error}"

    def eliminar(self, funcionario_id: int) -> Tuple[bool, str]:
        """
        Desactiva un funcionario (borrado lógico) y libera sus recursos asociados
        Marca el funcionario como inactivo, desactiva sus vehículos y libera parqueaderos
        IMPORTANTE: No elimina físicamente de la BD para mantener historial

        Args:
            funcionario_id (int): ID del funcionario a desactivar

        Returns:
            Tuple[bool, str]: (éxito, mensaje detallado)
        """
        from ..core.logger import logger

        # Verificar que el funcionario existe y está activo
        funcionario = self.obtener_por_id(funcionario_id)
        if not funcionario:
            return (
                False,
                f"🔍 Funcionario no encontrado\n\n"
                f"❌ No existe un funcionario activo con ID: {funcionario_id}\n"
                f"💡 Verifique que el funcionario no haya sido desactivado previamente",
            )

        try:
            nombre_completo = f"{funcionario['nombre']} {funcionario['apellidos']}"
            cedula = funcionario['cedula']

            # Obtener datos relacionados para mostrar resumen
            datos_relacionados = self.obtener_datos_relacionados(funcionario_id)
            vehiculos = datos_relacionados.get("vehiculos", [])
            parqueaderos_afectados = datos_relacionados.get("parqueaderos_afectados", [])

            logger.info(f"Iniciando desactivación de funcionario: {nombre_completo} (ID: {funcionario_id})")

            # Obtener IDs de parqueaderos afectados ANTES de eliminar asignaciones
            query_parqueaderos_ids = """
                SELECT DISTINCT a.parqueadero_id
                FROM asignaciones a
                JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE v.funcionario_id = %s AND a.activo = TRUE
            """
            parqueaderos_ids_result = self.db.fetch_all(query_parqueaderos_ids, (funcionario_id,))
            parqueaderos_ids = [p['parqueadero_id'] for p in parqueaderos_ids_result] if parqueaderos_ids_result else []

            # 1. Eliminar asignaciones activas físicamente
            parqueaderos_liberados = 0
            if parqueaderos_afectados:
                query_eliminar_asignaciones = """
                    DELETE FROM asignaciones
                    WHERE vehiculo_id IN (
                        SELECT id FROM vehiculos WHERE funcionario_id = %s
                    ) AND activo = TRUE
                """
                exito_asig, _ = self.db.execute_query(query_eliminar_asignaciones, (funcionario_id,))
                if exito_asig:
                    parqueaderos_liberados = len(parqueaderos_afectados)
                    logger.info(f"Eliminadas {parqueaderos_liberados} asignaciones físicamente")

            # 2. Actualizar estado de parqueaderos a "Disponible"
            if parqueaderos_ids:
                for parqueadero_id in parqueaderos_ids:
                    query_update_estado = """
                        UPDATE parqueaderos
                        SET estado = 'Disponible'
                        WHERE id = %s
                    """
                    self.db.execute_query(query_update_estado, (parqueadero_id,))
                logger.info(f"Actualizados {len(parqueaderos_ids)} parqueaderos a estado 'Disponible'")

            # 3. Eliminar vehículos asociados físicamente
            vehiculos_eliminados = 0
            if vehiculos:
                query_eliminar_vehiculos = """
                    DELETE FROM vehiculos
                    WHERE funcionario_id = %s
                """
                exito_veh, _ = self.db.execute_query(query_eliminar_vehiculos, (funcionario_id,))
                if exito_veh:
                    vehiculos_eliminados = len(vehiculos)
                    logger.info(f"Eliminados {vehiculos_eliminados} vehículos físicamente")

            # 4. Desactivar funcionario (borrado lógico)
            query_desactivar_funcionario = """
                UPDATE funcionarios
                SET activo = FALSE
                WHERE id = %s
            """
            exito_func, error_func = self.db.execute_query(query_desactivar_funcionario, (funcionario_id,))

            if not exito_func:
                logger.error(f"Error al desactivar funcionario {funcionario_id}: {error_func}")
                return (
                    False,
                    f"❌ Error al desactivar funcionario\n\n{error_func}"
                )

            logger.info(f"Funcionario {nombre_completo} desactivado exitosamente")

            # Mensaje de éxito
            mensaje_exito = (
                f"✅ Funcionario desactivado exitosamente\n\n"
                f"👤 Funcionario: {nombre_completo}\n"
                f"🆔 Cédula: {cedula}\n\n"
                f"📋 Resumen de operaciones:\n"
                f"   • Funcionario marcado como INACTIVO\n"
                f"   • Vehículos eliminados de la BD: {vehiculos_eliminados}\n"
                f"   • Asignaciones eliminadas de la BD: {parqueaderos_liberados}\n"
                f"   • Parqueaderos actualizados a 'Disponible': {len(parqueaderos_ids)}\n\n"
                f"⚠️ Los vehículos y asignaciones fueron eliminados permanentemente\n"
                f"💾 El historial del funcionario se mantiene en la base de datos\n"
                f"📊 El funcionario ya no aparecerá en listados activos"
            )

            return (True, mensaje_exito)

        except Exception as e:
            logger.error(f"Error inesperado al desactivar funcionario {funcionario_id}: {e}", exc_info=True)
            return (
                False,
                f"❌ Error inesperado al desactivar funcionario\n\n"
                f"Error: {str(e)}\n"
                f"💡 Consulte los logs para más detalles"
            )

    def eliminar_por_cedula(self, cedula: str) -> Tuple[bool, str]:
        """
        Desactiva un funcionario por su cédula (borrado lógico)

        Args:
            cedula (str): Cédula del funcionario a desactivar

        Returns:
            Tuple[bool, str]: (éxito, mensaje detallado)
        """
        # Buscar funcionario por cédula
        query = "SELECT id FROM funcionarios WHERE cedula = %s AND activo = TRUE"
        funcionario = self.db.fetch_one(query, (cedula,))

        if not funcionario:
            return (
                False,
                f"❌ No se encontró un funcionario activo con cédula: {cedula}"
            )

        # Usar el método eliminar() que ya implementa borrado lógico
        return self.eliminar(funcionario['id'])

    def reactivar(self, funcionario_id: int) -> Tuple[bool, str]:
        """
        Reactiva un funcionario previamente desactivado
        Marca el funcionario y sus vehículos como activos nuevamente

        Args:
            funcionario_id (int): ID del funcionario a reactivar

        Returns:
            Tuple[bool, str]: (éxito, mensaje detallado)
        """
        from ..core.logger import logger

        # Verificar que el funcionario existe y está inactivo
        query = "SELECT * FROM funcionarios WHERE id = %s AND activo = FALSE"
        funcionario = self.db.fetch_one(query, (funcionario_id,))

        if not funcionario:
            return (
                False,
                f"🔍 Funcionario no encontrado\n\n"
                f"❌ No existe un funcionario INACTIVO con ID: {funcionario_id}\n"
                f"💡 Verifique que el funcionario no esté ya activo"
            )

        try:
            nombre_completo = f"{funcionario['nombre']} {funcionario['apellidos']}"
            cedula = funcionario['cedula']

            logger.info(f"Iniciando reactivación de funcionario: {nombre_completo} (ID: {funcionario_id})")

            # 1. Reactivar vehículos asociados
            query_reactivar_vehiculos = """
                UPDATE vehiculos
                SET activo = TRUE
                WHERE funcionario_id = %s AND activo = FALSE
            """
            exito_veh, error_veh = self.db.execute_query(query_reactivar_vehiculos, (funcionario_id,))

            vehiculos_reactivados = 0
            if exito_veh:
                # Contar cuántos vehículos se reactivaron
                query_count = "SELECT COUNT(*) as total FROM vehiculos WHERE funcionario_id = %s AND activo = TRUE"
                result = self.db.fetch_one(query_count, (funcionario_id,))
                vehiculos_reactivados = result['total'] if result else 0
                logger.info(f"Reactivados {vehiculos_reactivados} vehículos")

            # 2. Reactivar funcionario
            query_reactivar_funcionario = """
                UPDATE funcionarios
                SET activo = TRUE
                WHERE id = %s
            """
            exito_func, error_func = self.db.execute_query(query_reactivar_funcionario, (funcionario_id,))

            if not exito_func:
                logger.error(f"Error al reactivar funcionario {funcionario_id}: {error_func}")
                return (
                    False,
                    f"❌ Error al reactivar funcionario\n\n{error_func}"
                )

            logger.info(f"Funcionario {nombre_completo} reactivado exitosamente")

            # Mensaje de éxito
            mensaje_exito = (
                f"✅ Funcionario reactivado exitosamente\n\n"
                f"👤 Funcionario: {nombre_completo}\n"
                f"🆔 Cédula: {cedula}\n\n"
                f"📋 Resumen de operaciones:\n"
                f"   • Funcionario marcado como ACTIVO\n"
                f"   • Vehículos reactivados: {vehiculos_reactivados}\n\n"
                f"✨ El funcionario vuelve a aparecer en los listados\n"
                f"🚗 Sus vehículos están disponibles para asignación"
            )

            return (True, mensaje_exito)

        except Exception as e:
            logger.error(f"Error inesperado al reactivar funcionario {funcionario_id}: {e}", exc_info=True)
            return (
                False,
                f"❌ Error inesperado al reactivar funcionario\n\n"
                f"Error: {str(e)}\n"
                f"💡 Consulte los logs para más detalles"
            )

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
