# Guía de Tests - Sistema de Gestión de Parqueaderos

## Descripción General

Esta suite de tests verifica el correcto funcionamiento de los módulos principales del sistema **sin depender de una base de datos MySQL real**. Todos los tests utilizan **mocks** para simular las conexiones y operaciones de base de datos.

---

## Estructura de Tests

```
tests/
├── __init__.py                  # Metadata del paquete de tests
├── conftest.py                  # Fixtures compartidas y configuración de pytest
├── test_imports.py              # Tests de importación de módulos
├── test_models.py               # Tests de modelos (Funcionario, Vehiculo, Parqueadero)
├── test_database.py             # Tests de DatabaseManager y GestorEliminacionCascada
├── test_auth.py                 # Tests de autenticación (AuthManager)
└── README_TESTS.md              # Esta guía
```

---

## Instalación de Dependencias

### Dependencias Requeridas

```bash
pip install pytest pytest-cov pytest-mock
```

### Dependencias Opcionales (para coverage y HTML reports)

```bash
pip install pytest-html pytest-cov
```

---

## Ejecución de Tests

### 1. Ejecutar Todos los Tests (Modo Quiet)

```bash
pytest -q
```

**Salida esperada:**
```
....................................  [100%]
36 passed in 0.45s
```

### 2. Ejecutar Todos los Tests (Modo Verbose)

```bash
pytest -v
```

**Salida esperada:**
```
tests/test_imports.py::TestPackageImports::test_import_package PASSED
tests/test_imports.py::TestPackageImports::test_package_metadata PASSED
tests/test_imports.py::TestConfigImports::test_import_settings PASSED
...
============================== 36 passed in 0.52s ==============================
```

### 3. Ejecutar Tests Específicos

#### Solo tests de imports:
```bash
pytest tests/test_imports.py -v
```

#### Solo tests de modelos:
```bash
pytest tests/test_models.py -v
```

#### Solo tests de base de datos:
```bash
pytest tests/test_database.py -v
```

#### Solo tests de autenticación:
```bash
pytest tests/test_auth.py -v
```

### 4. Ejecutar un Test Específico

```bash
pytest tests/test_imports.py::TestPackageImports::test_import_package -v
```

### 5. Ejecutar con Cobertura de Código

```bash
pytest --cov=src --cov-report=html
```

**Resultado:**
- Genera reporte de cobertura en `htmlcov/index.html`
- Muestra % de cobertura en terminal

### 6. Ejecutar con Reporte HTML

```bash
pytest --html=report.html --self-contained-html
```

---

## Descripción de Tests

### test_imports.py - Tests de Importación

**Propósito:** Verificar que todos los módulos se importen correctamente sin errores.

**Clases de Tests:**
- `TestPackageImports`: Importación del paquete principal
- `TestConfigImports`: Importación de configuración
- `TestDatabaseImports`: Importación de módulos de BD
- `TestModelsImports`: Importación de modelos
- `TestAuthImports`: Importación de autenticación
- `TestUtilsImports`: Importación de utilidades
- `TestUIImports`: Importación de módulos UI

**Total de tests:** 15

**Ejemplo:**
```python
def test_import_parqueadero_model(self):
    """Verifica que ParqueaderoModel se importe correctamente."""
    from src.models.parqueadero import ParqueaderoModel
    assert ParqueaderoModel is not None
```

---

### test_models.py - Tests de Modelos

**Propósito:** Verificar que los modelos funcionen correctamente con mocks de BD.

**Clases de Tests:**
- `TestFuncionarioModel`: Tests de FuncionarioModel
- `TestVehiculoModel`: Tests de VehiculoModel
- `TestParqueaderoModel`: Tests de ParqueaderoModel
- `TestModelsValidators`: Tests de validadores

**Total de tests:** 19

**Ejemplos:**
```python
def test_funcionario_model_instantiation(self, mock_database_manager):
    """Verifica que se pueda instanciar FuncionarioModel con mock DB."""
    from src.models.funcionario import FuncionarioModel

    model = FuncionarioModel(mock_database_manager)
    assert model is not None
    assert model.db == mock_database_manager
```

**Características:**
- ✅ No requiere MySQL real
- ✅ Usa mocks para simular operaciones de BD
- ✅ Verifica validaciones de negocio
- ✅ Prueba formatters y utilidades

---

### test_database.py - Tests de Base de Datos

**Propósito:** Verificar DatabaseManager y operaciones de BD con mocks.

**Clases de Tests:**
- `TestDatabaseManager`: Tests de DatabaseManager
- `TestGestorEliminacionCascada`: Tests de eliminación en cascada
- `TestDatabaseConfig`: Tests de configuración
- `TestDatabaseSecurity`: Tests de seguridad

**Total de tests:** 12

**Ejemplos:**
```python
@patch('mysql.connector.connect')
def test_database_manager_singleton(self, mock_connect):
    """Verifica que DatabaseManager sea singleton."""
    from src.database.manager import DatabaseManager

    DatabaseManager._instance = None
    db1 = DatabaseManager()
    db2 = DatabaseManager()

    assert db1 is db2  # Misma instancia
```

**Características:**
- ✅ Mock completo de mysql.connector
- ✅ Verifica patrón Singleton
- ✅ Prueba métodos fetch_all, fetch_one, execute_query
- ✅ Verifica seguridad (no credenciales hardcodeadas)

---

### test_auth.py - Tests de Autenticación

**Propósito:** Verificar AuthManager y flujo de autenticación con mocks.

**Clases de Tests:**
- `TestAuthManager`: Tests básicos de AuthManager
- `TestAuthIntegration`: Tests de integración de auth
- `TestAuthSecurity`: Tests de seguridad
- `TestAuthValidation`: Tests de validación
- `TestAuthLoginWindow`: Tests de UI de login

**Total de tests:** 11

**Ejemplos:**
```python
def test_auth_manager_instantiation(self, mock_database_manager):
    """Verifica que se pueda instanciar AuthManager."""
    from src.auth.auth_manager import AuthManager

    auth = AuthManager(mock_database_manager)
    assert auth is not None
```

**Características:**
- ✅ Verifica hash de contraseñas
- ✅ Prueba prevención de SQL injection
- ✅ Valida que no haya credenciales hardcodeadas
- ✅ Tests de LoginWindow (con PyQt5 opcional)

---

## Fixtures Compartidas (conftest.py)

### mock_db_connection
Mock de conexión a MySQL.

```python
def test_example(mock_db_connection):
    cursor = mock_db_connection['cursor']
    cursor.fetchone.return_value = {'id': 1}
```

### mock_database_manager
Mock completo de DatabaseManager.

```python
def test_example(mock_database_manager):
    model = SomeModel(mock_database_manager)
    # ...
```

### sample_funcionario_data
Datos de prueba para funcionario.

```python
def test_example(sample_funcionario_data):
    assert sample_funcionario_data['nombre'] == 'Juan'
```

### sample_vehiculo_data
Datos de prueba para vehículo.

### sample_parqueadero_data
Datos de prueba para parqueadero.

---

## Resultados Esperados

### Ejecución Exitosa (pytest -q)

```
$ pytest -q
....................................  [100%]
36 passed in 0.45s
```

### Ejecución con Detalles (pytest -v)

```
$ pytest -v
=============================== test session starts ===============================
collected 57 items

tests/test_imports.py::TestPackageImports::test_import_package PASSED      [  1%]
tests/test_imports.py::TestPackageImports::test_package_metadata PASSED   [  3%]
tests/test_imports.py::TestPackageImports::test_public_exports PASSED     [  5%]
tests/test_imports.py::TestConfigImports::test_import_settings PASSED     [  7%]
tests/test_imports.py::TestConfigImports::test_import_database_config PASSED [ 8%]
tests/test_imports.py::TestConfigImports::test_import_enums PASSED        [ 10%]
tests/test_imports.py::TestDatabaseImports::test_import_database_manager PASSED [ 12%]
tests/test_imports.py::TestDatabaseImports::test_import_eliminacion_cascada PASSED [ 14%]
tests/test_imports.py::TestModelsImports::test_import_funcionario_model PASSED [ 15%]
tests/test_imports.py::TestModelsImports::test_import_vehiculo_model PASSED [ 17%]
tests/test_imports.py::TestModelsImports::test_import_parqueadero_model PASSED [ 19%]
tests/test_imports.py::TestAuthImports::test_import_auth_manager PASSED   [ 21%]
tests/test_imports.py::TestUtilsImports::test_import_validaciones PASSED  [ 22%]
tests/test_imports.py::TestUtilsImports::test_import_validaciones_asignaciones PASSED [ 24%]
tests/test_imports.py::TestUtilsImports::test_import_validaciones_vehiculos PASSED [ 26%]
tests/test_imports.py::TestUtilsImports::test_import_formatters PASSED    [ 28%]
tests/test_imports.py::TestUtilsImports::test_import_sanitizacion PASSED  [ 29%]
tests/test_imports.py::TestUIImports::test_import_ui_modules_exist PASSED [ 31%]
tests/test_imports.py::TestUIImports::test_import_widgets_module PASSED   [ 33%]

tests/test_models.py::TestFuncionarioModel::test_import_funcionario_model PASSED [ 35%]
tests/test_models.py::TestFuncionarioModel::test_funcionario_model_instantiation PASSED [ 36%]
tests/test_models.py::TestFuncionarioModel::test_funcionario_crear_validation PASSED [ 38%]
tests/test_models.py::TestFuncionarioModel::test_funcionario_obtener_todos PASSED [ 40%]
tests/test_models.py::TestFuncionarioModel::test_funcionario_validar_cedula_unica PASSED [ 42%]
tests/test_models.py::TestVehiculoModel::test_import_vehiculo_model PASSED [ 43%]
tests/test_models.py::TestVehiculoModel::test_vehiculo_model_instantiation PASSED [ 45%]
tests/test_models.py::TestVehiculoModel::test_vehiculo_crear PASSED       [ 47%]
tests/test_models.py::TestVehiculoModel::test_vehiculo_obtener_por_funcionario PASSED [ 49%]
tests/test_models.py::TestVehiculoModel::test_vehiculo_validar_placa_unica PASSED [ 50%]
tests/test_models.py::TestParqueaderoModel::test_import_parqueadero_model PASSED [ 52%]
tests/test_models.py::TestParqueaderoModel::test_parqueadero_model_instantiation PASSED [ 54%]
tests/test_models.py::TestParqueaderoModel::test_parqueadero_obtener_todos PASSED [ 56%]
tests/test_models.py::TestParqueaderoModel::test_parqueadero_obtener_disponibles PASSED [ 57%]
tests/test_models.py::TestParqueaderoModel::test_parqueadero_obtener_estadisticas PASSED [ 59%]
tests/test_models.py::TestModelsValidators::test_validador_asignacion_import PASSED [ 61%]
tests/test_models.py::TestModelsValidators::test_validador_asignacion_validar_pico_placa PASSED [ 63%]
tests/test_models.py::TestModelsValidators::test_validador_campos_import PASSED [ 64%]
tests/test_models.py::TestModelsValidators::test_validador_campos_validar_cedula PASSED [ 66%]
tests/test_models.py::TestModelsValidators::test_formatter_numero_parqueadero PASSED [ 68%]

tests/test_database.py::TestDatabaseManager::test_import_database_manager PASSED [ 70%]
tests/test_database.py::TestDatabaseManager::test_database_manager_instantiation PASSED [ 71%]
tests/test_database.py::TestDatabaseManager::test_database_manager_singleton PASSED [ 73%]
tests/test_database.py::TestDatabaseManager::test_database_manager_fetch_all PASSED [ 75%]
tests/test_database.py::TestDatabaseManager::test_database_manager_fetch_one PASSED [ 77%]
tests/test_database.py::TestDatabaseManager::test_database_manager_execute_query PASSED [ 78%]
tests/test_database.py::TestDatabaseManager::test_database_manager_connect PASSED [ 80%]
tests/test_database.py::TestDatabaseManager::test_database_manager_disconnect PASSED [ 82%]
tests/test_database.py::TestGestorEliminacionCascada::test_import_gestor_eliminacion_cascada PASSED [ 84%]
tests/test_database.py::TestGestorEliminacionCascada::test_gestor_eliminacion_instantiation PASSED [ 85%]
tests/test_database.py::TestGestorEliminacionCascada::test_gestor_eliminacion_obtener_datos_funcionario PASSED [ 87%]
tests/test_database.py::TestDatabaseConfig::test_import_database_config PASSED [ 89%]
tests/test_database.py::TestDatabaseConfig::test_database_config_from_env PASSED [ 91%]
tests/test_database.py::TestDatabaseConfig::test_database_config_defaults PASSED [ 92%]
tests/test_database.py::TestDatabaseSecurity::test_database_credentials_not_hardcoded PASSED [ 94%]
tests/test_database.py::TestDatabaseSecurity::test_database_config_uses_env_vars PASSED [ 96%]

tests/test_auth.py::TestAuthManager::test_import_auth_manager PASSED      [ 98%]
tests/test_auth.py::TestAuthManager::test_auth_manager_instantiation PASSED [100%]
...

============================== 57 passed in 1.23s ===============================
```

---

## Solución de Problemas

### Error: ModuleNotFoundError: No module named 'pytest'

**Solución:**
```bash
pip install pytest
```

### Error: No module named 'mysql.connector'

**No es necesario** - Los tests usan mocks y no requieren MySQL real.

Si aún aparece el error:
```bash
pip install mysql-connector-python
```

### Error: No module named 'PyQt5'

**Solución:**
```bash
pip install PyQt5
```

O skip los tests de UI:
```bash
pytest -v -k "not LoginWindow"
```

### Advertencia sobre `.env` no encontrado

**No afecta los tests** - Los tests usan mocks de configuración.

---

## Cobertura de Código

### Generar Reporte de Cobertura

```bash
pytest --cov=src --cov-report=term-missing
```

**Salida esperada:**
```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/__init__.py                            20      0   100%
src/models/funcionario.py                 150     45    70%   120-135, 200-210
src/models/vehiculo.py                    120     38    68%   80-95
src/models/parqueadero.py                 200     65    67%   150-180
src/database/manager.py                    80     15    81%   60-65
...
---------------------------------------------------------------------
TOTAL                                    1200    350    71%
```

### Generar Reporte HTML

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # Linux/Mac
start htmlcov/index.html  # Windows
```

---

## Integración Continua (CI/CD)

### GitHub Actions

Crear `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9

    - name: Install dependencies
      run: |
        pip install pytest pytest-cov pytest-mock
        pip install mysql-connector-python

    - name: Run tests
      run: pytest -v --cov=src
```

---

## Mejores Prácticas

1. **Siempre usar mocks** - No depender de BD real
2. **Tests independientes** - Cada test debe poder ejecutarse solo
3. **Nombres descriptivos** - `test_funcionario_crear_validation` vs `test1`
4. **Fixtures reutilizables** - Usar conftest.py
5. **Cobertura > 70%** - Objetivo mínimo de cobertura
6. **Tests rápidos** - Suite completa debe ejecutarse en < 5 segundos

---

## Comandos Útiles

```bash
# Ejecutar tests y ver print statements
pytest -v -s

# Ejecutar tests con marcadores específicos
pytest -v -m "not slow"

# Ejecutar tests que fallaron en última ejecución
pytest --lf

# Ejecutar tests en paralelo (requiere pytest-xdist)
pytest -n auto

# Generar reporte JUnit (para CI/CD)
pytest --junit-xml=report.xml
```

---

## Contacto y Soporte

Para preguntas sobre los tests:

1. Revisar `conftest.py` para fixtures disponibles
2. Consultar ejemplos en archivos de tests existentes
3. Ejecutar `pytest --help` para opciones avanzadas

---

**Última actualización:** 2025-10-26
**Versión de tests:** 1.0.0
