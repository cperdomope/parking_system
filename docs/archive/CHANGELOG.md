# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

---

## [2.0.3] - 2025-11-02

### 🎯 Cambiado
- **CRÍTICO**: Eliminación física de vehículos al desactivar funcionario (en lugar de borrado lógico)
- Optimización de actualización de tabla sin recarga completa en pestaña de funcionarios
- Mejora significativa en tiempos de respuesta de botones "Eliminar" y "Reactivar"

### 🐛 Corregido
- Bug en reactivación de funcionarios: ahora desaparecen inmediatamente del filtro "Inactivos"
- Corrección de error `AttributeError` con `label_paginacion`
- Funcionarios reactivados ahora se obtienen correctamente de la base de datos

### 📚 Documentación
- Creación de README.md profesional con badges y estructura completa
- Guía detallada de instalación (INSTALLATION.md) para Windows, Linux y macOS
- Guía de contribución (CONTRIBUTING.md) con estándares de código
- Política de seguridad (SECURITY.md) con mejores prácticas OWASP
- Reorganización de documentación legacy en `docs/features/` y `docs/archive/`

### 🧹 Limpieza
- Eliminación de 7+ scripts legacy de debugging obsoletos
- Consolidación de documentación antigua en estructura organizada
- Creación de `.pre-commit-config.yaml` para hooks automáticos
- Creación de `requirements-dev.txt` para entorno de desarrollo
- Optimización de `.gitignore` con reglas completas

### 🔧 Infraestructura
- Creación de `setup.py` para instalación con pip
- Configuración de pre-commit hooks (Black, Flake8, isort)
- Estructura mejorada de archivos de configuración

---

## [2.0.2] - 2025-10-28

### 🐛 Corregido
- **CRÍTICO**: Corrección definitiva del bug PAR/IMPAR en asignaciones
- Eliminación de campo obsoleto `par_impar` de tabla vehiculos
- Filtrado correcto de parqueaderos parcialmente asignados

### 🔄 Refactorización
- Migración de cálculo PAR/IMPAR a nivel de lógica de negocio
- Eliminación de dependencia de campo de base de datos obsoleto

---

## [2.0.1] - 2025-10-25

### 🔒 Seguridad
- Implementación de sanitización de entrada completa (OWASP)
- Validación contra inyección SQL en todos los formularios
- Detección de caracteres peligrosos en entrada de usuario
- Hashing seguro de contraseñas con bcrypt

### ✨ Añadido
- Filtro de búsqueda en pestaña de funcionarios
- Paginación de resultados (configurable)
- Combo box de filtro Activos/Inactivos/Todos
- Estado activo/inactivo en funcionarios (borrado lógico)

### 📊 Mejorado
- Optimización de consultas SQL con índices
- Mejora en rendimiento de carga de tablas grandes
- Validaciones más robustas en formularios

---

## [2.0.0] - 2025-10-15

### 🚀 Nueva Versión Mayor

#### ✨ Características Principales
- Sistema de autenticación completo con interfaz futurista
- Gestión de usuarios con roles y permisos
- Control de intentos fallidos de login (5 intentos máximo)
- Bloqueo temporal de cuenta (30 minutos)
- Timeout de sesión configurable (8 horas por defecto)

#### 🎨 Interfaz
- Rediseño completo de la interfaz con PyQt5
- Dashboard con estadísticas en tiempo real
- 6 pestañas principales: Dashboard, Funcionarios, Vehículos, Parqueaderos, Asignaciones, Reportes
- Visualización gráfica de parqueaderos con widget personalizado
- Modales para ver/editar/eliminar registros

#### 📋 Funcionalidades
- CRUD completo de funcionarios con validaciones
- CRUD completo de vehículos con reglas de negocio
- Gestión de parqueaderos con estados dinámicos
- Sistema de asignaciones con validación de compatibilidad
- Exportación de reportes a CSV, Excel y PDF

#### 🔐 Seguridad
- Queries parametrizadas en todas las consultas SQL
- Validaciones centralizadas de entrada
- Logging completo de operaciones
- Gestión de secretos con variables de entorno (.env)

#### 🏗️ Arquitectura
- Separación clara en capas (UI, Models, Database, Utils)
- Patrón MVC adaptado para PyQt5
- Modelos de negocio desacoplados de la UI
- Gestor de base de datos con pool de conexiones

---

## [1.2.0] - 2025-09-20

### ✨ Añadido
- Soporte para carros híbridos con parqueadero dedicado
- Validación de pico y placa solidario
- Preferencias de compartir/no compartir parqueadero

### 🐛 Corregido
- Bug en cálculo de capacidad de parqueaderos
- Validación incorrecta de compatibilidad de vehículos

---

## [1.1.0] - 2025-09-10

### ✨ Añadido
- Sistema de reportes básico
- Exportación a CSV
- Estadísticas de ocupación

### 📊 Mejorado
- Interfaz más responsiva
- Validaciones más claras en formularios

---

## [1.0.0] - 2025-09-01

### 🚀 Release Inicial

#### Características
- CRUD básico de funcionarios
- CRUD básico de vehículos
- Gestión simple de parqueaderos
- Asignación manual de espacios
- Interfaz PyQt5 básica
- Base de datos MySQL

#### Reglas de Negocio
- Máximo 4 vehículos por funcionario
- Máximo 2 vehículos por parqueadero
- Tipos de vehículo: Carro, Moto, Bicicleta

---

## Tipos de Cambios

- `✨ Añadido`: Para nuevas características
- `🔄 Cambiado`: Para cambios en funcionalidad existente
- `🗑️ Deprecado`: Para características que serán removidas
- `🐛 Corregido`: Para corrección de bugs
- `🔒 Seguridad`: Para vulnerabilidades corregidas
- `📚 Documentación`: Solo cambios en documentación
- `🔧 Infraestructura`: Cambios en build, CI/CD, herramientas
- `🧹 Limpieza`: Refactorización, eliminación de código obsoleto
- `🎨 Interfaz`: Cambios visuales o de UX
- `📊 Mejorado`: Mejoras de rendimiento o usabilidad

---

## Enlaces

- [Unreleased Changes](https://github.com/tu-usuario/parking_system/compare/v2.0.3...HEAD)
- [2.0.3](https://github.com/tu-usuario/parking_system/compare/v2.0.2...v2.0.3)
- [2.0.2](https://github.com/tu-usuario/parking_system/compare/v2.0.1...v2.0.2)
- [2.0.1](https://github.com/tu-usuario/parking_system/compare/v2.0.0...v2.0.1)
- [2.0.0](https://github.com/tu-usuario/parking_system/compare/v1.2.0...v2.0.0)
