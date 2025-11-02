-- =====================================================
-- SISTEMA DE GESTIÓN DE PARQUEADERO
-- Base de Datos MySQL - Esquema Completo
-- =====================================================

-- Eliminar base de datos si existe y crear nueva
DROP DATABASE IF EXISTS parking_management;
CREATE DATABASE parking_management;
USE parking_management;

-- =====================================================
-- TABLA 1: FUNCIONARIOS
-- Almacena información de empleados
-- =====================================================
CREATE TABLE funcionarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL,
    direccion_grupo VARCHAR(100),
    cargo VARCHAR(50),
    celular VARCHAR(20),
    no_tarjeta_proximidad VARCHAR(30),
    permite_compartir BOOLEAN DEFAULT TRUE,
    pico_placa_solidario BOOLEAN DEFAULT FALSE,
    discapacidad BOOLEAN DEFAULT FALSE,
    tiene_parqueadero_exclusivo BOOLEAN DEFAULT FALSE COMMENT 'Permite hasta 4 vehículos sin restricción PAR/IMPAR (directivos)',
    tiene_carro_hibrido BOOLEAN DEFAULT FALSE COMMENT 'Carro híbrido - uso diario, parqueadero exclusivo (incentivo ambiental)',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    INDEX idx_cedula (cedula),
    INDEX idx_nombre_completo (nombre, apellidos),
    INDEX idx_cargo (cargo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- TABLA 2: VEHICULOS
-- Almacena información de vehículos
-- =====================================================
CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    funcionario_id INT NOT NULL,
    tipo_vehiculo ENUM('Carro', 'Moto', 'Bicicleta') NOT NULL,
    placa VARCHAR(10) UNIQUE NULL,  -- NULL permitido para bicicletas sin placa
    ultimo_digito CHAR(1),
    tipo_circulacion ENUM('PAR', 'IMPAR', 'N/A') DEFAULT 'N/A',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE CASCADE,
    INDEX idx_placa (placa),
    INDEX idx_tipo_circulacion (tipo_circulacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- TABLA 3: PARQUEADEROS
-- Define los 200 espacios disponibles
-- =====================================================
CREATE TABLE parqueaderos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_parqueadero INT UNIQUE NOT NULL,
    tipo_espacio ENUM('Carro', 'Moto', 'Bicicleta', 'Mixto') DEFAULT 'Carro',
    estado ENUM('Disponible', 'Parcialmente_Asignado', 'Completo') DEFAULT 'Disponible',
    observaciones TEXT,
    activo BOOLEAN DEFAULT TRUE,
    CHECK (numero_parqueadero BETWEEN 1 AND 200)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- TABLA 4: ASIGNACIONES
-- Relaciona vehículos con parqueaderos
-- =====================================================
CREATE TABLE asignaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    parqueadero_id INT NOT NULL,
    vehiculo_id INT NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin_asignacion TIMESTAMP NULL,
    activo BOOLEAN DEFAULT TRUE,
    estado_manual ENUM('Disponible','Parcialmente_Asignado','Completo') DEFAULT NULL,
    FOREIGN KEY (parqueadero_id) REFERENCES parqueaderos(id),
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id) ON DELETE CASCADE,
    UNIQUE KEY unique_vehiculo_activo (vehiculo_id, activo),
    INDEX idx_parqueadero_activo (parqueadero_id, activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- TABLA 5: HISTORIAL_ACCESOS
-- Registro de entradas/salidas
-- =====================================================
CREATE TABLE historial_accesos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehiculo_id INT NOT NULL,
    parqueadero_id INT NOT NULL,
    tipo_evento ENUM('Entrada', 'Salida') NOT NULL,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    FOREIGN KEY (vehiculo_id) REFERENCES vehiculos(id),
    FOREIGN KEY (parqueadero_id) REFERENCES parqueaderos(id),
    INDEX idx_fecha (fecha_hora),
    INDEX idx_vehiculo (vehiculo_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger para calcular automáticamente el tipo de circulación
DELIMITER $$
CREATE TRIGGER before_insert_vehiculo
BEFORE INSERT ON vehiculos
FOR EACH ROW
BEGIN
    -- Extraer último dígito de la placa
    SET NEW.ultimo_digito = RIGHT(NEW.placa, 1);
    
    -- Solo aplicar regla pico y placa para carros
    IF NEW.tipo_vehiculo = 'Carro' THEN
        IF NEW.ultimo_digito IN ('1','2','3','4','5') THEN
            SET NEW.tipo_circulacion = 'IMPAR';
        ELSEIF NEW.ultimo_digito IN ('6','7','8','9','0') THEN
            SET NEW.tipo_circulacion = 'PAR';
        END IF;
    ELSE
        SET NEW.tipo_circulacion = 'N/A';
    END IF;
END$$

-- Trigger para actualizar estado del parqueadero
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
        SELECT COUNT(*) INTO count_asignaciones
        FROM asignaciones a
        JOIN vehiculos v ON a.vehiculo_id = v.id
        WHERE a.parqueadero_id = NEW.parqueadero_id
        AND a.activo = TRUE
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

-- Trigger para liberar parqueadero al desactivar asignación
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
        SELECT COUNT(*) INTO count_asignaciones
        FROM asignaciones a
        JOIN vehiculos v ON a.vehiculo_id = v.id
        WHERE a.parqueadero_id = NEW.parqueadero_id
        AND a.activo = TRUE
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
            END IF;
        END IF;
    END IF;
END$$

DELIMITER ;

-- =====================================================
-- VISTAS ÚTILES
-- =====================================================

-- Vista de parqueaderos con información completa
CREATE VIEW vista_parqueaderos_completo AS
SELECT
    p.numero_parqueadero,
    p.estado,
    GROUP_CONCAT(
        CONCAT(
            f.nombre, ' ', f.apellidos,
            ' (', v.placa, '-', v.tipo_circulacion,
            IF(f.permite_compartir = FALSE, '-EXCLUSIVO', ''),
            IF(f.pico_placa_solidario = TRUE, '-SOLID', ''),
            IF(f.discapacidad = TRUE, '-DISC', ''),
            ')'
        )
        SEPARATOR ' | '
    ) AS asignados,
    COUNT(DISTINCT a.id) AS total_asignados
FROM parqueaderos p
LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
LEFT JOIN vehiculos v ON a.vehiculo_id = v.id
LEFT JOIN funcionarios f ON v.funcionario_id = f.id
WHERE p.activo = TRUE
GROUP BY p.id, p.numero_parqueadero, p.estado
ORDER BY p.numero_parqueadero;

-- Vista de funcionarios con vehículos
CREATE VIEW vista_funcionarios_vehiculos AS
SELECT
    f.cedula,
    f.nombre,
    f.apellidos,
    f.cargo,
    f.celular,
    f.permite_compartir,
    f.pico_placa_solidario,
    f.discapacidad,
    v.tipo_vehiculo,
    v.placa,
    v.tipo_circulacion,
    p.numero_parqueadero
FROM funcionarios f
LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
WHERE f.activo = TRUE
ORDER BY f.apellidos, f.nombre;

-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS
-- =====================================================

DELIMITER $$

-- Procedimiento para asignar vehículo a parqueadero
CREATE PROCEDURE sp_asignar_vehiculo(
    IN p_vehiculo_id INT,
    IN p_parqueadero_id INT
)
BEGIN
    DECLARE v_tipo_circulacion VARCHAR(10);
    DECLARE v_tipo_vehiculo VARCHAR(20);
    DECLARE v_funcionario_id INT;
    DECLARE v_permite_compartir BOOLEAN;
    DECLARE v_pico_placa_solidario BOOLEAN;
    DECLARE v_discapacidad BOOLEAN;
    DECLARE v_tiene_parqueadero_exclusivo BOOLEAN;
    DECLARE v_cargo VARCHAR(50);
    DECLARE v_count_mismo_tipo INT;
    DECLARE v_count_asignaciones_existentes INT;
    DECLARE v_count_vehiculos_funcionario INT;
    DECLARE v_ocupante_permite_compartir BOOLEAN;
    DECLARE v_ocupante_tiene_exclusivo BOOLEAN;
    DECLARE v_mensaje VARCHAR(500);
    DECLARE v_estado_calcular ENUM('Disponible','Parcialmente_Asignado','Completo');

    -- Obtener información del vehículo y funcionario
    SELECT
        v.tipo_circulacion,
        v.tipo_vehiculo,
        v.funcionario_id,
        f.permite_compartir,
        f.pico_placa_solidario,
        f.discapacidad,
        f.tiene_parqueadero_exclusivo,
        f.cargo
    INTO
        v_tipo_circulacion,
        v_tipo_vehiculo,
        v_funcionario_id,
        v_permite_compartir,
        v_pico_placa_solidario,
        v_discapacidad,
        v_tiene_parqueadero_exclusivo,
        v_cargo
    FROM vehiculos v
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE v.id = p_vehiculo_id;

    -- Contar asignaciones activas en el parqueadero
    SELECT COUNT(*) INTO v_count_asignaciones_existentes
    FROM asignaciones
    WHERE parqueadero_id = p_parqueadero_id
    AND activo = TRUE;

    -- VALIDACIÓN ESPECIAL: Si tiene parqueadero exclusivo para directivos (hasta 4 vehículos)
    IF v_tiene_parqueadero_exclusivo = TRUE AND v_cargo IN ('Director', 'Coordinador', 'Asesor') THEN
        -- Contar cuántos vehículos ya tiene asignados este funcionario en este parqueadero
        SELECT COUNT(*) INTO v_count_vehiculos_funcionario
        FROM asignaciones a
        JOIN vehiculos v ON a.vehiculo_id = v.id
        WHERE a.parqueadero_id = p_parqueadero_id
        AND a.activo = TRUE
        AND v.funcionario_id = v_funcionario_id;

        -- Verificar que no supere los 4 vehículos
        IF v_count_vehiculos_funcionario >= 4 THEN
            SET v_mensaje = 'El directivo ya tiene 4 vehículos asignados a este parqueadero exclusivo (límite máximo)';
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_mensaje;
        END IF;

        -- Verificar que no haya vehículos de otros funcionarios en este parqueadero
        IF v_count_asignaciones_existentes > 0 THEN
            SELECT COUNT(*) INTO v_count_vehiculos_funcionario
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            WHERE a.parqueadero_id = p_parqueadero_id
            AND a.activo = TRUE
            AND v.funcionario_id != v_funcionario_id;

            IF v_count_vehiculos_funcionario > 0 THEN
                SET v_mensaje = 'Este parqueadero tiene vehículos de otros funcionarios. El parqueadero exclusivo debe ser solo para el directivo.';
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_mensaje;
            END IF;
        END IF;

        -- Si pasa las validaciones, permitir asignación sin restricción PAR/IMPAR
        -- Continuar con la asignación normal (omite validaciones de pico y placa)
    ELSE
        -- VALIDACIONES NORMALES (para funcionarios sin parqueadero exclusivo)

        -- VALIDACIÓN 1: Si el funcionario NO permite compartir y ya hay vehículos en el parqueadero
        IF v_permite_compartir = FALSE AND v_count_asignaciones_existentes > 0 THEN
            SET v_mensaje = CONCAT('El funcionario ', v_cargo, ' no permite compartir parqueadero y este espacio ya está ocupado');
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_mensaje;
        END IF;

        -- VALIDACIÓN 2: Si ya hay vehículos, verificar si algún ocupante NO permite compartir o tiene exclusivo
        IF v_count_asignaciones_existentes > 0 THEN
            SELECT f.permite_compartir, f.tiene_parqueadero_exclusivo
            INTO v_ocupante_permite_compartir, v_ocupante_tiene_exclusivo
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE a.parqueadero_id = p_parqueadero_id
            AND a.activo = TRUE
            LIMIT 1;

            IF v_ocupante_permite_compartir = FALSE OR v_ocupante_tiene_exclusivo = TRUE THEN
                SET v_mensaje = 'Este parqueadero está ocupado por un funcionario con parqueadero exclusivo';
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
    -- INSERCIÓN CON LÓGICA ESPECIAL PARA DIRECTIVOS
    -- =====================================================

    IF v_tiene_parqueadero_exclusivo = TRUE AND v_cargo IN ('Director', 'Coordinador', 'Asesor') THEN
        -- CALCULAR EL ESTADO ANTES DE INSERTAR
        -- Contar cuántos vehículos habrá DESPUÉS de insertar este
        SELECT COUNT(*) + 1 INTO v_count_vehiculos_funcionario
        FROM asignaciones a
        JOIN vehiculos v ON a.vehiculo_id = v.id
        WHERE a.parqueadero_id = p_parqueadero_id
        AND a.activo = TRUE
        AND v.funcionario_id = v_funcionario_id;

        -- Determinar el estado según la cantidad DESPUÉS de insertar
        IF v_count_vehiculos_funcionario < 4 THEN
            SET v_estado_calcular = 'Parcialmente_Asignado';
        ELSE
            SET v_estado_calcular = 'Completo';
        END IF;

        -- INSERTAR CON estado_manual para que el trigger lo respete
        INSERT INTO asignaciones (parqueadero_id, vehiculo_id, activo, estado_manual)
        VALUES (p_parqueadero_id, p_vehiculo_id, TRUE, v_estado_calcular);

    ELSE
        -- Para funcionarios regulares, usar el comportamiento normal (triggers automáticos)
        INSERT INTO asignaciones (parqueadero_id, vehiculo_id, activo)
        VALUES (p_parqueadero_id, p_vehiculo_id, TRUE);
    END IF;

    SELECT 'Asignación realizada correctamente' AS mensaje;
END$$

-- Procedimiento para obtener estadísticas
CREATE PROCEDURE sp_obtener_estadisticas()
BEGIN
    SELECT 
        COUNT(*) AS total_parqueaderos,
        SUM(CASE WHEN estado = 'Disponible' THEN 1 ELSE 0 END) AS disponibles,
        SUM(CASE WHEN estado = 'Parcialmente_Asignado' THEN 1 ELSE 0 END) AS parcialmente_asignados,
        SUM(CASE WHEN estado = 'Completo' THEN 1 ELSE 0 END) AS completos
    FROM parqueaderos
    WHERE activo = TRUE;
END$$

DELIMITER ;

-- =====================================================
-- DATOS INICIALES
-- =====================================================

-- Insertar los 200 parqueaderos
INSERT INTO parqueaderos (numero_parqueadero, tipo_espacio) 
SELECT seq, 'Carro' 
FROM (
    SELECT @row := @row + 1 AS seq FROM 
    (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) t1,
    (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) t2,
    (SELECT 0 UNION ALL SELECT 1) t3,
    (SELECT @row:=0) t4
) t
WHERE seq <= 200;

-- Datos de prueba
INSERT INTO funcionarios (cedula, nombre, apellidos, direccion_grupo, cargo, celular, permite_compartir, pico_placa_solidario, discapacidad) VALUES
('12345678', 'Ana', 'Gómez', 'Recursos Humanos', 'Analista', '3001234567', TRUE, FALSE, FALSE),
('87654321', 'Luis', 'Pérez', 'Finanzas', 'Director', '3007654321', FALSE, FALSE, FALSE),  -- No permite compartir
('11223344', 'María', 'Rojas', 'IT', 'Desarrollador', '3002223333', TRUE, TRUE, FALSE),  -- Con pico placa solidario
('44332211', 'Carlos', 'Carrillo', 'Ventas', 'Ejecutivo', '3004445555', TRUE, FALSE, TRUE);  -- Con discapacidad

INSERT INTO vehiculos (funcionario_id, tipo_vehiculo, placa) VALUES
(1, 'Carro', 'BXY342'),  -- IMPAR
(2, 'Carro', 'CWZ870'),  -- PAR
(3, 'Carro', 'ABC129'),  -- PAR
(4, 'Carro', 'XYZ345'),  -- IMPAR
(1, 'Moto', 'MOT123'),
(3, 'Bicicleta', 'BICI01');