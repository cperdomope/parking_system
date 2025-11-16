# 🧪 Suite de Pruebas - Parking Management System

Documentación completa de la suite de pruebas del sistema de gestión de parqueaderos.

---

## 📋 Tabla de Contenidos

1. [Instalación](#instalación)
2. [Estructura de Tests](#estructura-de-tests)
3. [Ejecutar Tests](#ejecutar-tests)
4. [Tipos de Tests](#tipos-de-tests)
5. [Coverage](#coverage)
6. [CI/CD](#cicd)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Instalación

### Requisitos Previos
```bash
Python >= 3.8
pip >= 20.0
```

### Instalar Dependencias de Testing
```bash
# Desde la raíz del proyecto
pip install -r requirements_dev.txt
```

Si `requirements_dev.txt` no existe, crear con:
```txt
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
pytest-qt>=4.2.0
pytest-timeout>=2.1.0
pytest-xdist>=3.3.1

# Mocking
unittest-mock>=1.5.0
faker>=19.3.0

# Security Testing
bandit>=1.7.5
safety>=2.3.5

# Performance
pytest-benchmark>=4.0.0
memory-profiler>=0.61.0

# Code Quality
flake8>=6.0.0
black>=23.7.0
mypy>=1.4.1
