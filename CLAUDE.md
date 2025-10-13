# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) al trabajar con código en este repositorio.

## Descripción General del Proyecto

Este es un **Sistema de Gestión de Parqueadero** para "Ssalud Plaza Claro" construido con Python y PyQt5. Gestiona 200 espacios de parqueo, empleados (funcionarios), sus vehículos y asignaciones de parqueadero con un sistema de circulación basado en "pico y placa" (días pares/impares).

**Versión:** 1.1
**Estado:** Producción-ready (con consideraciones de seguridad)
**Última actualización:** 2025-01-13

## Requisitos del Sistema

### Requisitos Previos
- **Python:** 3.8 o superior
- **MySQL Server:** 5.7 o superior
- **Sistema Operativo:** Windows, Linux o macOS

### Instalación de Dependencias

Las dependencias están documentadas en [requirements.txt](requirements.txt):

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `PyQt5>=5.15.0` - Framework GUI
- `mysql-connector-python>=8.0.0` - Conector MySQL

**Dependencias opcionales (para funcionalidad extendida):**
- `matplotlib>=3.10.0` - Gráficos estadísticos en pestaña Reportes
- `openpyxl>=3.1.0` - Exportación de reportes a Excel
- `reportlab>=3.6.0` - Exportación de reportes a PDF

> **Nota:** El sistema funciona sin estas dependencias opcionales, pero con funcionalidad reducida en el módulo de Reportes (solo exportación CSV estará disponible).

## Ejecutar la Aplicación

### Con Autenticación (Recomendado para Producción)
```bash
python main_with_auth.py
```
Inicia el sistema con ventana de login que autentica usuarios contra la tabla `usuarios`.

**Credenciales de prueba:**
- Usuario: `splaza`
- Contraseña: `splaza123*`

### Sin Autenticación (Desarrollo)
```bash
python main_modular.py
```
Omite la autenticación y abre la aplicación principal directamente.

## Configuración de la Base de Datos

### Credenciales por Defecto

Configuradas en [src/config/settings.py](src/config/settings.py):
- **Host:** localhost
- **Puerto:** 3306
- **Usuario:** root
- **Contraseña:** root
- **Base de datos:** parking_management

⚠️ **IMPORTANTE:** Las credenciales están en texto plano. Para producción, usar variables de entorno (ver sección de Seguridad).

### Configuración Inicial

Ejecutar los archivos de esquema en orden:

```bash
# 1. Esquema principal (tablas, triggers, vistas, procedimientos)
mysql -u root -p < parking_database_schema.sql

# 2. Tabla de usuarios para autenticación
mysql -u root -p < users_table_schema.sql
```

Esto creará:
- Base de datos `parking_management`
- 200 espacios de parqueadero pre-configurados (distribuidos en 3 sótanos)
- Triggers automáticos para gestión de pico y placa
- Usuario administrador de prueba

## Arquitectura del Sistema

### Estructura Modular

```
parking_system/
├── main_with_auth.py          # Punto de entrada CON autenticación
├── main_modular.py             # Punto de entrada SIN autenticación
├── requirements.txt            # Dependencias del proyecto
├── CLAUDE.md                   # Documentación del proyecto (este archivo)
├── REPORTE_LIMPIEZA.md        # Informe de limpieza del código
│
├── parking_database_schema.sql # Esquema principal de BD
├── users_table_schema.sql      # Tabla de autenticación
│
└── src/
    ├── auth/                   # Sistema de autenticación
    │   ├── auth_manager.py     # Gestor de autenticación
    │   └── login_window.py     # Ventana de login
    │
    ├── config/                 # Configuración
    │   └── settings.py         # Configuración BD y constantes
    │
    ├── database/               # Capa de datos
    │   ├── manager.py          # Singleton para conexiones BD
    │   └── eliminacion_cascada.py  # Lógica de eliminación en cascada
    │
    ├── models/                 # Lógica de negocio (CRUD)
    │   ├── funcionario.py      # Modelo Funcionario
    │   ├── vehiculo.py         # Modelo Vehículo
    │   └── parqueadero.py      # Modelo Parqueadero
    │
    ├── ui/                     # Interfaz gráfica (Pestañas)
    │   ├── dashboard_tab.py    # Dashboard principal
    │   ├── funcionarios_tab.py # Gestión de empleados
    │   ├── vehiculos_tab.py    # Gestión de vehículos
    │   ├── asignaciones_tab.py # Asignación de parqueaderos
    │   ├── parqueaderos_tab.py # Vista de parqueaderos
    │   ├── reportes_tab.py     # Módulo de reportes y estadísticas (NUEVO v1.1)
    │   ├── modal_detalle_parqueadero.py  # Modal de detalles
    │   └── modales_vehiculos.py          # Modales CRUD vehículos
    │
    ├── utils/                  # Utilidades y validaciones
    │   ├── validaciones.py     # Validadores centralizados
    │   ├── validaciones_vehiculos.py     # Validaciones de vehículos
    │   └── validaciones_asignacion.py    # Validaciones de asignación
    │
    └── widgets/                # Componentes reutilizables
        ├── parking_widget.py   # Widget de espacio de parqueadero
        └── styles.py           # Estilos de la aplicación
```

### Patrones Arquitectónicos Clave

**1. Arquitectura MVC Modular**
- **Modelos** ([src/models/](src/models/)) - Lógica de negocio y operaciones de base de datos
- **Vistas** ([src/ui/](src/ui/)) - Presentación e interacción con el usuario
- **Controladores** - Integrados en las vistas mediante señales PyQt

**2. Gestor de Base de Datos (Singleton)**
- [src/database/manager.py](src/database/manager.py) implementa un patrón singleton para conexiones de base de datos
- Todas las operaciones de base de datos pasan por `DatabaseManager.fetch_all()`, `fetch_one()`, o `execute_query()`
- La lógica de reconexión automática asegura conexiones resilientes

**3. Comunicación Basada en Señales (PyQt)**
- La ventana principal ([main_modular.py](main_modular.py)) conecta señales PyQt entre pestañas para sincronización en tiempo real
- Cuando los datos cambian en una pestaña (ej. eliminar un funcionario), las señales propagan actualizaciones a todas las pestañas afectadas
- Ver `MainWindow.conectar_senales()` en [main_modular.py:73-117](main_modular.py#L73-L117) para el grafo completo de señales

**4. Sistema de Eliminación en Cascada**
- [src/database/eliminacion_cascada.py](src/database/eliminacion_cascada.py) implementa eliminación en cascada completa
- Cuando un funcionario es eliminado, se remueven TODOS los datos asociados:
  - Vehículos → Asignaciones → Espacios de parqueo (liberados) → Historial de accesos
- Usa transacciones de base de datos para asegurar atomicidad
- Incluye lógica de verificación para confirmar eliminación completa

**5. Separación Modelo-Vista**
- Los modelos ([src/models/](src/models/)) manejan lógica de negocio y operaciones de base de datos
- Los componentes UI ([src/ui/](src/ui/)) manejan presentación e interacción con el usuario
- Cada entidad principal (Funcionario, Vehiculo, Parqueadero, Asignacion) tiene su propio modelo y pestaña

**6. Validaciones Centralizadas**
- [src/utils/](src/utils/) contiene validadores reutilizables
- Validaciones de campos, reglas de negocio y permisos
- Mensajes de error consistentes en toda la aplicación

**7. Módulo de Reportes y Estadísticas** (NUEVO en v1.1)
- [src/ui/reportes_tab.py](src/ui/reportes_tab.py) contiene el sistema completo de reportes
- 7 sub-pestañas especializadas con visualización tabular
- Exportación a múltiples formatos (CSV, Excel, PDF)
- Visualizaciones estadísticas con matplotlib (3 gráficos en tiempo real)
- Filtros avanzados por tipo de vehículo, cargo y rango de fechas
- Actualización automática mediante señales PyQt cuando cambian los datos
- Degradación elegante: funciona sin dependencias opcionales

## Reglas de Negocio Críticas

### Lógica de Pico y Placa

**Cálculo automático:**
- Carros con último dígito de placa **1-5** → **IMPAR**
- Carros con último dígito de placa **6-9, 0** → **PAR**
- Calculado automáticamente mediante trigger de base de datos `before_insert_vehiculo`
- Solo aplica a **Carros** (Motos y Bicicletas tienen tipo de circulación N/A)

**Compartición de espacios:**
- Cada espacio de parqueo puede contener hasta **2 carros**
- DEBEN tener diferentes tipos de circulación (uno PAR, uno IMPAR)
- Validado automáticamente por triggers

### Estados de Espacios de Parqueo

- `Disponible` - Vacío (0 carros asignados)
- `Parcialmente_Asignado` - 1 carro asignado
- `Completo` - 2 carros asignados (uno PAR, uno IMPAR) o parqueadero exclusivo

Los estados se actualizan automáticamente mediante triggers `after_insert_asignacion` y `after_update_asignacion`.

### Reglas de Funcionarios

**Checkboxes mutuamente excluyentes** (solo uno puede estar activo):

1. **🔄 Pico y Placa Solidario**
   - Ignora restricciones PAR/IMPAR
   - Puede usar el parqueadero cualquier día

2. **♿ Funcionario con Discapacidad**
   - Prioridad para espacios especiales
   - Permite compartir parqueadero normalmente

3. **🚫 Parqueadero Exclusivo (No compartir)**
   - `permite_compartir = FALSE`
   - El espacio queda marcado como `Completo` inmediatamente
   - Solo este funcionario puede usar ese parqueadero

Si ningún checkbox está marcado, el funcionario es regular y comparte normalmente según las reglas de pico y placa.

### Restricciones de Unicidad

- La `cedula` del empleado debe ser **única** en todo el sistema
- La `placa` del vehículo debe ser **única**
- Un vehículo solo puede tener **una asignación activa** a la vez (forzado por clave única en `vehiculo_id, activo`)

## Módulo de Reportes (NUEVO v1.1)

El sistema incluye un módulo completo de reportes en [src/ui/reportes_tab.py](src/ui/reportes_tab.py) con 7 sub-pestañas:

### Sub-pestañas de Reportes

1. **📋 Reporte General** - Vista consolidada de funcionarios, vehículos y parqueaderos (11 columnas)
2. **👥 Funcionarios** - Listado completo de empleados con contador de vehículos
3. **🚗 Vehículos** - Registro de todos los vehículos con estado de asignación
4. **🅿️ Parqueaderos** - Estado de 200 espacios en 3 sótanos con ocupación detallada
5. **📍 Asignaciones** - Asignaciones activas con información completa
6. **🔄 Excepciones Pico y Placa** - Funcionarios con permisos especiales (solidario, discapacidad, exclusivo)
7. **📊 Estadísticas** - Visualización gráfica en tiempo real (requiere matplotlib)

### Funcionalidades de Exportación

Cada reporte puede exportarse a 3 formatos:

- **CSV** - Siempre disponible, sin dependencias adicionales
- **Excel (.xlsx)** - Requiere `openpyxl`. Headers estilizados, columnas auto-ajustadas
- **PDF** - Requiere `reportlab`. Formato horizontal con estilos corporativos

### Visualizaciones Estadísticas (Pestaña 7)

Requiere matplotlib para funcionar. Si no está instalado, muestra mensaje informativo.

**Gráficos disponibles:**
1. **Ocupación de Parqueaderos** - Gráfico de pastel (Disponible/Parcial/Completo)
2. **Distribución de Vehículos** - Gráfico de barras por tipo (Carro/Moto/Bicicleta)
3. **Funcionarios por Cargo** - Gráfico horizontal con Top 10 cargos

### Filtros Avanzados

El módulo incluye filtros globales que afectan todos los reportes:
- **Tipo de Vehículo:** Todos, Carro, Moto, Bicicleta
- **Cargo:** Lista completa de cargos disponibles
- **Rango de Fechas:** Fecha inicio y fecha fin con selector de calendario

### Actualización Automática

Los reportes se actualizan automáticamente cuando:
- Se modifica un funcionario
- Se crea/elimina un vehículo
- Se asigna/libera un parqueadero
- El usuario presiona el botón "🔄 Actualizar Todos los Reportes"

Esto se logra mediante conexión de señales PyQt:
```python
# En main_modular.py
self.tab_asignaciones.asignacion_actualizada.connect(
    self.tab_reportes.actualizar_reportes
)
self.tab_parqueaderos.parqueaderos_actualizados.connect(
    self.tab_reportes.actualizar_reportes
)
```

### Manejo de Errores

El módulo implementa degradación elegante:
- Si falta matplotlib → estadísticas no disponibles, resto funciona
- Si falta openpyxl → Excel no disponible, CSV y PDF funcionan
- Si falta reportlab → PDF no disponible, CSV y Excel funcionan
- Si un reporte individual falla → otros reportes continúan funcionando

Ver [INTEGRACION_REPORTES.md](INTEGRACION_REPORTES.md) para documentación técnica completa.

## Flujos de Desarrollo Comunes

### Agregar una Nueva Pestaña UI

1. **Crear nuevo archivo** en [src/ui/](src/ui/)
```python
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class NuevaPestañaTab(QWidget):
    # Definir señales
    datos_actualizados = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.setup_ui()
```

2. **Agregar pestaña** a [main_modular.py](main_modular.py) en `setup_ui()`:
```python
self.nueva_tab = NuevaPestañaTab(self.db)
self.tabs.addTab(self.nueva_tab, "Nueva Pestaña")
```

3. **Conectar señales** en `conectar_senales()`:
```python
self.nueva_tab.datos_actualizados.connect(
    self.dashboard_tab.actualizar_dashboard
)
```

### Modificar el Esquema de Base de Datos

1. Actualizar [parking_database_schema.sql](parking_database_schema.sql)
2. Probar localmente:
```bash
mysql -u root -p
DROP DATABASE parking_management;
SOURCE parking_database_schema.sql;
```
3. Actualizar clases de modelo en [src/models/](src/models/) si es necesario
4. Actualizar triggers si el comportamiento de cascada cambia

### Probar Eliminación en Cascada

El sistema de eliminación en cascada es crítico. Para probar:

```python
from src.database.eliminacion_cascada import GestorEliminacionCascada

gestor = GestorEliminacionCascada(db_manager)

# Previsualizar lo que será eliminado
reporte = gestor.generar_reporte_previa_eliminacion("12345678")  # cedula
print(reporte)

# Ejecutar eliminación
exito, mensaje, detalles = gestor.eliminar_funcionario_completo("12345678")
```

## Configuración de Base de Datos

Configuración por defecto en [src/config/settings.py](src/config/settings.py):
- Modificar dataclass `DatabaseConfig` para cambiar configuración de conexión
- Actualizar `CARGOS_DISPONIBLES` y `DIRECCIONES_DISPONIBLES` para opciones de menús desplegables
- Los enums `TipoVehiculo` y `TipoCirculacion` definen tipos de vehículos válidos

## Archivos Importantes

### Archivos Principales
- [main_with_auth.py](main_with_auth.py) - Punto de entrada con autenticación
- [main_modular.py](main_modular.py) - Ventana principal de aplicación y conexiones de señales
- [requirements.txt](requirements.txt) - Dependencias del proyecto
- [REPORTE_LIMPIEZA.md](REPORTE_LIMPIEZA.md) - Informe de limpieza del código
- [INTEGRACION_REPORTES.md](INTEGRACION_REPORTES.md) - Documentación del módulo de reportes (NUEVO v1.1)

### Base de Datos
- [parking_database_schema.sql](parking_database_schema.sql) - Esquema completo de base de datos con triggers
- [users_table_schema.sql](users_table_schema.sql) - Tabla de autenticación

### Módulos Core
- [src/database/manager.py](src/database/manager.py) - Capa de abstracción de base de datos (Singleton)
- [src/database/eliminacion_cascada.py](src/database/eliminacion_cascada.py) - Lógica de eliminación en cascada
- [src/config/settings.py](src/config/settings.py) - Todas las constantes de configuración

## Sistema de Autenticación

Los usuarios se autentican mediante [src/auth/auth_manager.py](src/auth/auth_manager.py):
- Las contraseñas se almacenan en texto plano (**NO LISTO PARA PRODUCCIÓN**)
- Los usuarios tienen roles (almacenados en columna `rol`)
- Se rastrea la marca de tiempo del último acceso
- Ventana de login: [src/auth/login_window.py](src/auth/login_window.py)

### ⚠️ Advertencia de Seguridad

**Para producción, implementar:**

1. **Variables de entorno** con `python-dotenv`:
```python
# Crear archivo .env (NO commitear a Git)
DB_PASSWORD=tu_password_real
DB_USER=root

# Modificar src/config/settings.py
from os import getenv
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    password: str = getenv("DB_PASSWORD", "root")
```

2. **Hash de contraseñas** con `bcrypt`:
```python
import bcrypt

# Al crear usuario
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Al verificar
bcrypt.checkpw(password.encode('utf-8'), stored_hash)
```

## Notas Importantes

### Características del Sistema
- El sistema usa PyQt5 para la GUI con un estilo "Fusion" personalizado
- Todo el texto está en español
- El código usa codificación UTF-8
- Los triggers de base de datos manejan la mayor parte de la gestión de estado automáticamente
- Las conexiones de señales aseguran que la UI se mantenga sincronizada en todas las pestañas

### Código Limpio
- **Última limpieza:** 2025-01-05
- Sin código duplicado ni archivos obsoletos
- Sin imports sin usar
- Archivos compilados (`__pycache__`, `*.pyc`) correctamente ignorados en `.gitignore`
- Ver [REPORTE_LIMPIEZA.md](REPORTE_LIMPIEZA.md) para detalles completos

### Estilo y Componentes UI
- PyQt5 con tema "Fusion" personalizado
- Estilos CSS centralizados en [src/widgets/styles.py](src/widgets/styles.py)
- ComboBoxes con flechas CSS personalizadas (sin dependencias de imágenes)
- Paleta de colores consistente: #2196F3 (azul primario), #27ae60 (verde éxito), #e74c3c (rojo error)
- Todos los textos en español con codificación UTF-8

### Gestión de Archivos Temporales
```bash
# Limpiar archivos compilados (se regeneran automáticamente)
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## Métricas del Proyecto

- **Líneas de código:** ~10,600 (después de agregar módulo de reportes)
- **Archivos Python:** 30
- **Pestañas principales:** 6 (Dashboard, Funcionarios, Vehículos, Parqueaderos, Asignaciones, Reportes)
- **Sub-pestañas de Reportes:** 7
- **Arquitectura:** MVC Modular
- **Cobertura de tests:** Sin tests (pendiente para v2.0)

---

**Última actualización:** 2025-01-13
**Versión:** 1.1
**Estado:** Producción-ready con mejoras de seguridad recomendadas
**Mantenedor:** Carlos Ivan Perdomo

**Novedades v1.1:**
- Módulo completo de Reportes con 7 sub-pestañas
- Exportación a CSV, Excel y PDF
- Visualizaciones estadísticas con matplotlib
- Filtros avanzados por tipo de vehículo, cargo y fechas
- Mejoras visuales en ComboBoxes (flechas CSS)
- **Agente CodeGuardian** para análisis y refactorización automática

## 🛡️ CodeGuardian - Agente de Calidad de Código

El proyecto incluye **CodeGuardian**, un agente especializado para mantener la calidad del código:

### Uso

```bash
# Opción 1: Comando slash en Claude Code
/codeguardian

# Opción 2: Script directo
python .claude/codeguardian_analyzer.py
```

### Funcionalidades

✅ **Análisis automático** de todo el repositorio
✅ **Verificación Python 3.13.2** - Compatibilidad exacta
✅ **Detección de funciones largas** (>100 líneas)
✅ **Análisis de documentación** - Funciones/clases sin docstrings
✅ **Métricas de código** - Líneas, funciones, clases, complejidad
✅ **Reporte detallado** - Genera `code_health_report.md` con score 0-100
✅ **Integración con herramientas** - ruff, flake8, black, isort, pylint

### Reporte Generado

El último análisis (2025-10-13) muestra:
- **31 archivos Python** analizados
- **11,348 líneas** de código
- **279 funciones** y **33 clases**
- **Score: 78/100** - Buen estado con mejoras pendientes
- **21 funciones largas** identificadas (prioridad: refactorización)
- **27 funciones sin docstring** (9.7%)

### Archivos Prioritarios para Refactorización

1. `src/ui/asignaciones_tab.py` - 1,714 líneas (función `setup_ui`: 484 líneas)
2. `src/ui/reportes_tab.py` - 1,491 líneas
3. `src/ui/funcionarios_tab.py` - 1,132 líneas

Ver [.claude/README_CODEGUARDIAN.md](.claude/README_CODEGUARDIAN.md) para documentación completa.

© 2025 - Sistema de Gestión de Parqueadero
