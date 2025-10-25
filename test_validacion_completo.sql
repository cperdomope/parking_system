-- Script de prueba para validar la lógica de parqueaderos completos
-- Este script verifica que los parqueaderos con 2 carros NO aparezcan en los filtros

USE parking_management;

-- 1. Ver todos los parqueaderos con sus asignaciones
SELECT
    p.id,
    p.numero_parqueadero,
    p.estado,
    COUNT(a.id) as total_asignaciones,
    GROUP_CONCAT(CONCAT(v.placa, '-', v.tipo_circulacion) SEPARATOR ' | ') as vehiculos
FROM parqueaderos p
LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
LEFT JOIN vehiculos v ON a.vehiculo_id = v.id AND v.tipo_vehiculo = 'Carro'
WHERE p.activo = TRUE
GROUP BY p.id, p.numero_parqueadero, p.estado
HAVING total_asignaciones > 0
ORDER BY total_asignaciones DESC, p.numero_parqueadero
LIMIT 20;

-- 2. Verificar parqueaderos que deberían estar COMPLETOS (2 carros)
SELECT
    p.id,
    p.numero_parqueadero,
    p.estado,
    COUNT(a.id) as total_carros,
    GROUP_CONCAT(CONCAT(v.placa, '-', v.tipo_circulacion) SEPARATOR ' | ') as vehiculos
FROM parqueaderos p
JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
JOIN vehiculos v ON a.vehiculo_id = v.id
WHERE p.activo = TRUE
AND v.tipo_vehiculo = 'Carro'
GROUP BY p.id, p.numero_parqueadero, p.estado
HAVING COUNT(a.id) >= 2
ORDER BY p.numero_parqueadero;

-- 3. Simular el query de obtener_disponibles() para tipo PAR
-- Este query NO debería devolver parqueaderos con 2 carros
SELECT DISTINCT p.id, p.numero_parqueadero, p.estado,
       COUNT(a2.id) as total_carros_asignados
FROM parqueaderos p
JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
JOIN vehiculos v ON a.vehiculo_id = v.id
JOIN funcionarios f ON v.funcionario_id = f.id
LEFT JOIN asignaciones a2 ON p.id = a2.parqueadero_id AND a2.activo = TRUE
LEFT JOIN vehiculos v2 ON a2.vehiculo_id = v2.id AND v2.tipo_vehiculo = 'Carro'
WHERE p.estado = 'Parcialmente_Asignado'
AND v.tipo_vehiculo = 'Carro'
AND v.tipo_circulacion != 'PAR'  -- Buscar espacios que necesiten PAR
AND p.activo = TRUE
AND f.permite_compartir = TRUE
AND f.pico_placa_solidario = FALSE
AND f.discapacidad = FALSE
AND f.tiene_parqueadero_exclusivo = FALSE
AND f.tiene_carro_hibrido = FALSE
GROUP BY p.id, p.numero_parqueadero, p.estado
HAVING COUNT(DISTINCT v2.id) = 1  -- Solo parqueaderos con EXACTAMENTE 1 carro
ORDER BY p.numero_parqueadero;

-- 4. Contar parqueaderos por estado
SELECT estado, COUNT(*) as total
FROM parqueaderos
WHERE activo = TRUE
GROUP BY estado;
