#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Verificación de Instalación
======================================

Verifica que todas las dependencias estén instaladas correctamente
y que los módulos principales puedan ser importados.

Uso:
    python verify_installation.py
"""

import sys
from typing import List, Tuple

# Colores para output en terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Imprime un encabezado con formato"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")

def check_python_version() -> bool:
    """Verifica la versión de Python"""
    print(f"{Colors.BOLD}Verificando versión de Python...{Colors.ENDC}")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 8:
        print(f"{Colors.GREEN}✓ Python {version_str} (OK){Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}✗ Python {version_str} (Requiere 3.8+){Colors.ENDC}")
        return False

def check_dependencies() -> Tuple[List[str], List[str]]:
    """Verifica las dependencias principales"""
    print(f"\n{Colors.BOLD}Verificando dependencias...{Colors.ENDC}")

    dependencies = [
        ('PyQt5', 'PyQt5'),
        ('mysql.connector', 'mysql-connector-python'),
        ('bcrypt', 'bcrypt'),
        ('openpyxl', 'openpyxl'),
        ('reportlab', 'reportlab'),
        ('matplotlib', 'matplotlib'),
        ('dotenv', 'python-dotenv'),
    ]

    installed = []
    missing = []

    for import_name, package_name in dependencies:
        try:
            __import__(import_name)
            print(f"{Colors.GREEN}✓ {package_name}{Colors.ENDC}")
            installed.append(package_name)
        except ImportError:
            print(f"{Colors.YELLOW}⚠ {package_name} (Opcional - no instalado){Colors.ENDC}")
            missing.append(package_name)

    return installed, missing

def check_project_imports() -> bool:
    """Verifica que los módulos del proyecto se puedan importar"""
    print(f"\n{Colors.BOLD}Verificando módulos del proyecto...{Colors.ENDC}")

    modules = [
        'src',
        'src.config.settings',
        'src.database.manager',
        'src.models.funcionario',
        'src.models.parqueadero',
        'src.models.vehiculo',
        'src.auth.auth_manager',
        'src.utils.validaciones',
        'src.utils.formatters',
        'src.core.logger',
    ]

    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"{Colors.GREEN}✓ {module}{Colors.ENDC}")
        except ImportError as e:
            print(f"{Colors.RED}✗ {module}: {e}{Colors.ENDC}")
            all_ok = False

    return all_ok

def check_database_connection() -> bool:
    """Intenta conectar a la base de datos"""
    print(f"\n{Colors.BOLD}Verificando conexión a base de datos...{Colors.ENDC}")

    try:
        from src.database.manager import DatabaseManager
        from src.config.settings import DB_CONFIG

        print(f"{Colors.BLUE}Host: {DB_CONFIG.host}:{DB_CONFIG.port}{Colors.ENDC}")
        print(f"{Colors.BLUE}Database: {DB_CONFIG.database}{Colors.ENDC}")
        print(f"{Colors.BLUE}User: {DB_CONFIG.user}{Colors.ENDC}")

        db = DatabaseManager()
        result = db.fetch_one("SELECT VERSION()", ())

        if result:
            print(f"{Colors.GREEN}✓ Conexión exitosa a MySQL {result[0]}{Colors.ENDC}")
            return True
        else:
            print(f"{Colors.YELLOW}⚠ Conexión establecida pero sin respuesta{Colors.ENDC}")
            return False

    except Exception as e:
        print(f"{Colors.YELLOW}⚠ No se pudo conectar a la base de datos{Colors.ENDC}")
        print(f"{Colors.YELLOW}  Razón: {str(e)}{Colors.ENDC}")
        print(f"{Colors.YELLOW}  (Esto es normal si aún no has configurado la BD){Colors.ENDC}")
        return False

def check_environment_file() -> bool:
    """Verifica que exista el archivo .env"""
    print(f"\n{Colors.BOLD}Verificando archivo de configuración...{Colors.ENDC}")

    import os
    if os.path.exists('.env'):
        print(f"{Colors.GREEN}✓ Archivo .env encontrado{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.YELLOW}⚠ Archivo .env no encontrado{Colors.ENDC}")
        print(f"{Colors.YELLOW}  Copia .env.example a .env y configúralo{Colors.ENDC}")
        return False

def print_summary(results: dict):
    """Imprime un resumen de la verificación"""
    print_header("RESUMEN DE VERIFICACIÓN")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"Total de verificaciones: {total}")
    print(f"{Colors.GREEN}Exitosas: {passed}{Colors.ENDC}")
    print(f"{Colors.RED}Fallidas: {total - passed}{Colors.ENDC}")

    print(f"\n{Colors.BOLD}Detalles:{Colors.ENDC}")
    for check, status in results.items():
        symbol = f"{Colors.GREEN}✓{Colors.ENDC}" if status else f"{Colors.RED}✗{Colors.ENDC}"
        print(f"  {symbol} {check}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}¡Instalación completa y correcta!{Colors.ENDC}")
        print(f"{Colors.GREEN}Puedes ejecutar la aplicación con:{Colors.ENDC}")
        print(f"{Colors.BLUE}  python -m src --auth{Colors.ENDC}")
    elif passed >= total - 1:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Instalación casi completa{Colors.ENDC}")
        print(f"{Colors.YELLOW}Revisa los elementos marcados con ⚠{Colors.ENDC}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Faltan componentes importantes{Colors.ENDC}")
        print(f"{Colors.RED}Revisa la documentación en docs/INSTALLATION.md{Colors.ENDC}")

def main():
    """Función principal"""
    print_header("VERIFICACIÓN DE INSTALACIÓN")
    print(f"{Colors.BOLD}Sistema de Gestión de Parqueaderos v2.0.3{Colors.ENDC}\n")

    results = {}

    # Verificaciones
    results['Python 3.8+'] = check_python_version()

    installed, missing = check_dependencies()
    results['Dependencias principales'] = len(installed) >= 3  # PyQt5, MySQL, bcrypt mínimo

    results['Módulos del proyecto'] = check_project_imports()
    results['Archivo .env'] = check_environment_file()
    results['Conexión a BD'] = check_database_connection()

    # Resumen
    print_summary(results)

    # Código de salida
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verificación cancelada por el usuario{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.ENDC}")
        sys.exit(1)
