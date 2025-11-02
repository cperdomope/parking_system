# Corrección de Triggers - Borrado Lógico

**Problema**: Los parqueaderos muestran estados incorrectos (Parcialmente_Asignado, Completo) cuando todos los funcionarios están inactivos.

**Causa**: Los triggers no estaban verificando si los funcionarios están activos.

**Solución**: Actualizar los triggers para considerar solo funcionarios y vehículos ACTIVOS.

---

## 🔧 Cómo Ejecutar la Corrección

### Opción 1: Usando el archivo BAT (Recomendado para Windows)

```bash
# Hacer doble clic en el archivo:
EJECUTAR_FIX_TRIGGERS.bat
```

### Opción 2: Usando MySQL directamente

```bash
# Desde línea de comandos:
mysql -u root -proot parking_management < fix_triggers_borrado_logico.sql
```

### Opción 3: Desde MySQL Workbench o cliente MySQL

1. Abrir MySQL Workbench
2. Conectarse a la base de datos `parking_management`
3. Abrir el archivo `fix_triggers_borrado_logico.sql`
4. Ejecutar todo el script (Ctrl+Shift+Enter)

---

## ✅ ¿Qué hace el script?

### 1. Elimina triggers antiguos
```sql
DROP TRIGGER IF EXISTS after_insert_asignacion;
DROP TRIGGER IF EXISTS after_update_asignacion;
DROP TRIGGER IF EXISTS after_delete_asignacion;
```

### 2. Crea triggers actualizados

Los nuevos triggers incluyen verificación de **funcionarios activos**:

```sql
SELECT COUNT(*) INTO count_asignaciones
FROM asignaciones a
JOIN vehiculos v ON a.vehiculo_id = v.id
JOIN funcionarios f ON v.funcionario_id = f.id  -- ← NUEVO
WHERE a.parqueadero_id = NEW.parqueadero_id
AND a.activo = TRUE
AND v.activo = TRUE
AND f.activo = TRUE                             -- ← NUEVO
AND v.tipo_vehiculo = 'Carro';
```

### 3. Corrige estados actuales

Actualiza todos los parqueaderos basándose en las asignaciones **actuales** de funcionarios activos:

```sql
UPDATE parqueaderos p
SET estado = (
    CASE
        WHEN count_activos = 0 THEN 'Disponible'
        WHEN count_activos = 1 THEN 'Parcialmente_Asignado'
        WHEN count_activos >= 2 THEN 'Completo'
    END
);
```

---

## 📊 Verificación

Después de ejecutar el script, verás:

### Resumen de Estados

```
+-------------------------+----------+------------+
| estado                  | cantidad | porcentaje |
+-------------------------+----------+------------+
| Disponible              |      195 |     97.50% |
| Parcialmente_Asignado   |        5 |      2.50% |
| Completo                |        0 |      0.00% |
+-------------------------+----------+------------+
```

### Parqueaderos con funcionarios inactivos

```
Debe mostrar 0 resultados
```

### Triggers actualizados

```
+------------------------------+--------+---------------+
| Trigger                      | Event  | Table         |
+------------------------------+--------+---------------+
| after_insert_asignacion      | INSERT | asignaciones  |
| after_update_asignacion      | UPDATE | asignaciones  |
| after_delete_asignacion      | DELETE | asignaciones  |
+------------------------------+--------+---------------+
```

---

## 🧪 Probar en la Aplicación

Después de ejecutar el script:

1. **Reiniciar la aplicación** (cerrar y volver a abrir)

2. **Ir a la pestaña Parqueaderos**

3. **Verificar** que todos los parqueaderos muestran **Disponible**
   (o el estado correcto según funcionarios ACTIVOS)

4. **Probar eliminar un funcionario**:
   - Los parqueaderos que ocupaba deben quedar **Disponibles**
   - El cambio debe ser **inmediato**

---

## ⚠️ Notas Importantes

1. **El script es seguro**:
   - Solo actualiza triggers
   - No elimina datos
   - Corrige estados incorrectos

2. **Ejecutar UNA SOLA VEZ**:
   - No es necesario ejecutarlo múltiples veces
   - Si ya se ejecutó correctamente, no hace falta repetirlo

3. **Backup recomendado** (opcional):
   ```bash
   mysqldump -u root -proot parking_management > backup_antes_fix.sql
   ```

4. **Verificar conexión a MySQL**:
   - Usuario: `root`
   - Contraseña: `root`
   - Base de datos: `parking_management`

---

## 🔄 Si algo sale mal

### Error: "Access denied for user"

Cambiar las credenciales en el comando:

```bash
mysql -u TU_USUARIO -pTU_PASSWORD parking_management < fix_triggers_borrado_logico.sql
```

### Error: "Unknown database"

Crear la base de datos primero:

```bash
mysql -u root -proot < parking_database_schema.sql
```

### Estados siguen incorrectos

Ejecutar manualmente la corrección de estados:

```sql
USE parking_management;

UPDATE parqueaderos p
SET estado = 'Disponible'
WHERE NOT EXISTS (
    SELECT 1
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    WHERE a.parqueadero_id = p.id
    AND a.activo = TRUE
    AND v.activo = TRUE
    AND f.activo = TRUE
);
```

---

## 📝 Log de Cambios

**Fecha**: 2025-10-26
**Versión**: 1.0
**Archivos**:
- `fix_triggers_borrado_logico.sql` - Script SQL principal
- `EJECUTAR_FIX_TRIGGERS.bat` - Script de ejecución para Windows
- `INSTRUCCIONES_FIX_TRIGGERS.md` - Este archivo

---

**Fin del Documento**
