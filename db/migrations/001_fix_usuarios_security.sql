-- =====================================================
-- MIGRACIÓN CRÍTICA DE SEGURIDAD
-- Eliminar campo contraseña en texto plano
-- Agregar campo password_hash con bcrypt
-- =====================================================

USE parking_management;

-- =====================================================
-- PASO 1: Verificar estructura actual
-- =====================================================
DESCRIBE usuarios;

-- =====================================================
-- PASO 2: Agregar password_hash si no existe
-- =====================================================
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL
COMMENT 'Hash bcrypt de la contraseña (work factor 12)';

-- =====================================================
-- PASO 3: Renombrar usuario a username (si existe)
-- =====================================================
ALTER TABLE usuarios
CHANGE COLUMN IF EXISTS usuario username VARCHAR(50) UNIQUE NOT NULL;

-- =====================================================
-- PASO 4: ELIMINAR contraseña en texto plano
-- ⚠️ ADVERTENCIA: Esto borrará las contraseñas actuales
-- Las contraseñas deben ser regeneradas con hash bcrypt
-- =====================================================
ALTER TABLE usuarios
DROP COLUMN IF EXISTS contraseña;

-- =====================================================
-- PASO 5: Actualizar usuario existente con hash bcrypt
-- Contraseña original: splaza123*
-- Hash bcrypt (work factor 12): $2b$12$...
-- =====================================================

-- Hash bcrypt generado para contraseña "splaza123*"
-- Work factor: 12
-- Algoritmo: bcrypt

UPDATE usuarios
SET password_hash = '$2b$12$dn3DwBjpkYwsq.TwXzAOv.gfbRes3F4xXt8xZIXQS6nB6jyCPAcE2'
WHERE username = 'splaza';

-- =====================================================
-- PASO 6: Hacer password_hash obligatorio
-- =====================================================
ALTER TABLE usuarios
MODIFY COLUMN password_hash VARCHAR(255) NOT NULL;

-- =====================================================
-- PASO 7: Verificar estructura final
-- =====================================================
DESCRIBE usuarios;

-- =====================================================
-- PASO 8: Verificar datos
-- =====================================================
SELECT
    id,
    username,
    rol,
    fecha_creacion,
    ultimo_acceso,
    activo,
    LEFT(password_hash, 20) as 'password_hash_preview'
FROM usuarios;

-- =====================================================
-- RESULTADO ESPERADO:
--
-- +----+----------+-----------------+---------------------+--------------+--------+
-- | id | username | rol             | fecha_creacion      | ultimo_acceso| activo |
-- +----+----------+-----------------+---------------------+--------------+--------+
-- |  1 | splaza   | Administrador   | 2025-11-16 ...      | NULL         |   1    |
-- +----+----------+-----------------+---------------------+--------------+--------+
--
-- password_hash debe comenzar con: $2b$12$...
-- =====================================================
