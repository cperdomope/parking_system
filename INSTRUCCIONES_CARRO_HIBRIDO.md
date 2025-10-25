# Instrucciones de Implementación: Checkbox "Carro Híbrido"

**Versión:** 1.3
**Fecha:** 2025-01-19
**Objetivo:** Implementar incentivo ambiental para carros híbridos

---

## 🎯 Descripción de la Funcionalidad

El checkbox **"🌿 Carro Híbrido (Incentivo Ambiental)"** permite marcar funcionarios que poseen vehículos híbridos, otorgándoles beneficios especiales:

### Beneficios para Carros Híbridos:
1. ✅ **Uso diario del parqueadero** - Ignora restricciones de pico y placa
2. ✅ **Parqueadero exclusivo** - No comparte con otros funcionarios
3. ✅ **Estado inmediato "Completo"** - Al asignar, el parqueadero se marca como Completo (color rojo)
4. ✅ **Prioridad de asignación** - Validaciones en la base de datos protegen el espacio

---

## 📋 Pasos de Implementación

### PASO 1: Ejecutar Migración de Base de Datos

Ejecutar el script SQL de migración:

```bash
mysql -u root -p parking_management < migracion_carro_hibrido.sql
```

Este script realiza:
- ✅ Agrega columna `tiene_carro_hibrido BOOLEAN DEFAULT FALSE`
- ✅ Actualiza procedimiento `validar_asignacion_parqueadero`
- ✅ Actualiza trigger `after_insert_asignacion`
- ✅ Actualiza trigger `after_delete_asignacion`

**Verificación:**
```sql
USE parking_management;

SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_DEFAULT, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'parking_management'
  AND TABLE_NAME = 'funcionarios'
  AND COLUMN_NAME = 'tiene_carro_hibrido';
```

Resultado esperado:
```
+----------------------+--------------+----------------+--------------------------------------------------+
| COLUMN_NAME          | COLUMN_TYPE  | COLUMN_DEFAULT | COLUMN_COMMENT                                   |
+----------------------+--------------+----------------+--------------------------------------------------+
| tiene_carro_hibrido  | tinyint(1)   | 0              | Carro híbrido - uso diario, parqueadero exclusivo|
+----------------------+--------------+----------------+--------------------------------------------------+
```

---

### PASO 2: Verificar Archivos Modificados

Los siguientes archivos ya han sido actualizados:

#### 1. Modelo de Funcionarios
**Archivo:** `src/models/funcionario.py`

**Cambios:**
- ✅ Parámetro `tiene_carro_hibrido` en método `crear()`
- ✅ Parámetro `tiene_carro_hibrido` en método `actualizar()`
- ✅ Query INSERT incluye columna `tiene_carro_hibrido`
- ✅ Query UPDATE incluye columna `tiene_carro_hibrido`
- ✅ Mensaje de confirmación: "🌿 Carro híbrido registrado..."

#### 2. Interfaz de Usuario
**Archivo:** `src/ui/funcionarios_tab.py`

**Cambios en formulario principal:**
- ✅ Checkbox `self.chk_carro_hibrido` con estilo verde (#27ae60)
- ✅ Tooltip explicativo con beneficios
- ✅ Handler `on_carro_hibrido_changed_main()` para exclusión mutua
- ✅ Layout actualizado con 4 checkboxes
- ✅ Método `guardar_funcionario()` incluye `tiene_carro_hibrido`
- ✅ Método `limpiar_formulario()` limpia el nuevo checkbox

**Cambios en modal de edición:**
- ✅ Checkbox `self.chk_carro_hibrido` en modal
- ✅ Handler `on_carro_hibrido_changed()` para exclusión mutua
- ✅ Método `cargar_datos()` carga el estado del checkbox
- ✅ Método `guardar_cambios()` incluye `tiene_carro_hibrido`

#### 3. Esquema de Base de Datos
**Archivo:** `parking_database_schema.sql`

**Cambios:**
- ✅ Línea 28: Columna `tiene_carro_hibrido` agregada

#### 4. Documentación
**Archivo:** `CLAUDE.md`

**Cambios:**
- ✅ Sección "Reglas de Funcionarios" actualizada con checkbox #4
- ✅ Versión actualizada a v1.3
- ✅ Descripción completa de beneficios

---

## 🔧 Lógica de Negocio

### Validaciones en la Base de Datos

El procedimiento `validar_asignacion_parqueadero` implementa:

```sql
-- Si es carro híbrido
IF v_tiene_carro_hibrido = TRUE THEN
    -- No se puede compartir con nadie
    IF v_count_asignaciones_existentes > 0 THEN
        SET mensaje_error = 'CARRO HÍBRIDO: El parqueadero ya está ocupado...';
        SET es_valido = FALSE;
    ELSE
        SET es_valido = TRUE;
    END IF;
END IF;

-- Si el parqueadero ya está ocupado por un carro híbrido
IF v_ocupante_tiene_hibrido = TRUE THEN
    SET mensaje_error = 'El parqueadero está ocupado por un CARRO HÍBRIDO...';
    SET es_valido = FALSE;
END IF;
```

### Triggers Actualizados

**Trigger `after_insert_asignacion`:**
```sql
-- Si es carro híbrido, marcar parqueadero como COMPLETO inmediatamente
IF v_tiene_hibrido = TRUE THEN
    UPDATE parqueaderos
    SET estado = 'Completo'
    WHERE id = NEW.parqueadero_id;
END IF;
```

---

## 🎨 Interfaz Visual

### Formulario de Funcionarios

```
┌───────────────────────────────────────────────────────────────┐
│ Registro de Funcionario                                       │
├───────────────────────────────────────────────────────────────┤
│ Cédula* | Nombre* | Apellidos*                                │
│ Dirección/Grupo* | Cargo* | Celular*                          │
│ No.Tarjeta Prox                                               │
│                                                               │
│ [ ] 🔄 Pico y Placa    [ ] ♿ Discapacidad                   │
│ [ ] 🏢 Exclusivo Directivo    [ ] 🌿 Carro Híbrido          │
│                                                               │
│ [Guardar] [Limpiar]                                          │
└───────────────────────────────────────────────────────────────┘
```

**Colores de Checkboxes:**
- 🔄 Pico y Placa: Azul (#2196F3)
- ♿ Discapacidad: Verde oscuro (#27ae60)
- 🏢 Exclusivo Directivo: Morado (#8e44ad)
- 🌿 Carro Híbrido: Verde claro (#27ae60) ← **NUEVO**

---

## ✅ Verificación Post-Implementación

### 1. Verificar Sintaxis

```bash
cd "d:\grado 11 sahron\OneDrive\Escritorio\parking_system"
python -m py_compile src/models/funcionario.py
python -m py_compile src/ui/funcionarios_tab.py
```

Salida esperada: Sin errores

### 2. Verificar Checkbox en Interfaz

```bash
python main_modular.py
```

**Verificar:**
1. Formulario de Funcionarios muestra 4 checkboxes
2. Checkbox "🌿 Carro Híbrido" tiene color verde
3. Al marcar un checkbox, los otros 3 se desmarcan automáticamente
4. Tooltip muestra información correcta

### 3. Probar Flujo Completo

**Caso de Prueba 1: Registro de Funcionario con Carro Híbrido**

1. Ir a pestaña "Funcionarios"
2. Llenar formulario:
   - Cédula: 123456789
   - Nombre: Juan
   - Apellidos: Pérez
   - Marcar: ✅ **Carro Híbrido**
3. Click en "Guardar"
4. Verificar mensaje: "🌿 Carro híbrido registrado (uso diario, parqueadero exclusivo - incentivo ambiental)"

**Caso de Prueba 2: Asignación de Parqueadero**

1. Ir a pestaña "Vehículos"
2. Registrar vehículo para Juan Pérez
3. Ir a pestaña "Asignaciones"
4. Asignar parqueadero al vehículo
5. **Verificar:** El parqueadero pasa a estado "Completo" (color rojo) inmediatamente
6. Intentar asignar otro vehículo al mismo parqueadero
7. **Verificar:** Sistema muestra error "El parqueadero está ocupado por un CARRO HÍBRIDO..."

**Caso de Prueba 3: Exclusión Mutua de Checkboxes**

1. Marcar "🌿 Carro Híbrido"
2. Intentar marcar "🏢 Exclusivo Directivo"
3. **Verificar:** "Carro Híbrido" se desmarca automáticamente

---

## 🐛 Solución de Problemas

### Error: Columna 'tiene_carro_hibrido' no existe

**Solución:** Ejecutar migración de BD:
```bash
mysql -u root -p parking_management < migracion_carro_hibrido.sql
```

### Error: Checkbox no aparece en interfaz

**Solución:** Verificar que los scripts de actualización se ejecutaron correctamente:
```bash
grep -n "chk_carro_hibrido" src/ui/funcionarios_tab.py
```

Debería mostrar múltiples coincidencias (declaración, handlers, layout, etc.)

### Error: Parqueadero no se marca como "Completo"

**Solución:** Verificar que el trigger se actualizó correctamente:
```sql
SHOW CREATE TRIGGER after_insert_asignacion;
```

Buscar la sección:
```sql
IF v_tiene_hibrido = TRUE THEN
    UPDATE parqueaderos SET estado = 'Completo' WHERE id = NEW.parqueadero_id;
END IF;
```

---

## 📊 Resumen de Cambios

| Componente | Archivo | Estado |
|------------|---------|--------|
| Base de Datos | `migracion_carro_hibrido.sql` | ✅ Listo |
| Esquema Principal | `parking_database_schema.sql` | ✅ Actualizado |
| Modelo Funcionario | `src/models/funcionario.py` | ✅ Actualizado |
| Interfaz Formulario | `src/ui/funcionarios_tab.py` | ✅ Actualizado |
| Interfaz Modal | `src/ui/funcionarios_tab.py` | ✅ Actualizado |
| Documentación | `CLAUDE.md` | ✅ Actualizado |

---

## 🚀 Siguiente Pasos

1. ✅ Ejecutar migración de base de datos
2. ✅ Probar casos de prueba mencionados arriba
3. ✅ Verificar que el parqueadero se marca como "Completo" (rojo)
4. ✅ Verificar que las validaciones funcionan correctamente
5. ✅ Capacitar a usuarios sobre el nuevo incentivo ambiental

---

**Implementado por:** Claude Code
**Revisado:** Pendiente
**Aprobado:** Pendiente

---

## 📞 Contacto

Para reportar errores o solicitar mejoras, contactar al equipo de desarrollo.
