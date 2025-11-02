#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada para ejecutar el sistema como módulo Python.

Uso:
    python -m src                    # Ejecutar sin autenticación
    python -m src --auth             # Ejecutar con autenticación
    python -m src --help             # Mostrar ayuda
"""

import sys
import argparse
from pathlib import Path

# Agregar el directorio raíz al path para imports
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))


def main():
    """Función principal del módulo"""
    parser = argparse.ArgumentParser(
        description='Sistema de Gestión de Parqueadero - Ssalud Plaza Claro',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python -m src                    # Ejecutar sin autenticación (modo desarrollo)
  python -m src --auth             # Ejecutar con autenticación (modo producción)
  python -m src --version          # Mostrar versión del sistema

Credenciales de prueba (con --auth):
  Usuario: splaza
  Contraseña: splaza123*
        """
    )
    
    parser.add_argument(
        '--auth',
        action='store_true',
        help='Ejecutar con autenticación (ventana de login)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Sistema de Gestión de Parqueadero v2.0.3'
    )
    
    args = parser.parse_args()
    
    # Ejecutar según el modo seleccionado
    if args.auth:
        print("[INFO] Iniciando sistema CON autenticación...")
        from scripts.main_with_auth import AuthenticatedApp
        app = AuthenticatedApp()
        sys.exit(app.run())
    else:
        print("[INFO] Iniciando sistema SIN autenticación (modo desarrollo)...")
        from PyQt5.QtWidgets import QApplication
        from scripts.main_modular import MainWindow
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
