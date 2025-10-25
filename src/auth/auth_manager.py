# -*- coding: utf-8 -*-
"""
Manejador de autenticación para el sistema de gestión de parqueadero
Versión 2.0 - Con seguridad mejorada (bcrypt + protección fuerza bruta)
"""

import time
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional, Tuple

import bcrypt

from ..database.manager import DatabaseManager

# Configurar logging
logger = logging.getLogger('auth_manager')


class AuthManager:
    """
    Clase para manejar la autenticación de usuarios con seguridad mejorada

    Características de seguridad:
    - Hash de contraseñas con bcrypt
    - Protección contra ataques de fuerza bruta
    - Logging de eventos de seguridad
    - Bloqueo temporal tras intentos fallidos
    """

    def __init__(self):
        self.db = DatabaseManager()
        self.current_user = None

        # Protección contra fuerza bruta
        self.failed_attempts = defaultdict(list)  # {username: [timestamp1, timestamp2, ...]}
        self.lockout_duration = 900  # 15 minutos en segundos
        self.max_attempts = 5  # Máximo de intentos fallidos antes del bloqueo

    def is_locked_out(self, usuario: str) -> Tuple[bool, int]:
        """
        Verifica si un usuario está bloqueado por intentos fallidos

        Args:
            usuario: Nombre de usuario

        Returns:
            Tuple[bool, int]: (está_bloqueado, segundos_restantes)
        """
        if usuario not in self.failed_attempts:
            return False, 0

        now = time.time()

        # Limpiar intentos antiguos (fuera del período de bloqueo)
        recent_attempts = [
            t for t in self.failed_attempts[usuario]
            if now - t < self.lockout_duration
        ]
        self.failed_attempts[usuario] = recent_attempts

        # Verificar si está bloqueado
        if len(recent_attempts) >= self.max_attempts:
            oldest_attempt = min(recent_attempts)
            remaining_seconds = int(self.lockout_duration - (now - oldest_attempt))
            return True, remaining_seconds

        return False, 0

    def authenticate(self, usuario: str, contraseña: str) -> Tuple[bool, str]:
        """
        Autentica un usuario con sus credenciales usando bcrypt

        Args:
            usuario: Nombre de usuario
            contraseña: Contraseña del usuario (texto plano)

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Verificar si está bloqueado
            is_locked, remaining = self.is_locked_out(usuario)
            if is_locked:
                minutes = remaining // 60
                seconds = remaining % 60
                msg = f"Cuenta bloqueada. Intente nuevamente en {minutes}:{seconds:02d}"
                logger.warning(f"LOGIN_BLOCKED | User: {usuario} | Remaining: {remaining}s")
                return False, msg

            # Consultar usuario y hash de contraseña
            query = """
            SELECT id, usuario, password_hash, rol, activo
            FROM usuarios
            WHERE usuario = %s AND activo = TRUE
            """

            result = self.db.fetch_one(query, (usuario,))

            if not result:
                # Usuario no existe o está inactivo
                self._register_failed_attempt(usuario)
                attempts_left = self.max_attempts - len(self.failed_attempts[usuario])
                logger.warning(f"LOGIN_FAILED | User: {usuario} | Reason: User not found")
                return False, f"Credenciales inválidas. Intentos restantes: {attempts_left}"

            password_hash = result["password_hash"]

            # Verificar contraseña con bcrypt
            if bcrypt.checkpw(contraseña.encode('utf-8'), bytes(password_hash)):
                # Login exitoso
                self.current_user = {
                    "id": result["id"],
                    "usuario": result["usuario"],
                    "rol": result["rol"],
                    "activo": result["activo"],
                }

                # Limpiar intentos fallidos
                if usuario in self.failed_attempts:
                    self.failed_attempts[usuario].clear()

                # Actualizar último acceso
                self._update_last_access(self.current_user["id"])

                logger.info(f"LOGIN_SUCCESS | User: {usuario} | ID: {self.current_user['id']}")
                return True, "Inicio de sesión exitoso"
            else:
                # Contraseña incorrecta
                self._register_failed_attempt(usuario)
                attempts_left = self.max_attempts - len(self.failed_attempts[usuario])
                logger.warning(f"LOGIN_FAILED | User: {usuario} | Reason: Invalid password")
                return False, f"Credenciales inválidas. Intentos restantes: {attempts_left}"

        except Exception as e:
            logger.error(f"LOGIN_ERROR | User: {usuario} | Error: {e}", exc_info=True)
            return False, f"Error en autenticación: {str(e)}"

    def _register_failed_attempt(self, usuario: str):
        """
        Registra un intento fallido de login

        Args:
            usuario: Nombre de usuario
        """
        self.failed_attempts[usuario].append(time.time())

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
                logger.error(f"Error actualizando último acceso: {error}")
        except Exception as e:
            logger.error(f"Error actualizando último acceso: {e}")

    def logout(self):
        """
        Cierra la sesión del usuario actual
        """
        if self.current_user:
            logger.info(f"LOGOUT | User: {self.current_user['usuario']}")
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

    @staticmethod
    def hash_password(password: str) -> bytes:
        """
        Genera un hash seguro de la contraseña usando bcrypt

        Args:
            password: Contraseña en texto plano

        Returns:
            bytes: Hash bcrypt de la contraseña

        Ejemplo:
            >>> password_hash = AuthManager.hash_password("mi_contraseña_segura")
            >>> # Guardar password_hash en la base de datos
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def verify_password(password: str, password_hash: bytes) -> bool:
        """
        Verifica si una contraseña coincide con su hash

        Args:
            password: Contraseña en texto plano
            password_hash: Hash bcrypt almacenado

        Returns:
            bool: True si la contraseña es correcta, False en caso contrario

        Ejemplo:
            >>> stored_hash = user.password_hash
            >>> if AuthManager.verify_password("intento_password", stored_hash):
            ...     print("Contraseña correcta")
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)
