# Implementación de Borrado Lógico para Funcionarios

**Fecha**: 2025-10-26
**Versión**: 2.0.3
**Tipo**: Feature - Mejora de Integridad de Datos

---

## 📋 Descripción del Cambio

Se ha modificado el sistema de eliminación de funcionarios para implementar **borrado lógico (soft delete)** en lugar de **borrado físico (hard delete)**.

### Antes (Borrado Físico)
```sql
DELETE FROM funcionarios WHERE id = ?;
-- El funcionario se eliminaba completamente de la base de datos
-- Se perdía todo el historial
```

### Ahora (Borrado Lógico)
```sql
UPDATE funcionarios SET activo = FALSE WHERE id = ?;
-- El funcionario se marca como inactivo
-- Se preserva el historial completo
```

---

## 🎯 Objetivo

**Mantener el historial completo** de funcionarios, vehículos y asignaciones incluso después de que un empleado deje la empresa o sea dado de baja del sistema.

---

## ⚙️ Cambios Implementados

### 1. Modificación del Modelo `FuncionarioModel`

**Archivo**: `src/models/funcionario.py`

#### Método `eliminar(funcionario_id)`

**Antes**:
```python
def eliminar(self, funcionario_id: int) -> Tuple[bool, str]:
    # Eliminaba físicamente usando gestor_eliminacion
    exito, mensaje, detalles = self.gestor_eliminacion.eliminar_funcionario_completo(str(funcionario_id))
    return exito, mensaje
```

**Ahora**:
```python
def eliminar(self, funcionario_id: int) -> Tuple[bool, str]:
    """
    Desactiva un funcionario (borrado lógico) y libera sus recursos asociados
    Marca el funcionario como inactivo, desactiva sus vehículos y libera parqueaderos
    IMPORTANTE: No elimina físicamente de la BD para mantener historial
    """
    # 1. Liberar parqueaderos (DELETE asignaciones)
    # 2. Desactivar vehículos (UPDATE vehiculos SET activo = FALSE)
    # 3. Desactivar funcionario (UPDATE funcionarios SET activo = FALSE)
```

#### Método `eliminar_por_cedula(cedula)`

**Antes**:
```python
def eliminar_por_cedula(self, cedula: str) -> Tuple[bool, str]:
    exito, mensaje, detalles = self.gestor_eliminacion.eliminar_funcionario_completo(cedula)
    return exito, mensaje
```

**Ahora**:
```python
def eliminar_por_cedula(self, cedula: str) -> Tuple[bool, str]:
    """
    Desactiva un funcionario por su cédula (borrado lógico)
    """
    # Busca el funcionario activo y llama a eliminar(id)
    query = "SELECT id FROM funcionarios WHERE cedula = %s AND activo = TRUE"
    funcionario = self.db.fetch_one(query, (cedula,))
    return self.eliminar(funcionario['id'])
```

---

## 🔄 Flujo de Eliminación (Borrado Lógico)

```
Usuario solicita eliminar funcionario
           ↓
┌──────────────────────────────────────────────────┐
│ 1. Verificar que funcionario existe y está activo│
└──────────────────┬───────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────┐
│ 2. Obtener datos relacionados                    │
│    • Lista de vehículos                           │
│    • Lista de parqueaderos asignados              │
└──────────────────┬───────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────┐
│ 3. Liberar parqueaderos                           │
│    DELETE FROM asignaciones                       │
│    WHERE vehiculo_id IN (...)                     │
└──────────────────┬───────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────┐
│ 4. Desactivar vehículos                           │
│    UPDATE vehiculos                               │
│    SET activo = FALSE                             │
│    WHERE funcionario_id = ?                       │
└──────────────────┬───────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────┐
│ 5. Desactivar funcionario                         │
│    UPDATE funcionarios                            │
│    SET activo = FALSE                             │
│    WHERE id = ?                                   │
└──────────────────┬───────────────────────────────┘
                   ↓
┌──────────────────────────────────────────────────┐
│ 6. Log y mensaje de confirmación                 │
│    • Funcionario marcado como INACTIVO            │
│    • X vehículos desactivados                     │
│    • Y parqueaderos liberados                     │
│    • Historial preservado en BD                   │
└───────────────────────────────────────────────────┘
```

---

## 📊 Impacto en la Base de Datos

### Tabla `funcionarios`

| Acción | Query | Efecto |
|--------|-------|--------|
| **Antes** | `DELETE FROM funcionarios WHERE id = ?` | Registro eliminado permanentemente |
| **Ahora** | `UPDATE funcionarios SET activo = FALSE WHERE id = ?` | Registro marcado como inactivo |

### Tabla `vehiculos`

| Acción | Query | Efecto |
|--------|-------|--------|
| **Antes** | `DELETE FROM vehiculos WHERE funcionario_id = ?` | Vehículos eliminados |
| **Ahora** | `UPDATE vehiculos SET activo = FALSE WHERE funcionario_id = ?` | Vehículos desactivados |

### Tabla `asignaciones`

| Acción | Query | Efecto |
|--------|-------|--------|
| **Antes** | `DELETE FROM asignaciones WHERE ...` | Asignaciones eliminadas |
| **Ahora** | `DELETE FROM asignaciones WHERE vehiculo_id IN (...)` | **Asignaciones eliminadas** (necesario para liberar parqueaderos) |

> **Nota**: Las asignaciones sí se eliminan físicamente porque:
> 1. Los parqueaderos deben quedar disponibles inmediatamente
> 2. El historial se preserva mediante los vehículos y funcionarios inactivos
> 3. Los triggers de BD actualizan automáticamente el estado del parqueadero

---

## ✅ Beneficios

1. **Preservación de historial**
   - Todos los datos del funcionario se mantienen
   - Se puede consultar quién ocupó qué parqueadero
   - Auditoría completa de vehículos registrados

2. **Integridad referencial**
   - No se rompen relaciones de clave foránea
   - Los datos históricos siguen siendo consultables

3. **Reversibilidad** (opcional para futuro)
   - Se podría implementar una función para reactivar funcionarios
   - `UPDATE funcionarios SET activo = TRUE WHERE id = ?`

4. **Cumplimiento normativo**
   - Mantiene registros para auditorías
   - Historial laboral disponible
   - Trazabilidad completa

---

## 🔍 Verificación

### Consultas para verificar el comportamiento

#### 1. Ver todos los funcionarios (activos e inactivos)
```sql
SELECT
    id, cedula, nombre, apellidos, cargo, activo, fecha_registro
FROM funcionarios
ORDER BY activo DESC, apellidos;
```

#### 2. Ver funcionarios solo activos (como lo hace la aplicación)
```sql
SELECT * FROM funcionarios WHERE activo = TRUE;
```

#### 3. Ver vehículos de funcionarios inactivos
```sql
SELECT
    v.placa, v.tipo, v.activo as vehiculo_activo,
    f.nombre, f.apellidos, f.activo as funcionario_activo
FROM vehiculos v
INNER JOIN funcionarios f ON v.funcionario_id = f.id
WHERE f.activo = FALSE;
```

#### 4. Verificar que NO hay asignaciones activas de inactivos
```sql
SELECT COUNT(*) as incorrectas
FROM asignaciones a
INNER JOIN vehiculos v ON a.vehiculo_id = v.id
INNER JOIN funcionarios f ON v.funcionario_id = f.id
WHERE f.activo = FALSE;
-- Debe retornar 0
```

---

## 🧪 Cómo Probar

### Opción 1: Desde la Aplicación

1. Ejecutar la aplicación:
   ```bash
   cd "d:\grado 11 sahron\OneDrive\Escritorio\parking_system"
   python -m scripts.main_with_auth
   ```

2. Login con credenciales:
   - Usuario: `splaza`
   - Contraseña: `splaza123*`

3. Ir a la pestaña **Funcionarios**

4. Seleccionar un funcionario y hacer clic en **Eliminar**

5. Verificar el mensaje de confirmación:
   ```
   ✅ Funcionario desactivado exitosamente

   👤 Funcionario: [Nombre]
   🆔 Cédula: [Cédula]

   📋 Resumen de operaciones:
      • Funcionario marcado como INACTIVO
      • Vehículos desactivados: X
      • Parqueaderos liberados: Y

   💾 El historial se mantiene en la base de datos
   📊 El funcionario ya no aparecerá en listados activos
   ```

6. **Verificar en la aplicación**:
   - El funcionario ya NO aparece en la lista
   - Sus vehículos NO aparecen en la pestaña Vehículos
   - Los parqueaderos que ocupaba ahora están DISPONIBLES

### Opción 2: Desde la Base de Datos

```bash
# Ejecutar script de verificación
mysql -u root -p parking_management < test_borrado_logico.sql
```

---

## 📝 Logging

Todos los eventos de desactivación se registran en `logs/parking_system.log`:

```
2025-10-26 19:15:30 - parking_system - INFO - Iniciando desactivación de funcionario: Juan Pérez (ID: 123)
2025-10-26 19:15:30 - parking_system - INFO - Liberados 2 parqueaderos
2025-10-26 19:15:30 - parking_system - INFO - Desactivados 3 vehículos
2025-10-26 19:15:30 - parking_system - INFO - Funcionario Juan Pérez desactivado exitosamente
```

---

## 🔮 Mejoras Futuras (Opcional)

1. **Función de reactivación**
   ```python
   def reactivar(self, funcionario_id: int) -> Tuple[bool, str]:
       """Reactiva un funcionario previamente desactivado."""
       query = "UPDATE funcionarios SET activo = TRUE WHERE id = %s"
       # También reactiva sus vehículos
   ```

2. **Papelera de reciclaje en UI**
   - Pestaña adicional para ver funcionarios inactivos
   - Botón de "Restaurar" para reactivar

3. **Historial de cambios**
   - Tabla `funcionarios_historial` con timestamps
   - Registro de quién desactivó y cuándo

4. **Reportes de auditoría**
   - Generar reportes de funcionarios por período
   - Incluir inactivos en reportes históricos

---

## ⚠️ Notas Importantes

1. **Las asignaciones SÍ se eliminan físicamente**
   - Necesario para liberar parqueaderos
   - El historial se preserva en funcionarios y vehículos inactivos

2. **Los queries existentes ya filtran por `activo = TRUE`**
   - `obtener_todos()` → `WHERE f.activo = TRUE`
   - `validar_cedula_unica()` → `WHERE cedula = ? AND activo = TRUE`
   - No requiere cambios adicionales en otros módulos

3. **Triggers de BD se ejecutan correctamente**
   - Al eliminar asignaciones, los triggers actualizan el estado del parqueadero
   - Los parqueaderos quedan disponibles automáticamente

---

## 📚 Archivos Modificados

- ✅ `src/models/funcionario.py` - Métodos `eliminar()` y `eliminar_por_cedula()`
- ✅ `test_borrado_logico.sql` - Script de verificación (NUEVO)
- ✅ `CAMBIO_BORRADO_LOGICO.md` - Esta documentación (NUEVO)

---

## 🔐 Seguridad

- El borrado lógico es más seguro que el físico
- Se evita pérdida accidental de datos
- Permite recuperación en caso de error humano
- Mantiene trazabilidad completa para auditorías

---

**Fin del Documento**
