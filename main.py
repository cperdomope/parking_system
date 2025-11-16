#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
SISTEMA DE GESTIÓN DE PARQUEADERO - Ssalud Plaza Claro
Punto de Entrada Principal
============================================================

Este es el ÚNICO punto de entrada de la aplicación.
Compatible con PyInstaller para generar ejecutables.

Autor: Sistema de Gestión
Versión: 2.1.0
Python: 3.8+
============================================================
"""

import sys
import os
import traceback
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURACIÓN CRÍTICA DE RUTAS PARA PYINSTALLER
# ============================================================
# Agregar la raíz del proyecto al PYTHONPATH para imports correctos
# Esto funciona tanto en desarrollo como en ejecutable empaquetado
if getattr(sys, 'frozen', False):
    # Modo PyInstaller: estamos en un ejecutable
    BASE_DIR = Path(sys._MEIPASS)
    RUNNING_AS_EXE = True
else:
    # Modo desarrollo: estamos ejecutando el script directamente
    BASE_DIR = Path(__file__).resolve().parent
    RUNNING_AS_EXE = False

# Agregar BASE_DIR al path si no está
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def log_error_to_file(error_message: str, exception: Exception = None):
    """
    Guarda errores críticos en un archivo de log cuando la app falla.

    Args:
        error_message: Mensaje descriptivo del error
        exception: Excepción capturada (opcional)
    """
    try:
        # Determinar dónde guardar el log de errores
        if RUNNING_AS_EXE:
            # En ejecutable: guardar junto al .exe
            log_file = Path(sys.executable).parent / "error_log.txt"
        else:
            # En desarrollo: guardar en la raíz del proyecto
            log_file = BASE_DIR / "error_log.txt"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 70 + "\n")
            f.write(f"ERROR FATAL - {timestamp}\n")
            f.write("=" * 70 + "\n")
            f.write(f"Modo de ejecución: {'Ejecutable' if RUNNING_AS_EXE else 'Desarrollo'}\n")
            f.write(f"Directorio base: {BASE_DIR}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"\n{error_message}\n\n")

            if exception:
                f.write("Detalles de la excepción:\n")
                f.write(f"Tipo: {type(exception).__name__}\n")
                f.write(f"Mensaje: {str(exception)}\n\n")
                f.write("Traceback completo:\n")
                f.write(traceback.format_exc())
                f.write("\n")

        print(f"\n[ERROR] Detalles guardados en: {log_file}")
        return str(log_file)

    except Exception as e:
        print(f"[ERROR CRÍTICO] No se pudo guardar el log de errores: {e}")
        return None


def show_error_dialog(message: str, log_file: str = None):
    """
    Muestra un diálogo de error gráfico al usuario.

    Args:
        message: Mensaje de error a mostrar
        log_file: Ruta al archivo de log (opcional)
    """
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox

        # Crear app temporal solo para el mensaje
        app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error Fatal - Sistema de Parqueadero")
        msg_box.setText("La aplicación no pudo iniciarse correctamente")

        detailed_text = message
        if log_file:
            detailed_text += f"\n\nDetalles completos guardados en:\n{log_file}"

        msg_box.setInformativeText(detailed_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    except Exception:
        # Si falla la GUI, mostrar por consola
        print("\n" + "=" * 70)
        print("ERROR FATAL")
        print("=" * 70)
        print(message)
        if log_file:
            print(f"\nDetalles guardados en: {log_file}")
        print("=" * 70)


def check_dependencies():
    """
    Verifica que todas las dependencias críticas estén instaladas.

    Returns:
        tuple: (éxito: bool, mensaje_error: str)
    """
    missing_deps = []

    try:
        import PyQt5
    except ImportError:
        missing_deps.append("PyQt5")

    try:
        import mysql.connector
    except ImportError:
        missing_deps.append("mysql-connector-python")

    if missing_deps:
        error_msg = (
            "Faltan las siguientes dependencias:\n" +
            "\n".join(f"  - {dep}" for dep in missing_deps) +
            "\n\nPor favor, instálalas con:\n" +
            f"pip install {' '.join(missing_deps)}"
        )
        return False, error_msg

    return True, ""


def main():
    """
    Función principal de la aplicación.

    Returns:
        int: Código de salida (0 = éxito, 1 = error)
    """
    log_file = None

    try:
        # ======================================================
        # 1. VERIFICAR DEPENDENCIAS
        # ======================================================
        print("[INFO] Verificando dependencias...")
        deps_ok, deps_error = check_dependencies()

        if not deps_ok:
            log_file = log_error_to_file(deps_error)
            show_error_dialog(deps_error, log_file)
            return 1

        # ======================================================
        # 2. IMPORTAR MÓDULOS DE LA APLICACIÓN
        # ======================================================
        print("[INFO] Cargando módulos del sistema...")

        try:
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import Qt

            # Importar módulos de la aplicación
            from src.auth.login_window import FuturisticLoginWindow
            from scripts.main_modular import MainWindow

        except ImportError as e:
            error_msg = (
                f"Error al importar módulos de la aplicación:\n{str(e)}\n\n"
                f"Verifica que la estructura del proyecto esté completa."
            )
            log_file = log_error_to_file(error_msg, e)
            show_error_dialog(error_msg, log_file)
            return 1

        # ======================================================
        # 3. CONFIGURAR APLICACIÓN PYQT
        # ======================================================
        print("[INFO] Inicializando interfaz gráfica...")

        # Habilitar DPI alto en Windows (mejora visualización)
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        # Crear aplicación
        app = QApplication(sys.argv)

        # Configurar para que no cierre al cerrar ventana (permite flujo login -> main)
        app.setQuitOnLastWindowClosed(False)

        # Metadatos de la aplicación
        app.setApplicationName("Sistema de Gestión de Parqueadero")
        app.setApplicationVersion("2.1.0")
        app.setOrganizationName("Ssalud Plaza Claro")

        # ======================================================
        # 4. MOSTRAR BANNER EN CONSOLA
        # ======================================================
        print("\n" + "=" * 70)
        print("  SISTEMA DE GESTIÓN DE PARQUEADERO")
        print("  Ssalud Plaza Claro")
        print("=" * 70)
        print(f"  Versión: 2.1.0")
        print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Modo: {'Ejecutable' if RUNNING_AS_EXE else 'Desarrollo'}")
        print(f"  Python: {sys.version.split()[0]}")
        print()
        print("  Módulos:")
        print("    ✓ Autenticación")
        print("    ✓ Dashboard")
        print("    ✓ Gestión de Funcionarios")
        print("    ✓ Gestión de Vehículos")
        print("    ✓ Gestión de Parqueaderos")
        print("    ✓ Asignaciones")
        print("    ✓ Reportes")
        print()
        print("=" * 70)
        print()

        # ======================================================
        # 5. IMPORTAR Y EJECUTAR APLICACIÓN AUTENTICADA
        # ======================================================
        print("[INFO] Iniciando sistema con autenticación...")

        # Importar clase de aplicación autenticada
        from scripts.main_with_auth import AuthenticatedApp

        # Crear instancia (pasamos la app ya creada)
        authenticated_app = AuthenticatedApp()

        # Iniciar aplicación
        return authenticated_app.start()

    except Exception as e:
        # ======================================================
        # MANEJO DE ERRORES GLOBALES
        # ======================================================
        error_msg = (
            f"Error inesperado durante la inicialización:\n"
            f"{type(e).__name__}: {str(e)}\n\n"
            f"La aplicación no puede continuar."
        )

        log_file = log_error_to_file(error_msg, e)
        show_error_dialog(error_msg, log_file)

        # Imprimir en consola para debugging
        print("\n" + "=" * 70)
        print("ERROR FATAL")
        print("=" * 70)
        traceback.print_exc()
        print("=" * 70)

        return 1


if __name__ == "__main__":
    # Ejecutar main y capturar código de salida
    exit_code = main()

    # Esperar input antes de cerrar si hubo error (útil cuando se ejecuta con doble clic)
    if exit_code != 0 and RUNNING_AS_EXE:
        input("\nPresiona ENTER para salir...")

    sys.exit(exit_code)
