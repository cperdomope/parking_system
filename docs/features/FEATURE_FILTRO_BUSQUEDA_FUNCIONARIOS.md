# 🔍 Feature: Filtro de Búsqueda por Cédula en Funcionarios

**Fecha:** 2025-10-26
**Versión:** 2.0.4
**Módulo:** Pestaña Funcionarios

---

## 📋 Descripción

Se implementó un **filtro de búsqueda en tiempo real** por cédula en la tabla de funcionarios, permitiendo localizar funcionarios de forma rápida e inmediata sin tener que desplazarse manualmente por toda la tabla.

---

## ✨ Funcionalidades Implementadas

### 1. Barra de Búsqueda
- **Ubicación:** Entre el formulario de registro y la tabla de funcionarios
- **Campo de texto:** Ingreso de cédula para filtrar
- **Botón "Limpiar":** Restaura la vista completa de todos los funcionarios
- **Label de resultados:** Muestra cantidad de coincidencias encontradas

### 2. Búsqueda en Tiempo Real
- **Filtrado automático:** Al escribir en el campo, la tabla se filtra instantáneamente
- **Búsqueda parcial:** No necesita escribir la cédula completa, puede buscar por primeros dígitos
- **Ejemplo:**
  - Si escribe "1234", muestra todos los funcionarios cuya cédula contenga "1234"
  - Si escribe "12345678", muestra solo el funcionario con esa cédula exacta

### 3. Indicadores Visuales
- **Sin resultados:** Mensaje en rojo "No se encontraron resultados"
- **1 resultado:** Mensaje en verde "1 resultado encontrado"
- **Múltiples resultados:** Mensaje en verde "X resultados encontrados"
- **Campo vacío:** Muestra todos los funcionarios

---

## 🎨 Interfaz de Usuario

```
┌─────────────────────────────────────────────────────────────────┐
│                      Buscar Funcionario                         │
├─────────────────────────────────────────────────────────────────┤
│ Buscar por Cédula: [________________]  [Limpiar]  "3 resultados"│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Lista de Funcionarios                         │
├──────────┬─────────┬───────────┬──────────┬─────────────────────┤
│ Cédula   │ Nombre  │ Apellidos │ ...      │ Estado   │ Acciones │
├──────────┼─────────┼───────────┼──────────┼──────────┼──────────┤
│ 12345678 │ Juan    │ Pérez     │ ...      │ Activo   │ ✏️👁️🗑️  │
│ 12340000 │ María   │ López     │ ...      │ Activo   │ ✏️👁️🗑️  │
│ 12389999 │ Pedro   │ García    │ ...      │ Inactivo │ 👁️🔄    │
└──────────┴─────────┴───────────┴──────────┴──────────┴──────────┘
```

---

## 🔧 Implementación Técnica

### Archivos Modificados

#### **src/ui/funcionarios_tab.py**

**1. Componentes UI agregados (líneas 297-347):**

```python
# Barra de búsqueda
search_group = QGroupBox("Buscar Funcionario")
search_layout = QHBoxLayout()

search_label = QLabel("Buscar por Cédula:")
self.txt_buscar_cedula = QLineEdit()
self.txt_buscar_cedula.setPlaceholderText("Ingrese la cédula para filtrar...")
self.txt_buscar_cedula.textChanged.connect(self.filtrar_funcionarios)

self.btn_limpiar_busqueda = QPushButton("Limpiar")
self.btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)

self.lbl_resultados = QLabel("")
```

**2. Método de filtrado (líneas 1031-1065):**

```python
def filtrar_funcionarios(self):
    """Filtra los funcionarios en la tabla según la cédula ingresada"""
    texto_busqueda = self.txt_buscar_cedula.text().strip()

    # Si el campo está vacío, mostrar todos
    if not texto_busqueda:
        for i in range(self.tabla_funcionarios.rowCount()):
            self.tabla_funcionarios.setRowHidden(i, False)
        self.lbl_resultados.setText("")
        return

    # Filtrar filas que coincidan con la búsqueda
    filas_visibles = 0
    for i in range(self.tabla_funcionarios.rowCount()):
        cedula_item = self.tabla_funcionarios.item(i, 0)
        if cedula_item:
            cedula = cedula_item.text()
            if texto_busqueda in cedula:
                self.tabla_funcionarios.setRowHidden(i, False)
                filas_visibles += 1
            else:
                self.tabla_funcionarios.setRowHidden(i, True)

    # Actualizar label de resultados
    if filas_visibles == 0:
        self.lbl_resultados.setText("No se encontraron resultados")
        self.lbl_resultados.setStyleSheet("color: #e74c3c; font-weight: bold;")
    elif filas_visibles == 1:
        self.lbl_resultados.setText("1 resultado encontrado")
        self.lbl_resultados.setStyleSheet("color: #27ae60; font-weight: bold;")
    else:
        self.lbl_resultados.setText(f"{filas_visibles} resultados encontrados")
        self.lbl_resultados.setStyleSheet("color: #27ae60; font-weight: bold;")
```

**3. Método de limpieza (líneas 1067-1072):**

```python
def limpiar_busqueda(self):
    """Limpia el campo de búsqueda y muestra todos los funcionarios"""
    self.txt_buscar_cedula.clear()
    for i in range(self.tabla_funcionarios.rowCount()):
        self.tabla_funcionarios.setRowHidden(i, False)
    self.lbl_resultados.setText("")
```

---

## 📊 Casos de Uso

### Caso 1: Búsqueda Exitosa
**Acción:** Usuario ingresa "1234" en el campo de búsqueda
**Resultado:**
- Se ocultan todas las filas cuya cédula NO contiene "1234"
- Se muestran solo las filas con cédulas que contengan "1234"
- Label muestra: "3 resultados encontrados" (en verde)

### Caso 2: Sin Resultados
**Acción:** Usuario ingresa "99999999" (cédula inexistente)
**Resultado:**
- Todas las filas se ocultan
- Label muestra: "No se encontraron resultados" (en rojo)

### Caso 3: Limpiar Búsqueda
**Acción:** Usuario hace clic en botón "Limpiar"
**Resultado:**
- Campo de búsqueda se vacía
- Todas las filas se vuelven visibles
- Label de resultados se limpia

### Caso 4: Búsqueda Parcial
**Acción:** Usuario ingresa solo "12"
**Resultado:**
- Muestra todos los funcionarios cuya cédula empiece con "12"
- Ej: 12345678, 12000000, 12999999, etc.

---

## 🎯 Ventajas

1. **Velocidad:** Búsqueda instantánea sin necesidad de recargar la tabla
2. **Facilidad de uso:** No requiere hacer clic en ningún botón para buscar
3. **Flexibilidad:** Permite búsquedas parciales
4. **Feedback visual:** Indica claramente cuántos resultados se encontraron
5. **Reversible:** Fácil de limpiar y volver a la vista completa

---

## 🧪 Pruebas Recomendadas

1. **Buscar cédula completa:** Ingresar una cédula completa y verificar que muestra solo ese funcionario
2. **Buscar primeros dígitos:** Ingresar los primeros 3-4 dígitos y verificar que filtra correctamente
3. **Buscar cédula inexistente:** Verificar mensaje de "No se encontraron resultados"
4. **Limpiar búsqueda:** Verificar que el botón "Limpiar" restaura todos los funcionarios
5. **Búsqueda con tabla vacía:** Verificar comportamiento cuando no hay funcionarios
6. **Búsqueda de funcionarios inactivos:** Verificar que filtra tanto activos como inactivos

---

## 📝 Notas Importantes

- El filtro **NO elimina** filas, solo las oculta temporalmente
- El filtro afecta **solo la visualización**, no los datos en la base de datos
- Al recargar la tabla (crear, editar, eliminar funcionario), el filtro se mantiene
- El filtro distingue entre activos e inactivos (ambos son filtrables)
- La búsqueda es **case-sensitive** y busca coincidencias exactas de caracteres

---

## 🔜 Mejoras Futuras Posibles

1. **Búsqueda por nombre/apellido:** Agregar opciones para filtrar por otros campos
2. **Búsqueda combinada:** Permitir filtrar por múltiples criterios simultáneamente
3. **Búsqueda case-insensitive:** Ignorar mayúsculas/minúsculas
4. **Historial de búsquedas:** Recordar búsquedas recientes
5. **Autocompletar:** Sugerir cédulas mientras se escribe
6. **Exportar resultados filtrados:** Permitir exportar solo los resultados visibles

---

## 📌 Relacionado Con

- **Borrado Lógico:** El filtro respeta el estado activo/inactivo de funcionarios
- **Reactivación:** Los funcionarios reactivados aparecen inmediatamente en el filtro
- **Estado Activo/Inactivo:** El filtro funciona para ambos estados

---

**Documentado por:** Claude Code
**Última actualización:** 2025-10-26
