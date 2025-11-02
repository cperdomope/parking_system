# Sistema de Gestión de Parqueaderos

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.3-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-orange.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Sistema completo de gestión de parqueaderos institucionales con interfaz gráfica moderna**

[Instalación](#instalación) • [Características](#características) • [Uso](#uso) • [Documentación](#documentación) • [Contribuir](#contribuir)

</div>

---

## Descripción

Sistema integral de gestión de parqueaderos desarrollado en Python con PyQt5 y MySQL. Permite administrar funcionarios, vehículos, asignaciones de espacios de parqueo y generar reportes completos con validaciones avanzadas de reglas de negocio.

### Características Principales

- **Gestión de Funcionarios**: CRUD completo con validación de cédulas, cargos y direcciones organizacionales
- **Gestión de Vehículos**: Registro de carros, motos y bicicletas con validaciones de placas y límites por funcionario
- **Gestión de Parqueaderos**: Visualización gráfica del estado de ocupación de cada espacio
- **Asignaciones Inteligentes**: Sistema de asignación con validación de reglas de negocio (pico y placa, capacidad, compatibilidad)
- **Reportes Avanzados**: Exportación a CSV, Excel y PDF con filtros personalizados
- **Autenticación Segura**: Sistema de login con hashing bcrypt y control de intentos fallidos
- **Borrado Lógico**: Preservación del historial con desactivación en lugar de eliminación física
- **Dashboard Visual**: Estadísticas en tiempo real y gráficos de ocupación

### Reglas de Negocio Implementadas

- Máximo 4 vehículos por funcionario
- Máximo 2 vehículos por parqueadero
- Validación de pico y placa solidario (PAR/IMPAR según último dígito de placa)
- Parqueadero exclusivo para carros híbridos
- Preferencias de compartir/no compartir espacio
- Privilegios especiales para directivos y personas con discapacidad

---

## Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.8+ | Lenguaje principal |
| **PyQt5** | 5.15+ | Interfaz gráfica |
| **MySQL** | 8.0+ | Base de datos |
| **bcrypt** | - | Hashing de contraseñas |
| **openpyxl** | 3.0+ | Exportación Excel |
| **reportlab** | 3.6+ | Generación de PDFs |
| **matplotlib** | 3.5+ | Gráficos estadísticos |
| **python-dotenv** | 0.19+ | Gestión de variables de entorno |

---

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- MySQL 8.0 o superior (o MariaDB 10.5+)
- pip (gestor de paquetes de Python)
- Git (opcional)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/parking_system.git
cd parking_system
```

### Paso 2: Crear Entorno Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Base de Datos

1. **Crear la base de datos**:
```sql
CREATE DATABASE parking_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **Importar esquemas**:
```bash
mysql -u root -p parking_management < db/schema/parking_database_schema.sql
mysql -u root -p parking_management < db/schema/users_table_schema.sql
```

3. **Aplicar migraciones** (si es necesario):
```bash
mysql -u root -p parking_management < db/migrations/migracion_carro_hibrido.sql
```

### Paso 5: Configurar Variables de Entorno

1. Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Editar `.env` con tus credenciales:
```env
# Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña_aqui
DB_NAME=parking_management

# Seguridad
SECRET_KEY=tu_clave_secreta_aqui_cambiar_en_produccion

# Aplicación
DEBUG=False
LOG_LEVEL=INFO
```

**IMPORTANTE**: Cambia `SECRET_KEY` y `DB_PASSWORD` en producción.

### Paso 6: Ejecutar la Aplicación

**Con autenticación (recomendado para producción)**:
```bash
python -m src --auth
```

**Sin autenticación (solo desarrollo)**:
```bash
python -m src
```

**Alternativas**:
```bash
# Sin auth
python scripts/run.py

# Con auth
python scripts/run_with_auth.py
```

---

## Uso

### Primer Login

Por defecto, el sistema crea un usuario administrador:

- **Usuario**: `admin`
- **Contraseña**: `admin123`

**IMPORTANTE**: Cambia esta contraseña después del primer login en producción.

### Navegación

El sistema cuenta con 6 pestañas principales:

1. **Dashboard**: Estadísticas generales, gráficos de ocupación
2. **Funcionarios**: CRUD de funcionarios con búsqueda, filtros y paginación
3. **Vehículos**: CRUD de vehículos con validaciones avanzadas
4. **Parqueaderos**: Visualización gráfica de todos los espacios
5. **Asignaciones**: Gestión de asignaciones funcionario-parqueadero
6. **Reportes**: Exportación de datos en múltiples formatos

### Atajos de Teclado

- `Ctrl + N`: Nuevo registro (en cada pestaña)
- `Ctrl + F`: Búsqueda/Filtros
- `Ctrl + R`: Recargar datos
- `Ctrl + Q`: Salir de la aplicación

---

## Estructura del Proyecto

```
parking_system/
├── src/                        # Código fuente principal
│   ├── auth/                   # Autenticación y gestión de usuarios
│   ├── config/                 # Configuración centralizada
│   ├── core/                   # Módulos core (logging, etc.)
│   ├── database/               # Acceso a datos y gestión de conexiones
│   ├── models/                 # Lógica de negocio (CRUD)
│   ├── ui/                     # Interfaz gráfica PyQt5
│   │   └── widgets/            # Widgets reutilizables
│   └── utils/                  # Utilidades y validaciones
├── scripts/                    # Scripts de ejecución
├── db/                         # Esquemas y migraciones SQL
│   ├── schema/                 # Esquemas de tablas
│   └── migrations/             # Migraciones
├── docs/                       # Documentación
├── tests/                      # Tests unitarios e integración
├── logs/                       # Archivos de log
├── requirements.txt            # Dependencias Python
├── .env.example                # Plantilla de configuración
└── README.md                   # Este archivo
```

---

## Documentación

### Documentación Disponible

- [INSTALLATION.md](docs/INSTALLATION.md) - Guía detallada de instalación
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitectura del sistema
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Referencia de clases y métodos
- [SECURITY.md](docs/SECURITY.md) - Guía de seguridad y mejores prácticas
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) - Cómo contribuir al proyecto

### Documentación Técnica

- [docs/features/](docs/features/) - Especificaciones de características
- [docs/CLAUDE.md](docs/CLAUDE.md) - Instrucciones para Claude AI
- [docs/CHANGELOG_HISTORICO.md](docs/CHANGELOG_HISTORICO.md) - Historial de cambios

---

## Tests

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/

# Tests específicos
python -m pytest tests/test_models.py
python -m pytest tests/test_auth.py

# Con cobertura
python -m pytest --cov=src tests/
```

### Estructura de Tests

```
tests/
├── unit/                       # Tests unitarios
│   ├── test_validators.py
│   ├── test_models.py
│   └── test_auth.py
├── integration/                # Tests de integración
│   └── test_database.py
└── conftest.py                 # Fixtures compartidas
```

---

## Contribuir

¡Las contribuciones son bienvenidas! Por favor lee [CONTRIBUTING.md](docs/CONTRIBUTING.md) para detalles sobre nuestro código de conducta y el proceso para enviar pull requests.

### Pasos para Contribuir

1. Fork el proyecto
2. Crea tu feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Estilo de Código

El proyecto sigue las guías de estilo PEP 8 y principios SOLID:

- Usa `black` para formateo automático
- Usa `flake8` para linting
- Usa `isort` para ordenar imports
- Añade type hints en funciones públicas
- Documenta clases y métodos con docstrings

---

## Seguridad

### Reportar Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, **NO** abras un issue público. En su lugar:

1. Envía un email a: security@example.com
2. Describe la vulnerabilidad en detalle
3. Espera nuestra respuesta (máximo 48 horas)

### Mejores Prácticas

- **NUNCA** subas el archivo `.env` al repositorio
- Cambia las credenciales por defecto en producción
- Usa HTTPS en producción
- Mantén las dependencias actualizadas
- Revisa los logs regularmente

Consulta [SECURITY.md](docs/SECURITY.md) para más información.

---

## Changelog

### v2.0.3 (2025-11-02)

- Eliminación física de vehículos al desactivar funcionario
- Mejora en tiempos de respuesta de botones
- Optimización de actualización de tabla sin recarga completa
- Corrección de bug en reactivación de funcionarios

### v2.0.2 (Anterior)

- Corrección de filtrado de parqueaderos parciales
- Eliminación de campo obsoleto PAR/IMPAR

### v2.0.1 (Anterior)

- Sanitización y mejoras de seguridad (OWASP)
- Implementación de borrado lógico
- Filtros y búsqueda en funcionarios
- Paginación de resultados

Consulta [docs/CHANGELOG_HISTORICO.md](docs/CHANGELOG_HISTORICO.md) para el historial completo.

---

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

---

## Soporte

### Obtener Ayuda

- **Documentación**: Consulta [docs/](docs/)
- **Issues**: Abre un issue en GitHub
- **Email**: soporte@example.com

### Estado del Proyecto

- **Versión Actual**: 2.0.3
- **Estado**: Activo, en desarrollo
- **Última Actualización**: Noviembre 2025

---

## Reconocimientos

- PyQt5 por el framework GUI
- MySQL por la base de datos robusta
- Comunidad Python por las excelentes librerías

---

## Roadmap

### Próximas Características (v2.1.0)

- [ ] Notificaciones por email
- [ ] Integración con QR codes
- [ ] App móvil (Flutter)
- [ ] API REST
- [ ] Dashboard web con analytics avanzados

### Mejoras Planificadas

- [ ] Tests con cobertura del 80%+
- [ ] CI/CD con GitHub Actions
- [ ] Docker Compose para despliegue
- [ ] Documentación Sphinx generada automáticamente

---

<div align="center">

**Desarrollado con ❤️ para mejorar la gestión de parqueaderos institucionales**

[⬆ Volver arriba](#sistema-de-gestión-de-parqueaderos)

</div>
