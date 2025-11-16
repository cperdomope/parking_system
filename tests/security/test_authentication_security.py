# -*- coding: utf-8 -*-
"""
Tests de Seguridad: Autenticación y Control de Acceso (CORREGIDO)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import bcrypt
from datetime import datetime, timedelta


class TestPasswordSecurity:
    """Tests de seguridad de contraseñas"""

    def test_password_is_hashed_with_bcrypt(self):
        """CRÍTICO: Verificar que las contraseñas se hashean con bcrypt"""
        from src.auth.auth_manager import AuthManager

        password = "test_password_123"
        hashed = AuthManager.hash_password(password)

        assert isinstance(hashed, bytes)
        assert hashed.startswith(b'$2b$')
        assert len(hashed) == 60

    def test_password_hash_is_unique(self):
        """Verificar que cada hash es único (salt aleatorio)"""
        from src.auth.auth_manager import AuthManager

        password = "same_password"
        hash1 = AuthManager.hash_password(password)
        hash2 = AuthManager.hash_password(password)

        assert hash1 != hash2

    def test_password_verification_works(self):
        """Verificar que la verificación de contraseñas funciona"""
        from src.auth.auth_manager import AuthManager

        password = "correct_password"
        wrong_password = "wrong_password"

        hashed = AuthManager.hash_password(password)

        assert AuthManager.verify_password(password, hashed)
        assert not AuthManager.verify_password(wrong_password, hashed)


class TestBruteForceProtection:
    """Tests de protección contra fuerza bruta"""

    def test_lockout_tracks_failed_attempts(self, mock_db_manager):
        """Verificar que se rastrean los intentos fallidos"""
        from src.auth.auth_manager import AuthManager

        auth = AuthManager()
        auth.db = mock_db_manager

        # Simular usuario inexistente
        mock_db_manager.fetch_one.return_value = None

        # Realizar intento fallido
        success, msg = auth.authenticate("test_user", "wrong_pass")

        assert success is False
        assert "test_user" in auth.failed_attempts
        assert len(auth.failed_attempts["test_user"]) == 1

    def test_account_lockout_after_max_attempts(self, mock_db_manager):
        """Verificar bloqueo después de 5 intentos"""
        from src.auth.auth_manager import AuthManager

        auth = AuthManager()
        auth.db = mock_db_manager
        mock_db_manager.fetch_one.return_value = None

        # Realizar 5 intentos fallidos
        for _ in range(5):
            auth.authenticate("test_user", "wrong")

        # Verificar que está bloqueado
        is_locked, remaining = auth.is_locked_out("test_user")
        assert is_locked is True
        assert remaining > 0

    def test_lockout_expires_after_timeout(self):
        """Verificar que el bloqueo expira"""
        from src.auth.auth_manager import AuthManager
        import time

        auth = AuthManager()
        auth.lockout_duration = 1  # 1 segundo para test

        # Simular intentos antiguos
        old_time = time.time() - 2
        auth.failed_attempts["test_user"] = [old_time] * 5

        # El bloqueo debe haber expirado
        is_locked, remaining = auth.is_locked_out("test_user")
        assert is_locked is False


class TestSessionSecurity:
    """Tests de seguridad de sesiones"""

    def test_logout_clears_session(self):
        """Verificar que logout limpia la sesión"""
        from src.auth.auth_manager import AuthManager

        auth = AuthManager()
        auth.current_user = {"id": 1, "usuario": "test"}

        auth.logout()

        assert auth.current_user is None
