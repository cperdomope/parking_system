-- =====================================================
-- SISTEMA DE GESTIÓN DE PARQUEADERO
-- Tabla de Usuarios para Autenticación
-- VERSION SEGURA CON BCRYPT
-- =====================================================

USE parking_management;

-- =====================================================
-- TABLA: USUARIOS
-- Almacena credenciales de acceso al sistema
-- ⚠️ IMPORTANTE: Las contraseñas se almacenan con hash bcrypt (work factor 12)
-- NUNCA almacenar contraseñas en texto plano
-- =====================================================
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT 'Nombre de usuario único',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hash bcrypt de la contraseña (work factor 12)',
    rol ENUM('Administrador', 'Usuario', 'Invitado') DEFAULT 'Usuario',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE,
    intentos_fallidos INT DEFAULT 0 COMMENT 'Contador de intentos fallidos de login',
    bloqueado_hasta TIMESTAMP NULL COMMENT 'Fecha/hora hasta cuando está bloqueado',
    INDEX idx_username (username),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Usuarios del sistema con autenticación bcrypt';

-- =====================================================
-- INSERTAR USUARIO ADMINISTRADOR POR DEFECTO
-- Username: splaza
-- Password: splaza123*
-- Hash bcrypt generado con work factor 12
-- =====================================================
INSERT INTO usuarios (username, password_hash, rol) VALUES
('splaza', '$2b$12$dn3DwBjpkYwsq.TwXzAOv.gfbRes3F4xXt8xZIXQS6nB6jyCPAcE2', 'Administrador');

-- =====================================================
-- VERIFICAR INSERCIÓN
-- =====================================================
SELECT
    id,
    username,
    rol,
    fecha_creacion,
    activo,
    LEFT(password_hash, 29) as 'bcrypt_hash_preview'
FROM usuarios;

-- =====================================================
-- RESULTADO ESPERADO:
-- +----+----------+-----------------+---------------------+--------+--------------------------+
-- | id | username | rol             | fecha_creacion      | activo | bcrypt_hash_preview      |
-- +----+----------+-----------------+---------------------+--------+--------------------------+
-- |  1 | splaza   | Administrador   | 2025-11-16 ...      |   1    | $2b$12$dn3DwBjpkYwsq.TwX... |
-- +----+----------+-----------------+---------------------+--------+--------------------------+
-- =====================================================
