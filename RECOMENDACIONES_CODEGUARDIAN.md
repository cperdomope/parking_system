# 🛡️ Recomendaciones de Mejora - CodeGuardian

**Fecha de Análisis:** 2025-10-13
**Versión del Sistema:** 1.1
**Python Version:** 3.13.2
**Score Actual:** 78/100

---

## 📊 Resumen Ejecutivo

CodeGuardian ha identificado **84 mejoras potenciales** en el código del Sistema de Gestión de Parqueadero. Este documento presenta las recomendaciones priorizadas para mejorar la mantenibilidad, legibilidad y compatibilidad con Python 3.13.2.

## 🎯 Prioridades de Refactorización

### ⚠️ ALTA PRIORIDAD

#### 1. Refactorizar `setup_ui()` en asignaciones_tab.py (484 líneas)

**Archivo:** `src/ui/asignaciones_tab.py:658-1142`
**Problema:** Función monolítica de 484 líneas que dificulta mantenimiento
**Impact Global:** Alto - archivo más crítico del sistema

**Propuesta de Refactorización:**

```python
# ANTES (484 líneas en una sola función)
def setup_ui(self):
    """Configura la interfaz de usuario"""
    # 484 líneas de código...

# DESPUÉS (dividido en 6 funciones especializadas)
def setup_ui(self) -> None:
    """
    Configura la interfaz de usuario principal.

    Organiza el layout en tres secciones:
    1. Panel de filtros (izquierda)
    2. Panel de nueva asignación (derecha)
    3. Tabla de asignaciones (ancho completo)
    """
    main_layout = QVBoxLayout()
    main_layout.setSpacing(15)
    main_layout.setContentsMargins(15, 15, 15, 15)

    # Crear secciones
    top_section = self._crear_seccion_superior()
    tabla_section = self._crear_seccion_tabla()

    main_layout.addWidget(top_section)
    main_layout.addWidget(tabla_section, 1)

    self.setLayout(main_layout)
    self.asignaciones_completas = []

def _crear_seccion_superior(self) -> QWidget:
    """Crea la sección superior con filtros y formulario de asignación."""
    top_section = QWidget()
    layout = QHBoxLayout(top_section)
    layout.setSpacing(15)

    filter_panel = self._crear_panel_filtros()
    assign_panel = self._crear_panel_asignacion()

    layout.addWidget(filter_panel)
    layout.addWidget(assign_panel)

    return top_section

def _crear_panel_filtros(self) -> QGroupBox:
    """
    Crea el panel de filtros de búsqueda.

    Returns:
        QGroupBox con campo de cédula y botón limpiar
    """
    filter_group = QGroupBox("🔍 Filtrar Asignaciones")
    filter_group.setMaximumWidth(350)
    filter_group.setStyleSheet(self._get_groupbox_style("#3498db"))

    # ... (líneas 671-742)

    return filter_group

def _crear_panel_asignacion(self) -> QGroupBox:
    """
    Crea el panel de nueva asignación de parqueadero.

    Returns:
        QGroupBox con formulario completo de asignación
    """
    assign_group = QGroupBox("✨ Nueva Asignación de Parqueadero")
    assign_group.setStyleSheet(self._get_groupbox_style("#27ae60"))

    # ... (líneas 744-1042)

    return assign_group

def _crear_seccion_tabla(self) -> QGroupBox:
    """
    Crea la sección de tabla de asignaciones actuales.

    Returns:
        QGroupBox con tabla configurada y estilizada
    """
    tabla_group = QGroupBox("📋 Asignaciones Actuales")
    tabla_group.setStyleSheet(self._get_groupbox_style("#e67e22"))

    # ... (líneas 1044-1139)

    return tabla_group

def _get_groupbox_style(self, border_color: str) -> str:
    """
    Genera el estilo CSS para QGroupBox.

    Args:
        border_color: Color del borde en formato hex (ej: "#3498db")

    Returns:
        String con el CSS completo para el QGroupBox
    """
    return f"""
        QGroupBox {{
            font-weight: bold;
            font-size: 13px;
            color: #2c3e50;
            border: 2px solid {border_color};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: #f8f9fa;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px 0 8px;
            background-color: white;
        }}
    """
```

**Beneficios:**
- ✅ Cada función tiene < 100 líneas
- ✅ Responsabilidades claras y separadas
- ✅ Más fácil de mantener y probar
- ✅ Reutilización de estilos CSS
- ✅ Type hints añadidos para mejor autocompletado

---

#### 2. Refactorizar `mostrar_asignaciones()` (138 líneas)

**Archivo:** `src/ui/asignaciones_tab.py:1500-1638`
**Problema:** Función larga con lógica compleja de renderizado de tabla

**Propuesta:**

```python
from typing import Dict, Any, List

def mostrar_asignaciones(self, asignaciones: List[Dict[str, Any]]) -> None:
    """
    Muestra las asignaciones en la tabla.

    Args:
        asignaciones: Lista de diccionarios con datos de asignaciones
    """
    self.tabla_asignaciones.setRowCount(len(asignaciones))

    for i, asig in enumerate(asignaciones):
        self._renderizar_fila_asignacion(i, asig)

def _renderizar_fila_asignacion(self, row: int, asig: Dict[str, Any]) -> None:
    """Renderiza una fila completa de la tabla con los datos de la asignación."""
    self._set_columna_sotano(row, asig)
    self._set_columna_parqueadero(row, asig)
    self._set_columna_funcionario(row, asig)
    self._set_columna_cedula(row, asig)
    self._set_columna_vehiculo(row, asig)
    self._set_columna_placa(row, asig)
    self._set_columna_circulacion(row, asig)
    self._set_columna_observaciones(row, asig)
    self._set_columna_acciones(row, asig)

def _set_columna_sotano(self, row: int, asig: Dict[str, Any]) -> None:
    """Configura la columna de sótano."""
    item = QTableWidgetItem(asig['sotano'])
    item.setTextAlignment(Qt.AlignCenter)
    self.tabla_asignaciones.setItem(row, 0, item)

def _set_columna_parqueadero(self, row: int, asig: Dict[str, Any]) -> None:
    """Configura la columna de parqueadero con indicadores especiales."""
    texto = f"P-{asig['numero_parqueadero']:03d}"
    if asig.get('estado_manual') == 'Completo':
        texto += " 🚫"

    item = QTableWidgetItem(texto)
    item.setTextAlignment(Qt.AlignCenter)

    if asig.get('estado_parqueadero') == 'Completo' and asig.get('estado_manual'):
        item.setBackground(QBrush(QColor("#fadbd8")))
        item.setForeground(QBrush(QColor("#c0392b")))

    self.tabla_asignaciones.setItem(row, 1, item)

def _set_columna_funcionario(self, row: int, asig: Dict[str, Any]) -> None:
    """Configura la columna de funcionario con indicadores visuales."""
    indicadores = self._obtener_indicadores_funcionario(asig)
    texto = asig['funcionario']
    if indicadores:
        texto = f"{texto} {' '.join(indicadores)}"

    item = QTableWidgetItem(texto)
    item.setTextAlignment(Qt.AlignCenter)

    if not asig.get('permite_compartir', True):
        item.setBackground(QBrush(QColor("#fadbd8")))
        item.setForeground(QBrush(QColor("#c0392b")))

    self.tabla_asignaciones.setItem(row, 2, item)

def _obtener_indicadores_funcionario(self, asig: Dict[str, Any]) -> List[str]:
    """
    Obtiene los indicadores visuales para un funcionario.

    Args:
        asig: Diccionario con datos de la asignación

    Returns:
        Lista de emojis indicadores
    """
    indicadores = []
    if not asig.get('permite_compartir', True):
        indicadores.append("🚫")
    if asig.get('pico_placa_solidario'):
        indicadores.append("🔄")
    if asig.get('discapacidad'):
        indicadores.append("♿")
    return indicadores

# ... (continuar con las demás columnas)
```

**Beneficios:**
- ✅ Cada función tiene una responsabilidad única
- ✅ Type hints para mejor type checking
- ✅ Más fácil de probar individualmente
- ✅ Código más limpio y legible

---

#### 3. Extraer Estilos CSS a Constantes

**Problema:** Estilos CSS duplicados en múltiples lugares

**Propuesta:**

Crear archivo `src/widgets/combobox_styles.py`:

```python
# -*- coding: utf-8 -*-
"""
Estilos CSS reutilizables para ComboBoxes del sistema
Compatible con Python 3.13.2
"""

COMBOBOX_STYLE_BASE = """
    QComboBox {
        border: 2px solid #bdc3c7;
        border-radius: 6px;
        padding: 8px 30px 8px 12px;
        font-size: 13px;
        background-color: white;
        color: #000000;
    }
    QComboBox:focus {
        border-color: #3498db;
    }
"""

COMBOBOX_DROPDOWN_STYLE = """
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #b0bec5;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
        background: transparent;
    }
    QComboBox::down-arrow {
        image: none;
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 7px solid #555;
        margin-right: 6px;
    }
    QComboBox::down-arrow:on {
        border-top: 7px solid #2196F3;
    }
"""

COMBOBOX_ITEMVIEW_STYLE = """
    QComboBox QAbstractItemView {
        border: 2px solid #2196F3;
        background-color: #ffffff;
        selection-background-color: #42A5F5 !important;
        selection-color: #ffffff !important;
    }
    QComboBox QAbstractItemView::item {
        padding: 8px;
        color: #000000;
        background-color: #ffffff;
        min-height: 25px;
    }
    QComboBox QAbstractItemView::item:selected {
        background-color: #42A5F5 !important;
        color: #ffffff !important;
        font-weight: bold;
    }
    QComboBox QAbstractItemView::item:hover {
        background-color: #42A5F5 !important;
        color: #ffffff !important;
        font-weight: bold;
    }
"""

def get_combobox_style(min_width: str = "120px") -> str:
    """
    Obtiene el estilo completo para ComboBox.

    Args:
        min_width: Ancho mínimo del ComboBox (ej: "120px", "180px")

    Returns:
        String con el CSS completo
    """
    return f"""
        {COMBOBOX_STYLE_BASE}
        QComboBox {{ min-width: {min_width}; }}
        {COMBOBOX_DROPDOWN_STYLE}
        {COMBOBOX_ITEMVIEW_STYLE}
    """
```

**Uso:**

```python
from ..widgets.combobox_styles import get_combobox_style

# Antes (70+ líneas repetidas)
self.combo_sotano.setStyleSheet("""
    QComboBox {
        border: 2px solid #bdc3c7;
        border-radius: 6px;
        # ... 70 líneas más
    }
""")

# Después (1 línea)
self.combo_sotano.setStyleSheet(get_combobox_style("120px"))
```

**Beneficios:**
- ✅ Elimina ~500 líneas de código duplicado
- ✅ Consistencia visual en toda la aplicación
- ✅ Más fácil actualizar estilos globalmente
- ✅ Reduce tamaño del archivo `asignaciones_tab.py`

---

### 🟨 MEDIA PRIORIDAD

#### 4. Agregar Type Hints Faltantes

**Archivos Afectados:**
- `src/ui/asignaciones_tab.py` - 15 funciones sin type hints
- `src/models/parqueadero.py` - 6 funciones sin type hints
- `src/ui/reportes_tab.py` - 12 funciones sin type hints

**Ejemplo:**

```python
# ANTES
def cargar_vehiculos_sin_asignar(self):
    query = """..."""
    vehiculos = self.db.fetch_all(query)
    # ...

# DESPUÉS
from typing import List, Dict, Any, Optional

def cargar_vehiculos_sin_asignar(self) -> None:
    """
    Carga TODOS los vehículos sin asignar (Carros, Motos y Bicicletas).

    Actualiza el combo de vehículos con información completa del vehículo
    y funcionario propietario.
    """
    query: str = """..."""
    vehiculos: List[Dict[str, Any]] = self.db.fetch_all(query)
    # ...

def filtrar_por_cedula(self, cedula: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Filtra las asignaciones por número de cédula.

    Args:
        cedula: Número de cédula a buscar (opcional)

    Returns:
        Lista de asignaciones que coinciden con el filtro
    """
    # ...
```

---

#### 5. Agregar Docstrings Faltantes (27 funciones)

**Funciones sin documentación:**

1. `EditarAsignacionDialog.cargar_datos_actuales()` - línea 351
2. `EditarAsignacionDialog.cargar_sotanos()` - línea 364
3. `EditarAsignacionDialog.cargar_parqueaderos_disponibles()` - línea 383
4. `EditarAsignacionDialog.guardar_cambios()` - línea 418
5. `VerAsignacionModal.cargar_datos()` - línea 594
6. `AsignacionesTab.cargar_vehiculos_sin_asignar()` - línea 1144
7. `AsignacionesTab.cargar_sotanos()` - línea 1187
8. `AsignacionesTab.cargar_parqueaderos_por_sotano()` - línea 1207
9. `AsignacionesTab.mostrar_info_vehiculo_seleccionado()` - línea 1262
10. `AsignacionesTab.cargar_parqueaderos_disponibles()` - línea 1287
11. `AsignacionesTab.realizar_asignacion()` - línea 1311
12. `AsignacionesTab.cargar_asignaciones()` - línea 1431
13. `AsignacionesTab.mostrar_asignaciones()` - línea 1500
14. `AsignacionesTab.filtrar_por_cedula()` - línea 1640
15. `AsignacionesTab.limpiar_filtro()` - línea 1657
16. `AsignacionesTab.ver_asignacion()` - línea 1662
17. `AsignacionesTab.liberar_asignacion()` - línea 1670
18. `AsignacionesTab.actualizar_vehiculos_sin_asignar()` - línea 1690
19. `AsignacionesTab.editar_asignacion()` - línea 1694
20. `AsignacionesTab.actualizar_asignaciones()` - línea 1708

**Template recomendado:**

```python
def cargar_vehiculos_sin_asignar(self) -> None:
    """
    Carga los vehículos sin asignación en el combo selector.

    Obtiene todos los vehículos activos que no tienen una asignación
    activa de parqueadero. Incluye información del funcionario propietario
    e indicadores visuales para casos especiales (exclusivo, solidario, discapacidad).

    La lista se ordena por: tipo de vehículo → apellido → nombre del funcionario.

    Modifica:
        self.combo_vehiculo_sin_asignar: Actualiza opciones del combo

    Raises:
        DatabaseError: Si hay problemas al consultar la base de datos
    """
    # ... código ...
```

---

#### 6. Optimizar Queries SQL Largas

**Problema:** Queries muy largas embebidas en el código

**Propuesta:** Crear archivo `src/database/queries.py`:

```python
# -*- coding: utf-8 -*-
"""
Queries SQL reutilizables del sistema de parqueadero
Compatible con Python 3.13.2
"""

from typing import Final

# Queries de Asignaciones
QUERY_ASIGNACIONES_COMPLETAS: Final[str] = """
    SELECT
        COALESCE(p.sotano, 'Sótano-1') as sotano,
        p.numero_parqueadero,
        p.estado as estado_parqueadero,
        CONCAT(f.nombre, ' ', f.apellidos) as funcionario,
        f.cedula,
        f.cargo,
        f.permite_compartir,
        f.pico_placa_solidario,
        f.discapacidad,
        v.tipo_vehiculo,
        v.placa,
        v.tipo_circulacion,
        COALESCE(a.observaciones, '') as observaciones,
        a.estado_manual,
        v.id as vehiculo_id
    FROM asignaciones a
    JOIN vehiculos v ON a.vehiculo_id = v.id
    JOIN funcionarios f ON v.funcionario_id = f.id
    JOIN parqueaderos p ON a.parqueadero_id = p.id
    WHERE a.activo = TRUE
    ORDER BY COALESCE(p.sotano, 'Sótano-1'), p.numero_parqueadero, v.tipo_circulacion
"""

QUERY_VEHICULOS_SIN_ASIGNAR: Final[str] = """
    SELECT v.*,
           f.nombre, f.apellidos, f.cedula, f.cargo,
           f.permite_compartir, f.pico_placa_solidario, f.discapacidad
    FROM vehiculos v
    JOIN funcionarios f ON v.funcionario_id = f.id
    LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
    WHERE v.activo = TRUE AND a.id IS NULL
    ORDER BY v.tipo_vehiculo, f.apellidos, f.nombre
"""

def query_check_asignaciones_existentes(parqueadero_id: int) -> tuple[str, tuple[int]]:
    """
    Genera query para verificar asignaciones existentes en un parqueadero.

    Args:
        parqueadero_id: ID del parqueadero a verificar

    Returns:
        Tupla con (query, parametros)
    """
    query = """
        SELECT COUNT(*) as total
        FROM asignaciones
        WHERE parqueadero_id = %s AND activo = TRUE
    """
    return (query, (parqueadero_id,))
```

**Uso:**

```python
from ..database.queries import QUERY_ASIGNACIONES_COMPLETAS, QUERY_VEHICULOS_SIN_ASIGNAR

def cargar_asignaciones(self) -> None:
    """Carga las asignaciones actuales en la tabla."""
    try:
        asignaciones = self.db.fetch_all(QUERY_ASIGNACIONES_COMPLETAS)
        self.asignaciones_completas = asignaciones
        self.mostrar_asignaciones(asignaciones)
    except Exception as e:
        print(f"Error al cargar asignaciones: {e}")
        self.tabla_asignaciones.setRowCount(0)
```

---

### 🟦 BAJA PRIORIDAD

#### 7. Reemplazar `print()` por Sistema de Logging

**Problema:** 15 llamadas a `print()` para debugging

**Propuesta:**

```python
import logging
from typing import Any

# Configurar logger en __init__
logger = logging.getLogger(__name__)

class AsignacionesTab(QWidget):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # ...

    def cargar_sotanos(self) -> None:
        """Carga los sótanos disponibles en el combo."""
        try:
            sotanos = self.parqueadero_model.obtener_sotanos_disponibles()
            self.combo_sotano.clear()
            self.combo_sotano.addItem("-- Seleccione sótano --", None)

            for sotano in sotanos:
                self.combo_sotano.addItem(sotano, sotano)

            # ANTES
            print(f"Sotanos cargados en asignaciones: {sotanos}")

            # DESPUÉS
            self.logger.info(f"Sótanos cargados: {len(sotanos)} - {sotanos}")

        except Exception as e:
            # ANTES
            print(f"Error al cargar sótanos: {e}")

            # DESPUÉS
            self.logger.error(f"Error al cargar sótanos", exc_info=True)
            # Fallback...
```

---

#### 8. Usar Enums para Estados de Parqueadero

**Propuesta:**

```python
from enum import Enum, auto

class EstadoParqueadero(Enum):
    """Estados posibles de un parqueadero."""
    DISPONIBLE = "Disponible"
    PARCIALMENTE_ASIGNADO = "Parcialmente_Asignado"
    COMPLETO = "Completo"

class TipoCirculacion(Enum):
    """Tipos de circulación vehicular según pico y placa."""
    PAR = "PAR"
    IMPAR = "IMPAR"
    NA = "N/A"  # Para motos y bicicletas

# Uso
if asig['tipo_circulacion'] == TipoCirculacion.PAR.value:
    circulacion_item.setBackground(QBrush(QColor("#e8f5e8")))
    circulacion_item.setForeground(QBrush(QColor("#2e7d32")))
```

---

## 📦 Herramientas Recomendadas

### Instalar Herramientas de Análisis

```bash
pip install ruff black isort pylint mypy
```

### Configuración Recomendada

Crear archivo `pyproject.toml`:

```toml
[tool.black]
line-length = 120
target-version = ['py313']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 120
skip_gitignore = true
known_first_party = ["src"]

[tool.ruff]
line-length = 120
target-version = "py313"
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "C",  # flake8-comprehensions
    "B",  # flake8-bugbear
]
ignore = [
    "E501",  # line too long (handled by black)
    "B008",  # do not perform function calls in argument defaults
]

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Cambiar a true gradualmente
```

### Comandos de Uso

```bash
# Formatear código automáticamente
black src/

# Organizar imports
isort src/

# Análisis de código
ruff check src/

# Type checking
mypy src/

# Análisis completo
pylint src/ --max-line-length=120
```

---

## 📈 Plan de Implementación

### Fase 1: Mejoras Inmediatas (1-2 días)

1. ✅ Instalar herramientas de análisis
2. ✅ Ejecutar `black` y `isort` en todo el proyecto
3. ✅ Extraer estilos CSS a `combobox_styles.py`
4. ✅ Agregar docstrings a funciones críticas (top 10)

### Fase 2: Refactorización Principal (3-5 días)

1. Refactorizar `setup_ui()` en `asignaciones_tab.py`
2. Refactorizar `mostrar_asignaciones()`
3. Agregar type hints a funciones públicas
4. Crear módulo `queries.py` para SQL

### Fase 3: Mejoras Adicionales (2-3 días)

1. Implementar sistema de logging
2. Agregar Enums para estados
3. Completar docstrings faltantes
4. Configurar pre-commit hooks

### Fase 4: Validación (1 día)

1. Ejecutar suite completa de análisis
2. Verificar que no se rompió funcionalidad
3. Actualizar `code_health_report.md`
4. Medir mejora en score (objetivo: 90+/100)

---

## 🎯 Objetivos de Mejora

| Métrica | Actual | Objetivo | Mejora |
|---------|--------|----------|--------|
| Score Global | 78/100 | 90+/100 | +12 puntos |
| Funciones Largas | 21 | <10 | -11 funciones |
| Sin Docstrings | 27 (9.7%) | <10 (3.5%) | -17 funciones |
| Código Duplicado | ~500 líneas | <100 líneas | -80% |
| Type Hints | ~30% | 80%+ | +50% |

---

## ⚠️ Advertencias Importantes

1. **NO refactorizar sin tests:** Antes de grandes refactorizaciones, crear tests unitarios
2. **Cambios incrementales:** Hacer commits pequeños y frecuentes
3. **Probar en desarrollo:** Siempre probar cambios antes de mergear a main
4. **Backup:** Tener backup del código funcional actual
5. **Documentar cambios:** Actualizar CLAUDE.md con cada mejora

---

## 📝 Notas Finales

### Compatibilidad Python 3.13.2

✅ El código actual es **100% compatible** con Python 3.13.2
✅ No se detectaron sintaxis deprecated
✅ Todos los imports son válidos

### Código Limpio

El código ya tiene:
- ✅ Codificación UTF-8 consistente
- ✅ Sin archivos obsoletos
- ✅ Sin imports sin usar
- ✅ Arquitectura MVC clara

### Siguientes Pasos

1. Revisar este documento con el equipo
2. Priorizar las mejoras según impacto/esfuerzo
3. Crear issues en Git para trackear cada mejora
4. Ejecutar CodeGuardian semanalmente para monitorear progreso

---

**Generado por:** CodeGuardian v1.0
**Fecha:** 2025-10-13
**Para:** Sistema de Gestión de Parqueadero v1.1

© 2025 - Recomendaciones de Mejora Continua
