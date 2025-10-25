-- =====================================================
-- MIGRACIÓN: Agregar funcionalidad "Carro Híbrido"
-- Fecha: 2025-01-19
-- Descripción: Agrega checkbox para incentivar vehículos híbridos
--              - Permite uso diario (ignora pico y placa)
--              - Parqueadero exclusivo (estado Completo inmediato)
-- =====================================================

USE parking_management;

-- PASO 1: Agregar columna a la tabla funcionarios
ALTER TABLE funcionarios
ADD COLUMN tiene_carro_hibrido BOOLEAN DEFAULT FALSE
COMMENT 'Funcionario con carro híbrido - uso diario, parqueadero exclusivo'
AFTER tiene_parqueadero_exclusivo;

-- PASO 2: Actualizar procedimiento de validación de asignaciones
DROP PROCEDURE IF EXISTS validar_asignacion_parqueadero;

DELIMITER $$

CREATE PROCEDURE validar_asignacion_parqueadero(
    IN p_vehiculo_id INT,
    IN p_parqueadero_id INT,
    OUT es_valido BOOLEAN,
    OUT mensaje_error VARCHAR(500)
)
BEGIN
    DECLARE v_tipo_vehiculo VARCHAR(20);
    DECLARE v_tipo_circulacion VARCHAR(10);
    DECLARE v_funcionario_id INT;
    DECLARE v_cargo VARCHAR(100);
    DECLARE v_pico_placa_solidario BOOLEAN;
    DECLARE v_discapacidad BOOLEAN;
    DECLARE v_permite_compartir BOOLEAN;
    DECLARE v_tiene_parqueadero_exclusivo BOOLEAN;
    DECLARE v_tiene_carro_hibrido BOOLEAN;
    DECLARE v_estado_parqueadero VARCHAR(50);
    DECLARE v_count_asignaciones_existentes INT;
    DECLARE v_ocupante_tipo_circulacion VARCHAR(10);
    DECLARE v_ocupante_permite_compartir BOOLEAN;
    DECLARE v_ocupante_tiene_exclusivo BOOLEAN;
    DECLARE v_ocupante_tiene_hibrido BOOLEAN;

    -- Inicializar valores por defecto
    SET es_valido = FALSE;
    SET mensaje_error = '';

    -- Obtener información del vehículo y funcionario
    SELECT
        v.tipo_vehiculo,
        v.tipo_circulacion,
        v.funcionario_id,
        f.cargo,
        f.pico_placa_solidario,
        f.discapacidad,
        f.permite_compartir,
        f.tiene_parqueadero_exclusivo,
        f.tiene_carro_hibrido
    INTO
        v_tipo_vehiculo,
        v_tipo_circulacion,
        v_funcionario_id,
        v_cargo,
        v_pico_placa_solidario,
        v_discapacidad,
        v_permite_compartir,
        v_tiene_parqueadero_exclusivo,
        v_tiene_carro_hibrido
    FROM vehiculos v
    INNER JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE v.id = p_vehiculo_id AND v.activo = TRUE;

    -- Obtener estado del parqueadero y número de asignaciones
    SELECT estado, COUNT(a.id)
    INTO v_estado_parqueadero, v_count_asignaciones_existentes
    FROM parqueaderos p
    LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
    WHERE p.id = p_parqueadero_id
    GROUP BY p.id, p.estado;

    -- ========== VALIDACIÓN 1: CARRO HÍBRIDO (NUEVA LÓGICA) ==========
    IF v_tiene_carro_hibrido = TRUE THEN
        -- Carro híbrido debe tener parqueadero exclusivo
        -- No se puede compartir con nadie
        IF v_count_asignaciones_existentes > 0 THEN
            SET mensaje_error = 'CARRO HÍBRIDO: El parqueadero ya está ocupado. Los carros híbridos requieren parqueadero exclusivo.';
            SET es_valido = FALSE;
        ELSE
            -- Parqueadero disponible para carro híbrido
            SET es_valido = TRUE;
        END IF;
        LEAVE proc_label;
    END IF;

    -- Verificar si el parqueadero ya está ocupado por un carro híbrido
    IF v_count_asignaciones_existentes > 0 THEN
        SELECT f.tiene_carro_hibrido
        INTO v_ocupante_tiene_hibrido
        FROM asignaciones a
        INNER JOIN vehiculos v ON a.vehiculo_id = v.id
        INNER JOIN funcionarios f ON v.funcionario_id = f.id
        WHERE a.parqueadero_id = p_parqueadero_id AND a.activo = TRUE
        LIMIT 1;

        IF v_ocupante_tiene_hibrido = TRUE THEN
            SET mensaje_error = 'El parqueadero está ocupado por un CARRO HÍBRIDO (uso exclusivo). Debe seleccionar otro espacio.';
            SET es_valido = FALSE;
            LEAVE proc_label;
        END IF;
    END IF;

    -- ========== VALIDACIÓN 2: EXCLUSIVO DIRECTIVO (hasta 4 vehículos) ==========
    IF v_tiene_parqueadero_exclusivo = TRUE AND v_cargo IN ('Director', 'Coordinador', 'Asesor') THEN
        -- Validar que no exceda 4 vehículos
        IF v_count_asignaciones_existentes >= 4 THEN
            SET mensaje_error = 'EXCLUSIVO DIRECTIVO: Ya tiene 4 vehículos asignados (máximo permitido). Debe liberar un espacio primero.';
            SET es_valido = FALSE;
        ELSE
            -- Validar que todos los vehículos pertenezcan al mismo funcionario
            IF EXISTS (
                SELECT 1 FROM asignaciones a
                INNER JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE a.parqueadero_id = p_parqueadero_id
                  AND a.activo = TRUE
                  AND v.funcionario_id != v_funcionario_id
            ) THEN
                SET mensaje_error = 'EXCLUSIVO DIRECTIVO: Este parqueadero ya está asignado a otro funcionario.';
                SET es_valido = FALSE;
            ELSE
                SET es_valido = TRUE;
            END IF;
        END IF;
        LEAVE proc_label;
    END IF;

    -- ========== VALIDACIÓN 3: PARQUEADERO NO COMPARTIDO (permite_compartir = FALSE) ==========
    IF v_permite_compartir = FALSE THEN
        IF v_count_asignaciones_existentes > 0 THEN
            SET mensaje_error = 'NO COMPARTIR: El funcionario tiene marcado "No permite compartir" pero el parqueadero ya está ocupado.';
            SET es_valido = FALSE;
        ELSE
            SET es_valido = TRUE;
        END IF;
        LEAVE proc_label;
    END IF;

    -- Verificar si el ocupante actual no permite compartir
    IF v_count_asignaciones_existentes > 0 THEN
        SELECT f.permite_compartir, f.tiene_parqueadero_exclusivo
        INTO v_ocupante_permite_compartir, v_ocupante_tiene_exclusivo
        FROM asignaciones a
        INNER JOIN vehiculos v ON a.vehiculo_id = v.id
        INNER JOIN funcionarios f ON v.funcionario_id = f.id
        WHERE a.parqueadero_id = p_parqueadero_id AND a.activo = TRUE
        LIMIT 1;

        IF v_ocupante_permite_compartir = FALSE OR v_ocupante_tiene_exclusivo = TRUE THEN
            SET mensaje_error = 'El parqueadero está ocupado por un funcionario con PARQUEADERO EXCLUSIVO (no compartido).';
            SET es_valido = FALSE;
            LEAVE proc_label;
        END IF;
    END IF;

    -- ========== VALIDACIÓN 4: EXCLUSIVO DIRECTIVO (ocupante actual) ==========
    IF v_tiene_parqueadero_exclusivo = TRUE AND v_cargo IN ('Director', 'Coordinador', 'Asesor') THEN
        IF v_count_asignaciones_existentes >= 4 THEN
            SET mensaje_error = 'EXCLUSIVO DIRECTIVO: El parqueadero ya tiene 4 vehículos asignados (límite alcanzado).';
            SET es_valido = FALSE;
        ELSE
            SET es_valido = TRUE;
        END IF;
        LEAVE proc_label;
    END IF;

    -- ========== VALIDACIÓN 5: PICO Y PLACA (funcionarios regulares) ==========
    IF v_tipo_vehiculo = 'Carro' THEN
        IF v_estado_parqueadero = 'Disponible' THEN
            SET es_valido = TRUE;
        ELSIF v_estado_parqueadero = 'Parcialmente_Asignado' THEN
            -- Verificar compatibilidad de tipo de circulación (PAR/IMPAR)
            SELECT v2.tipo_circulacion
            INTO v_ocupante_tipo_circulacion
            FROM asignaciones a
            INNER JOIN vehiculos v2 ON a.vehiculo_id = v2.id
            WHERE a.parqueadero_id = p_parqueadero_id AND a.activo = TRUE
            LIMIT 1;

            -- Permitir si tiene pico y placa solidario
            IF v_pico_placa_solidario = TRUE THEN
                SET es_valido = TRUE;
            ELSIF v_tipo_circulacion = v_ocupante_tipo_circulacion THEN
                SET mensaje_error = CONCAT('PICO Y PLACA: Incompatible. El parqueadero ya tiene un vehículo ',
                                          v_ocupante_tipo_circulacion, '. Su vehículo también es ',
                                          v_tipo_circulacion, '. Debe buscar uno con circulación opuesta.');
                SET es_valido = FALSE;
            ELSE
                SET es_valido = TRUE;
            END IF;
        ELSE
            SET mensaje_error = 'El parqueadero está COMPLETO. No hay espacio disponible.';
            SET es_valido = FALSE;
        END IF;
    ELSE
        -- Motos y bicicletas
        IF v_estado_parqueadero = 'Completo' THEN
            SET mensaje_error = 'El parqueadero está COMPLETO.';
            SET es_valido = FALSE;
        ELSE
            SET es_valido = TRUE;
        END IF;
    END IF;

END$$

DELIMITER ;

-- PASO 3: Actualizar trigger para marcar parqueadero como COMPLETO si es carro híbrido
DROP TRIGGER IF EXISTS after_insert_asignacion;

DELIMITER $$

CREATE TRIGGER after_insert_asignacion
AFTER INSERT ON asignaciones
FOR EACH ROW
BEGIN
    DECLARE v_count_asignaciones INT;
    DECLARE v_tiene_hibrido BOOLEAN;
    DECLARE v_tiene_exclusivo BOOLEAN;
    DECLARE v_cargo VARCHAR(100);

    -- Verificar si es carro híbrido
    SELECT f.tiene_carro_hibrido, f.tiene_parqueadero_exclusivo, f.cargo
    INTO v_tiene_hibrido, v_tiene_exclusivo, v_cargo
    FROM vehiculos v
    INNER JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE v.id = NEW.vehiculo_id;

    -- Si es carro híbrido, marcar parqueadero como COMPLETO inmediatamente
    IF v_tiene_hibrido = TRUE THEN
        UPDATE parqueaderos
        SET estado = 'Completo'
        WHERE id = NEW.parqueadero_id;
    ELSE
        -- Lógica normal para otros casos
        SELECT COUNT(*) INTO v_count_asignaciones
        FROM asignaciones
        WHERE parqueadero_id = NEW.parqueadero_id AND activo = TRUE;

        IF v_tiene_exclusivo = TRUE AND v_cargo IN ('Director', 'Coordinador', 'Asesor') THEN
            -- Directivo: Completo solo cuando llega a 4 vehículos
            IF v_count_asignaciones >= 4 THEN
                UPDATE parqueaderos SET estado = 'Completo' WHERE id = NEW.parqueadero_id;
            ELSIF v_count_asignaciones >= 1 THEN
                UPDATE parqueaderos SET estado = 'Parcialmente_Asignado' WHERE id = NEW.parqueadero_id;
            END IF;
        ELSE
            -- Funcionarios regulares: Completo con 2 vehículos
            IF v_count_asignaciones >= 2 THEN
                UPDATE parqueaderos SET estado = 'Completo' WHERE id = NEW.parqueadero_id;
            ELSIF v_count_asignaciones = 1 THEN
                UPDATE parqueaderos SET estado = 'Parcialmente_Asignado' WHERE id = NEW.parqueadero_id;
            END IF;
        END IF;
    END IF;
END$$

DELIMITER ;

-- PASO 4: Actualizar trigger after_delete_asignacion
DROP TRIGGER IF EXISTS after_delete_asignacion;

DELIMITER $$

CREATE TRIGGER after_delete_asignacion
AFTER DELETE ON asignaciones
FOR EACH ROW
BEGIN
    DECLARE v_count_asignaciones INT;
    DECLARE v_tiene_exclusivo BOOLEAN DEFAULT FALSE;
    DECLARE v_cargo VARCHAR(100);

    SELECT COUNT(*) INTO v_count_asignaciones
    FROM asignaciones
    WHERE parqueadero_id = OLD.parqueadero_id AND activo = TRUE;

    -- Verificar si algún ocupante restante es directivo
    IF v_count_asignaciones > 0 THEN
        SELECT f.tiene_parqueadero_exclusivo, f.cargo
        INTO v_tiene_exclusivo, v_cargo
        FROM asignaciones a
        INNER JOIN vehiculos v ON a.vehiculo_id = v.id
        INNER JOIN funcionarios f ON v.funcionario_id = f.id
        WHERE a.parqueadero_id = OLD.parqueadero_id AND a.activo = TRUE
        LIMIT 1;
    END IF;

    IF v_count_asignaciones = 0 THEN
        UPDATE parqueaderos SET estado = 'Disponible' WHERE id = OLD.parqueadero_id;
    ELSIF v_tiene_exclusivo = TRUE AND v_cargo IN ('Director', 'Coordinador', 'Asesor') THEN
        -- Directivo: solo Completo con 4 vehículos
        IF v_count_asignaciones >= 4 THEN
            UPDATE parqueaderos SET estado = 'Completo' WHERE id = OLD.parqueadero_id;
        ELSE
            UPDATE parqueaderos SET estado = 'Parcialmente_Asignado' WHERE id = OLD.parqueadero_id;
        END IF;
    ELSE
        -- Regular: Completo con 2 vehículos
        IF v_count_asignaciones >= 2 THEN
            UPDATE parqueaderos SET estado = 'Completo' WHERE id = OLD.parqueadero_id;
        ELSE
            UPDATE parqueaderos SET estado = 'Parcialmente_Asignado' WHERE id = OLD.parqueadero_id;
        END IF;
    END IF;
END$$

DELIMITER ;

-- PASO 5: Verificar la migración
SELECT 'Migracion completada exitosamente' AS resultado;
SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_DEFAULT, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'parking_management'
  AND TABLE_NAME = 'funcionarios'
  AND COLUMN_NAME = 'tiene_carro_hibrido';
