-- =====================================================
-- SCRIPT DE PRUEBA: Verificar corrección de bug
-- Parqueaderos parcialmente asignados en combobox
-- =====================================================

USE parking_management;

-- =====================================================
-- PASO 1: Verificar parqueaderos con 1 carro asignado
-- =====================================================
SELECT
    p.id,
    p.numero_parqueadero,
    p.estado,
    p.tipo_espacio,
    COALESCE(p.sotano, 'Sótano-1') as sotano,
    COUNT(a.id) as total_asignaciones,
    GROUP_CONCAT(
        CONCAT(
            v.placa, ' (',
            v.tipo_circulacion, ') - ',
            CASE
                WHEN f.pico_placa_solidario = 1 THEN 'Solidario'
                WHEN f.discapacidad = 1 THEN 'Discapacidad'
                WHEN f.tiene_parqueadero_exclusivo = 1 THEN 'Exclusivo'
                WHEN f.tiene_carro_hibrido = 1 THEN 'Híbrido'
                ELSE 'Regular'
            END
        )
        SEPARATOR ' | '
    ) as vehiculos_info
FROM parqueaderos p
LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
LEFT JOIN vehiculos v ON a.vehiculo_id = v.id AND v.tipo_vehiculo = 'Carro'
LEFT JOIN funcionarios f ON v.funcionario_id = f.id
WHERE p.activo = TRUE
AND p.estado IN ('Parcialmente_Asignado', 'Completo')
GROUP BY p.id, p.numero_parqueadero, p.estado, p.tipo_espacio, p.sotano
HAVING total_asignaciones >= 1
ORDER BY p.numero_parqueadero
LIMIT 20;

-- =====================================================
-- PASO 2: Simular obtener_disponibles() con tipo PAR
-- Esto debe devolver parqueaderos con 1 carro IMPAR
-- =====================================================
SELECT DISTINCT p.id, p.numero_parqueadero, p.estado, p.tipo_espacio,
       COALESCE(p.sotano, 'Sótano-1') as sotano
FROM parqueaderos p
WHERE p.estado = 'Parcialmente_Asignado'
AND p.tipo_espacio = 'Carro'
AND p.activo = TRUE
AND (
    -- Verificar que tiene EXACTAMENTE 1 carro
    SELECT COUNT(*)
    FROM asignaciones a2
    JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
    WHERE a2.parqueadero_id = p.id
    AND a2.activo = TRUE
    AND v2.tipo_vehiculo = 'Carro'
) = 1
AND (
    -- Verificar que el carro existente tiene tipo de circulación complementario
    SELECT v.tipo_circulacion
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) != 'PAR'  -- Busca parqueaderos con IMPAR para asignar un PAR
AND (
    -- Verificar que el funcionario del carro existente permite compartir
    SELECT f.permite_compartir
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = TRUE
AND (
    -- Verificar que NO tiene pico y placa solidario
    SELECT f.pico_placa_solidario
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = FALSE
AND (
    -- Verificar que NO tiene discapacidad
    SELECT f.discapacidad
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = FALSE
AND (
    -- Verificar que NO tiene parqueadero exclusivo
    SELECT f.tiene_parqueadero_exclusivo
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = FALSE
AND (
    -- Verificar que NO tiene carro híbrido
    SELECT f.tiene_carro_hibrido
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = FALSE
ORDER BY p.numero_parqueadero;

-- =====================================================
-- PASO 3: Simular obtener_disponibles() con tipo IMPAR
-- Esto debe devolver parqueaderos con 1 carro PAR
-- =====================================================
SELECT DISTINCT p.id, p.numero_parqueadero, p.estado, p.tipo_espacio,
       COALESCE(p.sotano, 'Sótano-1') as sotano
FROM parqueaderos p
WHERE p.estado = 'Parcialmente_Asignado'
AND p.tipo_espacio = 'Carro'
AND p.activo = TRUE
AND (
    SELECT COUNT(*)
    FROM asignaciones a2
    JOIN vehiculos v2 ON a2.vehiculo_id = v2.id
    WHERE a2.parqueadero_id = p.id
    AND a2.activo = TRUE
    AND v2.tipo_vehiculo = 'Carro'
) = 1
AND (
    SELECT v.tipo_circulacion
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) != 'IMPAR'  -- Busca parqueaderos con PAR para asignar un IMPAR
AND (
    SELECT f.permite_compartir
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = TRUE
AND (
    SELECT f.pico_placa_solidario
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = FALSE
AND (
    SELECT f.discapacidad
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = FALSE
AND (
    SELECT f.tiene_parqueadero_exclusivo
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = FALSE
AND (
    SELECT f.tiene_carro_hibrido
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.tipo_vehiculo = 'Carro'
    LIMIT 1
) = FALSE
ORDER BY p.numero_parqueadero;

-- =====================================================
-- RESULTADO ESPERADO:
-- - PASO 1: Lista de parqueaderos con asignaciones actuales
-- - PASO 2: Parqueaderos con 1 carro IMPAR (disponibles para PAR)
-- - PASO 3: Parqueaderos con 1 carro PAR (disponibles para IMPAR)
-- =====================================================
