-- ========================================
-- MIGRACION RAPIDA - TABLA USUARIOS
-- Copiar y pegar en MySQL Workbench
-- ========================================

USE parking_management;

-- 1. Agregar password_hash si no existe
ALTER TABLE usuarios
ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL;

-- 2. Renombrar usuario a username (si aplica)
ALTER TABLE usuarios
CHANGE COLUMN IF EXISTS usuario username VARCHAR(50) UNIQUE NOT NULL;

-- 3. Actualizar con hash bcrypt para splaza (contraseña: splaza123*)
UPDATE usuarios
SET password_hash = '$2b$12$dn3DwBjpkYwsq.TwXzAOv.gfbRes3F4xXt8xZIXQS6nB6jyCPAcE2'
WHERE username = 'splaza';

-- 4. ELIMINAR campo contraseña (CRÍTICO - Texto plano)
ALTER TABLE usuarios
DROP COLUMN IF EXISTS contraseña;

-- 5. Hacer password_hash obligatorio
ALTER TABLE usuarios
MODIFY COLUMN password_hash VARCHAR(255) NOT NULL;

-- ========================================
-- VERIFICACION
-- ========================================

-- Ver estructura (NO debe existir "contraseña")
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
-- Campo "contraseña" eliminado
-- Campo "password_hash" existe (NOT NULL)
-- Hash comienza con: $2b$12$
--
-- Login credentials (sin cambios):
-- Usuario: splaza
-- Contraseña: splaza123*
-- ========================================
