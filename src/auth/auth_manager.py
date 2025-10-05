# -*- coding: utf-8 -*-
"""
Manejador de autenticación para el sistema de gestión de parqueadero
"""

from typing import Optional, Dict
from datetime import datetime
from ..database.manager import DatabaseManager


class AuthManager:
    """
    Clase para manejar la autenticación de usuarios
    """

    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None

    def authenticate(self, usuario: str, contraseña: str) -> bool:
        """
        Autentica un usuario con sus credenciales

        Args:
            usuario: Nombre de usuario
            contraseña: Contraseña del usuario

        Returns:
            bool: True si la autenticación es exitosa, False en caso contrario
        """
        try:
            query = """
            SELECT id, usuario, rol, activo
            FROM usuarios
            WHERE usuario = %s AND contraseña = %s AND activo = TRUE
            """

            # Usar fetch_one para obtener un solo resultado
            result = self.db.fetch_one(query, (usuario, contraseña))

            if result:
                self.current_user = {
                    'id': result['id'],
                    'usuario': result['usuario'],
                    'rol': result['rol'],
                    'activo': result['activo']
                }

                # Actualizar último acceso
                self._update_last_access(self.current_user['id'])

                return True
            else:
                return False

        except Exception as e:
            print(f"Error en autenticación: {e}")
            return False

    def _update_last_access(self, user_id: int):
        """
        Actualiza la fecha del último acceso del usuario

        Args:
            user_id: ID del usuario
        """
        try:
            query = "UPDATE usuarios SET ultimo_acceso = %s WHERE id = %s"
            success, error = self.db.execute_query(query, (datetime.now(), user_id))
            if not success:
                print(f"Error actualizando último acceso: {error}")
        except Exception as e:
            print(f"Error actualizando último acceso: {e}")

    def logout(self):
        """
        Cierra la sesión del usuario actual
        """
        self.current_user = None

    def get_current_user(self) -> Optional[Dict]:
        """
        Obtiene la información del usuario actual

        Returns:
            Dict: Información del usuario actual o None si no hay sesión activa
        """
        return self.current_user

    def is_authenticated(self) -> bool:
        """
        Verifica si hay un usuario autenticado

        Returns:
            bool: True si hay un usuario autenticado, False en caso contrario
        """
        return self.current_user is not None