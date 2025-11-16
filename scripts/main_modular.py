#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sistema de Gestión de Parqueadero - Aplicación Principal"""

import sys
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QMessageBox
)

from src.database.manager import DatabaseManager
from src.ui.dashboard_tab import DashboardWidget
from src.ui.funcionarios_tab import FuncionariosTab
from src.ui.vehiculos_tab import VehiculosTab
from src.ui.parqueaderos_tab import ParqueaderosTab
from src.ui.asignaciones_tab import AsignacionesTab
from src.ui.reportes_tab import ReportesTab
from src.ui.widgets.styles import AppStyles


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación modular"""

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()

        if not self.db.connection:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")
            sys.exit(1)

        self.setup_ui()
        self.setStyleSheet(AppStyles.MAIN_STYLE)

    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        self.setWindowTitle("Sistema de Gestión de Parqueadero - Ssalud Plaza Claro")

        # Configurar tamaño mínimo de ventana
        self.setMinimumSize(1200, 700)

        # Maximizar ventana automáticamente al iniciar
        self.showMaximized()

        # Widget central con pestañas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Crear las pestañas principales usando los nuevos módulos
        self.tab_dashboard = DashboardWidget(self.db)
        self.tab_funcionarios = FuncionariosTab(self.db)
        self.tab_vehiculos = VehiculosTab(self.db)
        self.tab_parqueaderos = ParqueaderosTab(self.db)
        self.tab_asignaciones = AsignacionesTab(self.db)
        self.tab_reportes = ReportesTab(self.db)

        # Agregar pestañas en el orden solicitado
        self.tabs.addTab(self.tab_dashboard, "🏠 Dashboard")
        self.tabs.addTab(self.tab_funcionarios, "👥 Funcionarios")
        self.tabs.addTab(self.tab_vehiculos, "🚗 Vehículos")
        self.tabs.addTab(self.tab_asignaciones, "📋 Asignaciones")
        self.tabs.addTab(self.tab_parqueaderos, "🅿️ Parqueaderos")
        self.tabs.addTab(self.tab_reportes, "📊 Reportes")

        # Conectar señales entre pestañas
        self.conectar_senales()

        # Barra de estado
        self.statusBar().showMessage("Sistema modular iniciado correctamente")

        # Configurar menú
        self.crear_menu()

    def conectar_senales(self):
        """Conecta las señales entre las diferentes pestañas para sincronización completa"""

        # ============================================
        # CONEXIONES DESDE FUNCIONARIOS
        # ============================================
        # Cuando se cree un funcionario, actualizar:
        self.tab_funcionarios.funcionario_creado.connect(self.tab_vehiculos.actualizar_combo_funcionarios)  # Combo en vehículos
        self.tab_funcionarios.funcionario_creado.connect(self.tab_dashboard.actualizar_dashboard)  # Dashboard

        # Cuando se ELIMINE un funcionario en cascada, actualizar TODAS las pestañas:
        self.tab_funcionarios.funcionario_eliminado.connect(self.tab_vehiculos.actualizar_vehiculos)  # Eliminar vehículos de la tabla
        self.tab_funcionarios.funcionario_eliminado.connect(self.tab_vehiculos.actualizar_combo_funcionarios)  # Actualizar combo
        self.tab_funcionarios.funcionario_eliminado.connect(self.tab_asignaciones.actualizar_asignaciones)  # Eliminar asignaciones de la tabla
        self.tab_funcionarios.funcionario_eliminado.connect(self.tab_parqueaderos.actualizar_parqueaderos)  # Actualizar estados de parqueaderos
        self.tab_funcionarios.funcionario_eliminado.connect(self.tab_dashboard.actualizar_dashboard)  # Actualizar estadísticas

        # ============================================
        # CONEXIONES DESDE VEHÍCULOS
        # ============================================
        # Cuando se cree/elimine un vehículo, actualizar:
        self.tab_vehiculos.vehiculo_creado.connect(self.tab_asignaciones.actualizar_vehiculos_sin_asignar)  # Lista sin asignar
        self.tab_vehiculos.vehiculo_creado.connect(self.tab_asignaciones.cargar_asignaciones)  # Tabla asignaciones actuales
        self.tab_vehiculos.vehiculo_creado.connect(self.tab_parqueaderos.actualizar_parqueaderos)  # Lista parqueaderos
        self.tab_vehiculos.vehiculo_creado.connect(self.tab_dashboard.actualizar_dashboard)  # Dashboard
        self.tab_vehiculos.vehiculo_creado.connect(self.tab_funcionarios.actualizar_funcionarios)  # Tabla funcionarios (contador vehículos)

        # ============================================
        # CONEXIONES DESDE ASIGNACIONES
        # ============================================
        # Cuando se actualicen asignaciones, actualizar:
        self.tab_asignaciones.asignacion_actualizada.connect(self.tab_parqueaderos.actualizar_parqueaderos)  # Vista parqueaderos
        self.tab_asignaciones.asignacion_actualizada.connect(self.tab_dashboard.actualizar_dashboard)  # Dashboard
        self.tab_asignaciones.asignacion_actualizada.connect(self.tab_vehiculos.actualizar_vehiculos)  # Tabla vehículos
        self.tab_asignaciones.asignacion_actualizada.connect(self.tab_funcionarios.actualizar_funcionarios)  # Tabla funcionarios

        # ============================================
        # CONEXIONES DESDE PARQUEADEROS
        # ============================================
        # Cuando se actualicen parqueaderos, actualizar:
        self.tab_parqueaderos.parqueaderos_actualizados.connect(self.tab_dashboard.actualizar_dashboard)  # Dashboard

        # ============================================
        # CONEXIONES HACIA REPORTES
        # ============================================
        # Actualizar reportes cuando cambien asignaciones o parqueaderos:
        self.tab_asignaciones.asignacion_actualizada.connect(self.tab_reportes.actualizar_reportes)  # Actualizar reportes
        self.tab_parqueaderos.parqueaderos_actualizados.connect(self.tab_reportes.actualizar_reportes)  # Actualizar reportes

        # ============================================
        # CONEXIONES DESDE DASHBOARD
        # ============================================
        # La funcionalidad de búsqueda fue eliminada del dashboard.

    def crear_menu(self):
        """Crea el menú de la aplicación"""
        menubar = self.menuBar()

        # Menú Archivo
        menu_archivo = menubar.addMenu("&Archivo")

        accion_salir = menu_archivo.addAction("Salir")
        accion_salir.triggered.connect(self.close)

        # Menú Ayuda
        menu_ayuda = menubar.addMenu("&Ayuda")

        accion_acerca = menu_ayuda.addAction("Acerca de")
        accion_acerca.triggered.connect(self.mostrar_acerca_de)

    def mostrar_acerca_de(self):
        """Muestra el diálogo 'Acerca de'"""
        QMessageBox.about(
            self,
            "Acerca de",
            "Sistema de Gestión de Parqueadero - Versión Modular\n"
            "Versión 1.0\n\n"
            "Desarrollado por Carlos Ivan Perdomo con una arquitectura modular para facilitar"
            " el mantenimiento y la depuración.\n\n"
            "© 2025 - Sistema de Gestión"
        )

    def closeEvent(self, event):
        """Evento al cerrar la aplicación"""
        reply = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro de que desea salir?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.db.disconnect()
            event.accept()
        else:
            event.ignore()


def main():
    """Función principal para iniciar la aplicación"""
    # Imprimir información del sistema en consola
    print("=" * 70)
    print("  SISTEMA DE GESTION DE PARQUEADERO - Ssalud Plaza Claro")
    print("=" * 70)
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Version: 1.0")
    print()
    print("  Modulos cargados:")
    print("    [OK] DatabaseManager")
    print("    [OK] Dashboard")
    print("    [OK] Funcionarios")
    print("    [OK] Vehiculos")
    print("    [OK] Parqueaderos")
    print("    [OK] Asignaciones")
    print("    [OK] Reportes (7 pestanas)")
    print()
    print("  Pestanas de Reportes:")
    print("    1. Reporte General")
    print("    2. Funcionarios")
    print("    3. Vehiculos")
    print("    4. Parqueaderos")
    print("    5. Asignaciones")
    print("    6. Excepciones Pico y Placa")
    print("    7. Estadisticas (graficos)")
    print()
    print("=" * 70)
    print()

    app = QApplication(sys.argv)

    # Configurar el estilo de la aplicación
    app.setStyle('Fusion')

    # Crear y mostrar la ventana principal
    window = MainWindow()
    window.show()

    # Ejecutar el loop de eventos
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()