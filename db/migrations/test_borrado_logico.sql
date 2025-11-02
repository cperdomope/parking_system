-- ============================================================================
-- SCRIPT DE PRUEBA: Borrado Lógico de Funcionarios
-- ============================================================================
-- Descripción: Verifica que el borrado lógico funciona correctamente
-- Fecha: 2025-10-26
-- Versión: 1.0
-- ============================================================================

USE parking_management;

-- 1. Ver todos los funcionarios (activos e inactivos)
SELECT
    'ESTADO ACTUAL DE FUNCIONARIOS' as Reporte;

SELECT
    id,
    cedula,
    nombre,
    apellidos,
    cargo,
    activo,
    fecha_registro
FROM funcionarios
ORDER BY activo DESC, apellidos, nombre;

-- 2. Contar funcionarios por estado
SELECT
    'CONTEO POR ESTADO' as Reporte;

SELECT
    activo as Estado,
    COUNT(*) as Total
FROM funcionarios
GROUP BY activo;

-- 3. Ver vehículos de funcionarios inactivos
SELECT
    'VEHÍCULOS DE FUNCIONARIOS INACTIVOS' as Reporte;

SELECT
    v.id,
    v.placa,
    v.tipo,
    v.activo as vehiculo_activo,
    f.nombre,
    f.apellidos,
    f.cedula,
    f.activo as funcionario_activo
FROM vehiculos v
INNER JOIN funcionarios f ON v.funcionario_id = f.id
WHERE f.activo = FALSE
ORDER BY f.apellidos, v.placa;

-- 4. Ver parqueaderos que fueron de funcionarios inactivos
SELECT
    'HISTORIAL DE PARQUEADEROS DE INACTIVOS' as Reporte;

SELECT
    p.id,
    p.numero_parqueadero,
    p.sotano,
    p.estado as estado_actual,
    COUNT(a.id) as asignaciones_historicas
FROM parqueaderos p
LEFT JOIN asignaciones a ON p.id = a.parqueadero_id
LEFT JOIN vehiculos v ON a.vehiculo_id = v.id
LEFT JOIN funcionarios f ON v.funcionario_id = f.id
WHERE f.activo = FALSE
GROUP BY p.id, p.numero_parqueadero, p.sotano, p.estado
ORDER BY p.sotano, p.numero_parqueadero;

-- 5. Verificar que NO hay asignaciones activas de funcionarios inactivos
SELECT
    'VERIFICACIÓN: Asignaciones activas de inactivos (debe ser 0)' as Reporte;

SELECT
    COUNT(*) as asignaciones_incorrectas
FROM asignaciones a
INNER JOIN vehiculos v ON a.vehiculo_id = v.id
INNER JOIN funcionarios f ON v.funcionario_id = f.id
WHERE f.activo = FALSE;

-- 6. Reporte completo de un funcionario inactivo (si existe)
SELECT
    'DETALLE COMPLETO DE FUNCIONARIO INACTIVO (ejemplo)' as Reporte;

SELECT
    f.id,
    f.cedula,
    f.nombre,
    f.apellidos,
    f.cargo,
    f.activo,
    f.fecha_registro,
    COUNT(DISTINCT v.id) as total_vehiculos_registrados,
    SUM(CASE WHEN v.activo = TRUE THEN 1 ELSE 0 END) as vehiculos_activos,
    SUM(CASE WHEN v.activo = FALSE THEN 1 ELSE 0 END) as vehiculos_inactivos
FROM funcionarios f
LEFT JOIN vehiculos v ON f.id = v.funcionario_id
WHERE f.activo = FALSE
GROUP BY f.id, f.cedula, f.nombre, f.apellidos, f.cargo, f.activo, f.fecha_registro
LIMIT 1;

-- ============================================================================
-- FIN DEL SCRIPT DE PRUEBA
-- ============================================================================
