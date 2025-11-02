# CLAUDE.md - Sistema de Gestión de Parqueaderos

> Documentación oficial del proyecto PARKING_SYSTEM para Claude Code (claude.ai/code)

**Versión:** 2.0.5
**Estado:** Producción
**Última actualización:** 2025-10-26

---

## 🧩 Descripción del Proyecto

**PARKING_SYSTEM** es un sistema integral de gestión de parqueaderos desarrollado para "Salud Plaza Claro", que permite administrar de manera eficiente **200 espacios de parqueo** distribuidos en 3 sótanos, junto con la gestión de empleados (funcionarios), sus vehículos y las asignaciones de espacios.

### Características Principales

- 📊 **Dashboard en tiempo real** con estadísticas y visualización de ocupación
- 👥 **Gestión de funcionarios** con validación de cédulas y cargos
- 🚗 **Gestión de vehículos** (Carros, Motos, Bicicletas, Carros Híbridos)
- 🅿️ **Asignación inteligente** basada en reglas de pico y placa (PAR/IMPAR/N/A)
- 🏢 **Parqueaderos exclusivos** para directivos (números 1-20 por sótano)
- 📈 **Módulo de reportes** con exportación a CSV/Excel/PDF
- 🔐 **Sistema de autenticación** con bcrypt y protección contra fuerza bruta
- 🔄 **Sincronización en tiempo real** entre todas las pestañas usando señales PyQt5
- 📝 **Logging profesional** con RotatingFileHandler
- ⚙️ **Configuración basada en .env** para seguridad en producción
- 🗑️ **Borrado lógico** de funcionarios preservando historial completo
- 🔍 **Búsqueda en tiempo real** por cédula con filtrado instantáneo
- 📄 **Paginación inteligente** con máximo 5 registros por página
- ♻️ **Reactivación de funcionarios** con restauración completa de vehículos

### Modelo de Negocio

El sistema implementa un modelo de **circulación vehicular** basado en días PAR/IMPAR:

- **PAR**: Vehículos que circulan días pares (2, 4, 6, 8, 10...)
- **IMPAR**: Vehículos que circulan días impares (1, 3, 5, 7, 9...)
- **N/A**: Vehículos sin restricción (directivos, motos, bicicletas, carros híbridos)

**Regla de compartición**: Un espacio de parqueo puede ser compartido por máximo 2 carros con circulaciones complementarias (PAR + IMPAR).

---

## 🆕 Funcionalidades Recientes (v2.0.4 - v2.0.5)

### 1. Borrado Lógico de Funcionarios (v2.0.4)

**Implementación:** Octubre 2025

El sistema ahora utiliza **borrado lógico** en lugar de eliminación física para preservar el historial completo:

**Características:**
- ✅ Funcionarios marcados como `activo = FALSE` en lugar de eliminarse
- ✅ Vehículos asociados también se desactivan (preservando historial)
- ✅ Asignaciones de parqueaderos se liberan automáticamente
- ✅ Parqueaderos vuelven a estado "Disponible" mediante triggers actualizados
- ✅ Toda la operación registrada en logs con detalles completos

**Archivos relacionados:**
- `src/models/funcionario.py` - Método `eliminar()` actualizado
- `fix_triggers_borrado_logico.sql` - Triggers actualizados con filtro `activo = TRUE`
- `CAMBIO_BORRADO_LOGICO.md` - Documentación completa

**Consulta SQL para verificar:**
```sql
-- Ver funcionarios inactivos con su historial
SELECT * FROM funcionarios WHERE activo = FALSE;

-- Ver vehículos de funcionarios inactivos
SELECT v.* FROM vehiculos v
JOIN funcionarios f ON v.funcionario_id = f.id
WHERE f.activo = FALSE;
```

### 2. Columna Estado y Reactivación (v2.0.4)

**Implementación:** Octubre 2025

Nueva columna visual "Estado" en la tabla de funcionarios con capacidad de reactivación:

**Características:**
- ✅ Columna "Estado" muestra "Activo" (verde) o "Inactivo" (rojo)
- ✅ Botones dinámicos según estado:
  - **Activos:** ✏️ Editar, 👁️ Ver, 🗑️ Eliminar
  - **Inactivos:** 👁️ Ver, 🔄 Reactivar
- ✅ Reactivación restaura funcionario y todos sus vehículos
- ✅ Actualización automática de todas las pestañas vía señales PyQt5

**Archivos relacionados:**
- `src/ui/funcionarios_tab.py` - UI actualizada con columna Estado
- `src/models/funcionario.py` - Métodos `reactivar()` y `obtener_todos_incluyendo_inactivos()`
- `FEATURE_ESTADO_ACTIVO_INACTIVO.md` - Documentación completa

### 3. Filtro de Búsqueda por Cédula (v2.0.4)

**Implementación:** Octubre 2025

Búsqueda en tiempo real para localizar funcionarios rápidamente:

**Características:**
- ✅ Búsqueda instantánea mientras escribes
- ✅ Búsqueda parcial (no requiere cédula completa)
- ✅ Contador de resultados en tiempo real
- ✅ Botón "Limpiar" para resetear búsqueda
- ✅ Indicadores visuales (verde: encontrados, rojo: sin resultados)

**Ejemplo de uso:**
```
Buscar: "1234" → Muestra todos los funcionarios con "1234" en la cédula
Buscar: "12345678" → Muestra solo el funcionario con esa cédula exacta
```

**Archivos relacionados:**
- `src/ui/funcionarios_tab.py` - Barra de búsqueda y método `filtrar_funcionarios()`
- `FEATURE_FILTRO_BUSQUEDA_FUNCIONARIOS.md` - Documentación completa

### 4. Paginación de Tabla de Funcionarios (v2.0.5)

**Implementación:** Octubre 2025

Sistema de paginación completo para mejorar rendimiento y experiencia de usuario:

**Características:**
- ✅ Máximo **5 funcionarios por página**
- ✅ Controles de navegación completos:
  - **<<** Primera página
  - **<** Página anterior
  - **>** Página siguiente
  - **>>** Última página
- ✅ Indicador "Página X de Y"
- ✅ Contador total "Total: X funcionarios"
- ✅ Botones deshabilitados inteligentemente (grises cuando no aplican)
- ✅ Integración perfecta con búsqueda (resultados también paginados)

**Ventajas:**
- 🚀 **Rendimiento:** Solo renderiza 5 filas, carga instantánea
- 👁️ **Claridad:** Vista limpia sin scroll infinito
- 📊 **Escalabilidad:** Funciona igual con 10 o 1000 funcionarios

**Configuración:**
```python
# src/ui/funcionarios_tab.py, línea 46
self.filas_por_pagina = 5  # Cambiar según necesidad
```

**Archivos relacionados:**
- `src/ui/funcionarios_tab.py` - Sistema completo de paginación
- `FEATURE_PAGINACION_FUNCIONARIOS.md` - Documentación completa

### 5. Sincronización Mejorada entre Pestañas (v2.0.4)

**Implementación:** Octubre 2025

Sincronización automática de vehículos al reactivar funcionarios:

**Antes:**
- ❌ Al reactivar funcionario, vehículos no aparecían hasta reiniciar aplicación

**Después:**
- ✅ Al reactivar funcionario, pestaña Vehículos se actualiza automáticamente
- ✅ Emite señal `funcionario_eliminado` que refresca todas las pestañas
- ✅ Sincronización instantánea: Funcionarios → Vehículos → Asignaciones → Parqueaderos

**Implementación técnica:**
```python
# src/ui/funcionarios_tab.py, línea 969-971
self.funcionario_creado.emit()      # Actualiza combos y dashboard
self.funcionario_eliminado.emit()   # Actualiza tabla de vehículos
```

---

## ⚙️ Tecnologías Utilizadas

### Backend & Core

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.8+ | Lenguaje principal |
| **MySQL** | 5.7+ | Base de datos relacional |
| **mysql-connector-python** | 8.0+ | Conector de BD |
| **bcrypt** | 4.0+ | Hash de contraseñas |
| **python-dotenv** | 1.0+ | Variables de entorno |

### Frontend & UI

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **PyQt5** | 5.15+ | Framework GUI |
| **QSS** | - | Estilos personalizados |

### Reportes & Visualización

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **matplotlib** | 3.10+ | Gráficos estadísticos |
| **openpyxl** | 3.1+ | Exportación Excel |
| **reportlab** | 3.6+ | Exportación PDF |

### Testing & Quality

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **pytest** | 7.0+ | Framework de testing |
| **pytest-mock** | 3.0+ | Mocking para tests |
| **unittest.mock** | - | Mocks de BD |

### Base de Datos

**Motor**: MySQL 5.7+

**Características utilizadas**:
- Triggers automáticos (gestión de estados)
- Procedimientos almacenados
- Vistas materializadas
- Transacciones ACID
- Índices compuestos para optimización

---
## 🚀 Instalación y Ejecución

### Requisitos Previos

- **Python 3.8 o superior**
- **MySQL Server 5.7 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)

### Paso 1: Clonar el Repositorio

```bash
git clone <repository-url>
cd parking_system
```

### Paso 2: Instalar Dependencias

```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# O instalar solo las dependencias principales (sin reportes avanzados)
pip install PyQt5 mysql-connector-python bcrypt python-dotenv
```

**Dependencias opcionales** (para funcionalidad completa de reportes):
```bash
pip install matplotlib openpyxl reportlab
```

### Paso 3: Configurar Variables de Entorno

```bash
# Copiar plantilla de configuración
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o usar tu editor favorito
```

**Variables importantes en .env**:
```bash
# Base de datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password_real
DB_NAME=parking_management

# Seguridad
DEBUG=false
SECRET_KEY=<generar_clave_segura_64_caracteres>

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs
```

**Generar SECRET_KEY seguro**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Paso 4: Configurar Base de Datos

```bash
# 1. Crear base de datos y tablas principales
mysql -u root -p < parking_database_schema.sql

# 2. Crear tabla de usuarios para autenticación
mysql -u root -p < users_table_schema.sql
```

Esto creará:
- Base de datos `parking_management`
- 200 espacios de parqueadero pre-configurados
- Triggers automáticos para gestión de estados
- Usuario administrador de prueba: `splaza` / `splaza123*`

### Paso 5: Ejecutar la Aplicación

#### Producción (con autenticación):
```bash
python main_with_auth.py
```

#### Desarrollo (sin autenticación):
```bash
python main_modular.py
```

### Paso 6: Verificar Instalación

```bash
# Verificar configuración
python -c "from src.config.settings import print_config_summary; print_config_summary()"

# Ejecutar tests
pytest tests/ -v

# Ver logs
tail -f logs/parking_system.log
```

---

## 🧱 Estructura del Proyecto

```
parking_system/
│
├── 📄 main_with_auth.py          # Punto de entrada CON autenticación ⭐
├── 📄 main_modular.py             # Punto de entrada SIN autenticación (desarrollo)
├── 📄 requirements.txt            # Dependencias del proyecto
├── 📄 .env.example                # Plantilla de variables de entorno
├── 📄 .gitignore                  # Archivos ignorados por Git
│
├── 📁 docs/                       # Documentación
│   └── CLAUDE.md                  # Este archivo
│
├── 📁 tests/                      # Suite de tests ⭐
│   ├── conftest.py                # Fixtures compartidos
│   ├── test_imports.py            # Tests de importación
│   ├── test_models.py             # Tests de modelos
│   ├── test_database.py           # Tests de BD
│   └── test_auth.py               # Tests de autenticación
│
├── 📁 logs/                       # Archivos de log (auto-creado)
│   └── parking_system.log         # Log principal
│
├── 📁 reports/                    # Reportes exportados (auto-creado)
│
├── 📄 parking_database_schema.sql # Esquema principal de BD
├── 📄 users_table_schema.sql      # Tabla de autenticación
│
└── 📁 src/                        # Código fuente principal
    │
    ├── 📄 __init__.py             # Inicialización del paquete
    ├── 📄 __main__.py             # Entry point alternativo
    │
    ├── 📁 core/                   # Módulos centrales ⭐ NUEVO
    │   ├── __init__.py
    │   └── logger.py              # Sistema de logging profesional
    │
    ├── 📁 auth/                   # Autenticación y seguridad
    │   ├── __init__.py
    │   ├── auth_manager.py        # Gestor de autenticación (bcrypt)
    │   └── login_window.py        # Ventana de login (PyQt5)
    │
    ├── 📁 config/                 # Configuración
    │   ├── __init__.py
    │   └── settings.py            # Configuración centralizada con .env ⭐
    │
    ├── 📁 database/               # Capa de acceso a datos
    │   ├── __init__.py
    │   ├── manager.py             # DatabaseManager (Singleton)
    │   └── eliminacion_cascada.py # Lógica de eliminación en cascada
    │
    ├── 📁 models/                 # Modelos de negocio (CRUD)
    │   ├── __init__.py
    │   ├── funcionario.py         # Modelo Funcionario
    │   ├── vehiculo.py            # Modelo Vehículo
    │   └── parqueadero.py         # Modelo Parqueadero
    │
    ├── 📁 ui/                     # Interfaz gráfica (PyQt5)
    │   ├── __init__.py
    │   ├── dashboard_tab.py       # Dashboard principal
    │   ├── funcionarios_tab.py    # Gestión de empleados
    │   ├── vehiculos_tab.py       # Gestión de vehículos
    │   ├── asignaciones_tab.py    # Asignación de parqueaderos
    │   ├── parqueaderos_tab.py    # Visualización de parqueaderos
    │   ├── reportes_tab.py        # Módulo de reportes y estadísticas
    │   ├── modal_detalle_parqueadero.py  # Modal de detalles
    │   └── modales_vehiculos.py   # Modales CRUD vehículos
    │
    ├── 📁 utils/                  # Utilidades y validaciones
    │   ├── __init__.py
    │   ├── formatters.py          # Formateadores de datos ⭐ NUEVO
    │   ├── validaciones.py        # Validadores centralizados
    │   ├── validaciones_vehiculos.py      # Validaciones de vehículos
    │   └── validaciones_asignaciones.py   # Validaciones de asignación
    │
    └── 📁 widgets/                # Componentes UI reutilizables
        ├── __init__.py
        ├── parking_widget.py      # Widget de espacio de parqueadero
        └── styles.py              # Estilos QSS de la aplicación
```

### Arquitectura MVC Modular

El proyecto sigue una arquitectura **Modelo-Vista-Controlador (MVC)** con separación clara de responsabilidades:

#### **Modelos** (`src/models/`)
- Lógica de negocio
- Operaciones CRUD
- Validaciones de datos
- Interacción con la base de datos

#### **Vistas** (`src/ui/`)
- Presentación visual (PyQt5)
- Interacción con el usuario
- Renderizado de componentes
- Manejo de eventos UI

#### **Controladores** (integrados en vistas)
- Coordinación entre modelo y vista
- Manejo de señales PyQt5
- Lógica de presentación

### Patrones de Diseño Implementados

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **Singleton** | `DatabaseManager` | Única instancia de conexión BD |
| **Observer** | Señales PyQt5 | Sincronización entre pestañas |
| **Factory** | Modales de vehículos | Creación dinámica de formularios |
| **Strategy** | Validaciones | Diferentes estrategias de validación |
| **Repository** | Models | Abstracción de acceso a datos |

---

## 🔐 Autenticación

### Sistema de Autenticación (v2.0+)

El sistema implementa un **sistema de autenticación robusto** con las siguientes características:

#### Características de Seguridad

1. **Hash de contraseñas con bcrypt**
   - Contraseñas nunca almacenadas en texto plano
   - Salt único por contraseña
   - Factor de costo configurable (default: 12)

2. **Protección contra fuerza bruta**
   - Máximo 5 intentos fallidos por usuario
   - Bloqueo temporal de 15 minutos tras exceder intentos
   - Contador de intentos restantes mostrado al usuario

3. **Logging de eventos de seguridad**
   - Todos los intentos de login (exitosos y fallidos) son registrados
   - Bloqueos de cuenta registrados con timestamp
   - Logs almacenados en `logs/parking_system.log`

4. **Gestión de sesiones**
   - Sesión activa almacenada en memoria
   - Timeout configurable (default: 480 minutos)
   - Cierre de sesión manual disponible

### Credenciales de Prueba

**Usuario administrador** (creado automáticamente):
- **Usuario:** `splaza`
- **Contraseña:** `splaza123*`
- **Rol:** Administrador

### Estructura de la Tabla `usuarios`

```sql
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARBINARY(60) NOT NULL,  -- bcrypt hash
    rol ENUM('Administrador', 'Usuario') DEFAULT 'Usuario',
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP NULL,
    INDEX idx_usuario (usuario),
    INDEX idx_activo (activo)
);
```

### Flujo de Autenticación

```
┌─────────────┐
│ Login Form  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│ AuthManager.authenticate()  │
└──────┬──────────────────────┘
       │
       ├──► ¿Usuario bloqueado? ──► SÍ ──► Mostrar tiempo restante
       │                           NO
       ├──► ¿Usuario existe?    ──► NO ──► Registrar intento fallido
       │                           SÍ
       ├──► bcrypt.checkpw()    ──► FAIL ──► Registrar intento fallido
       │                           PASS
       ├──► Limpiar intentos fallidos
       ├──► Crear sesión (current_user)
       ├──► Actualizar último_acceso
       └──► Log: LOGIN_SUCCESS
                │
                ▼
       ┌────────────────┐
       │  Main Window   │
       └────────────────┘
```

### Uso Programático

```python
from src.auth.auth_manager import AuthManager

# Crear instancia
auth = AuthManager()

# Autenticar usuario
success, message = auth.authenticate("splaza", "splaza123*")

if success:
    # Obtener información del usuario actual
    user = auth.get_current_user()
    print(f"Bienvenido, {user['usuario']}")
else:
    print(f"Error: {message}")

# Cerrar sesión
auth.logout()
```

### Eventos de Seguridad Registrados

Los siguientes eventos se registran automáticamente:

| Evento | Nivel | Formato |
|--------|-------|---------|
| Login exitoso | INFO | `LOGIN_SUCCESS \| User: {usuario} \| ID: {id}` |
| Login fallido | WARNING | `LOGIN_FAILED \| User: {usuario} \| Reason: {razon}` |
| Cuenta bloqueada | WARNING | `LOGIN_BLOCKED \| User: {usuario} \| Remaining: {tiempo}s` |
| Logout | INFO | `LOGOUT \| User: {usuario}` |
| Error de autenticación | ERROR | `LOGIN_ERROR \| User: {usuario} \| Error: {error}` |

### Ejemplo de Logs

```
2025-10-26 15:23:45 - parking_system - INFO - AuthManager inicializado correctamente
2025-10-26 15:24:12 - auth_manager - INFO - LOGIN_SUCCESS | User: splaza | ID: 1
2025-10-26 15:45:30 - auth_manager - INFO - LOGOUT | User: splaza
2025-10-26 15:46:01 - auth_manager - WARNING - LOGIN_FAILED | User: admin | Reason: User not found
```

---

## 🧑‍💻 Cómo Contribuir

### Guía para Contribuidores

Agradecemos las contribuciones al proyecto. Por favor, sigue estas pautas:

#### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clonar tu fork
git clone https://github.com/tu-usuario/parking_system.git
cd parking_system

# Añadir upstream
git remote add upstream https://github.com/original-repo/parking_system.git
```

#### 2. Crear Branch de Desarrollo

```bash
# Crear branch desde main
git checkout -b feature/nombre-de-tu-feature

# O para bugs
git checkout -b fix/descripcion-del-bug
```

**Convención de nombres de branches**:
- `feature/` - Nuevas funcionalidades
- `fix/` - Correcciones de bugs
- `refactor/` - Refactorización de código
- `docs/` - Cambios en documentación
- `test/` - Añadir o corregir tests

#### 3. Configurar Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install pytest pytest-mock

# Copiar configuración de desarrollo
cp .env.example .env

# Configurar BD de pruebas (opcional)
mysql -u root -p < parking_database_schema.sql
```

#### 4. Hacer Cambios

**Estándares de código**:
- **PEP 8**: Seguir guía de estilo de Python
- **Type hints**: Usar anotaciones de tipo cuando sea posible
- **Docstrings**: Documentar funciones y clases
- **Comentarios**: Código auto-explicativo, comentarios solo cuando sea necesario

**Ejemplo**:
```python
def calcular_ocupacion(sotano: int) -> float:
    """
    Calcula el porcentaje de ocupación de un sótano.

    Args:
        sotano: Número de sótano (1, 2, o 3)

    Returns:
        float: Porcentaje de ocupación (0.0 a 100.0)

    Raises:
        ValueError: Si el sótano no es válido
    """
    if sotano not in [1, 2, 3]:
        raise ValueError(f"Sótano inválido: {sotano}")

    # Lógica de cálculo...
    return ocupacion_porcentaje
```

#### 5. Commit y Push

**Convención de commits** (Conventional Commits):

```bash
# Formato: <tipo>: <descripción corta>
#
# Tipos:
#   feat:     Nueva funcionalidad
#   fix:      Corrección de bug
#   refactor: Refactorización de código
#   docs:     Cambios en documentación
#   test:     Añadir o corregir tests
#   chore:    Tareas de mantenimiento

# Ejemplos:
git commit -m "feat: Añadir validación de placa duplicada"
git commit -m "fix: Corregir bug en cálculo de pico y placa"
git commit -m "docs: Actualizar README con instrucciones de instalación"
git commit -m "test: Añadir tests para módulo de autenticación"
```

### Estándares de Seguridad

**Nunca hacer**:
```python
# ❌ NO hardcodear credenciales
password = "admin123"

# ❌ NO usar queries concatenadas
query = f"SELECT * FROM usuarios WHERE usuario = '{usuario}'"

# ❌ NO loguear información sensible
logger.info(f"Password: {password}")
```

**Hacer**:
```python
# ✅ Usar variables de entorno
from src.config.settings import DB_CONFIG

# ✅ Usar queries parametrizadas
query = "SELECT * FROM usuarios WHERE usuario = %s"
result = db.fetch_one(query, (usuario,))

# ✅ Ocultar información sensible en logs
logger.info(f"Usuario autenticado: {usuario}")
```

---

## 🧪 Cómo Ejecutar los Tests

### Suite de Tests

El proyecto incluye una suite completa de tests usando **pytest** con mocks para evitar dependencias de MySQL.

#### Instalación de Dependencias de Testing

```bash
pip install pytest pytest-mock
```

### Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidos (mocks de BD)
├── test_imports.py          # Tests de importación (19 tests)
├── test_models.py           # Tests de modelos (20 tests)
├── test_database.py         # Tests de DatabaseManager (16 tests)
└── test_auth.py             # Tests de autenticación (15 tests)
```

**Total**: 70 tests implementados

### Ejecutar Tests

#### Todos los tests

```bash
# Ejecutar todos los tests con output verbose
pytest tests/ -v

# Con cobertura de código
pytest tests/ --cov=src --cov-report=html

# Solo tests que fallaron la última vez
pytest tests/ --lf

# Detener en el primer fallo
pytest tests/ -x
```

#### Tests específicos

```bash
# Por archivo
pytest tests/test_models.py -v

# Por clase
pytest tests/test_models.py::TestFuncionarioModel -v

# Por función específica
pytest tests/test_models.py::TestFuncionarioModel::test_crear_funcionario -v

# Por pattern
pytest tests/ -k "test_import" -v
```

#### Con opciones avanzadas

```bash
# Mostrar prints
pytest tests/ -v -s

# Mostrar summary detallado
pytest tests/ -v -ra

# Ejecutar en paralelo (requiere pytest-xdist)
pip install pytest-xdist
pytest tests/ -v -n auto

# Generar reporte HTML
pytest tests/ --html=test_report.html --self-contained-html
```

### Resultados Esperados

#### Tests de Importación (`test_imports.py`)

```bash
pytest tests/test_imports.py -v
```

**Resultado esperado**: ✅ 19/19 tests passing (100%)

#### Tests de Modelos (`test_models.py`)

```bash
pytest tests/test_models.py -v
```

**Resultado esperado**: ✅ 17/20 tests passing (85%)

#### Tests de Base de Datos (`test_database.py`)

```bash
pytest tests/test_database.py -v
```

**Resultado esperado**: ✅ 15/16 tests passing (93%)

#### Tests de Autenticación (`test_auth.py`)

```bash
pytest tests/test_auth.py -v
```

**Resultado esperado**: ⚠️ 2/15 tests passing (13%)

**Nota**: La mayoría de tests funcionales fallan porque AuthManager usa una implementación diferente. Los tests de importación sí pasan.

### Cobertura de Código

```bash
# Generar reporte de cobertura
pytest tests/ --cov=src --cov-report=html --cov-report=term

# Ver reporte en navegador
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

**Cobertura actual**:
- `src/models/`: ~80%
- `src/database/`: ~85%
- `src/auth/`: ~70%
- `src/config/`: ~95%
- **Total**: ~77%

---

## 📚 Recursos Adicionales

### Documentación del Proyecto

#### Configuración y Setup
- **CONFIGURACION_README.md** - Guía completa de configuración y variables de entorno
- **ejemplo_uso_configuracion.py** - Ejemplos prácticos de uso del sistema de configuración
- **.env.example** - Plantilla con todas las variables de entorno disponibles (177 líneas)

#### Testing
- **tests/README_TESTS.md** - Guía detallada del sistema de testing

#### Features y Funcionalidades
- **CAMBIO_BORRADO_LOGICO.md** - Implementación completa de borrado lógico (v2.0.4)
- **FEATURE_ESTADO_ACTIVO_INACTIVO.md** - Columna Estado y sistema de reactivación (v2.0.4)
- **FEATURE_FILTRO_BUSQUEDA_FUNCIONARIOS.md** - Búsqueda en tiempo real por cédula (v2.0.4)
- **FEATURE_PAGINACION_FUNCIONARIOS.md** - Sistema de paginación de 5 filas (v2.0.5)

#### Scripts de Base de Datos
- **fix_triggers_borrado_logico.sql** - Actualización de triggers para borrado lógico
- **test_borrado_logico.sql** - Queries de verificación de borrado lógico
- **ejecutar_fix_triggers.py** - Script automatizado para ejecutar correcciones de triggers

### Comandos Útiles

```bash
# Ver configuración actual del sistema
python -c "from src.config.settings import print_config_summary; print_config_summary()"

# Validar configuración antes de producción
python -c "from src.config.settings import validate_config; print(validate_config())"

# Ver logs en tiempo real
tail -f logs/parking_system.log

# Limpiar archivos compilados de Python
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Ejecutar tests con cobertura
pytest tests/ --cov=src --cov-report=html

# Generar SECRET_KEY seguro para producción
python -c "import secrets; print(secrets.token_hex(32))"

# Verificar imports del paquete
python -c "import src; print(src.__version__)"

# Test rápido de conexión a BD
python -c "from src.database.manager import DatabaseManager; db = DatabaseManager()"

# Ejecutar corrección de triggers (borrado lógico)
python ejecutar_fix_triggers.py

# Verificar funcionarios inactivos
python -c "from src.database.manager import DatabaseManager; db = DatabaseManager(); print(db.fetch_all('SELECT * FROM funcionarios WHERE activo = FALSE'))"

# Ver estados de parqueaderos
python -c "from src.database.manager import DatabaseManager; db = DatabaseManager(); print(db.fetch_all('SELECT estado, COUNT(*) as cantidad FROM parqueaderos GROUP BY estado'))"
```

### Enlaces Útiles

- **PyQt5 Documentation**: https://doc.qt.io/qt-5/
- **MySQL Documentation**: https://dev.mysql.com/doc/
- **pytest Documentation**: https://docs.pytest.org/
- **PEP 8 Style Guide**: https://peps.python.org/pep-0008/
- **Python dotenv**: https://github.com/theskumar/python-dotenv
- **bcrypt**: https://pypi.org/project/bcrypt/
- **Conventional Commits**: https://www.conventionalcommits.org/

---

## 📋 Reglas de Negocio

### 1. Lógica de Pico y Placa

```python
# src/config/settings.py
class TipoCirculacion(Enum):
    PAR = "PAR"      # Circula días pares (2, 4, 6, 8...)
    IMPAR = "IMPAR"  # Circula días impares (1, 3, 5, 7...)
    NA = "N/A"       # Sin restricción
```

### 2. Estados de Parqueaderos

| Vehículos Asignados | Estado | Color | Puede Recibir |
|---------------------|--------|-------|---------------|
| 0 | DISPONIBLE | 🟢 Verde | Cualquier vehículo |
| 1 Carro PAR | PARCIALMENTE_ASIGNADO | 🟡 Amarillo | Solo Carro IMPAR |
| 1 Carro IMPAR | PARCIALMENTE_ASIGNADO | 🟡 Amarillo | Solo Carro PAR |
| 1 Carro N/A | COMPLETO | 🔴 Rojo | Ninguno |
| 2 Carros (PAR+IMPAR) | COMPLETO | 🔴 Rojo | Ninguno |

### 3. Parqueaderos Exclusivos

**Números 1-20** de cada sótano están reservados para directivos:
- Director
- Coordinador
- Asesor

---

## 🆘 Soporte

### Troubleshooting

#### Error: python-dotenv no instalado
```bash
pip install python-dotenv
```

#### Error: Archivo .env no encontrado
```bash
cp .env.example .env
# Editar .env con credenciales reales
```

#### Error: Conexión a BD fallida
```bash
# Verificar que MySQL está corriendo
mysql -u root -p -e "SHOW DATABASES;"

# Verificar credenciales en .env
cat .env | grep DB_
```

---

## 📄 Licencia

**Proprietary** - Sistema de Gestión de Parqueaderos Salud Plaza Claro

---

## 👨‍💻 Autor

**Sistema de Gestión de Parqueaderos**
Versión 2.0.5
2025-10-26

---

## 📝 Historial de Versiones

### v2.0.5 (Octubre 2025) - Paginación y Optimización
- ✅ Sistema de paginación completo (5 filas por página)
- ✅ Controles de navegación intuitivos (<< < > >>)
- ✅ Integración perfecta con búsqueda
- ✅ Corrección de bugs en alineación de labels (Qt.AlignCenter)

### v2.0.4 (Octubre 2025) - Borrado Lógico y Búsqueda
- ✅ Borrado lógico de funcionarios (preservación de historial)
- ✅ Columna Estado (Activo/Inactivo) con indicadores visuales
- ✅ Sistema de reactivación de funcionarios
- ✅ Filtro de búsqueda en tiempo real por cédula
- ✅ Actualización de triggers para considerar solo activos
- ✅ Sincronización mejorada entre pestañas

### v2.0.3 (Octubre 2025) - Seguridad y Testing
- ✅ Sistema de autenticación con bcrypt
- ✅ Protección contra fuerza bruta
- ✅ Suite de testing completa (70 tests)
- ✅ Logging profesional con RotatingFileHandler
- ✅ Configuración basada en .env

### v2.0.2 (Octubre 2025) - Correcciones Críticas
- ✅ Bug PAR/IMPAR corregido
- ✅ Filtrado de parqueaderos parciales mejorado

### v2.0.1 (Octubre 2025) - Mejoras de Seguridad
- ✅ Sanitización de inputs (Fase 1 OWASP)
- ✅ Queries parametrizadas
- ✅ Validación de datos robusta

---

**Última actualización**: 2025-10-26
**Mantenido por**: Sistema de Gestión de Parqueaderos
**Versión del documento**: 4.0
