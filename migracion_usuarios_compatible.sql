-- ========================================
-- MIGRACION USUARIOS - COMPATIBLE MYSQL 5.7+
-- Ejecutar en MySQL Workbench
-- ========================================

USE parking_management;

-- IMPORTANTE: Si alguna query falla con error de columna duplicada o no existente,
-- simplemente continuar con la siguiente query. Eso es normal.

-- ========================================
-- PASO 1: Agregar password_hash
-- (Ignorar si dice "Duplicate column name")
-- ========================================
ALTER TABLE usuarios
ADD COLUMN password_hash VARCHAR(255) NULL
COMMENT 'Hash bcrypt de la contraseña (work factor 12)';

-- ========================================
-- PASO 2: Renombrar usuario a username
-- (Ignorar si dice "Unknown column 'usuario'")
-- ========================================
ALTER TABLE usuarios
CHANGE COLUMN usuario username VARCHAR(50) UNIQUE NOT NULL;

-- ========================================
-- PASO 3: Actualizar hash bcrypt
-- Contraseña: splaza123*
-- ========================================
UPDATE usuarios
SET password_hash = '$2b$12$dn3DwBjpkYwsq.TwXzAOv.gfbRes3F4xXt8xZIXQS6nB6jyCPAcE2'
WHERE username = 'splaza';

-- ========================================
-- PASO 4: Eliminar campo contraseña
-- (Ignorar si dice "Can't DROP 'contraseña'")
-- ========================================
ALTER TABLE usuarios
DROP COLUMN contraseña;

-- ========================================
-- PASO 5: Hacer password_hash obligatorio
-- ========================================
ALTER TABLE usuarios
MODIFY COLUMN password_hash VARCHAR(255) NOT NULL;

-- ========================================
-- VERIFICACION
-- ========================================

-- Ver estructura final
DESCRIBE usuarios;

-- Ver datos (hash debe comenzar con $2b$12$)
SELECT
    id,
    username,
    rol,
    LEFT(password_hash, 29) as 'hash_bcrypt',
    activo
FROM usuarios;

-- ========================================
-- RESULTADO ESPERADO:
--
-- ESTRUCTURA:
-- - Campo "contraseña" NO EXISTE
-- - Campo "password_hash" existe (NOT NULL)
-- - Campo "username" existe
--
-- DATOS:
-- - Hash comienza con: $2b$12$
-- - Login: splaza / splaza123*
-- ========================================
