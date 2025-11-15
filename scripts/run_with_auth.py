#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de conveniencia para ejecutar el sistema CON autenticación.

Uso:
    python scripts/run_with_auth.py
    python scripts/run_with_auth.py --help
"""

import sys
import argparse
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from scripts.main_with_auth import AuthenticatedApp


def main():
    """Ejecutar aplicación con autenticación"""
    parser = argparse.ArgumentParser(
        description='Sistema de Gestión de Parqueadero (con autenticación)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Este script ejecuta el sistema en modo producción CON autenticación.

Credenciales de prueba:
  Usuario: splaza
  Contraseña: splaza123*

Para ejecutar sin autenticación (desarrollo), usar: python scripts/run.py

Versión: 2.0.3
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Sistema de Gestión de Parqueadero v2.0.3'
    )
    
    args = parser.parse_args()
    
    print("[INFO] Iniciando sistema CON autenticación (modo producción)...")
    print("[INFO] Mostrando ventana de login...")

    app = AuthenticatedApp()
    sys.exit(app.start())


if __name__ == '__main__':
    main()
