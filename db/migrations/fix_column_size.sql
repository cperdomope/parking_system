-- =====================================================
-- MIGRACIÓN: Aumentar tamaño de columnas direccion_grupo y cargo
-- Fecha: 2025-11-09
-- Descripción: Aumenta VARCHAR(100) a VARCHAR(255) para direccion_grupo
--              y VARCHAR(50) a VARCHAR(255) para cargo
-- =====================================================

USE parking_management;

-- Aumentar tamaño de columna direccion_grupo de VARCHAR(100) a VARCHAR(255)
ALTER TABLE funcionarios
MODIFY COLUMN direccion_grupo VARCHAR(255);

-- Aumentar tamaño de columna cargo de VARCHAR(50) a VARCHAR(255)
ALTER TABLE funcionarios
MODIFY COLUMN cargo VARCHAR(255);

-- Verificar cambios
DESCRIBE funcionarios;

SELECT 'Migración completada exitosamente. Columnas direccion_grupo y cargo ahora soportan hasta 255 caracteres.' AS mensaje;
