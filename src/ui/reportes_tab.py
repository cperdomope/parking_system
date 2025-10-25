# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Reportes del sistema de gestión de parqueadero
"""

import csv
from datetime import datetime

from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..database.manager import DatabaseManager

# Imports opcionales para exportación
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

# Imports para gráficos con matplotlib
try:
    import matplotlib

    matplotlib.use("Qt5Agg")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ReportesTab(QWidget):
    """Pestaña de generación y visualización de reportes del sistema"""

    # Señales
    reporte_generado = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager

        # Inicializar filtros
        self.filtros_activos = {"tipo_vehiculo": None, "cargo": None, "fecha_inicio": None, "fecha_fin": None}

        self.setup_ui()
        self.actualizar_reportes()

    def setup_ui(self):
        """Configura la interfaz de usuario de la pestaña Reportes"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        # Título de la sección
        title_label = QLabel("📊 Sistema de Reportes")
        title_label.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """
        )
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Sección de filtros
        filtros_group = QGroupBox("Filtros de Reporte")
        filtros_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """
        )

        # Layout vertical principal para separar en dos filas
        filtros_main_layout = QVBoxLayout()
        filtros_main_layout.setSpacing(10)

        # FILA 1: ComboBox de Tipo de Vehículo y Cargo
        fila1_layout = QHBoxLayout()
        fila1_layout.setSpacing(15)

        # ComboBox: Tipo de Vehículo
        fila1_layout.addWidget(QLabel("Tipo Vehículo:"))
        self.combo_tipo_vehiculo = QComboBox()
        self.combo_tipo_vehiculo.addItems(["Todos", "Carro", "Moto", "Bicicleta"])
        self.combo_tipo_vehiculo.setStyleSheet(
            """
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                min-width: 120px;
            }
        """
        )
        fila1_layout.addWidget(self.combo_tipo_vehiculo)

        # ComboBox: Cargo
        fila1_layout.addWidget(QLabel("Cargo:"))
        self.combo_cargo = QComboBox()
        self.combo_cargo.addItems(
            [
                "Todos",
                "Director",
                "Coordinador",
                "Asesor",
                "Auxiliar",
                "Conductor",
                "Jefe de Oficina",
                "Profesional",
                "Técnico",
                "Otro",
            ]
        )
        self.combo_cargo.setStyleSheet(
            """
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                min-width: 140px;
            }
        """
        )
        fila1_layout.addWidget(self.combo_cargo)
        fila1_layout.addStretch()

        # FILA 2: Fechas y Botones
        fila2_layout = QHBoxLayout()
        fila2_layout.setSpacing(15)

        # Fecha Inicial
        fila2_layout.addWidget(QLabel("Fecha Inicio:"))
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate().addMonths(-1))  # Hace 1 mes
        self.date_inicio.setDisplayFormat("dd/MM/yyyy")
        self.date_inicio.setStyleSheet(
            """
            QDateEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                min-width: 110px;
            }
        """
        )
        fila2_layout.addWidget(self.date_inicio)

        # Fecha Final
        fila2_layout.addWidget(QLabel("Fecha Fin:"))
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setStyleSheet(
            """
            QDateEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 3px;
                min-width: 110px;
            }
        """
        )
        fila2_layout.addWidget(self.date_fin)

        # Botón Aplicar Filtros
        self.btn_aplicar_filtros = QPushButton("Aplicar Filtros")
        self.btn_aplicar_filtros.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
                min-width: 130px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
        )
        self.btn_aplicar_filtros.clicked.connect(self.aplicar_filtros)
        fila2_layout.addWidget(self.btn_aplicar_filtros)

        # Botón Limpiar Filtros
        self.btn_limpiar_filtros = QPushButton("Limpiar")
        self.btn_limpiar_filtros.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #5d6d7e;
            }
        """
        )
        self.btn_limpiar_filtros.clicked.connect(self.limpiar_filtros)
        fila2_layout.addWidget(self.btn_limpiar_filtros)

        fila2_layout.addStretch()

        # Agregar las dos filas al layout principal
        filtros_main_layout.addLayout(fila1_layout)
        filtros_main_layout.addLayout(fila2_layout)

        filtros_group.setLayout(filtros_main_layout)
        main_layout.addWidget(filtros_group)

        # Botón global de actualización
        btn_layout = QHBoxLayout()
        self.btn_actualizar_global = QPushButton("🔄 Actualizar Todos los Reportes")
        self.btn_actualizar_global.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
        )
        self.btn_actualizar_global.clicked.connect(self.actualizar_reportes)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_actualizar_global)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # TabWidget para las subpestañas de reportes
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #5dade2;
                color: white;
            }
        """
        )
        main_layout.addWidget(self.tab_widget)

        # Crear las 7 subpestañas
        self.tab_general = self._crear_tab_reporte_general()
        self.tab_funcionarios = self._crear_tab_funcionarios()
        self.tab_vehiculos = self._crear_tab_vehiculos()
        self.tab_parqueaderos = self._crear_tab_parqueaderos()
        self.tab_asignaciones = self._crear_tab_asignaciones()
        self.tab_excepciones = self._crear_tab_excepciones()
        self.tab_estadisticas = self._crear_tab_estadisticas()

        self.tab_widget.addTab(self.tab_general, "📋 Reporte General")
        self.tab_widget.addTab(self.tab_funcionarios, "👥 Funcionarios")
        self.tab_widget.addTab(self.tab_vehiculos, "🚗 Vehículos")
        self.tab_widget.addTab(self.tab_parqueaderos, "🅿️ Parqueaderos")
        self.tab_widget.addTab(self.tab_asignaciones, "📍 Asignaciones")
        self.tab_widget.addTab(self.tab_excepciones, "🔄 Excepciones Pico y Placa")
        self.tab_widget.addTab(self.tab_estadisticas, "📊 Estadísticas")

    def _crear_tab_reporte_general(self):
        """Crea la pestaña de Reporte General"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Descripción
        desc_label = QLabel("Vista consolidada del sistema: funcionarios, vehículos y ocupación de parqueaderos")
        desc_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(desc_label)

        # Tabla
        self.tabla_general = QTableWidget()
        self.tabla_general.setColumnCount(11)
        self.tabla_general.setHorizontalHeaderLabels(
            [
                "Cédula",
                "Nombre Completo",
                "Cargo",
                "Dirección/Grupo",
                "Celular",
                "Tipo Vehículo",
                "Placa",
                "Circulación",
                "N° Parqueadero",
                "Estado Parq.",
                "Pico y Placa Solidario",
            ]
        )
        self.tabla_general.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_general.setAlternatingRowColors(True)
        self.tabla_general.setStyleSheet(
            """
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #2c3e50;
            }
        """
        )
        layout.addWidget(self.tabla_general)

        # Botones de acción
        btn_layout = self._crear_botones_exportacion(self.tabla_general, "reporte_general")
        layout.addLayout(btn_layout)

        return widget

    def _crear_tab_funcionarios(self):
        """Crea la pestaña de Funcionarios"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Descripción
        desc_label = QLabel("Listado completo de funcionarios activos en el sistema")
        desc_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(desc_label)

        # Tabla
        self.tabla_funcionarios = QTableWidget()
        self.tabla_funcionarios.setColumnCount(10)
        self.tabla_funcionarios.setHorizontalHeaderLabels(
            [
                "ID",
                "Cédula",
                "Nombre",
                "Apellidos",
                "Dirección/Grupo",
                "Cargo",
                "Celular",
                "Tarjeta Prox.",
                "Vehículos",
                "Fecha Registro",
            ]
        )
        self.tabla_funcionarios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_funcionarios.setAlternatingRowColors(True)
        self.tabla_funcionarios.setStyleSheet(
            """
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #16a085;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #138d75;
            }
        """
        )
        layout.addWidget(self.tabla_funcionarios)

        # Botones de acción
        btn_layout = self._crear_botones_exportacion(self.tabla_funcionarios, "reporte_funcionarios")
        layout.addLayout(btn_layout)

        return widget

    def _crear_tab_vehiculos(self):
        """Crea la pestaña de Vehículos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Descripción
        desc_label = QLabel("Registro de todos los vehículos y su tipo de circulación")
        desc_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(desc_label)

        # Tabla
        self.tabla_vehiculos = QTableWidget()
        self.tabla_vehiculos.setColumnCount(9)
        self.tabla_vehiculos.setHorizontalHeaderLabels(
            [
                "ID",
                "Placa",
                "Tipo Vehículo",
                "Circulación",
                "Propietario",
                "Cédula",
                "Estado Asignación",
                "N° Parqueadero",
                "Fecha Registro",
            ]
        )
        self.tabla_vehiculos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_vehiculos.setAlternatingRowColors(True)
        self.tabla_vehiculos.setStyleSheet(
            """
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #8e44ad;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #7d3c98;
            }
        """
        )
        layout.addWidget(self.tabla_vehiculos)

        # Botones de acción
        btn_layout = self._crear_botones_exportacion(self.tabla_vehiculos, "reporte_vehiculos")
        layout.addLayout(btn_layout)

        return widget

    def _crear_tab_parqueaderos(self):
        """Crea la pestaña de Parqueaderos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Descripción
        desc_label = QLabel("Estado de ocupación de todos los parqueaderos (200 espacios en 3 sótanos)")
        desc_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(desc_label)

        # Tabla
        self.tabla_parqueaderos = QTableWidget()
        self.tabla_parqueaderos.setColumnCount(8)
        self.tabla_parqueaderos.setHorizontalHeaderLabels(
            [
                "N° Parqueadero",
                "Sótano",
                "Tipo Vehículo",
                "Estado",
                "Vehículos Asignados",
                "Circulación PAR",
                "Circulación IMPAR",
                "Observaciones",
            ]
        )
        self.tabla_parqueaderos.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_parqueaderos.setAlternatingRowColors(True)
        self.tabla_parqueaderos.setStyleSheet(
            """
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #e67e22;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #d35400;
            }
        """
        )
        layout.addWidget(self.tabla_parqueaderos)

        # Botones de acción
        btn_layout = self._crear_botones_exportacion(self.tabla_parqueaderos, "reporte_parqueaderos")
        layout.addLayout(btn_layout)

        return widget

    def _crear_tab_asignaciones(self):
        """Crea la pestaña de Asignaciones"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Descripción
        desc_label = QLabel("Asignaciones activas de vehículos a parqueaderos")
        desc_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(desc_label)

        # Tabla
        self.tabla_asignaciones = QTableWidget()
        self.tabla_asignaciones.setColumnCount(10)
        self.tabla_asignaciones.setHorizontalHeaderLabels(
            [
                "ID Asignación",
                "N° Parqueadero",
                "Placa",
                "Tipo Vehículo",
                "Propietario",
                "Cédula",
                "Circulación",
                "Fecha Asignación",
                "Estado",
                "Observaciones",
            ]
        )
        self.tabla_asignaciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_asignaciones.setAlternatingRowColors(True)
        self.tabla_asignaciones.setStyleSheet(
            """
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #2980b9;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #1f618d;
            }
        """
        )
        layout.addWidget(self.tabla_asignaciones)

        # Botones de acción
        btn_layout = self._crear_botones_exportacion(self.tabla_asignaciones, "reporte_asignaciones")
        layout.addLayout(btn_layout)

        return widget

    def _crear_tab_excepciones(self):
        """Crea la pestaña de Excepciones Pico y Placa"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # Descripción
        desc_label = QLabel(
            "Funcionarios con excepciones especiales: Pico y Placa Solidario, Discapacidad y Parqueadero Exclusivo"
        )
        desc_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(desc_label)

        # Tabla
        self.tabla_excepciones = QTableWidget()
        self.tabla_excepciones.setColumnCount(9)
        self.tabla_excepciones.setHorizontalHeaderLabels(
            [
                "Cédula",
                "Nombre Completo",
                "Cargo",
                "Pico y Placa Solidario",
                "Discapacidad",
                "Exclusivo Directivo",
                "Placa",
                "N° Parqueadero",
                "Observaciones",
            ]
        )
        self.tabla_excepciones.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_excepciones.setAlternatingRowColors(True)
        self.tabla_excepciones.setStyleSheet(
            """
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #c0392b;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: 1px solid #a93226;
            }
        """
        )
        layout.addWidget(self.tabla_excepciones)

        # Botones de acción
        btn_layout = self._crear_botones_exportacion(self.tabla_excepciones, "reporte_excepciones")
        layout.addLayout(btn_layout)

        return widget

    def _crear_tab_estadisticas(self):
        """Crea la pestaña de Estadísticas con gráficos matplotlib"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)

        if not MATPLOTLIB_AVAILABLE:
            # Mensaje si matplotlib no está disponible
            msg_label = QLabel(
                "⚠️ La visualización de estadísticas requiere matplotlib.\n\n" "Instalar con: pip install matplotlib"
            )
            msg_label.setStyleSheet(
                """
                QLabel {
                    color: #e67e22;
                    font-size: 14px;
                    padding: 20px;
                    background-color: #fef5e7;
                    border: 2px solid #f39c12;
                    border-radius: 5px;
                }
            """
            )
            msg_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(msg_label)
            return widget

        # Descripción
        desc_label = QLabel("Visualización gráfica de estadísticas del sistema en tiempo real")
        desc_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 5px;")
        layout.addWidget(desc_label)

        # Botón de actualización
        btn_actualizar = QPushButton("🔄 Actualizar Gráficos")
        btn_actualizar.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        btn_actualizar.clicked.connect(self.actualizar_estadisticas)
        layout.addWidget(btn_actualizar, alignment=Qt.AlignCenter)

        # Layout de gráficos
        graficos_layout = QVBoxLayout()

        # Crear canvas para los 3 gráficos
        self.figura_estadisticas = Figure(figsize=(12, 10))
        self.canvas_estadisticas = FigureCanvas(self.figura_estadisticas)
        graficos_layout.addWidget(self.canvas_estadisticas)

        layout.addLayout(graficos_layout)

        return widget

    def _crear_botones_exportacion(self, tabla, nombre_base):
        """Crea los botones de exportación para una tabla"""
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        # Botón Exportar CSV
        btn_csv = QPushButton("📄 CSV")
        btn_csv.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """
        )
        btn_csv.clicked.connect(lambda: self.exportar_csv(tabla, nombre_base))
        btn_layout.addWidget(btn_csv)

        # Botón Exportar Excel
        btn_excel = QPushButton("📊 Excel")
        btn_excel.setStyleSheet(
            """
            QPushButton {
                background-color: #16a085;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """
        )
        btn_excel.clicked.connect(lambda: self.exportar_excel(tabla, nombre_base))
        btn_layout.addWidget(btn_excel)

        # Botón Exportar PDF
        btn_pdf = QPushButton("📕 PDF")
        btn_pdf.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        btn_pdf.clicked.connect(lambda: self.exportar_pdf(tabla, nombre_base))
        btn_layout.addWidget(btn_pdf)

        btn_layout.addStretch()
        return btn_layout

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados y actualiza los reportes"""
        # Capturar valores de filtros
        tipo_vehiculo = self.combo_tipo_vehiculo.currentText()
        cargo = self.combo_cargo.currentText()
        fecha_inicio = self.date_inicio.date().toPyDate()
        fecha_fin = self.date_fin.date().toPyDate()

        # Validar rango de fechas
        if fecha_inicio > fecha_fin:
            QMessageBox.warning(self, "Error en fechas", "La fecha de inicio no puede ser posterior a la fecha de fin.")
            return

        # Actualizar filtros activos
        self.filtros_activos["tipo_vehiculo"] = None if tipo_vehiculo == "Todos" else tipo_vehiculo
        self.filtros_activos["cargo"] = None if cargo == "Todos" else cargo
        self.filtros_activos["fecha_inicio"] = fecha_inicio
        self.filtros_activos["fecha_fin"] = fecha_fin

        # Actualizar reportes con filtros
        self.actualizar_reportes()

    def limpiar_filtros(self):
        """Limpia todos los filtros y resetea a valores por defecto"""
        # Resetear combos
        self.combo_tipo_vehiculo.setCurrentIndex(0)  # "Todos"
        self.combo_cargo.setCurrentIndex(0)  # "Todos"

        # Resetear fechas
        self.date_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.date_fin.setDate(QDate.currentDate())

        # Limpiar filtros activos
        self.filtros_activos = {"tipo_vehiculo": None, "cargo": None, "fecha_inicio": None, "fecha_fin": None}

        # Actualizar reportes sin filtros
        self.actualizar_reportes()

    def _construir_filtro_sql(self, tabla_alias=""):
        """Construye la cláusula WHERE para los filtros activos"""
        condiciones = []
        params = []

        # Prefijo para tabla
        prefix = f"{tabla_alias}." if tabla_alias else ""

        # Filtro por tipo de vehículo
        if self.filtros_activos.get("tipo_vehiculo"):
            condiciones.append(f"{prefix}tipo_vehiculo = %s")
            params.append(self.filtros_activos["tipo_vehiculo"])

        # Filtro por cargo (solo si la tabla tiene cargo)
        if self.filtros_activos.get("cargo") and "funcionario" in tabla_alias.lower():
            condiciones.append(f"{prefix}cargo = %s")
            params.append(self.filtros_activos["cargo"])

        # Filtro por rango de fechas
        if self.filtros_activos.get("fecha_inicio") and self.filtros_activos.get("fecha_fin"):
            if "fecha_registro" in tabla_alias or "fecha_creacion" in tabla_alias:
                condiciones.append(f"{prefix}fecha_registro BETWEEN %s AND %s")
                params.append(self.filtros_activos["fecha_inicio"])
                params.append(self.filtros_activos["fecha_fin"])

        return (" AND " + " AND ".join(condiciones), params) if condiciones else ("", [])

    def actualizar_reportes(self):
        """Actualiza todos los reportes cargando datos desde la base de datos"""
        errores = []

        # Actualizar cada reporte individualmente con manejo de errores
        try:
            self.actualizar_reporte_general()
        except Exception as e:
            errores.append(f"Reporte General: {str(e)}")

        try:
            self.actualizar_funcionarios()
        except Exception as e:
            errores.append(f"Funcionarios: {str(e)}")

        try:
            self.actualizar_vehiculos()
        except Exception as e:
            errores.append(f"Vehículos: {str(e)}")

        try:
            self.actualizar_parqueaderos()
        except Exception as e:
            errores.append(f"Parqueaderos: {str(e)}")

        try:
            self.actualizar_asignaciones()
        except Exception as e:
            errores.append(f"Asignaciones: {str(e)}")

        try:
            self.actualizar_excepciones()
        except Exception as e:
            errores.append(f"Excepciones: {str(e)}")

        # Actualizar estadísticas si matplotlib está disponible
        if MATPLOTLIB_AVAILABLE:
            try:
                self.actualizar_estadisticas()
            except Exception as e:
                errores.append(f"Estadísticas: {str(e)}")

        # Emitir señal de reporte generado
        self.reporte_generado.emit()

        # Mostrar resultado
        if errores:
            QMessageBox.warning(
                self, "Actualización parcial", "Algunos reportes no se pudieron actualizar:\n\n" + "\n".join(errores)
            )
        else:
            # Solo mostrar mensaje de éxito si se llamó desde el botón global
            # No mostrar cuando se actualiza por señales
            pass

    def actualizar_reporte_general(self):
        """Actualiza el reporte general con datos consolidados"""
        query = """
            SELECT
                f.cedula,
                CONCAT(f.nombre, ' ', f.apellidos) as nombre_completo,
                f.cargo,
                f.direccion_grupo,
                f.celular,
                v.tipo_vehiculo,
                v.placa,
                v.tipo_circulacion,
                p.numero_parqueadero,
                p.estado as estado_parqueadero,
                CASE WHEN f.pico_placa_solidario = 1 THEN 'Sí' ELSE 'No' END as pico_placa_solidario
            FROM funcionarios f
            LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
            WHERE f.activo = TRUE
            ORDER BY f.apellidos, f.nombre
        """
        datos = self.db.fetch_all(query)
        self._llenar_tabla(self.tabla_general, datos)

    def actualizar_funcionarios(self):
        """Actualiza el reporte de funcionarios"""
        # Construir query base
        query = """
            SELECT
                f.id,
                f.cedula,
                f.nombre,
                f.apellidos,
                f.direccion_grupo,
                f.cargo,
                f.celular,
                f.no_tarjeta_proximidad,
                COUNT(v.id) as total_vehiculos,
                DATE_FORMAT(f.fecha_registro, '%Y-%m-%d') as fecha_registro
            FROM funcionarios f
            LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
            WHERE f.activo = TRUE
        """

        # Aplicar filtros
        params = []
        if self.filtros_activos.get("cargo"):
            query += " AND f.cargo = %s"
            params.append(self.filtros_activos["cargo"])

        if self.filtros_activos.get("fecha_inicio") and self.filtros_activos.get("fecha_fin"):
            query += " AND f.fecha_registro BETWEEN %s AND %s"
            params.append(self.filtros_activos["fecha_inicio"])
            params.append(self.filtros_activos["fecha_fin"])

        query += """
            GROUP BY f.id, f.cedula, f.nombre, f.apellidos, f.direccion_grupo,
                     f.cargo, f.celular, f.no_tarjeta_proximidad, f.fecha_registro
            ORDER BY f.apellidos, f.nombre
        """

        datos = self.db.fetch_all(query, tuple(params) if params else None)
        self._llenar_tabla(self.tabla_funcionarios, datos)

    def actualizar_vehiculos(self):
        """Actualiza el reporte de vehículos"""
        query = """
            SELECT
                v.id,
                COALESCE(v.placa, 'Sin Placa') as placa,
                v.tipo_vehiculo,
                v.tipo_circulacion,
                CONCAT(f.nombre, ' ', f.apellidos) as propietario,
                f.cedula,
                CASE
                    WHEN a.id IS NOT NULL THEN 'Asignado'
                    ELSE 'Sin Asignar'
                END as estado_asignacion,
                COALESCE(p.numero_parqueadero, 'N/A') as numero_parqueadero,
                DATE_FORMAT(v.fecha_registro, '%Y-%m-%d') as fecha_registro
            FROM vehiculos v
            INNER JOIN funcionarios f ON v.funcionario_id = f.id
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
            WHERE v.activo = TRUE
        """

        # Aplicar filtros
        params = []
        if self.filtros_activos.get("tipo_vehiculo"):
            query += " AND v.tipo_vehiculo = %s"
            params.append(self.filtros_activos["tipo_vehiculo"])

        if self.filtros_activos.get("cargo"):
            query += " AND f.cargo = %s"
            params.append(self.filtros_activos["cargo"])

        if self.filtros_activos.get("fecha_inicio") and self.filtros_activos.get("fecha_fin"):
            query += " AND v.fecha_registro BETWEEN %s AND %s"
            params.append(self.filtros_activos["fecha_inicio"])
            params.append(self.filtros_activos["fecha_fin"])

        query += " ORDER BY v.placa"

        datos = self.db.fetch_all(query, tuple(params) if params else None)
        self._llenar_tabla(self.tabla_vehiculos, datos)

    def actualizar_parqueaderos(self):
        """Actualiza el reporte de parqueaderos"""
        # Verificar si existe la columna 'sotano'
        try:
            check_query = "SHOW COLUMNS FROM parqueaderos LIKE 'sotano'"
            column_exists = self.db.fetch_one(check_query) is not None
        except Exception as e:
            print(f"Advertencia al verificar columna 'sotano': {e}")
            column_exists = False

        if column_exists:
            query = """
                SELECT
                    p.numero_parqueadero,
                    COALESCE(p.sotano, 'Sótano-1') as sotano,
                    p.tipo_espacio,
                    p.estado,
                    COUNT(a.id) as vehiculos_asignados,
                    GROUP_CONCAT(CASE WHEN v.tipo_circulacion = 'PAR' THEN v.placa END) as circulacion_par,
                    GROUP_CONCAT(CASE WHEN v.tipo_circulacion = 'IMPAR' THEN v.placa END) as circulacion_impar,
                    CASE
                        WHEN p.estado = 'Disponible' THEN 'Libre'
                        WHEN p.estado = 'Parcialmente_Asignado' THEN 'Puede compartir'
                        WHEN p.estado = 'Completo' THEN 'Ocupado'
                        ELSE p.estado
                    END as observaciones
                FROM parqueaderos p
                LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
                LEFT JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE p.activo = TRUE
                GROUP BY p.id, p.numero_parqueadero, p.sotano, p.tipo_espacio, p.estado
                ORDER BY COALESCE(p.sotano, 'Sótano-1'), p.numero_parqueadero
            """
        else:
            query = """
                SELECT
                    p.numero_parqueadero,
                    'Sótano-1' as sotano,
                    p.tipo_espacio,
                    p.estado,
                    COUNT(a.id) as vehiculos_asignados,
                    GROUP_CONCAT(CASE WHEN v.tipo_circulacion = 'PAR' THEN v.placa END) as circulacion_par,
                    GROUP_CONCAT(CASE WHEN v.tipo_circulacion = 'IMPAR' THEN v.placa END) as circulacion_impar,
                    CASE
                        WHEN p.estado = 'Disponible' THEN 'Libre'
                        WHEN p.estado = 'Parcialmente_Asignado' THEN 'Puede compartir'
                        WHEN p.estado = 'Completo' THEN 'Ocupado'
                        ELSE p.estado
                    END as observaciones
                FROM parqueaderos p
                LEFT JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
                LEFT JOIN vehiculos v ON a.vehiculo_id = v.id
                WHERE p.activo = TRUE
                GROUP BY p.id, p.numero_parqueadero, p.tipo_espacio, p.estado
                ORDER BY p.numero_parqueadero
            """

        datos = self.db.fetch_all(query)
        self._llenar_tabla(self.tabla_parqueaderos, datos)

    def actualizar_asignaciones(self):
        """Actualiza el reporte de asignaciones activas"""
        query = """
            SELECT
                a.id as id_asignacion,
                p.numero_parqueadero,
                COALESCE(v.placa, 'Sin Placa') as placa,
                v.tipo_vehiculo,
                CONCAT(f.nombre, ' ', f.apellidos) as propietario,
                f.cedula,
                v.tipo_circulacion,
                DATE_FORMAT(a.fecha_asignacion, '%Y-%m-%d %H:%i') as fecha_asignacion,
                CASE WHEN a.activo = 1 THEN 'Activa' ELSE 'Inactiva' END as estado,
                CASE
                    WHEN f.pico_placa_solidario = 1 THEN 'Pico y Placa Solidario'
                    WHEN f.tiene_parqueadero_exclusivo = 1 THEN 'Exclusivo Directivo'
                    ELSE 'Normal'
                END as observaciones
            FROM asignaciones a
            INNER JOIN parqueaderos p ON a.parqueadero_id = p.id
            INNER JOIN vehiculos v ON a.vehiculo_id = v.id
            INNER JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE a.activo = TRUE
            ORDER BY a.fecha_asignacion DESC
        """
        datos = self.db.fetch_all(query)
        self._llenar_tabla(self.tabla_asignaciones, datos)

    def actualizar_excepciones(self):
        """Actualiza el reporte de excepciones (Pico y Placa Solidario, Discapacidad, Exclusivo)"""
        query = """
            SELECT
                f.cedula,
                CONCAT(f.nombre, ' ', f.apellidos) as nombre_completo,
                f.cargo,
                CASE WHEN f.pico_placa_solidario = 1 THEN '✅ Sí' ELSE '❌ No' END as pico_placa_solidario,
                CASE WHEN f.discapacidad = 1 THEN '✅ Sí' ELSE '❌ No' END as discapacidad,
                CASE WHEN f.tiene_parqueadero_exclusivo = 1 THEN '✅ Sí' ELSE '❌ No' END as parqueadero_exclusivo,
                COALESCE(v.placa, 'Sin vehículo') as placa,
                COALESCE(p.numero_parqueadero, 'N/A') as numero_parqueadero,
                CASE
                    WHEN f.pico_placa_solidario = 1 THEN 'Puede usar parqueadero cualquier día'
                    WHEN f.discapacidad = 1 THEN 'Prioridad para espacios especiales'
                    WHEN f.tiene_parqueadero_exclusivo = 1 THEN 'Parqueadero exclusivo (hasta 4 vehículos)'
                    ELSE 'Sin excepciones'
                END as observaciones
            FROM funcionarios f
            LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
            WHERE f.activo = TRUE
                AND (f.pico_placa_solidario = 1 OR f.discapacidad = 1 OR f.tiene_parqueadero_exclusivo = 1)
            ORDER BY f.apellidos, f.nombre
        """
        datos = self.db.fetch_all(query)
        self._llenar_tabla(self.tabla_excepciones, datos)

    def actualizar_estadisticas(self):
        """Actualiza los gráficos de estadísticas"""
        if not MATPLOTLIB_AVAILABLE:
            return

        try:
            # Limpiar figura
            self.figura_estadisticas.clear()

            # Crear subplots 2x2 (usaremos 3)
            ax1 = self.figura_estadisticas.add_subplot(2, 2, 1)
            ax2 = self.figura_estadisticas.add_subplot(2, 2, 2)
            ax3 = self.figura_estadisticas.add_subplot(2, 1, 2)

            # Gráfico 1: Ocupación de Parqueaderos
            self._grafico_ocupacion_parqueaderos(ax1)

            # Gráfico 2: Distribución de Tipos de Vehículo
            self._grafico_distribucion_vehiculos(ax2)

            # Gráfico 3: Funcionarios por Cargo
            self._grafico_funcionarios_por_cargo(ax3)

            # Ajustar layout
            self.figura_estadisticas.tight_layout(pad=3.0)

            # Refrescar canvas
            self.canvas_estadisticas.draw()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar estadísticas: {str(e)}")

    def _grafico_ocupacion_parqueaderos(self, ax):
        """Genera gráfico de pastel para ocupación de parqueaderos"""
        try:
            query = """
                SELECT
                    estado,
                    COUNT(*) as cantidad
                FROM parqueaderos
                WHERE activo = TRUE
                GROUP BY estado
            """
            datos = self.db.fetch_all(query)

            if not datos:
                ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
                return

            estados = [d["estado"] for d in datos]
            cantidades = [d["cantidad"] for d in datos]

            # Colores personalizados
            colores_map = {
                "Disponible": "#2ecc71",  # Verde
                "Parcialmente_Asignado": "#f39c12",  # Naranja
                "Completo": "#e74c3c",  # Rojo
            }
            colores = [colores_map.get(e, "#95a5a6") for e in estados]

            # Etiquetas más legibles
            labels_map = {"Disponible": "Disponible", "Parcialmente_Asignado": "Parcial", "Completo": "Completo"}
            labels = [labels_map.get(e, e) for e in estados]

            # Crear gráfico de pastel
            wedges, texts, autotexts = ax.pie(
                cantidades,
                labels=labels,
                autopct="%1.1f%%",
                colors=colores,
                startangle=90,
                textprops={"fontsize": 9, "weight": "bold"},
            )

            ax.set_title("Ocupación de Parqueaderos", fontsize=12, weight="bold", pad=10)

        except Exception as e:
            ax.text(0.5, 0.5, f"Error: {str(e)}", ha="center", va="center", fontsize=8)

    def _grafico_distribucion_vehiculos(self, ax):
        """Genera gráfico de barras para distribución de tipos de vehículo"""
        try:
            query = """
                SELECT
                    v.tipo_vehiculo,
                    COUNT(*) as cantidad
                FROM vehiculos v
                INNER JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE v.activo = TRUE
            """

            # Aplicar filtros
            params = []
            if self.filtros_activos.get("tipo_vehiculo"):
                query += " AND v.tipo_vehiculo = %s"
                params.append(self.filtros_activos["tipo_vehiculo"])

            if self.filtros_activos.get("cargo"):
                query += " AND f.cargo = %s"
                params.append(self.filtros_activos["cargo"])

            if self.filtros_activos.get("fecha_inicio") and self.filtros_activos.get("fecha_fin"):
                query += " AND v.fecha_registro BETWEEN %s AND %s"
                params.append(self.filtros_activos["fecha_inicio"])
                params.append(self.filtros_activos["fecha_fin"])

            query += """
                GROUP BY v.tipo_vehiculo
                ORDER BY cantidad DESC
            """

            datos = self.db.fetch_all(query, tuple(params) if params else None)

            if not datos:
                ax.text(0.5, 0.5, "Sin datos", ha="center", va="center", transform=ax.transAxes)
                return

            tipos = [d["tipo_vehiculo"] for d in datos]
            cantidades = [d["cantidad"] for d in datos]

            # Colores personalizados
            colores_map = {
                "Carro": "#3498db",  # Azul
                "Moto": "#9b59b6",  # Morado
                "Bicicleta": "#1abc9c",  # Verde azulado
            }
            colores = [colores_map.get(t, "#95a5a6") for t in tipos]

            # Crear gráfico de barras
            bars = ax.bar(tipos, cantidades, color=colores, edgecolor="black", linewidth=1.5)

            # Agregar valores encima de las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{int(height)}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    weight="bold",
                )

            ax.set_title("Distribución de Vehículos", fontsize=12, weight="bold", pad=10)
            ax.set_xlabel("Tipo de Vehículo", fontsize=10)
            ax.set_ylabel("Cantidad", fontsize=10)
            ax.grid(axis="y", alpha=0.3, linestyle="--")

        except Exception as e:
            ax.text(0.5, 0.5, f"Error: {str(e)}", ha="center", va="center", transform=ax.transAxes, fontsize=8)

    def _grafico_funcionarios_por_cargo(self, ax):
        """Genera gráfico de barras horizontales para funcionarios por cargo"""
        try:
            query = """
                SELECT
                    cargo,
                    COUNT(*) as cantidad
                FROM funcionarios
                WHERE activo = TRUE
            """

            # Aplicar filtros
            params = []
            if self.filtros_activos.get("cargo"):
                query += " AND cargo = %s"
                params.append(self.filtros_activos["cargo"])

            if self.filtros_activos.get("fecha_inicio") and self.filtros_activos.get("fecha_fin"):
                query += " AND fecha_registro BETWEEN %s AND %s"
                params.append(self.filtros_activos["fecha_inicio"])
                params.append(self.filtros_activos["fecha_fin"])

            query += """
                GROUP BY cargo
                ORDER BY cantidad DESC
                LIMIT 10
            """

            datos = self.db.fetch_all(query, tuple(params) if params else None)

            if not datos:
                ax.text(0.5, 0.5, "Sin datos", ha="center", va="center", transform=ax.transAxes)
                return

            cargos = [d["cargo"] if d["cargo"] else "Sin cargo" for d in datos]
            cantidades = [d["cantidad"] for d in datos]

            # Crear gráfico de barras horizontales
            bars = ax.barh(cargos, cantidades, color="#34495e", edgecolor="black", linewidth=1.5)

            # Agregar valores al final de las barras
            for i, (bar, cantidad) in enumerate(zip(bars, cantidades)):
                ax.text(
                    bar.get_width() + 0.1,
                    bar.get_y() + bar.get_height() / 2,
                    f"{int(cantidad)}",
                    ha="left",
                    va="center",
                    fontsize=9,
                    weight="bold",
                )

            ax.set_title("Funcionarios por Cargo (Top 10)", fontsize=12, weight="bold", pad=10)
            ax.set_xlabel("Cantidad de Funcionarios", fontsize=10)
            ax.set_ylabel("Cargo", fontsize=10)
            ax.grid(axis="x", alpha=0.3, linestyle="--")

            # Ajustar límites del eje X para dar espacio a los números
            max_val = max(cantidades) if cantidades else 1
            ax.set_xlim(0, max_val * 1.15)

        except Exception as e:
            ax.text(0.5, 0.5, f"Error: {str(e)}", ha="center", va="center", transform=ax.transAxes, fontsize=8)

    def _llenar_tabla(self, tabla, datos):
        """Llena una tabla con los datos proporcionados"""
        tabla.setRowCount(0)

        if not datos:
            return

        for row_data in datos:
            row_position = tabla.rowCount()
            tabla.insertRow(row_position)

            for col_index, (key, value) in enumerate(row_data.items()):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Solo lectura
                tabla.setItem(row_position, col_index, item)

    def exportar_csv(self, tabla, nombre_base):
        """Exporta los datos de la tabla a un archivo CSV"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar como CSV", f"{nombre_base}_{timestamp}.csv", "Archivos CSV (*.csv)"
            )

            if not filename:
                return

            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)

                # Escribir encabezados
                headers = []
                for col in range(tabla.columnCount()):
                    headers.append(tabla.horizontalHeaderItem(col).text())
                writer.writerow(headers)

                # Escribir datos
                for row in range(tabla.rowCount()):
                    row_data = []
                    for col in range(tabla.columnCount()):
                        item = tabla.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar CSV: {str(e)}")

    def exportar_excel(self, tabla, nombre_base):
        """Exporta los datos a Excel usando openpyxl"""
        if not OPENPYXL_AVAILABLE:
            QMessageBox.warning(
                self,
                "Librería no disponible",
                "La exportación a Excel requiere instalar la librería 'openpyxl'.\n\n"
                "Instalar con: pip install openpyxl\n\n"
                "Por ahora, use la exportación a CSV.",
            )
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar como Excel", f"{nombre_base}_{timestamp}.xlsx", "Archivos Excel (*.xlsx)"
            )

            if not filename:
                return

            # Crear workbook y hoja activa
            wb = Workbook()
            ws = wb.active
            ws.title = nombre_base[:31]  # Excel limita nombres de hoja a 31 caracteres

            # Estilo para encabezados
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            header_alignment = Alignment(horizontal="center", vertical="center")

            # Escribir encabezados
            headers = []
            for col in range(tabla.columnCount()):
                header_text = tabla.horizontalHeaderItem(col).text()
                headers.append(header_text)
                cell = ws.cell(row=1, column=col + 1, value=header_text)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment

            # Escribir datos
            for row in range(tabla.rowCount()):
                for col in range(tabla.columnCount()):
                    item = tabla.item(row, col)
                    value = item.text() if item else ""
                    cell = ws.cell(row=row + 2, column=col + 1, value=value)
                    cell.alignment = Alignment(horizontal="left", vertical="center")

            # Ajustar ancho de columnas
            for col in range(1, tabla.columnCount() + 1):
                ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = 20

            # Guardar archivo
            wb.save(filename)
            QMessageBox.information(self, "Éxito", f"Datos exportados correctamente a:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar Excel: {str(e)}")

    def exportar_pdf(self, tabla, nombre_base):
        """Exporta los datos a PDF usando reportlab"""
        if not REPORTLAB_AVAILABLE:
            QMessageBox.warning(
                self,
                "Librería no disponible",
                "La exportación a PDF requiere instalar la librería 'reportlab'.\n\n"
                "Instalar con: pip install reportlab\n\n"
                "Por ahora, use la exportación a CSV.",
            )
            return

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar como PDF", f"{nombre_base}_{timestamp}.pdf", "Archivos PDF (*.pdf)"
            )

            if not filename:
                return

            # Crear documento PDF
            doc = SimpleDocTemplate(
                filename, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
            )

            # Contenedor de elementos
            elements = []
            styles = getSampleStyleSheet()

            # Título del reporte
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=18,
                textColor=colors.HexColor("#2c3e50"),
                spaceAfter=20,
                alignment=1,  # Centrado
            )
            title = Paragraph(f"Reporte: {nombre_base.replace('_', ' ').title()}", title_style)
            elements.append(title)

            # Fecha y hora de generación
            date_style = ParagraphStyle(
                "DateStyle",
                parent=styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor("#7f8c8d"),
                spaceAfter=20,
                alignment=1,
            )
            date_text = Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style)
            elements.append(date_text)
            elements.append(Spacer(1, 0.2 * inch))

            # Extraer datos de la tabla
            data = []

            # Encabezados
            headers = []
            for col in range(tabla.columnCount()):
                headers.append(tabla.horizontalHeaderItem(col).text())
            data.append(headers)

            # Filas de datos
            for row in range(tabla.rowCount()):
                row_data = []
                for col in range(tabla.columnCount()):
                    item = tabla.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            # Crear tabla PDF
            # Calcular ancho de columnas dinámicamente
            page_width = landscape(A4)[0] - 60  # Restar márgenes
            col_width = page_width / tabla.columnCount()

            table = Table(data, colWidths=[col_width] * tabla.columnCount())

            # Estilo de la tabla
            table.setStyle(
                TableStyle(
                    [
                        # Encabezados
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        # Datos
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )

            elements.append(table)

            # Pie de página con información del sistema
            elements.append(Spacer(1, 0.3 * inch))
            footer_style = ParagraphStyle(
                "FooterStyle", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#95a5a6"), alignment=1
            )
            footer = Paragraph("Sistema de Gestión de Parqueadero - Ssalud Plaza Claro © 2025", footer_style)
            elements.append(footer)

            # Construir PDF
            doc.build(elements)
            QMessageBox.information(self, "Éxito", f"PDF generado correctamente en:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar PDF: {str(e)}")
