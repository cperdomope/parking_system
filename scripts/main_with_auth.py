#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
=====================================================
SISTEMA DE GESTIÓN DE PARQUEADERO - CON AUTENTICACIÓN
Aplicación Principal con Login y PyQt5
=====================================================
Autor: Sistema de Gestión
Versión: 2.1
Python: 3.8+
=====================================================
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# Importaciones de módulos locales
from src.auth.login_window import FuturisticLoginWindow
from scripts.main_modular import MainWindow


class AuthenticatedApp:
    """
    Aplicación principal que maneja la autenticación y luego lanza el sistema
    """

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # No cerrar al cerrar ventana principal

        # Configurar atributos de aplicación
        self.app.setApplicationName("Sistema de Gestión de Parqueadero")
        self.app.setApplicationVersion("1.0")
        self.app.setOrganizationName("Ssalud Plaza Claro")

        self.login_window = None
        self.main_window = None
        self.current_user = None

    def start(self):
        """Inicia la aplicación mostrando primero el login"""
        try:
            self.show_login()
            return self.app.exec_()
        except Exception as e:
            QMessageBox.critical(None, "Error Fatal",
                               f"Error al iniciar la aplicación:\n{str(e)}")
            return 1

    def show_login(self):
        """Muestra la ventana de login"""
        self.login_window = FuturisticLoginWindow()

        # Conectar señal de login exitoso
        self.login_window.login_successful.connect(self.on_login_success)

        # Conectar señal de cierre para limpiar recursos
        self.app.aboutToQuit.connect(self.cleanup_resources)

        # Centrar ventana en pantalla
        self.center_window(self.login_window)

        # Mostrar ventana de login
        self.login_window.show()

    def on_login_success(self, user_data):
        """
        Maneja el evento de login exitoso

        Args:
            user_data: Diccionario con información del usuario autenticado
        """
        self.current_user = user_data

        # Mostrar aplicación principal primero
        self.show_main_application()

        # Ocultar ventana de login después de abrir la aplicación principal
        if self.login_window:
            self.login_window.hide()
            # No eliminar login_window, la reutilizaremos

    def show_main_application(self):
        """Muestra la aplicación principal del sistema de parqueadero"""
        try:
            self.main_window = MainWindow()

            # Configurar información del usuario en la ventana principal
            self.setup_user_info()

            # Conectar el evento de cierre para regresar al login
            self.main_window.closeEvent = self.on_main_window_close

            # Asegurar que la ventana no esté maximizada
            self.main_window.showNormal()

            # Centrar y mostrar ventana principal
            self.center_window(self.main_window)
            self.main_window.show()

        except Exception as e:
            QMessageBox.critical(None, "Error",
                               f"Error al abrir la aplicación principal:\n{str(e)}")
            self.show_login()  # Volver al login en caso de error

    def setup_user_info(self):
        """Configura la información del usuario en la ventana principal"""
        if self.main_window and self.current_user:
            # Actualizar título de ventana con información del usuario
            title = f"Sistema de Gestión de Parqueadero - {self.current_user['usuario']} ({self.current_user['rol']})"
            self.main_window.setWindowTitle(title)

            # Almacenar información del usuario en la ventana principal para uso posterior
            self.main_window.current_user = self.current_user

    def on_main_window_close(self, event):
        """Maneja el cierre de la ventana principal para regresar al login"""
        from PyQt5.QtWidgets import QMessageBox

        # Crear diálogo personalizado
        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("Cerrar Sesión")
        msg_box.setText("¿Qué desea hacer?")
        msg_box.setInformativeText("Seleccione una opción:")

        # Botones personalizados
        btn_login = msg_box.addButton("Regresar al Login", QMessageBox.AcceptRole)
        btn_exit = msg_box.addButton("Salir del Sistema", QMessageBox.DestructiveRole)
        btn_cancel = msg_box.addButton("Cancelar", QMessageBox.RejectRole)

        msg_box.setDefaultButton(btn_login)
        msg_box.exec_()

        reply = msg_box.clickedButton()

        if reply == btn_login:
            # Regresar al login
            self.return_to_login()
            event.accept()
        elif reply == btn_exit:
            # Salir completamente
            self.exit_application()
            event.accept()
        else:
            # Cancelar cierre
            event.ignore()

    def return_to_login(self):
        """Regresa al login cerrando la ventana principal"""
        try:
            # Cerrar ventana principal
            if self.main_window:
                self.main_window.hide()
                self.main_window = None

            # Limpiar datos de usuario actual
            self.current_user = None

            # Mostrar login nuevamente
            if self.login_window:
                # Limpiar campos del login
                self.login_window.user_input.clear()
                self.login_window.password_input.clear()
                self.login_window._login_success_pending = False

                # Centrar y mostrar login
                self.center_window(self.login_window)
                self.login_window.show()
            else:
                # Si no existe login window, crear una nueva
                self.show_login()

        except Exception as e:
            print(f"Error regresando al login: {e}")
            self.exit_application()

    def exit_application(self):
        """Sale completamente de la aplicación"""
        try:
            self.cleanup_resources()
            self.app.quit()
        except Exception as e:
            print(f"Error cerrando aplicación: {e}")
            self.app.quit()

    def cleanup_resources(self):
        """Limpia todos los recursos antes de cerrar la aplicación"""
        try:
            print("Cerrando aplicación y limpiando recursos...")

            # Solo cerrar la base de datos al final, desde la aplicación principal
            if self.main_window and hasattr(self.main_window, 'db'):
                self.main_window.db.disconnect()
                print("Conexión a base de datos cerrada")

            print("Recursos limpiados correctamente")

        except Exception as e:
            print(f"Error durante limpieza de recursos: {e}")

    def center_window(self, window):
        """
        Centra una ventana en la pantalla

        Args:
            window: Ventana a centrar
        """
        screen = self.app.primaryScreen().geometry()
        window_geometry = window.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        window.move(window_geometry.topLeft())


def main():
    """Función principal de la aplicación"""
    from datetime import datetime

    # Imprimir información del sistema en consola
    print("=" * 70)
    print("  SISTEMA DE GESTION DE PARQUEADERO - Ssalud Plaza Claro")
    print("  (Con Autenticacion)")
    print("=" * 70)
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Version: 1.0")
    print()
    print("  Modulos cargados:")
    print("    [OK] Sistema de Autenticacion")
    print("    [OK] DatabaseManager")
    print("    [OK] Dashboard")
    print("    [OK] Funcionarios")
    print("    [OK] Vehiculos")
    print("    [OK] Parqueaderos")
    print("    [OK] Asignaciones")
    print("    [OK] Reportes (7 pestanas)")
    print()
    print("  Credenciales de prueba:")
    print("    Usuario: splaza")
    print("    Password: splaza123*")
    print()
    print("=" * 70)
    print()

    # Habilitar DPI alto en Windows
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Crear y ejecutar aplicación
    app = AuthenticatedApp()
    return app.start()


if __name__ == "__main__":
    sys.exit(main())