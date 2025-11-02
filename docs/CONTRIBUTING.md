# Guía de Contribución

¡Gracias por tu interés en contribuir al Sistema de Gestión de Parqueaderos! Este documento proporciona directrices y mejores prácticas para contribuir al proyecto.

---

## Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [¿Cómo Puedo Contribuir?](#cómo-puedo-contribuir)
- [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
- [Estilo de Código](#estilo-de-código)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Sugerir Mejoras](#sugerir-mejoras)
- [Estructura del Proyecto](#estructura-del-proyecto)

---

## Código de Conducta

### Nuestro Compromiso

En el interés de fomentar un ambiente abierto y acogedor, nos comprometemos a hacer de la participación en nuestro proyecto y nuestra comunidad una experiencia libre de acoso para todos.

### Comportamiento Esperado

- Usar lenguaje acogedor e inclusivo
- Ser respetuoso de diferentes puntos de vista y experiencias
- Aceptar críticas constructivas de forma profesional
- Enfocarse en lo que es mejor para la comunidad
- Mostrar empatía hacia otros miembros

### Comportamiento Inaceptable

- Uso de lenguaje o imágenes sexualizadas
- Trolling, comentarios insultantes o ataques personales
- Acoso público o privado
- Publicar información privada de otros sin permiso explícito

---

## ¿Cómo Puedo Contribuir?

### Reportar Bugs

Antes de crear un reporte de bug:
- Verifica que no exista ya un issue similar
- Asegúrate de estar usando la última versión
- Recopila toda la información relevante

**Template para Reportar Bugs:**

```markdown
**Descripción del Bug**
Descripción clara y concisa del bug.

**Pasos para Reproducir**
1. Ir a '...'
2. Hacer clic en '....'
3. Hacer scroll hasta '....'
4. Ver error

**Comportamiento Esperado**
Descripción de lo que esperabas que sucediera.

**Screenshots**
Si aplica, añade screenshots para ayudar a explicar el problema.

**Entorno:**
 - OS: [e.g. Windows 10]
 - Python: [e.g. 3.10.5]
 - Versión del Sistema: [e.g. 2.0.3]

**Información Adicional**
Cualquier contexto adicional sobre el problema.
```

### Sugerir Mejoras

**Template para Sugerencias:**

```markdown
**¿Tu sugerencia está relacionada con un problema?**
Descripción clara del problema. Ej: Siempre me frustro cuando [...]

**Describe la solución que te gustaría**
Descripción clara de lo que quieres que suceda.

**Describe alternativas consideradas**
Descripción de soluciones o características alternativas.

**Contexto Adicional**
Añade cualquier contexto o screenshots sobre la sugerencia.
```

### Contribuir con Código

1. **Fork el repositorio**
2. **Crea una rama** desde `main`:
   ```bash
   git checkout -b feature/nueva-caracteristica
   # o
   git checkout -b fix/correccion-bug
   ```
3. **Realiza tus cambios** siguiendo el estilo de código
4. **Añade tests** si es aplicable
5. **Commit tus cambios** con mensajes descriptivos
6. **Push a tu fork**
7. **Abre un Pull Request**

---

## Configuración del Entorno de Desarrollo

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/parking_system.git
cd parking_system
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias de Desarrollo

```bash
pip install -r requirements-dev.txt
```

### 4. Configurar Pre-commit Hooks

```bash
pre-commit install
```

Esto ejecutará automáticamente:
- Black (formateo)
- Flake8 (linting)
- isort (ordenar imports)
- Detección de secretos

### 5. Configurar Base de Datos

```bash
# Crear base de datos
mysql -u root -p -e "CREATE DATABASE parking_management_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Importar esquemas
mysql -u root -p parking_management_test < db/schema/parking_database_schema.sql
mysql -u root -p parking_management_test < db/schema/users_table_schema.sql
```

### 6. Copiar y Configurar .env

```bash
cp .env.example .env
# Editar .env con credenciales de desarrollo
```

### 7. Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_models.py
```

---

## Estilo de Código

### Guías de Estilo

El proyecto sigue estrictamente:
- **PEP 8**: Guía de estilo de Python
- **PEP 257**: Convenciones de docstrings
- **Principios SOLID**: Para diseño orientado a objetos

### Herramientas Automáticas

```bash
# Formatear código con Black
black src/

# Ordenar imports con isort
isort src/

# Verificar linting con Flake8
flake8 src/

# Type checking con mypy
mypy src/
```

### Convenciones de Nombrado

```python
# Clases: PascalCase
class FuncionarioModel:
    pass

# Funciones y variables: snake_case
def obtener_funcionario_por_id(funcionario_id: int):
    nombre_completo = "Juan Pérez"
    return nombre_completo

# Constantes: SCREAMING_SNAKE_CASE
MAX_VEHICULOS_POR_FUNCIONARIO = 4
CARGOS_DIRECTIVOS = ["Director", "Coordinador"]

# Privados: prefijo con _
def _metodo_interno():
    pass
```

### Docstrings

Todos los módulos, clases y funciones públicas deben tener docstrings:

```python
def validar_cedula(cedula: str) -> tuple[bool, str]:
    """
    Valida el formato de una cédula colombiana.

    Args:
        cedula (str): Número de cédula a validar

    Returns:
        tuple[bool, str]: (es_valida, mensaje_error)

    Examples:
        >>> validar_cedula("1234567890")
        (True, "")
        >>> validar_cedula("123")
        (False, "La cédula debe tener entre 6 y 10 dígitos")
    """
    pass
```

### Type Hints

Usa type hints en todas las funciones públicas:

```python
from typing import Optional, List, Dict, Tuple

def obtener_vehiculos(
    funcionario_id: int,
    activos_solo: bool = True
) -> List[Dict[str, any]]:
    """Obtiene vehículos de un funcionario"""
    pass

def crear_funcionario(
    nombre: str,
    apellidos: str,
    cedula: str
) -> Tuple[bool, Optional[int]]:
    """Crea un funcionario y retorna (exito, id)"""
    pass
```

### Manejo de Errores

```python
# Bueno: Específico y con mensaje descriptivo
try:
    db.execute_query(query, params)
except mysql.connector.Error as e:
    logger.error(f"Error al insertar funcionario: {e}")
    return (False, "Error de base de datos")

# Malo: Catch genérico sin contexto
try:
    db.execute_query(query, params)
except:
    return False
```

---

## Proceso de Pull Request

### Checklist Antes de Enviar

- [ ] He actualizado la documentación si es necesario
- [ ] He añadido tests que prueban mi cambio
- [ ] Todos los tests existentes pasan
- [ ] He ejecutado black, isort y flake8
- [ ] He actualizado el CHANGELOG.md
- [ ] Mi código sigue el estilo del proyecto
- [ ] Mi commit message es descriptivo

### Mensajes de Commit

Seguimos la convención de [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(scope): descripción corta

Descripción más detallada si es necesario.

Fixes #123
```

**Tipos de commit:**

- `feat`: Nueva característica
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Formateo, sin cambios de código
- `refactor`: Refactorización sin cambiar funcionalidad
- `test`: Añadir o modificar tests
- `chore`: Tareas de mantenimiento

**Ejemplos:**

```bash
feat(vehiculos): añadir soporte para carros híbridos

- Añadida columna es_hibrido a tabla vehiculos
- Validación de asignación exclusiva para híbridos
- Tests de regla de negocio

Fixes #45
```

```bash
fix(auth): corregir validación de sesión expirada

El timeout de sesión no se estaba verificando correctamente.
Ahora se valida contra SESSION_TIMEOUT de settings.

Closes #67
```

### Revisión de Pull Requests

Tu PR será revisado por un mantenedor. Pueden solicitar:
- Cambios en el código
- Más tests
- Documentación adicional
- Refactorización

**Sé receptivo a la retroalimentación** y discute respetuosamente si no estás de acuerdo.

---

## Estructura del Proyecto

```
parking_system/
├── src/                    # Código fuente
│   ├── auth/               # Autenticación
│   ├── config/             # Configuración
│   ├── core/               # Módulos core (logging)
│   ├── database/           # Acceso a datos
│   ├── models/             # Lógica de negocio
│   ├── ui/                 # Interfaz PyQt5
│   └── utils/              # Utilidades
├── scripts/                # Scripts de ejecución
├── db/                     # Esquemas SQL
├── docs/                   # Documentación
├── tests/                  # Tests
│   ├── unit/               # Tests unitarios
│   └── integration/        # Tests de integración
├── .pre-commit-config.yaml # Configuración pre-commit
├── requirements.txt        # Dependencias producción
├── requirements-dev.txt    # Dependencias desarrollo
└── setup.py                # Configuración de paquete
```

### Capas de Arquitectura

```
UI (PyQt5) → Models → Database → MySQL
           ↓
         Utils (Validaciones, Formateo)
```

- **UI**: No debe contener lógica de negocio
- **Models**: Toda la lógica de negocio y validaciones
- **Database**: Solo acceso a datos, sin lógica
- **Utils**: Funciones reutilizables sin estado

---

## Testing

### Escribir Tests

```python
# tests/unit/test_validators.py
import pytest
from src.utils.validaciones import ValidadorCampos

def test_validar_cedula_valida():
    """Test de cédula válida"""
    valido, mensaje = ValidadorCampos.validar_cedula("1234567890")
    assert valido is True
    assert mensaje == ""

def test_validar_cedula_muy_corta():
    """Test de cédula muy corta"""
    valido, mensaje = ValidadorCampos.validar_cedula("123")
    assert valido is False
    assert "entre 6 y 10 dígitos" in mensaje

@pytest.mark.parametrize("cedula,esperado", [
    ("1234567890", True),
    ("123456", True),
    ("12345", False),
    ("12345678901", False),
])
def test_validar_cedula_parametrizado(cedula, esperado):
    """Test parametrizado de cédulas"""
    valido, _ = ValidadorCampos.validar_cedula(cedula)
    assert valido is esperado
```

### Cobertura de Tests

Apuntamos a una cobertura mínima del **80%**:

```bash
# Generar reporte de cobertura
pytest --cov=src --cov-report=html --cov-report=term

# Ver reporte en navegador
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

---

## Documentación

### Añadir Documentación

Si añades una nueva característica, documenta:

1. **Docstrings en el código**
2. **README.md**: Si cambia el uso básico
3. **docs/**: Documentación técnica detallada
4. **CHANGELOG.md**: Añade entrada con tu cambio

### Generar Documentación Sphinx

```bash
cd docs/
sphinx-build -b html . _build/html
```

---

## Despliegue

Solo los mantenedores pueden hacer releases. El proceso es:

1. Actualizar versión en `src/__init__.py` y `src/config/settings.py`
2. Actualizar `CHANGELOG.md`
3. Crear tag de versión:
   ```bash
   git tag -a v2.1.0 -m "Release v2.1.0"
   git push origin v2.1.0
   ```
4. Crear release en GitHub

---

## Recursos Adicionales

- [PEP 8 - Guía de Estilo de Python](https://pep8.org/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [MySQL Connector/Python](https://dev.mysql.com/doc/connector-python/en/)
- [Pytest Documentation](https://docs.pytest.org/)

---

## Contacto

Si tienes preguntas, puedes:
- Abrir un issue en GitHub
- Enviar email a: dev@example.com

---

¡Gracias por contribuir! 🚀
