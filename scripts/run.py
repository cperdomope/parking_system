#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de conveniencia para ejecutar el sistema SIN autenticación.

Uso:
    python scripts/run.py
    python scripts/run.py --help
"""

import sys
import argparse
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from PyQt5.QtWidgets import QApplication
from scripts.main_modular import MainWindow


def main():
    """Ejecutar aplicación sin autenticación"""
    parser = argparse.ArgumentParser(
        description='Sistema de Gestión de Parqueadero (sin autenticación)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Este script ejecuta el sistema en modo desarrollo SIN autenticación.
Para ejecutar con autenticación, usar: python scripts/run_with_auth.py

Versión: 2.0.3
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Sistema de Gestión de Parqueadero v2.0.3'
    )
    
    args = parser.parse_args()
    
    print("[INFO] Iniciando sistema SIN autenticación (modo desarrollo)...")
    print("[INFO] Conectando a base de datos...")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
