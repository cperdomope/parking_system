-- ============================================================
-- Migración: Mejorar mensajes de error de excepciones
-- Fecha: 2025-11-07
-- Descripción: Actualiza los mensajes de error del procedimiento
--              asignar_vehiculo_a_parqueadero para que sean más
--              claros y específicos sobre las restricciones de
--              funcionarios con excepciones.
-- ============================================================

USE parking_management;

-- Eliminar el procedimiento existente
DROP PROCEDURE IF EXISTS asignar_vehiculo_a_parqueadero;

-- Recrear el procedimiento con mensajes mejorados
DELIMITER //

CREATE PROCEDURE asignar_vehiculo_a_parqueadero(
    IN p_vehiculo_id INT,
    IN p_parqueadero_id INT,
    IN p_observaciones TEXT
)
BEGIN
    DECLARE v_tipo_vehiculo VARCHAR(20);
    DECLARE v_tipo_circulacion VARCHAR(10);
    DECLARE v_count_asignaciones_existentes INT;
    DECLARE v_count_mismo_tipo INT;
    DECLARE v_funcionario_id INT;
    DECLARE v_cargo VARCHAR(50);
    DECLARE v_permite_compartir BOOLEAN;
    DECLARE v_tiene_parqueadero_exclusivo BOOLEAN;
    DECLARE v_pico_placa_solidario BOOLEAN;
    DECLARE v_ocupante_permite_compartir BOOLEAN;
    DECLARE v_ocupante_tiene_exclusivo BOOLEAN;
    DECLARE v_mensaje VARCHAR(500);

    -- Obtener datos del vehículo
    SELECT v.tipo_vehiculo, v.tipo_circulacion, v.funcionario_id,
           f.cargo, f.permite_compartir, f.tiene_parqueadero_exclusivo,
           f.pico_placa_solidario
    INTO v_tipo_vehiculo, v_tipo_circulacion, v_funcionario_id,
         v_cargo, v_permite_compartir, v_tiene_parqueadero_exclusivo,
         v_pico_placa_solidario
    FROM vehiculos v
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE v.id = p_vehiculo_id;

    -- Contar vehículos ya asignados en el parqueadero (SOLO CARROS, ignorar motos/bicicletas)
    SELECT COUNT(*) INTO v_count_asignaciones_existentes
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    WHERE a.parqueadero_id = p_parqueadero_id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro';

    -- =====================================================
    -- LÓGICA ESPECIAL PARA DIRECTIVOS CON PARQUEADERO EXCLUSIVO
    -- =====================================================
    IF v_tiene_parqueadero_exclusivo = TRUE THEN
        -- Continuar con la asignación normal (omite validaciones de pico y placa)
    ELSE
        -- VALIDACIONES NORMALES (para funcionarios sin parqueadero exclusivo)

        -- VALIDACIÓN 1: Si el funcionario NO permite compartir y ya hay vehículos en el parqueadero
        -- IMPORTANTE: Solo validar si NO es directivo exclusivo
        IF v_permite_compartir = FALSE AND v_count_asignaciones_existentes > 0 AND v_tiene_parqueadero_exclusivo = FALSE THEN
            SET v_mensaje = 'Funcionario con tipo de excepción NO permite compartir espacio.\n\nEste parqueadero ya está ocupado.\n\nSolución: Seleccione un parqueadero disponible (sin vehículos asignados).';
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_mensaje;
        END IF;

        -- VALIDACIÓN 2: Si ya hay vehículos, verificar si algún ocupante NO permite compartir o tiene exclusivo
        IF v_count_asignaciones_existentes > 0 THEN
            SELECT f.permite_compartir, f.tiene_parqueadero_exclusivo, v.funcionario_id
            INTO v_ocupante_permite_compartir, v_ocupante_tiene_exclusivo, @ocupante_funcionario_id
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE a.parqueadero_id = p_parqueadero_id
            AND a.activo = TRUE
            LIMIT 1;

            -- Solo bloquear si el ocupante tiene exclusivo Y es un funcionario DIFERENTE
            IF (v_ocupante_permite_compartir = FALSE OR v_ocupante_tiene_exclusivo = TRUE) AND @ocupante_funcionario_id != v_funcionario_id THEN
                SET v_mensaje = 'Este parqueadero está ocupado por un funcionario con tipo de excepción.\n\nNo se permite compartir este espacio.\n\nSolución: Seleccione otro parqueadero disponible.';
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_mensaje;
            END IF;
        END IF;

        -- VALIDACIÓN 3: Para carros, verificar tipo de circulación (solo si NO tiene pico_placa_solidario)
        IF v_tipo_vehiculo = 'Carro' AND v_tipo_circulacion != 'N/A' THEN
            IF v_pico_placa_solidario = FALSE THEN
                -- Aplicar restricción PAR/IMPAR normal
                SELECT COUNT(*) INTO v_count_mismo_tipo
                FROM asignaciones a
                JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE a.parqueadero_id = p_parqueadero_id
                AND a.activo = TRUE
                AND v.tipo_circulacion = v_tipo_circulacion;

                IF v_count_mismo_tipo > 0 THEN
                    SET v_mensaje = CONCAT('Ya existe un vehículo ', v_tipo_circulacion, ' en este parqueadero. Active "Pico y placa solidario" para compartir.');
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_mensaje;
                END IF;
            END IF;
            -- Si pico_placa_solidario = TRUE, se permite asignar sin verificar PAR/IMPAR
        END IF;
    END IF;

    -- Desactivar asignaciones previas del vehículo
    UPDATE asignaciones
    SET activo = FALSE, fecha_fin_asignacion = NOW()
    WHERE vehiculo_id = p_vehiculo_id AND activo = TRUE;

    -- =====================================================
    -- INSERCIÓN CON LÓGICA ESPECIAL
    -- CAMBIO v2.0.5: Motos y Bicicletas SIEMPRE marcan como Completo
    -- =====================================================

    -- Crear nueva asignación
    INSERT INTO asignaciones (vehiculo_id, parqueadero_id, fecha_asignacion, activo, observaciones)
    VALUES (p_vehiculo_id, p_parqueadero_id, NOW(), TRUE, p_observaciones);

    -- Actualizar estado del parqueadero basado en el tipo de vehículo
    IF v_tipo_vehiculo IN ('Moto', 'Bicicleta') THEN
        -- CAMBIO v2.0.5: Motos y bicicletas SIEMPRE marcan como Completo
        UPDATE parqueaderos
        SET estado = 'Completo'
        WHERE id = p_parqueadero_id;
    ELSE
        -- CARROS: Aplicar lógica normal de conteo
        -- Recalcular cuántos carros hay después de esta asignación
        SELECT COUNT(*) INTO v_count_asignaciones_existentes
        FROM asignaciones a
        JOIN vehiculos v ON a.vehiculo_id = v.id
        WHERE a.parqueadero_id = p_parqueadero_id
        AND a.activo = TRUE
        AND v.tipo_vehiculo = 'Carro';

        -- Actualizar estado según cantidad de carros
        IF v_count_asignaciones_existentes >= 4 THEN
            UPDATE parqueaderos SET estado = 'Completo' WHERE id = p_parqueadero_id;
        ELSEIF v_count_asignaciones_existentes > 0 THEN
            UPDATE parqueaderos SET estado = 'Parcial' WHERE id = p_parqueadero_id;
        ELSE
            UPDATE parqueaderos SET estado = 'Disponible' WHERE id = p_parqueadero_id;
        END IF;
    END IF;
END //

DELIMITER ;

-- Verificar que el procedimiento se creó correctamente
SELECT 'Procedimiento asignar_vehiculo_a_parqueadero actualizado correctamente' AS resultado;
