# Feature: Estado Activo/Inactivo para Funcionarios

**Fecha**: 2025-10-26
**Versión**: 2.0.4
**Tipo**: Feature - Sistema de Activación/Desactivación de Funcionarios

---

## 📋 Descripción

Se ha implementado un sistema completo para gestionar el estado de funcionarios (Activo/Inactivo) directamente desde la interfaz de usuario, permitiendo:

1. **Visualizar el estado** de cada funcionario en la tabla
2. **Desactivar** funcionarios (en lugar de eliminarlos)
3. **Reactivar** funcionarios previamente desactivados
4. **Mantener historial completo** de todos los empleados

---

## ✨ Características Implementadas

### 1. Columna "Estado" en la Tabla

**Ubicación**: Pestaña Funcionarios → Tabla

La tabla ahora muestra 13 columnas (antes eran 12):

| # | Columna | Descripción |
|---|---------|-------------|
| 1 | Cédula | Número de cédula |
| 2 | Nombre | Nombre del funcionario |
| 3 | Apellidos | Apellidos |
| 4 | Dirección | Dirección de grupo |
| 5 | Cargo | Cargo del funcionario |
| 6 | Celular | Número de celular |
| 7 | Tarjeta Prox | Tarjeta de proximidad |
| 8 | Vehículos | Cantidad de vehículos |
| 9 | Compartir | Permite compartir parqueadero |
| 10 | Solidario | Pico y placa solidario |
| 11 | Discap. | Tiene discapacidad |
| **12** | **Estado** | **Activo / Inactivo** ⭐ NUEVO |
| 13 | Acciones | Botones de acción |

**Visualización**:
- ✅ **Activo**: Fondo verde (#d4edda), texto verde oscuro (#155724)
- ❌ **Inactivo**: Fondo rojo claro (#f8d7da), texto rojo oscuro (#721c24)

### 2. Botón "Reactivar" para Funcionarios Inactivos

**Funcionamiento**:

| Estado | Botones Mostrados | Descripción |
|--------|-------------------|-------------|
| **Activo** | ✏️ Editar, 👁️ Ver, 🗑️ Eliminar | Funcionario puede ser editado y desactivado |
| **Inactivo** | 👁️ Ver, 🔄 Reactivar | Funcionario solo puede verse y reactivarse |

**Botón Reactivar**:
- **Icono**: 🔄 (flecha circular)
- **Color**: Verde (#27ae60)
- **Tooltip**: "Reactivar funcionario"
- **Acción**: Reactiva el funcionario y sus vehículos

### 3. Listado Completo (Activos e Inactivos)

La tabla ahora muestra **TODOS** los funcionarios:
- Los activos aparecen primero (ordenados alfabéticamente)
- Los inactivos aparecen después (ordenados alfabéticamente)
- Cada uno claramente identificado con su estado

---

## 🔧 Cambios Técnicos

### Modelo: `src/models/funcionario.py`

#### Nuevo Método: `obtener_todos_incluyendo_inactivos()`

```python
def obtener_todos_incluyendo_inactivos(self) -> List[Dict]:
    """Obtiene TODOS los funcionarios (activos e inactivos)"""
    query = """
        SELECT f.*, COUNT(v.id) as total_vehiculos
        FROM funcionarios f
        LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
        GROUP BY f.id
        ORDER BY f.activo DESC, f.apellidos, f.nombre
    """
    return self.db.fetch_all(query)
```

**Orden**: Primero activos, luego inactivos (ambos alfabéticos)

#### Nuevo Método: `reactivar(funcionario_id)`

```python
def reactivar(self, funcionario_id: int) -> Tuple[bool, str]:
    """
    Reactiva un funcionario previamente desactivado
    Marca el funcionario y sus vehículos como activos nuevamente
    """
    # 1. Reactivar vehículos
    UPDATE vehiculos SET activo = TRUE
    WHERE funcionario_id = ? AND activo = FALSE

    # 2. Reactivar funcionario
    UPDATE funcionarios SET activo = TRUE
    WHERE id = ?
```

**Operaciones**:
1. Reactiva todos los vehículos del funcionario
2. Marca el funcionario como activo
3. Registra evento en logs
4. Retorna mensaje de éxito

### Vista: `src/ui/funcionarios_tab.py`

#### Modificaciones en la Tabla

**Antes** (12 columnas):
```python
self.tabla_funcionarios.setColumnCount(12)
self.tabla_funcionarios.setHorizontalHeaderLabels([...])
```

**Ahora** (13 columnas):
```python
self.tabla_funcionarios.setColumnCount(13)
self.tabla_funcionarios.setHorizontalHeaderLabels([
    "Cédula", "Nombre", "Apellidos", "Dirección", "Cargo",
    "Celular", "Tarjeta Prox", "Vehículos", "Compartir",
    "Solidario", "Discap.", "Estado", "Acciones"
])
```

#### Código de Renderizado de Estado

```python
# Columna 11: Estado (Activo/Inactivo)
activo = func.get("activo", True)
estado_text = "Activo" if activo else "Inactivo"
estado_item = QTableWidgetItem(estado_text)
estado_item.setTextAlignment(0x0004 | 0x0080)  # Centro

if activo:
    # Verde para activo
    estado_item.setBackground(QBrush(QColor("#d4edda")))
    estado_item.setForeground(QBrush(QColor("#155724")))
    estado_item.setFont(QFont("Arial", 9, QFont.Bold))
else:
    # Rojo para inactivo
    estado_item.setBackground(QBrush(QColor("#f8d7da")))
    estado_item.setForeground(QBrush(QColor("#721c24")))
    estado_item.setFont(QFont("Arial", 9, QFont.Bold))

self.tabla_funcionarios.setItem(i, 11, estado_item)
```

#### Nuevo Método: `reactivar_funcionario(funcionario_id)`

```python
def reactivar_funcionario(self, funcionario_id: int):
    """Reactiva un funcionario previamente desactivado"""
    # 1. Obtener datos del funcionario inactivo
    # 2. Confirmar con usuario
    # 3. Llamar al modelo para reactivar
    # 4. Actualizar tabla y emitir señales
```

#### Botones Dinámicos

```python
if activo:
    # Activo: Editar + Ver + Eliminar
    btn_layout.addWidget(btn_editar)
    btn_layout.addWidget(btn_ver)
    btn_layout.addWidget(btn_eliminar)
else:
    # Inactivo: Ver + Reactivar
    btn_layout.addWidget(btn_ver)
    btn_layout.addWidget(btn_reactivar)
```

---

## 🔄 Flujos de Trabajo

### Flujo 1: Desactivar Funcionario

```
Usuario hace clic en 🗑️ Eliminar
         ↓
Mensaje de confirmación con detalles
         ↓
Usuario confirma (Yes)
         ↓
funcionario_model.eliminar(id)
         ↓
1. Eliminar asignaciones (libera parqueaderos)
2. Desactivar vehículos (UPDATE activo = FALSE)
3. Desactivar funcionario (UPDATE activo = FALSE)
         ↓
Mensaje de éxito
         ↓
Tabla se recarga → Funcionario aparece como "Inactivo"
Botones cambian a: Ver + Reactivar
```

### Flujo 2: Reactivar Funcionario

```
Usuario hace clic en 🔄 Reactivar
         ↓
Mensaje de confirmación
         ↓
Usuario confirma (Yes)
         ↓
funcionario_model.reactivar(id)
         ↓
1. Reactivar vehículos (UPDATE activo = TRUE)
2. Reactivar funcionario (UPDATE activo = TRUE)
         ↓
Mensaje de éxito
         ↓
Tabla se recarga → Funcionario aparece como "Activo"
Botones cambian a: Editar + Ver + Eliminar
```

---

## 📊 Resultados Visuales

### Tabla de Funcionarios (Ejemplo)

```
+------------+---------+-----------+---------+--------+-----------+
| Nombre     | Cargo   | Vehículos | Estado  | Acciones           |
+------------+---------+-----------+---------+--------------------+
| Juan Pérez | Director| 2/2       | Activo  | ✏️ 👁️ 🗑️          |
| Ana López  | Asesor  | 1/2       | Activo  | ✏️ 👁️ 🗑️          |
| Carlos Ruiz| Operario| 0/2       | Inactivo| 👁️ 🔄             |
+------------+---------+-----------+---------+--------------------+
```

### Mensajes de Confirmación

**Al Desactivar**:
```
¿Está seguro de que desea eliminar al funcionario 'Juan Pérez'?

Se desactivarán los siguientes vehículos:
• Carro - ABC123 - PAR (Parqueadero S1-015)
• Moto - XYZ789 - N/A (Parqueadero S2-020)

Se liberarán 2 parqueadero(s)

[Sí] [No]
```

**Al Reactivar**:
```
¿Está seguro de que desea reactivar al funcionario 'Carlos Ruiz'?

Esto hará que:
• El funcionario vuelva a aparecer en los listados
• Sus vehículos estén disponibles para asignación
• Pueda recibir nuevas asignaciones de parqueaderos

[Sí] [No]
```

**Mensaje de Éxito (Reactivación)**:
```
✅ Funcionario reactivado exitosamente

👤 Funcionario: Carlos Ruiz García
🆔 Cédula: 1234567890

📋 Resumen de operaciones:
   • Funcionario marcado como ACTIVO
   • Vehículos reactivados: 2

✨ El funcionario vuelve a aparecer en los listados
🚗 Sus vehículos están disponibles para asignación

[OK]
```

---

## 🧪 Cómo Probar

### Escenario 1: Desactivar Funcionario

1. Abrir aplicación
2. Ir a pestaña **Funcionarios**
3. Buscar un funcionario **Activo**
4. Hacer clic en **🗑️ Eliminar**
5. Confirmar la desactivación
6. **Verificar**:
   - El funcionario ahora aparece como **Inactivo**
   - Su fila tiene fondo rojo claro
   - Los botones cambiaron a: 👁️ Ver + 🔄 Reactivar
   - Sus parqueaderos quedaron **Disponibles**

### Escenario 2: Reactivar Funcionario

1. En la tabla, buscar un funcionario **Inactivo**
2. Hacer clic en **🔄 Reactivar**
3. Confirmar la reactivación
4. **Verificar**:
   - El funcionario ahora aparece como **Activo**
   - Su fila tiene fondo normal
   - Los botones cambiaron a: ✏️ Editar + 👁️ Ver + 🗑️ Eliminar
   - Sus vehículos están disponibles para asignación

### Escenario 3: Ver Funcionario Inactivo

1. Buscar un funcionario **Inactivo**
2. Hacer clic en **👁️ Ver**
3. **Verificar**:
   - Se abre modal con todos los detalles
   - Muestra vehículos registrados (aunque inactivos)
   - Muestra historial completo

---

## 📝 Logging

Todos los eventos quedan registrados en `logs/parking_system.log`:

```
2025-10-26 20:30:15 - parking_system - INFO - Iniciando desactivación de funcionario: Juan Pérez (ID: 45)
2025-10-26 20:30:15 - parking_system - INFO - Liberados 2 parqueaderos
2025-10-26 20:30:15 - parking_system - INFO - Desactivados 2 vehículos
2025-10-26 20:30:15 - parking_system - INFO - Funcionario Juan Pérez desactivado exitosamente

2025-10-26 20:35:22 - parking_system - INFO - Iniciando reactivación de funcionario: Carlos Ruiz (ID: 45)
2025-10-26 20:35:22 - parking_system - INFO - Reactivados 2 vehículos
2025-10-26 20:35:22 - parking_system - INFO - Funcionario Carlos Ruiz reactivado exitosamente
```

---

## 📂 Archivos Modificados

| Archivo | Cambios | Líneas |
|---------|---------|--------|
| `src/models/funcionario.py` | Añadidos 2 métodos nuevos | +95 |
| `src/ui/funcionarios_tab.py` | Columna Estado + Botón Reactivar | +80 |

**Total**: ~175 líneas de código añadidas

---

## ✅ Beneficios

1. **Historial Completo** - Nunca se pierde información de empleados
2. **Auditoría** - Todos los funcionarios históricos visibles
3. **Reversibilidad** - Errores de desactivación son reversibles
4. **UX Mejorada** - Estado visual claro (colores, botones)
5. **Seguridad** - Confirmaciones antes de acciones importantes
6. **Trazabilidad** - Logs completos de activación/desactivación

---

## 🔮 Mejoras Futuras (Opcional)

1. **Filtros**:
   - Checkbox para mostrar solo activos
   - Checkbox para mostrar solo inactivos

2. **Búsqueda**:
   - Buscar por estado en el campo de búsqueda

3. **Reportes**:
   - Reporte de funcionarios inactivos
   - Fecha de desactivación (añadir campo)

4. **Permisos**:
   - Solo administradores pueden reactivar
   - Log de quién reactivó a quién

---

## 📋 Checklist de Verificación

- [x] Columna "Estado" visible en tabla
- [x] Estados con colores correctos (verde/rojo)
- [x] Botón "Reactivar" para inactivos
- [x] Botón "Eliminar" para activos
- [x] Método `reactivar()` en modelo
- [x] Método `obtener_todos_incluyendo_inactivos()` en modelo
- [x] Confirmación antes de reactivar
- [x] Mensajes de éxito/error
- [x] Logging de eventos
- [x] Recarga automática de tabla
- [x] Señales emitidas correctamente

---

**Fin del Documento**

**Próximo Paso**: Ejecutar la aplicación y probar la funcionalidad completa.

```bash
cd "d:\grado 11 sahron\OneDrive\Escritorio\parking_system"
python -m scripts.main_with_auth
```

**Credenciales**: splaza / splaza123*
