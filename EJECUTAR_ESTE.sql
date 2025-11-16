-- ========================================
-- MIGRACION ESPECIFICA PARA TU BASE DE DATOS
-- Ejecutar línea por línea en MySQL Workbench
-- ========================================

USE parking_management;

-- ========================================
-- PASO 1: Renombrar "usuario" a "username"
-- ========================================
ALTER TABLE usuarios
CHANGE COLUMN usuario username VARCHAR(50) UNIQUE NOT NULL;

-- Verificar: Debe decir "1 row(s) affected"


-- ========================================
-- PASO 2: Modificar password_hash de VARBINARY a VARCHAR
-- ========================================
ALTER TABLE usuarios
MODIFY COLUMN password_hash VARCHAR(255) NULL;

-- Verificar: Debe decir "1 row(s) affected"


-- ========================================
-- PASO 3: Actualizar con hash bcrypt
-- Contraseña: splaza123*
-- ========================================
UPDATE usuarios
SET password_hash = '$2b$12$dn3DwBjpkYwsq.TwXzAOv.gfbRes3F4xXt8xZIXQS6nB6jyCPAcE2'
WHERE username = 'splaza';

-- Verificar: Debe decir "1 row(s) affected"


-- ========================================
-- PASO 4: ELIMINAR "contraseña" (CRÍTICO)
-- ========================================
ALTER TABLE usuarios
DROP COLUMN contraseña;

-- Verificar: Debe decir "Records: 0  Duplicates: 0  Warnings: 0"


-- ========================================
-- PASO 5: Hacer password_hash obligatorio
-- ========================================
ALTER TABLE usuarios
MODIFY COLUMN password_hash VARCHAR(255) NOT NULL;

-- Verificar: Debe decir "1 row(s) affected"


-- ========================================
-- VERIFICACION FINAL
-- ========================================
DESCRIBE usuarios;

-- DEBE MOSTRAR:
-- - username (NO "usuario")
-- - password_hash VARCHAR(255) NOT NULL (NO "contraseña")
-- - NO debe aparecer "contraseña"


SELECT
    id,
    username,
    rol,
    LEFT(password_hash, 29) as 'hash_bcrypt',
    activo
FROM usuarios;

-- DEBE MOSTRAR:
-- - username: splaza
-- - hash_bcrypt: $2b$12$dn3DwBjpkYwsq.TwX


-- ========================================
-- RESULTADO FINAL ESPERADO:
--
-- Campos eliminados:
-- X contraseña (texto plano)
-- X usuario (renombrado a username)
--
-- Campos correctos:
-- ✓ username VARCHAR(50)
-- ✓ password_hash VARCHAR(255) NOT NULL
-- ✓ Hash bcrypt: $2b$12$...
--
-- Login credentials (sin cambios):
-- Usuario: splaza
-- Contraseña: splaza123*
-- ========================================
