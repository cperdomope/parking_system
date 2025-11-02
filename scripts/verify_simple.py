#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script simple de verificación de instalación"""

import sys

def main():
    print("="*60)
    print(" VERIFICACION DE INSTALACION ".center(60))
    print("="*60)
    print("\nSistema de Gestion de Parqueaderos v2.0.3\n")

    errors = []

    # 1. Verificar Python
    print("1. Verificando version de Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   OK: Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"   ERROR: Python {version.major}.{version.minor} (Requiere 3.8+)")
        errors.append("Python version")

    # 2. Verificar dependencias
    print("\n2. Verificando dependencias...")
    deps = [
        ('PyQt5', 'PyQt5'),
        ('mysql.connector', 'mysql-connector-python'),
        ('bcrypt', 'bcrypt'),
        ('openpyxl', 'openpyxl'),
        ('reportlab', 'reportlab'),
        ('matplotlib', 'matplotlib'),
        ('dotenv', 'python-dotenv'),
    ]

    for import_name, package_name in deps:
        try:
            __import__(import_name)
            print(f"   OK: {package_name}")
        except ImportError:
            print(f"   ADVERTENCIA: {package_name} (opcional)")

    # 3. Verificar módulos del proyecto
    print("\n3. Verificando modulos del proyecto...")
    modules = [
        'src',
        'src.config.settings',
        'src.database.manager',
        'src.models.funcionario',
        'src.auth.auth_manager',
    ]

    for module in modules:
        try:
            __import__(module)
            print(f"   OK: {module}")
        except ImportError as e:
            print(f"   ERROR: {module} - {e}")
            errors.append(module)

    # 4. Verificar .env
    print("\n4. Verificando archivo .env...")
    import os
    if os.path.exists('.env'):
        print("   OK: Archivo .env encontrado")
    else:
        print("   ADVERTENCIA: Archivo .env no encontrado")
        print("   Copia .env.example a .env y configuralo")

    # 5. Verificar conexión a BD
    print("\n5. Verificando conexion a base de datos...")
    try:
        from src.database.manager import DatabaseManager
        db = DatabaseManager()
        result = db.fetch_one("SELECT VERSION()", ())
        print(f"   OK: Conectado a MySQL {result[0]}")
    except Exception as e:
        print(f"   ADVERTENCIA: No se pudo conectar ({str(e)[:50]}...)")
        print("   Esto es normal si aun no has configurado la BD")

    # Resumen
    print("\n" + "="*60)
    print(" RESUMEN ".center(60))
    print("="*60)

    if not errors:
        print("\nInstalacion completa y correcta!")
        print("Puedes ejecutar la aplicacion con:")
        print("  python -m src --auth")
        return 0
    else:
        print(f"\nSe encontraron {len(errors)} errores:")
        for error in errors:
            print(f"  - {error}")
        print("\nRevisa la documentacion en docs/INSTALLATION.md")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nVerificacion cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
