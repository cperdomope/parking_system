-- ============================================================================
-- CORRECCIÓN DE TRIGGERS - Borrado Lógico de Funcionarios
-- ============================================================================
-- Descripción: Actualiza triggers para considerar solo funcionarios activos
-- Fecha: 2025-10-26
-- Versión: 1.0
-- ============================================================================

USE parking_management;

-- Paso 1: Eliminar triggers antiguos
DROP TRIGGER IF EXISTS after_insert_asignacion;
DROP TRIGGER IF EXISTS after_update_asignacion;
DROP TRIGGER IF EXISTS after_delete_asignacion;

DELIMITER $$

-- ============================================================================
-- TRIGGER 1: Actualizar estado al INSERTAR asignación
-- ============================================================================
CREATE TRIGGER after_insert_asignacion
AFTER INSERT ON asignaciones
FOR EACH ROW
BEGIN
    DECLARE count_asignaciones INT;

    -- Si hay estado_manual, usarlo en lugar del automático
    IF NEW.estado_manual IS NOT NULL THEN
        UPDATE parqueaderos
        SET estado = NEW.estado_manual
        WHERE id = NEW.parqueadero_id;
    ELSE
        -- Contar asignaciones activas para este parqueadero
        -- IMPORTANTE: Solo contar vehículos de funcionarios ACTIVOS
        SELECT COUNT(*) INTO count_asignaciones
        FROM asignaciones a
        JOIN vehiculos v ON a.vehiculo_id = v.id
        JOIN funcionarios f ON v.funcionario_id = f.id
        WHERE a.parqueadero_id = NEW.parqueadero_id
        AND a.activo = TRUE
        AND v.activo = TRUE
        AND f.activo = TRUE
        AND v.tipo_vehiculo = 'Carro';

        -- Actualizar estado basado en cantidad
        IF count_asignaciones = 0 THEN
            UPDATE parqueaderos
            SET estado = 'Disponible'
            WHERE id = NEW.parqueadero_id;
        ELSEIF count_asignaciones = 1 THEN
            UPDATE parqueaderos
            SET estado = 'Parcialmente_Asignado'
            WHERE id = NEW.parqueadero_id;
        ELSEIF count_asignaciones >= 2 THEN
            UPDATE parqueaderos
            SET estado = 'Completo'
            WHERE id = NEW.parqueadero_id;
        END IF;
    END IF;
END$$

-- ============================================================================
-- TRIGGER 2: Actualizar estado al MODIFICAR asignación
-- ============================================================================
CREATE TRIGGER after_update_asignacion
AFTER UPDATE ON asignaciones
FOR EACH ROW
BEGIN
    DECLARE count_asignaciones INT;

    -- Si hay estado_manual definido, usarlo
    IF NEW.estado_manual IS NOT NULL THEN
        UPDATE parqueaderos
        SET estado = NEW.estado_manual
        WHERE id = NEW.parqueadero_id;
    ELSEIF OLD.activo = TRUE AND NEW.activo = FALSE THEN
        -- Contar asignaciones activas restantes
        -- IMPORTANTE: Solo contar vehículos de funcionarios ACTIVOS
        SELECT COUNT(*) INTO count_asignaciones
        FROM asignaciones a
        JOIN vehiculos v ON a.vehiculo_id = v.id
        JOIN funcionarios f ON v.funcionario_id = f.id
        WHERE a.parqueadero_id = NEW.parqueadero_id
        AND a.activo = TRUE
        AND v.activo = TRUE
        AND f.activo = TRUE
        AND v.tipo_vehiculo = 'Carro';

        -- Actualizar estado solo si no hay estado_manual en otras asignaciones activas
        IF NOT EXISTS (
            SELECT 1 FROM asignaciones
            WHERE parqueadero_id = NEW.parqueadero_id
            AND activo = TRUE
            AND estado_manual IS NOT NULL
        ) THEN
            IF count_asignaciones = 0 THEN
                UPDATE parqueaderos
                SET estado = 'Disponible'
                WHERE id = NEW.parqueadero_id;
            ELSEIF count_asignaciones = 1 THEN
                UPDATE parqueaderos
                SET estado = 'Parcialmente_Asignado'
                WHERE id = NEW.parqueadero_id;
            ELSEIF count_asignaciones >= 2 THEN
                UPDATE parqueaderos
                SET estado = 'Completo'
                WHERE id = NEW.parqueadero_id;
            END IF;
        END IF;
    END IF;
END$$

-- ============================================================================
-- TRIGGER 3: Actualizar estado al ELIMINAR asignación
-- ============================================================================
CREATE TRIGGER after_delete_asignacion
AFTER DELETE ON asignaciones
FOR EACH ROW
BEGIN
    DECLARE count_asignaciones INT;

    -- Contar asignaciones activas restantes
    -- IMPORTANTE: Solo contar vehículos de funcionarios ACTIVOS
    SELECT COUNT(*) INTO count_asignaciones
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = OLD.parqueadero_id
    AND a.activo = TRUE
    AND v.activo = TRUE
    AND f.activo = TRUE
    AND v.tipo_vehiculo = 'Carro';

    -- Actualizar estado del parqueadero
    IF count_asignaciones = 0 THEN
        UPDATE parqueaderos
        SET estado = 'Disponible'
        WHERE id = OLD.parqueadero_id;
    ELSEIF count_asignaciones = 1 THEN
        UPDATE parqueaderos
        SET estado = 'Parcialmente_Asignado'
        WHERE id = OLD.parqueadero_id;
    ELSEIF count_asignaciones >= 2 THEN
        UPDATE parqueaderos
        SET estado = 'Completo'
        WHERE id = OLD.parqueadero_id;
    END IF;
END$$

DELIMITER ;

-- ============================================================================
-- CORRECCIÓN DE ESTADOS ACTUALES
-- ============================================================================

-- Actualizar todos los parqueaderos basándose en asignaciones actuales
-- Solo considerando funcionarios y vehículos ACTIVOS

UPDATE parqueaderos p
SET estado = (
    CASE
        WHEN (
            SELECT COUNT(*)
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE a.parqueadero_id = p.id
            AND a.activo = TRUE
            AND v.activo = TRUE
            AND f.activo = TRUE
            AND v.tipo_vehiculo = 'Carro'
        ) = 0 THEN 'Disponible'
        WHEN (
            SELECT COUNT(*)
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE a.parqueadero_id = p.id
            AND a.activo = TRUE
            AND v.activo = TRUE
            AND f.activo = TRUE
            AND v.tipo_vehiculo = 'Carro'
        ) = 1 THEN 'Parcialmente_Asignado'
        WHEN (
            SELECT COUNT(*)
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE a.parqueadero_id = p.id
            AND a.activo = TRUE
            AND v.activo = TRUE
            AND f.activo = TRUE
            AND v.tipo_vehiculo = 'Carro'
        ) >= 2 THEN 'Completo'
        ELSE 'Disponible'
    END
);

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

-- Mostrar resumen de estados después de la corrección
SELECT
    'RESUMEN DE ESTADOS DESPUÉS DE CORRECCIÓN' as Reporte;

SELECT
    estado,
    COUNT(*) as cantidad,
    CONCAT(ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM parqueaderos), 2), '%') as porcentaje
FROM parqueaderos
GROUP BY estado
ORDER BY FIELD(estado, 'Disponible', 'Parcialmente_Asignado', 'Completo');

-- Verificar parqueaderos con estado incorrecto (no debería haber ninguno)
SELECT
    'VERIFICACIÓN: Parqueaderos con asignaciones de funcionarios inactivos' as Reporte;

SELECT
    p.id,
    p.numero_parqueadero,
    p.sotano,
    p.estado,
    COUNT(a.id) as asignaciones_inactivas
FROM parqueaderos p
JOIN asignaciones a ON p.id = a.parqueadero_id
JOIN vehiculos v ON a.vehiculo_id = v.id
JOIN funcionarios f ON v.funcionario_id = f.id
WHERE f.activo = FALSE
GROUP BY p.id, p.numero_parqueadero, p.sotano, p.estado;

-- Mostrar triggers creados
SELECT
    'TRIGGERS ACTUALIZADOS' as Reporte;

SHOW TRIGGERS WHERE `Table` = 'asignaciones';

-- ============================================================================
-- FIN DEL SCRIPT
-- ============================================================================

SELECT
    '✅ Script ejecutado exitosamente' as Resultado,
    'Triggers actualizados para considerar solo funcionarios activos' as Detalle;
