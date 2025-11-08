# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Funcionarios del sistema de gestión de parqueadero
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..config.settings import CARGOS_DISPONIBLES, DIRECCIONES_DISPONIBLES
from ..database.manager import DatabaseManager
from ..models.funcionario import FuncionarioModel
from ..utils.formatters import format_numero_parqueadero

# Nuevas utilidades de refactorización
from .utils import InputValidators
from .utils.button_factory import ButtonFactory


class FuncionariosTab(QWidget):
    """Pestaña de gestión de funcionarios"""

    # Señales que se emiten para sincronizar con otras pestañas
    funcionario_creado = pyqtSignal()
    funcionario_eliminado = pyqtSignal()  # Nueva señal para eliminación en cascada

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.funcionario_model = FuncionarioModel(self.db)

        # Variables de paginación
        self.filas_por_pagina = 4
        self.pagina_actual = 1
        self.total_funcionarios = 0
        self.funcionarios_completos = []  # Lista completa de funcionarios

        self.setup_ui()
        self.cargar_funcionarios()

    def cargar_items_personalizados(self):
        """Carga items personalizados desde el archivo JSON"""
        import json
        import os

        try:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
            config_file = os.path.join(config_dir, "custom_items.json")

            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    custom_items = json.load(f)

                # Cargar cargos personalizados
                if "cargos" in custom_items:
                    for cargo in custom_items["cargos"]:
                        if cargo and cargo.strip():
                            self.combo_cargo.addItem(cargo)

                # Cargar direcciones personalizadas
                if "direcciones" in custom_items:
                    for direccion in custom_items["direcciones"]:
                        if direccion and direccion.strip():
                            self.combo_direccion.addItem(direccion)

        except Exception as e:
            print(f"Error al cargar items personalizados: {e}")

    def crear_label_obligatorio(self, texto):
        """Crea un QLabel con asterisco rojo para campos obligatorios"""
        label_html = f'<span style="color: #2c3e50;">{texto}</span> <span style="color: red; font-weight: bold;">*</span>'
        label = QLabel(label_html)
        return label

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout()

        # Formulario de registro
        form_group = QGroupBox("Registro de Funcionario")
        form_layout = QGridLayout()
        form_layout.setSpacing(10)  # Espaciado uniforme

        # ===== FILA 0: Cédula, Nombre, Apellidos, Celular (distribuidos uniformemente) =====
        form_layout.addWidget(self.crear_label_obligatorio("Cédula:"), 0, 0)
        self.txt_cedula = QLineEdit()
        self.txt_cedula.setValidator(InputValidators.CEDULA)
        self.txt_cedula.setPlaceholderText("Solo números")
        self.txt_cedula.setMaxLength(10)
        form_layout.addWidget(self.txt_cedula, 0, 1, 1, 2)  # Span 2 columnas

        form_layout.addWidget(self.crear_label_obligatorio("Nombre:"), 0, 3)
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setValidator(InputValidators.NOMBRE)
        self.txt_nombre.setPlaceholderText("Escriba su nombre")
        form_layout.addWidget(self.txt_nombre, 0, 4, 1, 2)  # Span 2 columnas

        form_layout.addWidget(self.crear_label_obligatorio("Apellidos:"), 0, 6)
        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setValidator(InputValidators.APELLIDOS)
        self.txt_apellidos.setPlaceholderText("Digite su apellido")
        form_layout.addWidget(self.txt_apellidos, 0, 7, 1, 2)  # Span 2 columnas

        form_layout.addWidget(self.crear_label_obligatorio("Celular:"), 0, 9)
        self.txt_celular = QLineEdit()
        self.txt_celular.setValidator(InputValidators.CELULAR)
        self.txt_celular.setPlaceholderText("10 dígitos numéricos (ej: 3001234567)")
        self.txt_celular.setMaxLength(10)
        form_layout.addWidget(self.txt_celular, 0, 10, 1, 2)  # Span 2 columnas

        # ===== FILA 1: Dirección/Grupo, Cargo, Tipo de Excepción, No.Tarjeta Prox (distribuidos uniformemente) =====
        form_layout.addWidget(self.crear_label_obligatorio("Dirección/Grupo:"), 1, 0)

        # Container para Dirección/Grupo con botón de agregar
        direccion_container = QWidget()
        direccion_layout = QHBoxLayout(direccion_container)
        direccion_layout.setContentsMargins(0, 0, 0, 0)
        direccion_layout.setSpacing(5)

        self.combo_direccion = QComboBox()
        self.combo_direccion.addItem("-- Seleccione --", "")
        self.combo_direccion.addItems(DIRECCIONES_DISPONIBLES)
        # Configurar tooltips para cada item del combo de direcciones
        self.combo_direccion.setItemData(0, "Seleccione una dirección o grupo organizacional", Qt.ToolTipRole)
        for i in range(1, self.combo_direccion.count()):
            texto_direccion = self.combo_direccion.itemText(i)
            self.combo_direccion.setItemData(i, texto_direccion, Qt.ToolTipRole)
        self.combo_direccion.setMinimumWidth(180)
        self.combo_direccion.view().setMinimumWidth(400)
        self.combo_direccion.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        direccion_layout.addWidget(self.combo_direccion)

        # Botón para agregar nueva dirección
        btn_add_direccion = QPushButton("+")
        btn_add_direccion.setFixedSize(20, 26)
        btn_add_direccion.setToolTip("Agregar nueva Dirección/Grupo")
        btn_add_direccion.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border: none;
                border-radius: 4px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            """
        )
        btn_add_direccion.clicked.connect(lambda: self.agregar_item_combo("Dirección/Grupo", self.combo_direccion))
        direccion_layout.addWidget(btn_add_direccion)

        form_layout.addWidget(direccion_container, 1, 1, 1, 2)  # Span 2 columnas

        form_layout.addWidget(self.crear_label_obligatorio("Cargo:"), 1, 3)

        # Container para Cargo con botón de agregar
        cargo_container = QWidget()
        cargo_layout = QHBoxLayout(cargo_container)
        cargo_layout.setContentsMargins(0, 0, 0, 0)
        cargo_layout.setSpacing(5)

        self.combo_cargo = QComboBox()
        self.combo_cargo.addItem("-- Seleccione --", "")
        self.combo_cargo.addItems(CARGOS_DISPONIBLES)
        cargo_layout.addWidget(self.combo_cargo)

        # Botón para agregar nuevo cargo
        btn_add_cargo = QPushButton("+")
        btn_add_cargo.setFixedSize(20, 26)
        btn_add_cargo.setToolTip("Agregar nuevo Cargo")
        btn_add_cargo.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                font-size: 18px;
                border: none;
                border-radius: 4px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            """
        )
        btn_add_cargo.clicked.connect(lambda: self.agregar_item_combo("Cargo", self.combo_cargo))
        cargo_layout.addWidget(btn_add_cargo)

        form_layout.addWidget(cargo_container, 1, 4, 1, 2)  # Span 2 columnas

        # Cargar items personalizados (cargos y direcciones guardados previamente)
        self.cargar_items_personalizados()

        # ===== ComboBox: Tipo de Excepción =====
        form_layout.addWidget(QLabel("Tipo de Excepción:"), 1, 6)
        self.combo_tipo_excepcion = QComboBox()
        self.combo_tipo_excepcion.addItem("-- Ninguna --", "ninguna")
        self.combo_tipo_excepcion.addItem("Pico y Placa Solidario", "pico_placa_solidario")
        self.combo_tipo_excepcion.addItem("Funcionario con Discapacidad", "discapacidad")
        self.combo_tipo_excepcion.addItem("Exclusivo Directivo (4 carros)", "exclusivo_directivo")
        self.combo_tipo_excepcion.addItem("Carro Híbrido (Incentivo Ambiental)", "carro_hibrido")
        self.combo_tipo_excepcion.setMinimumWidth(150)

        # Configurar tooltips para cada opción
        self.combo_tipo_excepcion.setItemData(0, "Funcionario regular sin excepciones", Qt.ToolTipRole)
        self.combo_tipo_excepcion.setItemData(1, "Permite usar el parqueadero en días que normalmente no le corresponderían (ignora PAR/IMPAR)", Qt.ToolTipRole)
        self.combo_tipo_excepcion.setItemData(2, "Marca al funcionario con condición de discapacidad. Tiene prioridad para espacios especiales", Qt.ToolTipRole)
        self.combo_tipo_excepcion.setItemData(3, "Permite registrar hasta 4 vehículos (solo carros) en el mismo parqueadero. Disponible para cualquier cargo", Qt.ToolTipRole)
        self.combo_tipo_excepcion.setItemData(4, "Carro híbrido: Puede usar el parqueadero TODOS LOS DÍAS (parqueadero exclusivo - incentivo ambiental)", Qt.ToolTipRole)

        # Permitir ajuste de ancho del dropdown
        self.combo_tipo_excepcion.view().setMinimumWidth(450)
        self.combo_tipo_excepcion.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)

        form_layout.addWidget(self.combo_tipo_excepcion, 1, 7, 1, 2)  # Span 2 columnas

        # No.Tarjeta Prox en la misma fila 1
        form_layout.addWidget(QLabel("No.Tarjeta Prox:"), 1, 9)
        self.txt_tarjeta = QLineEdit()
        self.txt_tarjeta.setValidator(InputValidators.TARJETA_CLARO)
        self.txt_tarjeta.setPlaceholderText("Alfanumérico, máx 15 caracteres")
        self.txt_tarjeta.setMaxLength(15)
        form_layout.addWidget(self.txt_tarjeta, 1, 10, 1, 2)  # Span 2 columnas

        # ===== FILA 2: Botones =====
        # Botones centrados en fila 2
        self.btn_guardar_funcionario = QPushButton("Guardar")
        self.btn_guardar_funcionario.clicked.connect(self.guardar_funcionario)
        self.btn_guardar_funcionario.setProperty("class", "success")
        self.btn_guardar_funcionario.setMinimumWidth(120)
        self.btn_guardar_funcionario.setMinimumHeight(40)
        self.btn_guardar_funcionario.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """
        )

        self.btn_limpiar_funcionario = QPushButton("Limpiar")
        self.btn_limpiar_funcionario.clicked.connect(self.limpiar_formulario)
        self.btn_limpiar_funcionario.setMinimumWidth(120)
        self.btn_limpiar_funcionario.setMinimumHeight(40)
        self.btn_limpiar_funcionario.setStyleSheet(
            """
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
            QPushButton:pressed {
                background-color: #5d6d7e;
            }
        """
        )

        # Agregar botones en fila 2, columnas 4 y 5
        form_layout.addWidget(self.btn_guardar_funcionario, 2, 4)
        form_layout.addWidget(self.btn_limpiar_funcionario, 2, 5)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Barra de búsqueda y filtros
        search_group = QGroupBox("Buscar y Filtrar Funcionarios")
        search_layout = QHBoxLayout()

        # Filtro por Estado
        estado_label = QLabel("Estado:")
        estado_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.combo_filtro_estado = QComboBox()
        self.combo_filtro_estado.addItem("Todos", "todos")
        self.combo_filtro_estado.addItem("Activos", "activos")
        self.combo_filtro_estado.addItem("Inactivos", "inactivos")
        self.combo_filtro_estado.setCurrentIndex(1)  # Por defecto: Activos
        self.combo_filtro_estado.currentIndexChanged.connect(self.filtrar_funcionarios)
        self.combo_filtro_estado.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #27ae60;
                border-radius: 5px;
                font-size: 13px;
                min-width: 120px;
                background-color: white;
            }
            QComboBox:focus {
                border: 2px solid #229954;
                background-color: #e8f8f0;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 5px;
            }
        """)

        search_label = QLabel("Buscar Por:")
        search_label.setStyleSheet("font-weight: bold; font-size: 12px;")

        self.txt_buscar_cedula = QLineEdit()
        self.txt_buscar_cedula.setPlaceholderText("Cédula, nombre, apellido")
        self.txt_buscar_cedula.textChanged.connect(self.filtrar_funcionarios)
        self.txt_buscar_cedula.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #3498db;
                border-radius: 5px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #2980b9;
                background-color: #e8f4fd;
            }
        """)

        self.btn_limpiar_busqueda = QPushButton("Limpiar")
        self.btn_limpiar_busqueda.clicked.connect(self.limpiar_busqueda)
        self.btn_limpiar_busqueda.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)

        self.lbl_resultados = QLabel("")
        self.lbl_resultados.setStyleSheet("font-size: 11px; color: #7f8c8d; font-style: italic;")

        search_layout.addWidget(estado_label)
        search_layout.addWidget(self.combo_filtro_estado)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.txt_buscar_cedula)
        search_layout.addWidget(self.btn_limpiar_busqueda)
        search_layout.addWidget(self.lbl_resultados)
        search_layout.addStretch()

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Tabla de funcionarios con configuración fija y mejorada
        tabla_group = QGroupBox("Lista de Funcionarios")
        tabla_layout = QVBoxLayout()

        # Botón Importar Data encima de la tabla
        btn_importar_container = QHBoxLayout()
        btn_importar_container.addStretch()

        self.btn_importar_excel = QPushButton("📊 Importar")
        self.btn_importar_excel.setMinimumWidth(120)
        self.btn_importar_excel.setMinimumHeight(35)
        self.btn_importar_excel.setToolTip("Importar data desde Excel (.xlsx o .xls)")
        self.btn_importar_excel.setStyleSheet(
            """
            QPushButton {
                background-color: #16a085;
                color: white;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
            QPushButton:pressed {
                background-color: #138d75;
            }
        """
        )
        self.btn_importar_excel.clicked.connect(self.importar_desde_excel)
        btn_importar_container.addWidget(self.btn_importar_excel)
        btn_importar_container.addStretch()
        tabla_layout.addLayout(btn_importar_container)

        self.tabla_funcionarios = QTableWidget()
        self.tabla_funcionarios.setColumnCount(15)
        self.tabla_funcionarios.setHorizontalHeaderLabels(
            [
                "Cédula",
                "Nombre",
                "Apellidos",
                "Dirección",
                "Cargo",
                "Celular",
                "Tarjeta Prox",
                "Vehículos",
                "Compartir",
                "Solidario",
                "Discap.",
                "Híbrido",
                "Exclusivo",
                "Estado",
                "Acciones",
            ]
        )

        # Configuración visual mejorada
        self.tabla_funcionarios.setAlternatingRowColors(True)
        self.tabla_funcionarios.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_funcionarios.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_funcionarios.verticalHeader().setVisible(False)

        # Establecer anchos de columna fijos
        self.tabla_funcionarios.setColumnWidth(0, 100)  # Cédula
        self.tabla_funcionarios.setColumnWidth(1, 120)  # Nombre
        self.tabla_funcionarios.setColumnWidth(2, 120)  # Apellidos
        self.tabla_funcionarios.setColumnWidth(3, 150)  # Dirección
        self.tabla_funcionarios.setColumnWidth(4, 130)  # Cargo
        self.tabla_funcionarios.setColumnWidth(5, 100)  # Celular
        self.tabla_funcionarios.setColumnWidth(6, 100)  # Tarjeta Prox
        self.tabla_funcionarios.setColumnWidth(7, 80)  # Vehículos
        self.tabla_funcionarios.setColumnWidth(8, 80)  # Compartir
        self.tabla_funcionarios.setColumnWidth(9, 80)  # Solidario
        self.tabla_funcionarios.setColumnWidth(10, 70)  # Discapacidad
        self.tabla_funcionarios.setColumnWidth(11, 70)  # Híbrido
        self.tabla_funcionarios.setColumnWidth(12, 85)  # Exclusivo
        self.tabla_funcionarios.setColumnWidth(13, 90)  # Estado
        self.tabla_funcionarios.setColumnWidth(14, 110)  # Acciones

        # Configurar altura de filas para mejor visualización
        altura_fila = 50
        self.tabla_funcionarios.verticalHeader().setDefaultSectionSize(altura_fila)

        # Establecer altura para mostrar exactamente 4 filas + scroll horizontal visible
        # Cálculo: altura_encabezado (45px) + (4 filas × 50px) + scroll horizontal (20px) = 265px
        altura_encabezado = 45
        num_filas_visibles = 4
        espacio_scroll = 20
        altura_total = altura_encabezado + (num_filas_visibles * altura_fila) + espacio_scroll
        self.tabla_funcionarios.setMinimumHeight(altura_total)
        self.tabla_funcionarios.setMaximumHeight(altura_total)

        # Estilo de encabezados
        self.tabla_funcionarios.horizontalHeader().setStyleSheet(
            """
            QHeaderView::section {
                background-color: #34B5A9;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-right: 1px solid #2D9B8F;
            }
        """
        )

        # Estilo general de la tabla
        self.tabla_funcionarios.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                gridline-color: #bdc3c7;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #e8f4fd;
                color: #2c3e50;
            }
            QTableWidget::item:hover {
                background-color: #f5f5f5;
            }
        """
        )

        # Configurar scroll horizontal para que siempre esté visible
        self.tabla_funcionarios.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tabla_funcionarios.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        tabla_layout.addWidget(self.tabla_funcionarios)

        # Controles de paginación
        paginacion_layout = QHBoxLayout()
        paginacion_layout.setSpacing(8)
        paginacion_layout.setContentsMargins(0, 5, 0, 0)

        # Botón Primera Página
        self.btn_primera_pagina = ButtonFactory.create_pagination_button("⏮️ Primera")
        self.btn_primera_pagina.setFixedHeight(35)
        self.btn_primera_pagina.clicked.connect(self.ir_a_primera_pagina)

        # Botón Página Anterior
        self.btn_anterior = ButtonFactory.create_pagination_button("◀️ Anterior")
        self.btn_anterior.setFixedHeight(35)
        self.btn_anterior.clicked.connect(self.pagina_anterior)

        # Label de información de página
        self.lbl_pagina = QLabel("Página 1 de 1")
        self.lbl_pagina.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        self.lbl_pagina.setAlignment(Qt.AlignCenter)

        # Botón Página Siguiente
        self.btn_siguiente = ButtonFactory.create_pagination_button("Siguiente ▶️")
        self.btn_siguiente.setFixedHeight(35)
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)

        # Botón Última Página
        self.btn_ultima_pagina = ButtonFactory.create_pagination_button("Última ⏭️")
        self.btn_ultima_pagina.setFixedHeight(35)
        self.btn_ultima_pagina.clicked.connect(self.ir_a_ultima_pagina)

        # Label total de registros
        self.lbl_total_registros = QLabel("Total: 0 funcionarios")
        self.lbl_total_registros.setStyleSheet("font-size: 11px; color: #7f8c8d; font-style: italic;")

        paginacion_layout.addStretch()
        paginacion_layout.addWidget(self.btn_primera_pagina)
        paginacion_layout.addWidget(self.btn_anterior)
        paginacion_layout.addWidget(self.lbl_pagina)
        paginacion_layout.addWidget(self.btn_siguiente)
        paginacion_layout.addWidget(self.btn_ultima_pagina)
        paginacion_layout.addSpacing(20)
        paginacion_layout.addWidget(self.lbl_total_registros)
        paginacion_layout.addStretch()

        tabla_layout.addLayout(paginacion_layout)
        tabla_group.setLayout(tabla_layout)
        layout.addWidget(tabla_group)

        self.setLayout(layout)

    def on_pico_placa_changed_main(self, state):
        """Cuando se marca Pico y Placa en el formulario principal, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_discapacidad.blockSignals(True)
            self.chk_exclusivo_directivo.blockSignals(True)
            self.chk_carro_hibrido.blockSignals(True)
            self.chk_discapacidad.setChecked(False)
            self.chk_exclusivo_directivo.setChecked(False)
            self.chk_carro_hibrido.setChecked(False)
            self.chk_discapacidad.blockSignals(False)
            self.chk_exclusivo_directivo.blockSignals(False)
            self.chk_carro_hibrido.blockSignals(False)

    def on_discapacidad_changed_main(self, state):
        """Cuando se marca Discapacidad en el formulario principal, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_exclusivo_directivo.blockSignals(True)
            self.chk_carro_hibrido.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_exclusivo_directivo.setChecked(False)
            self.chk_carro_hibrido.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_exclusivo_directivo.blockSignals(False)
            self.chk_carro_hibrido.blockSignals(False)

    def on_exclusivo_directivo_changed_main(self, state):
        """Cuando se marca Exclusivo Directivo, desmarca las otras opciones y valida el cargo"""
        if state == 2:  # Checked
            # Validar cargo
            from ..config.settings import CARGOS_DIRECTIVOS
            cargo_actual = self.combo_cargo.currentText()

            if cargo_actual not in CARGOS_DIRECTIVOS and cargo_actual != "-- Seleccione --":
                # Bloquear el checkbox y mostrar advertencia
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "⚠️ Cargo No Permitido",
                    f"El parqueadero exclusivo directivo solo está disponible para:\n\n"
                    f"✅ {', '.join(CARGOS_DIRECTIVOS)}\n\n"
                    f"❌ Cargo actual: {cargo_actual}\n\n"
                    f"Por favor, cambie el cargo antes de activar esta opción."
                )
                self.chk_exclusivo_directivo.blockSignals(True)
                self.chk_exclusivo_directivo.setChecked(False)
                self.chk_exclusivo_directivo.blockSignals(False)
                return

            # Desmarcar las otras opciones
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_discapacidad.blockSignals(True)
            self.chk_carro_hibrido.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_discapacidad.setChecked(False)
            self.chk_carro_hibrido.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_discapacidad.blockSignals(False)
            self.chk_carro_hibrido.blockSignals(False)

    def on_carro_hibrido_changed_main(self, state):
        """Cuando se marca Carro Híbrido, desmarca las otras opciones"""
        if state == 2:  # Checked
            # Desmarcar las otras opciones
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_discapacidad.blockSignals(True)
            self.chk_exclusivo_directivo.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_discapacidad.setChecked(False)
            self.chk_exclusivo_directivo.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_discapacidad.blockSignals(False)
            self.chk_exclusivo_directivo.blockSignals(False)

    def on_cargo_changed(self, cargo: str):
        """Validaciones o acciones cuando cambia el cargo (si es necesario en el futuro)"""
        # Método mantenido para compatibilidad futura si se necesitan validaciones por cargo
        pass

    def guardar_funcionario(self):
        """Guarda un nuevo funcionario en la base de datos con validaciones completas"""
        # ========== OBTENER VALORES ==========
        cedula = self.txt_cedula.text().strip()
        nombre = self.txt_nombre.text().strip()
        apellidos = self.txt_apellidos.text().strip()
        direccion = self.combo_direccion.currentText()
        cargo = self.combo_cargo.currentText()
        celular = self.txt_celular.text().strip()
        tarjeta = self.txt_tarjeta.text().strip()

        # ========== VALIDACIONES DE CAMPOS OBLIGATORIOS ==========

        # 1. CÉDULA (OBLIGATORIO)
        if not cedula:
            QMessageBox.warning(self, "⚠️ Campo Obligatorio", "La cédula es obligatoria")
            self.txt_cedula.setFocus()
            return

        if not cedula.isdigit():
            QMessageBox.warning(self, "⚠️ Validación", "La cédula solo debe contener números")
            self.txt_cedula.setFocus()
            return

        if len(cedula) < 7 or len(cedula) > 10:
            mensaje = f"La cédula debe tener entre 7 y 10 dígitos\nDígitos ingresados: {len(cedula)}"
            QMessageBox.warning(self, "⚠️ Validación", mensaje)
            self.txt_cedula.setFocus()
            return

        # 2. NOMBRE (OBLIGATORIO)
        if not nombre:
            QMessageBox.warning(self, "⚠️ Campo Obligatorio", "El nombre es obligatorio")
            self.txt_nombre.setFocus()
            return

        if len(nombre) < 2:
            QMessageBox.warning(self, "⚠️ Validación", "El nombre debe tener al menos 2 caracteres")
            self.txt_nombre.setFocus()
            return

        # 3. APELLIDOS (OBLIGATORIO)
        if not apellidos:
            QMessageBox.warning(self, "⚠️ Campo Obligatorio", "Los apellidos son obligatorios")
            self.txt_apellidos.setFocus()
            return

        if len(apellidos) < 2:
            QMessageBox.warning(self, "⚠️ Validación", "Los apellidos deben tener al menos 2 caracteres")
            self.txt_apellidos.setFocus()
            return

        # 4. DIRECCIÓN/GRUPO (OBLIGATORIO)
        if not direccion or direccion == "-- Seleccione --":
            QMessageBox.warning(self, "⚠️ Campo Obligatorio", "Debe seleccionar una Dirección/Grupo")
            self.combo_direccion.setFocus()
            return

        # 5. CARGO (OBLIGATORIO)
        if not cargo or cargo == "-- Seleccione --":
            QMessageBox.warning(self, "⚠️ Campo Obligatorio", "Debe seleccionar un Cargo")
            self.combo_cargo.setFocus()
            return

        # 6. CELULAR (OBLIGATORIO)
        if not celular:
            QMessageBox.warning(self, "⚠️ Campo Obligatorio", "El celular es obligatorio")
            self.txt_celular.setFocus()
            return

        if len(celular) != 10:
            mensaje = f"El celular debe tener exactamente 10 dígitos\nDígitos ingresados: {len(celular)}"
            QMessageBox.warning(self, "⚠️ Validación", mensaje)
            self.txt_celular.setFocus()
            return

        if not celular.isdigit():
            QMessageBox.warning(self, "⚠️ Validación", "El celular solo debe contener números")
            self.txt_celular.setFocus()
            return

        # 7. TARJETA PROX (OPCIONAL)
        if tarjeta and len(tarjeta) < 3:
            QMessageBox.warning(self, "⚠️ Validación", "La tarjeta de proximidad debe tener al menos 3 caracteres\n(Este campo es opcional)")
            self.txt_tarjeta.setFocus()
            return

        # Determinar los valores de los campos según el tipo de excepción seleccionado
        tipo_excepcion = self.combo_tipo_excepcion.currentData()

        if tipo_excepcion == "carro_hibrido":
            # Carro híbrido (incentivo ambiental)
            permite_compartir = False
            pico_placa_solidario = False
            discapacidad = False
            tiene_parqueadero_exclusivo = False
            tiene_carro_hibrido = True
        elif tipo_excepcion == "exclusivo_directivo":
            # Exclusivo directivo (hasta 4 vehículos)
            permite_compartir = False
            pico_placa_solidario = False
            discapacidad = False
            tiene_parqueadero_exclusivo = True
            tiene_carro_hibrido = False
        elif tipo_excepcion == "pico_placa_solidario":
            # Pico y placa solidario
            permite_compartir = True
            pico_placa_solidario = True
            discapacidad = False
            tiene_parqueadero_exclusivo = False
            tiene_carro_hibrido = False
        elif tipo_excepcion == "discapacidad":
            # Funcionario con discapacidad
            permite_compartir = True
            pico_placa_solidario = False
            discapacidad = True
            tiene_parqueadero_exclusivo = False
            tiene_carro_hibrido = False
        else:  # "ninguna" o cualquier otro valor
            # Ninguno marcado (funcionario regular que comparte)
            permite_compartir = True
            pico_placa_solidario = False
            discapacidad = False
            tiene_parqueadero_exclusivo = False
            tiene_carro_hibrido = False

        exito, mensaje = self.funcionario_model.crear(
            cedula=self.txt_cedula.text(),
            nombre=self.txt_nombre.text(),
            apellidos=self.txt_apellidos.text(),
            direccion_grupo=(
                self.combo_direccion.currentText() if self.combo_direccion.currentText() != "-- Seleccione --" else ""
            ),
            cargo=self.combo_cargo.currentText() if self.combo_cargo.currentText() != "-- Seleccione --" else "",
            celular=self.txt_celular.text(),
            tarjeta=self.txt_tarjeta.text(),
            permite_compartir=permite_compartir,
            pico_placa_solidario=pico_placa_solidario,
            discapacidad=discapacidad,
            tiene_parqueadero_exclusivo=tiene_parqueadero_exclusivo,
            tiene_carro_hibrido=tiene_carro_hibrido,
        )

        if exito:
            QMessageBox.information(self, "✅ Éxito", mensaje)
            self.limpiar_formulario()
            self.cargar_funcionarios()
            # Emitir señal para notificar a otras pestañas
            self.funcionario_creado.emit()
        else:
            # Los mensajes ya vienen formateados desde el modelo
            if "tabla 'funcionarios' no existe" in mensaje.lower():
                QMessageBox.critical(
                    self,
                    "🚫 Error de Base de Datos",
                    f"{mensaje}\n\n🛠️ Solución: Ejecute el script 'parking_database_schema.sql'",
                )
            elif "estructura de la tabla" in mensaje.lower():
                QMessageBox.critical(
                    self,
                    "🚫 Error de Estructura",
                    f"{mensaje}\n\n🛠️ Solución: Verifique la estructura de la base de datos",
                )
            else:
                QMessageBox.critical(self, "🚫 Error", mensaje)

    def agregar_item_combo(self, tipo_campo, combo_widget):
        """
        Abre un modal para agregar un nuevo item al ComboBox especificado

        Args:
            tipo_campo: Nombre del campo ("Cargo" o "Dirección/Grupo")
            combo_widget: El QComboBox al que se agregará el item
        """
        import json
        import os
        from PyQt5.QtWidgets import QInputDialog

        # Solicitar el nuevo item mediante un diálogo
        texto, ok = QInputDialog.getText(
            self,
            f"Agregar {tipo_campo}",
            f"Ingrese el nuevo {tipo_campo}:",
            QLineEdit.Normal,
            ""
        )

        if ok and texto.strip():
            nuevo_item = texto.strip()

            # Verificar si el item ya existe (sin distinguir mayúsculas/minúsculas)
            items_existentes = [combo_widget.itemText(i).lower() for i in range(combo_widget.count())]

            if nuevo_item.lower() in items_existentes:
                QMessageBox.warning(
                    self,
                    "⚠️ Item Duplicado",
                    f"El {tipo_campo} '{nuevo_item}' ya existe en la lista."
                )
                return

            # Agregar el nuevo item al ComboBox (justo antes del final)
            combo_widget.addItem(nuevo_item)

            # Seleccionar el nuevo item automáticamente
            index = combo_widget.findText(nuevo_item)
            if index >= 0:
                combo_widget.setCurrentIndex(index)

            # Guardar el nuevo item de forma permanente
            try:
                # Obtener la ruta del archivo de configuración
                config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
                config_file = os.path.join(config_dir, "custom_items.json")

                # Cargar items personalizados existentes
                custom_items = {}
                if os.path.exists(config_file):
                    with open(config_file, "r", encoding="utf-8") as f:
                        custom_items = json.load(f)

                # Determinar la clave según el tipo de campo
                key = "cargos" if tipo_campo == "Cargo" else "direcciones"

                # Agregar el nuevo item a la lista
                if key not in custom_items:
                    custom_items[key] = []

                if nuevo_item not in custom_items[key]:
                    custom_items[key].append(nuevo_item)

                # Guardar en el archivo
                with open(config_file, "w", encoding="utf-8") as f:
                    json.dump(custom_items, f, ensure_ascii=False, indent=4)

                # Mostrar confirmación
                QMessageBox.information(
                    self,
                    "✅ Item Agregado",
                    f"El {tipo_campo} '{nuevo_item}' ha sido agregado exitosamente.\n\n"
                    f"Este cambio es permanente y estará disponible en futuras sesiones."
                )

            except Exception as e:
                QMessageBox.warning(
                    self,
                    "⚠️ Advertencia",
                    f"El {tipo_campo} '{nuevo_item}' ha sido agregado temporalmente,\n"
                    f"pero no se pudo guardar de forma permanente.\n\n"
                    f"Error: {str(e)}"
                )

    def limpiar_formulario(self):
        """Limpia el formulario de funcionarios"""
        self.txt_cedula.clear()
        self.txt_nombre.clear()
        self.txt_apellidos.clear()
        self.combo_direccion.setCurrentIndex(0)
        self.combo_cargo.setCurrentIndex(0)
        self.txt_celular.clear()
        self.txt_tarjeta.clear()
        # Limpiar tipo de excepción (volver a "Ninguna")
        self.combo_tipo_excepcion.setCurrentIndex(0)

    def cargar_funcionarios(self):
        """Carga la lista de funcionarios en la tabla con paginación, respetando el filtro de estado"""
        # Obtener todos los funcionarios
        todos_funcionarios = self.funcionario_model.obtener_todos_incluyendo_inactivos()

        # Aplicar filtro de estado
        filtro_estado = self.combo_filtro_estado.currentData()
        if filtro_estado == "activos":
            self.funcionarios_completos = [func for func in todos_funcionarios if func.get("activo", True)]
        elif filtro_estado == "inactivos":
            self.funcionarios_completos = [func for func in todos_funcionarios if not func.get("activo", True)]
        else:  # "todos"
            self.funcionarios_completos = todos_funcionarios

        self.total_funcionarios = len(self.funcionarios_completos)

        # Calcular paginación
        total_paginas = (self.total_funcionarios + self.filas_por_pagina - 1) // self.filas_por_pagina
        if total_paginas == 0:
            total_paginas = 1

        # Ajustar página actual si excede el total
        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas

        # Calcular índices de inicio y fin para la página actual
        inicio = (self.pagina_actual - 1) * self.filas_por_pagina
        fin = min(inicio + self.filas_por_pagina, self.total_funcionarios)

        # Obtener funcionarios para la página actual
        funcionarios_pagina = self.funcionarios_completos[inicio:fin]

        # Configurar tabla para mostrar solo las filas de esta página
        self.tabla_funcionarios.setRowCount(len(funcionarios_pagina))

        for i, func in enumerate(funcionarios_pagina):
            # Ajustar índices ya que eliminamos la columna ID oculta
            cedula_item = QTableWidgetItem(func.get("cedula", ""))
            cedula_item.setTextAlignment(0x0004 | 0x0080)  # Centro horizontal y vertical
            self.tabla_funcionarios.setItem(i, 0, cedula_item)

            nombre_item = QTableWidgetItem(func.get("nombre", ""))
            nombre_item.setTextAlignment(0x0001 | 0x0080)  # Izquierda horizontal, centro vertical
            self.tabla_funcionarios.setItem(i, 1, nombre_item)

            apellidos_item = QTableWidgetItem(func.get("apellidos", ""))
            apellidos_item.setTextAlignment(0x0001 | 0x0080)  # Izquierda horizontal, centro vertical
            self.tabla_funcionarios.setItem(i, 2, apellidos_item)

            direccion_item = QTableWidgetItem(func.get("direccion_grupo", ""))
            direccion_item.setTextAlignment(0x0001 | 0x0080)  # Izquierda horizontal, centro vertical
            self.tabla_funcionarios.setItem(i, 3, direccion_item)

            cargo_item = QTableWidgetItem(func.get("cargo", ""))
            cargo_item.setTextAlignment(0x0001 | 0x0080)  # Izquierda horizontal, centro vertical
            self.tabla_funcionarios.setItem(i, 4, cargo_item)

            celular_item = QTableWidgetItem(func.get("celular", ""))
            celular_item.setTextAlignment(0x0004 | 0x0080)  # Centro horizontal y vertical
            self.tabla_funcionarios.setItem(i, 5, celular_item)

            tarjeta_item = QTableWidgetItem(func.get("no_tarjeta_proximidad", "") or "")
            tarjeta_item.setTextAlignment(0x0004 | 0x0080)  # Centro horizontal y vertical
            self.tabla_funcionarios.setItem(i, 6, tarjeta_item)

            # Formatear número de vehículos con mejor presentación
            total_vehiculos = func.get("total_vehiculos", 0)
            vehiculos_item = QTableWidgetItem(f"{total_vehiculos}/2")
            vehiculos_item.setTextAlignment(0x0004 | 0x0080)  # Centro horizontal y vertical
            self.tabla_funcionarios.setItem(i, 7, vehiculos_item)

            # ===== NUEVAS COLUMNAS: Indicadores visuales =====

            # Columna 8: Permite Compartir
            # Mostrar "NO" si tiene marcado cualquiera de las tres opciones:
            # - NO permite_compartir (Parqueadero Exclusivo)
            # - pico_placa_solidario (Pico y Placa Solidario)
            # - discapacidad (Funcionario con Discapacidad)
            permite_compartir = func.get("permite_compartir", True)
            tiene_pico_placa = func.get("pico_placa_solidario", False)
            tiene_discapacidad = func.get("discapacidad", False)

            # Si tiene alguna de las tres opciones, NO comparte
            no_comparte = (not permite_compartir) or tiene_pico_placa or tiene_discapacidad

            compartir_item = QTableWidgetItem("🚫 NO" if no_comparte else "✅ Sí")
            compartir_item.setTextAlignment(0x0004 | 0x0080)  # Centro
            if no_comparte:
                # Fondo rojo para exclusivo
                compartir_item.setBackground(QBrush(QColor("#fadbd8")))
                compartir_item.setForeground(QBrush(QColor("#c0392b")))
            else:
                compartir_item.setBackground(QBrush(QColor("#d4edda")))
                compartir_item.setForeground(QBrush(QColor("#155724")))
            self.tabla_funcionarios.setItem(i, 8, compartir_item)

            # Columna 9: Pico Placa Solidario
            pico_placa = tiene_pico_placa
            solidario_item = QTableWidgetItem("🔄 Sí" if pico_placa else "❌")
            solidario_item.setTextAlignment(0x0004 | 0x0080)  # Centro
            if pico_placa:
                solidario_item.setBackground(QBrush(QColor("#d1ecf1")))
                solidario_item.setForeground(QBrush(QColor("#0c5460")))
            self.tabla_funcionarios.setItem(i, 9, solidario_item)

            # Columna 10: Discapacidad
            discapacidad = tiene_discapacidad
            discap_item = QTableWidgetItem("♿ Sí" if discapacidad else "❌")
            discap_item.setTextAlignment(0x0004 | 0x0080)  # Centro
            if discapacidad:
                discap_item.setBackground(QBrush(QColor("#d4edda")))
                discap_item.setForeground(QBrush(QColor("#155724")))
            self.tabla_funcionarios.setItem(i, 10, discap_item)

            # Columna 11: Carro Híbrido
            tiene_hibrido = func.get("tiene_carro_hibrido", False)
            hibrido_item = QTableWidgetItem("🌿 Sí" if tiene_hibrido else "❌")
            hibrido_item.setTextAlignment(0x0004 | 0x0080)  # Centro
            if tiene_hibrido:
                hibrido_item.setBackground(QBrush(QColor("#d4edda")))
                hibrido_item.setForeground(QBrush(QColor("#27ae60")))
            self.tabla_funcionarios.setItem(i, 11, hibrido_item)

            # Columna 12: Exclusivo Directivo
            tiene_exclusivo = func.get("tiene_parqueadero_exclusivo", False)
            exclusivo_item = QTableWidgetItem("🏢 Sí" if tiene_exclusivo else "❌")
            exclusivo_item.setTextAlignment(0x0004 | 0x0080)  # Centro
            if tiene_exclusivo:
                exclusivo_item.setBackground(QBrush(QColor("#e8daef")))
                exclusivo_item.setForeground(QBrush(QColor("#8e44ad")))
            self.tabla_funcionarios.setItem(i, 12, exclusivo_item)

            # Columna 13: Estado (Activo/Inactivo)
            activo = func.get("activo", True)
            estado_text = "Activo" if activo else "Inactivo"
            estado_item = QTableWidgetItem(estado_text)
            estado_item.setTextAlignment(0x0004 | 0x0080)  # Centro

            if activo:
                # Verde para activo
                estado_item.setBackground(QBrush(QColor("#d4edda")))
                estado_item.setForeground(QBrush(QColor("#155724")))
                estado_item.setFont(QFont("Arial", 9, QFont.Bold))
            else:
                # Rojo para inactivo
                estado_item.setBackground(QBrush(QColor("#f8d7da")))
                estado_item.setForeground(QBrush(QColor("#721c24")))
                estado_item.setFont(QFont("Arial", 9, QFont.Bold))

            self.tabla_funcionarios.setItem(i, 13, estado_item)

            # Botones de acciones (Editar, Ver, Eliminar/Reactivar) - Solo íconos sin fondo
            btn_layout = QHBoxLayout()
            btn_widget = QWidget()
            btn_widget.funcionario_id = func.get("id")  # Almacenar ID para búsquedas rápidas
            btn_layout.setSpacing(8)  # Mayor espaciado entre botones
            btn_layout.setContentsMargins(5, 3, 5, 3)

            # Botón Editar - Ícono con color fuerte para mejor visibilidad
            btn_editar = QPushButton("✏️")
            btn_editar.setFixedSize(32, 32)
            btn_editar.setToolTip("Editar funcionario")
            btn_editar.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(52, 152, 219, 0.25);
                    border: none;
                    font-size: 18px;
                    padding: 0px;
                    border-radius: 5px;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background-color: rgba(52, 152, 219, 0.4);
                    border-radius: 5px;
                }
                QPushButton:pressed {
                    background-color: rgba(52, 152, 219, 0.6);
                    border-radius: 5px;
                }
            """
            )
            btn_editar.clicked.connect(lambda _, fid=func.get("id"): self.editar_funcionario(fid))

            # Botón Ver - Solo ícono sin fondo
            btn_ver = QPushButton("👁️")
            btn_ver.setFixedSize(28, 28)
            btn_ver.setToolTip("Ver detalles del funcionario")
            btn_ver.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 16px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(149, 165, 166, 0.15);
                    border-radius: 4px;
                }
                QPushButton:pressed {
                    background-color: rgba(149, 165, 166, 0.25);
                    border-radius: 4px;
                }
            """
            )
            btn_ver.clicked.connect(lambda _, fid=func.get("id"): self.ver_funcionario(fid))

            # Botón Eliminar o Reactivar según el estado
            if activo:
                # Si está activo, mostrar botón Eliminar - Solo ícono sin fondo
                btn_eliminar = QPushButton("🗑️")
                btn_eliminar.setFixedSize(28, 28)
                btn_eliminar.setToolTip("Desactivar funcionario")
                btn_eliminar.setStyleSheet(
                    """
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        font-size: 16px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: rgba(231, 76, 60, 0.15);
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: rgba(231, 76, 60, 0.25);
                        border-radius: 4px;
                    }
                """
                )
                btn_eliminar.clicked.connect(lambda _, fid=func.get("id"): self.eliminar_funcionario(fid))

                btn_layout.addWidget(btn_editar)
                btn_layout.addWidget(btn_ver)
                btn_layout.addWidget(btn_eliminar)
            else:
                # Si está inactivo, mostrar botón Reactivar - Solo ícono sin fondo
                btn_reactivar = QPushButton("🔄")
                btn_reactivar.setFixedSize(28, 28)
                btn_reactivar.setToolTip("Reactivar funcionario")
                btn_reactivar.setStyleSheet(
                    """
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        font-size: 16px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: rgba(39, 174, 96, 0.15);
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: rgba(39, 174, 96, 0.25);
                        border-radius: 4px;
                    }
                """
                )
                btn_reactivar.clicked.connect(lambda _, fid=func.get("id"): self.reactivar_funcionario(fid))

                # Solo mostrar botón de Ver y Reactivar para inactivos
                btn_layout.addWidget(btn_ver)
                btn_layout.addWidget(btn_reactivar)

            btn_widget.setLayout(btn_layout)
            self.tabla_funcionarios.setCellWidget(i, 14, btn_widget)

        # Actualizar controles de paginación
        self.actualizar_controles_paginacion()

    def actualizar_controles_paginacion(self):
        """Actualiza los labels y botones de paginación"""
        total_paginas = (self.total_funcionarios + self.filas_por_pagina - 1) // self.filas_por_pagina
        if total_paginas == 0:
            total_paginas = 1

        # Actualizar label de página
        self.lbl_pagina.setText(f"Página {self.pagina_actual} de {total_paginas}")

        # Actualizar label de total registros
        if self.total_funcionarios == 0:
            self.lbl_total_registros.setText("Total: 0 funcionarios")
        elif self.total_funcionarios == 1:
            self.lbl_total_registros.setText("Total: 1 funcionario")
        else:
            self.lbl_total_registros.setText(f"Total: {self.total_funcionarios} funcionarios")

        # Habilitar/deshabilitar botones según la página actual
        self.btn_primera_pagina.setEnabled(self.pagina_actual > 1)
        self.btn_anterior.setEnabled(self.pagina_actual > 1)
        self.btn_siguiente.setEnabled(self.pagina_actual < total_paginas)
        self.btn_ultima_pagina.setEnabled(self.pagina_actual < total_paginas)

    def ir_a_primera_pagina(self):
        """Navega a la primera página"""
        self.pagina_actual = 1
        self.cargar_funcionarios()

    def ir_a_ultima_pagina(self):
        """Navega a la última página"""
        total_paginas = (self.total_funcionarios + self.filas_por_pagina - 1) // self.filas_por_pagina
        if total_paginas == 0:
            total_paginas = 1
        self.pagina_actual = total_paginas
        self.cargar_funcionarios()

    def pagina_anterior(self):
        """Navega a la página anterior"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.cargar_funcionarios()

    def pagina_siguiente(self):
        """Navega a la página siguiente"""
        total_paginas = (self.total_funcionarios + self.filas_por_pagina - 1) // self.filas_por_pagina
        if self.pagina_actual < total_paginas:
            self.pagina_actual += 1
            self.cargar_funcionarios()

    def editar_funcionario(self, funcionario_id: int):
        """Abre el modal para editar un funcionario"""
        funcionario_data = self.funcionario_model.obtener_por_id(funcionario_id)
        if funcionario_data:
            modal = EditarFuncionarioModal(self, funcionario_data)
            if modal.exec_() == QDialog.Accepted:
                self.cargar_funcionarios()
                self.funcionario_creado.emit()

    def ver_funcionario(self, funcionario_id: int):
        """Abre el modal para ver los detalles de un funcionario"""
        try:
            funcionario_data = self.funcionario_model.obtener_por_id(funcionario_id)
            if funcionario_data:
                # Obtener datos relacionados (vehículos, asignaciones)
                datos_relacionados = self.funcionario_model.obtener_datos_relacionados(funcionario_id)
                modal = VerFuncionarioModal(self, funcionario_data, datos_relacionados)
                modal.exec_()
            else:
                QMessageBox.warning(self, "Advertencia", "Funcionario no encontrado")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir el modal de visualización: {str(e)}")

    def eliminar_funcionario(self, funcionario_id: int):
        """Elimina un funcionario después de confirmación con información detallada"""
        # Obtener datos del funcionario y sus elementos relacionados
        funcionario_data = self.funcionario_model.obtener_por_id(funcionario_id)
        datos_relacionados = self.funcionario_model.obtener_datos_relacionados(funcionario_id)

        if not funcionario_data:
            QMessageBox.warning(self, "Advertencia", "Funcionario no encontrado")
            return

        # Construir mensaje de confirmación detallado
        nombre_completo = f"{funcionario_data['nombre']} {funcionario_data['apellidos']}"
        mensaje = f"¿Está seguro de que desea eliminar al funcionario '{nombre_completo}'?\n\n"

        vehiculos = datos_relacionados["vehiculos"]
        parqueaderos = datos_relacionados["parqueaderos_afectados"]

        if vehiculos:
            mensaje += "Se eliminarán los siguientes vehículos:\n"
            for vehiculo in vehiculos:
                estado_asignacion = (
                    f" (Parqueadero {format_numero_parqueadero(vehiculo['numero_parqueadero'])})"
                    if vehiculo["tiene_asignacion"]
                    else " (Sin asignar)"
                )
                mensaje += f"• {vehiculo['tipo_vehiculo']} - {vehiculo['placa']} - {vehiculo['tipo_circulacion']}{estado_asignacion}\n"
            mensaje += "\n"

        if parqueaderos:
            mensaje += f"Se liberarán {len(parqueaderos)} parqueadero(s):\n"
            for parq in parqueaderos:
                mensaje += f"• {format_numero_parqueadero(parq['numero_parqueadero'])} (actualmente {parq['estado'].replace('_', ' ')})\n"
            mensaje += "\n"

        mensaje += "Esta acción no se puede deshacer."

        # Mostrar diálogo de confirmación
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Confirmar eliminación")
        msg_box.setText("Eliminación en cascada")
        msg_box.setInformativeText(mensaje)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        if msg_box.exec_() == QMessageBox.Yes:
            exito, error_msg = self.funcionario_model.eliminar(funcionario_id)
            if exito:
                QMessageBox.information(
                    self,
                    "Éxito",
                    "Funcionario y todos sus datos asociados eliminados correctamente.\n\nLos parqueaderos han quedado disponibles.",
                )
                # Actualización optimizada: remover fila de la tabla sin recargar todo
                self._actualizar_fila_eliminada(funcionario_id)
                # Emitir señal específica para eliminación en cascada
                self.funcionario_eliminado.emit()
                # También emitir la señal general para mantener compatibilidad
                self.funcionario_creado.emit()
            else:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el funcionario.\n\nError: {error_msg}")

    def reactivar_funcionario(self, funcionario_id: int):
        """Reactiva un funcionario previamente desactivado"""
        # Obtener datos del funcionario directamente de la base de datos (garantiza datos correctos)
        query = "SELECT nombre, apellidos FROM funcionarios WHERE id = %s AND activo = FALSE"
        funcionario_data = self.db.fetch_one(query, (funcionario_id,))

        if not funcionario_data:
            QMessageBox.warning(self, "Advertencia", "Funcionario no encontrado o ya está activo")
            return

        # Confirmar reactivación
        nombre_completo = f"{funcionario_data['nombre']} {funcionario_data['apellidos']}"
        respuesta = QMessageBox.question(
            self,
            "Confirmar Reactivación",
            f"¿Está seguro de que desea reactivar al funcionario '{nombre_completo}'?\n\n"
            f"Esto hará que:\n"
            f"• El funcionario vuelva a aparecer en los listados\n"
            f"• Sus vehículos estén disponibles para asignación\n"
            f"• Pueda recibir nuevas asignaciones de parqueaderos",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            exito, mensaje = self.funcionario_model.reactivar(funcionario_id)
            if exito:
                QMessageBox.information(
                    self,
                    "Éxito",
                    mensaje
                )
                # Actualización optimizada: remover fila de la tabla sin recargar todo
                self._actualizar_fila_reactivada(funcionario_id)
                # Emitir ambas señales para actualizar todas las pestañas
                self.funcionario_creado.emit()  # Actualiza combos y dashboard
                self.funcionario_eliminado.emit()  # Actualiza tabla de vehículos, asignaciones y parqueaderos
            else:
                QMessageBox.critical(self, "Error", mensaje)

    def _actualizar_fila_eliminada(self, funcionario_id: int):
        """Actualiza la tabla de manera optimizada cuando se elimina un funcionario"""
        filtro_estado = self.combo_filtro_estado.currentData()

        # Si estamos viendo "Activos" o "Todos", simplemente remover la fila de la tabla visual
        if filtro_estado in ["activos", "todos"]:
            # Buscar la fila en la tabla actual
            for row in range(self.tabla_funcionarios.rowCount()):
                # El ID del funcionario está almacenado en la columna 0 (cédula) como data
                cedula_item = self.tabla_funcionarios.item(row, 0)
                if cedula_item:
                    # Buscar el funcionario en la lista completa por cédula
                    cedula = cedula_item.text()
                    for idx, func in enumerate(self.funcionarios_completos):
                        if func.get("cedula") == cedula and func.get("id") == funcionario_id:
                            # Actualizar el estado en memoria
                            self.funcionarios_completos[idx]["activo"] = False
                            # Remover la fila de la tabla visual
                            self.tabla_funcionarios.removeRow(row)
                            return

        # Si estamos viendo "Inactivos", necesitamos recargar para mostrar el nuevo inactivo
        if filtro_estado == "inactivos":
            self.cargar_funcionarios()

    def _actualizar_fila_reactivada(self, funcionario_id: int):
        """Actualiza la tabla de manera optimizada cuando se reactiva un funcionario"""
        filtro_estado = self.combo_filtro_estado.currentData()

        # Si estamos viendo "Inactivos", remover la fila inmediatamente
        if filtro_estado == "inactivos":
            # Buscar y remover la fila que contiene este funcionario
            for row in range(self.tabla_funcionarios.rowCount()):
                # Buscar el widget de acciones que tiene el funcionario_id almacenado
                widget_acciones = self.tabla_funcionarios.cellWidget(row, 14)  # Columna 14 es Acciones
                if widget_acciones and hasattr(widget_acciones, 'funcionario_id'):
                    if widget_acciones.funcionario_id == funcionario_id:
                        # Encontramos la fila correcta, removerla inmediatamente
                        self.tabla_funcionarios.removeRow(row)
                        # Actualizar contador de funcionarios
                        self.total_funcionarios = max(0, self.total_funcionarios - 1)
                        # Actualizar label de paginación
                        total_paginas = (self.total_funcionarios + self.filas_por_pagina - 1) // self.filas_por_pagina if self.total_funcionarios > 0 else 1
                        self.lbl_pagina.setText(f"Página {self.pagina_actual} de {total_paginas}")
                        # Actualizar label de total registros
                        self.lbl_total_registros.setText(f"Total: {self.total_funcionarios} funcionarios")
                        return

        # Si estamos viendo "Activos" o "Todos", recargar para mostrar el reactivado
        else:
            self.cargar_funcionarios()

    def actualizar_funcionarios(self):
        """Actualiza la lista de funcionarios"""
        # Forzar reconexión para ver commits frescos de otros threads
        self.db.force_reconnect()
        self.cargar_funcionarios()

    def filtrar_funcionarios(self):
        """Filtra los funcionarios según la cédula ingresada y el estado (activo/inactivo)"""
        texto_busqueda = self.txt_buscar_cedula.text().strip()
        filtro_estado = self.combo_filtro_estado.currentData()

        # Obtener todos los funcionarios de nuevo (necesario para aplicar filtros)
        todos_funcionarios = self.funcionario_model.obtener_todos_incluyendo_inactivos()

        # Aplicar filtro de estado primero
        if filtro_estado == "activos":
            funcionarios_filtrados = [func for func in todos_funcionarios if func.get("activo", True)]
        elif filtro_estado == "inactivos":
            funcionarios_filtrados = [func for func in todos_funcionarios if not func.get("activo", True)]
        else:  # "todos"
            funcionarios_filtrados = todos_funcionarios

        # Aplicar filtro de búsqueda si hay texto (busca en cédula, nombre y apellidos)
        if texto_busqueda:
            texto_busqueda_lower = texto_busqueda.lower()
            funcionarios_filtrados = [
                func for func in funcionarios_filtrados
                if (texto_busqueda_lower in func.get("cedula", "").lower()
                    or texto_busqueda_lower in func.get("nombre", "").lower()
                    or texto_busqueda_lower in func.get("apellidos", "").lower())
            ]

        # Guardar temporalmente la lista completa
        lista_original = self.funcionarios_completos
        self.funcionarios_completos = funcionarios_filtrados
        self.total_funcionarios = len(funcionarios_filtrados)

        # Resetear a la primera página
        self.pagina_actual = 1

        # Calcular paginación
        total_paginas = (self.total_funcionarios + self.filas_por_pagina - 1) // self.filas_por_pagina
        if total_paginas == 0:
            total_paginas = 1

        # Calcular índices de inicio y fin para la página actual
        inicio = (self.pagina_actual - 1) * self.filas_por_pagina
        fin = min(inicio + self.filas_por_pagina, self.total_funcionarios)

        # Obtener funcionarios para la página actual
        funcionarios_pagina = self.funcionarios_completos[inicio:fin]

        # Configurar tabla para mostrar solo las filas de esta página
        self.tabla_funcionarios.setRowCount(len(funcionarios_pagina))

        for i, func in enumerate(funcionarios_pagina):
            # Ajustar índices ya que eliminamos la columna ID oculta
            cedula_item = QTableWidgetItem(func.get("cedula", ""))
            cedula_item.setTextAlignment(0x0004 | 0x0080)  # Centro horizontal y vertical
            self.tabla_funcionarios.setItem(i, 0, cedula_item)

            nombre_item = QTableWidgetItem(func.get("nombre", ""))
            nombre_item.setTextAlignment(0x0001 | 0x0080)  # Izquierda horizontal, centro vertical
            self.tabla_funcionarios.setItem(i, 1, nombre_item)

            apellidos_item = QTableWidgetItem(func.get("apellidos", ""))
            apellidos_item.setTextAlignment(0x0001 | 0x0080)  # Izquierda horizontal, centro vertical
            self.tabla_funcionarios.setItem(i, 2, apellidos_item)

            direccion_item = QTableWidgetItem(func.get("direccion_grupo", ""))
            direccion_item.setTextAlignment(0x0001 | 0x0080)  # Izquierda horizontal, centro vertical
            self.tabla_funcionarios.setItem(i, 3, direccion_item)

            cargo_item = QTableWidgetItem(func.get("cargo", ""))
            cargo_item.setTextAlignment(0x0001 | 0x0080)  # Izquierda horizontal, centro vertical
            self.tabla_funcionarios.setItem(i, 4, cargo_item)

            celular_item = QTableWidgetItem(func.get("celular", ""))
            celular_item.setTextAlignment(0x0004 | 0x0080)  # Centro horizontal y vertical
            self.tabla_funcionarios.setItem(i, 5, celular_item)

            tarjeta_item = QTableWidgetItem(func.get("no_tarjeta_proximidad", "") or "")
            tarjeta_item.setTextAlignment(0x0004 | 0x0080)  # Centro horizontal y vertical
            self.tabla_funcionarios.setItem(i, 6, tarjeta_item)

            # Formatear número de vehículos con mejor presentación
            total_vehiculos = func.get("total_vehiculos", 0)
            vehiculos_item = QTableWidgetItem(f"{total_vehiculos}/2")
            vehiculos_item.setTextAlignment(0x0004 | 0x0080)  # Centro horizontal y vertical
            self.tabla_funcionarios.setItem(i, 7, vehiculos_item)

            # ===== NUEVAS COLUMNAS: Indicadores visuales =====
            permite_compartir = func.get("permite_compartir", True)
            tiene_pico_placa = func.get("pico_placa_solidario", False)
            tiene_discapacidad = func.get("discapacidad", False)

            no_comparte = (not permite_compartir) or tiene_pico_placa or tiene_discapacidad

            compartir_item = QTableWidgetItem("🚫 NO" if no_comparte else "✅ Sí")
            compartir_item.setTextAlignment(0x0004 | 0x0080)
            if no_comparte:
                compartir_item.setBackground(QBrush(QColor("#fadbd8")))
                compartir_item.setForeground(QBrush(QColor("#c0392b")))
            else:
                compartir_item.setBackground(QBrush(QColor("#d4edda")))
                compartir_item.setForeground(QBrush(QColor("#155724")))
            self.tabla_funcionarios.setItem(i, 8, compartir_item)

            solidario_item = QTableWidgetItem("🔄 Sí" if tiene_pico_placa else "❌")
            solidario_item.setTextAlignment(0x0004 | 0x0080)
            if tiene_pico_placa:
                solidario_item.setBackground(QBrush(QColor("#d1ecf1")))
                solidario_item.setForeground(QBrush(QColor("#0c5460")))
            self.tabla_funcionarios.setItem(i, 9, solidario_item)

            discap_item = QTableWidgetItem("♿ Sí" if tiene_discapacidad else "❌")
            discap_item.setTextAlignment(0x0004 | 0x0080)
            if tiene_discapacidad:
                discap_item.setBackground(QBrush(QColor("#d4edda")))
                discap_item.setForeground(QBrush(QColor("#155724")))
            self.tabla_funcionarios.setItem(i, 10, discap_item)

            # Columna 11: Carro Híbrido
            tiene_hibrido = func.get("tiene_carro_hibrido", False)
            hibrido_item = QTableWidgetItem("🌿 Sí" if tiene_hibrido else "❌")
            hibrido_item.setTextAlignment(0x0004 | 0x0080)  # Centro
            if tiene_hibrido:
                hibrido_item.setBackground(QBrush(QColor("#d4edda")))
                hibrido_item.setForeground(QBrush(QColor("#27ae60")))
            self.tabla_funcionarios.setItem(i, 11, hibrido_item)

            # Columna 12: Exclusivo Directivo
            tiene_exclusivo = func.get("tiene_parqueadero_exclusivo", False)
            exclusivo_item = QTableWidgetItem("🏢 Sí" if tiene_exclusivo else "❌")
            exclusivo_item.setTextAlignment(0x0004 | 0x0080)  # Centro
            if tiene_exclusivo:
                exclusivo_item.setBackground(QBrush(QColor("#e8daef")))
                exclusivo_item.setForeground(QBrush(QColor("#8e44ad")))
            self.tabla_funcionarios.setItem(i, 12, exclusivo_item)

            # Columna 13: Estado (Activo/Inactivo)
            activo = func.get("activo", True)
            estado_text = "Activo" if activo else "Inactivo"
            estado_item = QTableWidgetItem(estado_text)
            estado_item.setTextAlignment(0x0004 | 0x0080)

            if activo:
                estado_item.setBackground(QBrush(QColor("#d4edda")))
                estado_item.setForeground(QBrush(QColor("#155724")))
                estado_item.setFont(QFont("Arial", 9, QFont.Bold))
            else:
                estado_item.setBackground(QBrush(QColor("#f8d7da")))
                estado_item.setForeground(QBrush(QColor("#721c24")))
                estado_item.setFont(QFont("Arial", 9, QFont.Bold))

            self.tabla_funcionarios.setItem(i, 13, estado_item)

            # Botones de acciones (Editar, Ver, Eliminar/Reactivar) - Solo íconos sin fondo
            btn_layout = QHBoxLayout()
            btn_widget = QWidget()
            btn_widget.funcionario_id = func.get("id")  # Almacenar ID para búsquedas rápidas
            btn_layout.setSpacing(8)  # Mayor espaciado entre botones
            btn_layout.setContentsMargins(5, 3, 5, 3)

            # Botón Editar - Ícono con color fuerte para mejor visibilidad
            btn_editar = QPushButton("✏️")
            btn_editar.setFixedSize(32, 32)
            btn_editar.setToolTip("Editar funcionario")
            btn_editar.setStyleSheet(
                """
                QPushButton {
                    background-color: rgba(52, 152, 219, 0.25);
                    border: none;
                    font-size: 18px;
                    padding: 0px;
                    border-radius: 5px;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background-color: rgba(52, 152, 219, 0.4);
                    border-radius: 5px;
                }
                QPushButton:pressed {
                    background-color: rgba(52, 152, 219, 0.6);
                    border-radius: 5px;
                }
            """
            )
            btn_editar.clicked.connect(lambda _, fid=func.get("id"): self.editar_funcionario(fid))

            # Botón Ver - Solo ícono sin fondo
            btn_ver = QPushButton("👁️")
            btn_ver.setFixedSize(28, 28)
            btn_ver.setToolTip("Ver detalles del funcionario")
            btn_ver.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 16px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(149, 165, 166, 0.15);
                    border-radius: 4px;
                }
                QPushButton:pressed {
                    background-color: rgba(149, 165, 166, 0.25);
                    border-radius: 4px;
                }
            """
            )
            btn_ver.clicked.connect(lambda _, fid=func.get("id"): self.ver_funcionario(fid))

            # Botón Eliminar o Reactivar según el estado
            if activo:
                # Si está activo, mostrar botón Eliminar - Solo ícono sin fondo
                btn_eliminar = QPushButton("🗑️")
                btn_eliminar.setFixedSize(28, 28)
                btn_eliminar.setToolTip("Desactivar funcionario")
                btn_eliminar.setStyleSheet(
                    """
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        font-size: 16px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: rgba(231, 76, 60, 0.15);
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: rgba(231, 76, 60, 0.25);
                        border-radius: 4px;
                    }
                """
                )
                btn_eliminar.clicked.connect(lambda _, fid=func.get("id"): self.eliminar_funcionario(fid))

                btn_layout.addWidget(btn_editar)
                btn_layout.addWidget(btn_ver)
                btn_layout.addWidget(btn_eliminar)
            else:
                # Si está inactivo, mostrar botón Reactivar - Solo ícono sin fondo
                btn_reactivar = QPushButton("🔄")
                btn_reactivar.setFixedSize(28, 28)
                btn_reactivar.setToolTip("Reactivar funcionario")
                btn_reactivar.setStyleSheet(
                    """
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        font-size: 16px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: rgba(39, 174, 96, 0.15);
                        border-radius: 4px;
                    }
                    QPushButton:pressed {
                        background-color: rgba(39, 174, 96, 0.25);
                        border-radius: 4px;
                    }
                """
                )
                btn_reactivar.clicked.connect(lambda _, fid=func.get("id"): self.reactivar_funcionario(fid))

                # Solo mostrar botón de Ver y Reactivar para inactivos
                btn_layout.addWidget(btn_ver)
                btn_layout.addWidget(btn_reactivar)

            btn_widget.setLayout(btn_layout)
            self.tabla_funcionarios.setCellWidget(i, 14, btn_widget)

        # Restaurar lista original
        self.funcionarios_completos = lista_original

        # Actualizar controles de paginación
        self.actualizar_controles_paginacion()

        # Actualizar label de resultados
        total_resultados = len(funcionarios_filtrados)
        if total_resultados == 0:
            self.lbl_resultados.setText("No se encontraron resultados")
            self.lbl_resultados.setStyleSheet("font-size: 11px; color: #e74c3c; font-style: italic; font-weight: bold;")
        elif total_resultados == 1:
            self.lbl_resultados.setText("1 resultado encontrado")
            self.lbl_resultados.setStyleSheet("font-size: 11px; color: #27ae60; font-style: italic; font-weight: bold;")
        else:
            self.lbl_resultados.setText(f"{total_resultados} resultados encontrados")
            self.lbl_resultados.setStyleSheet("font-size: 11px; color: #27ae60; font-style: italic; font-weight: bold;")

    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda y muestra todos los funcionarios"""
        self.txt_buscar_cedula.clear()
        self.pagina_actual = 1
        self.cargar_funcionarios()
        self.lbl_resultados.setText("")

    def importar_desde_excel(self):
        """Importa funcionarios masivamente desde un archivo Excel (.xlsx o .xls)"""
        try:
            # Verificar si pandas y openpyxl están instalados
            try:
                import pandas as pd
            except ImportError:
                QMessageBox.critical(
                    self,
                    "Error de Dependencias",
                    "La librería 'pandas' no está instalada.\n\n"
                    "Para usar esta función, ejecute:\n"
                    "pip install pandas openpyxl xlrd"
                )
                return

            # Abrir diálogo para seleccionar archivo
            archivo, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar archivo Excel de funcionarios",
                "",
                "Archivos Excel (*.xlsx *.xls);;Todos los archivos (*.*)"
            )

            if not archivo:
                return  # Usuario canceló

            # Leer el archivo Excel
            try:
                df = pd.read_excel(archivo)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error al Leer Archivo",
                    f"No se pudo leer el archivo Excel.\n\nError: {str(e)}\n\n"
                    "Asegúrese de que el archivo no esté abierto en otra aplicación."
                )
                return

            # Validar columnas requeridas
            columnas_requeridas = ["Cedula", "Nombre", "Apellidos", "Direccion", "Cargo", "Celular"]
            columnas_opcionales = ["Tarjeta_Prox", "Tipo_Excepcion"]

            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            if columnas_faltantes:
                QMessageBox.critical(
                    self,
                    "Error en Estructura del Archivo",
                    f"El archivo Excel no tiene las columnas requeridas.\n\n"
                    f"Columnas faltantes: {', '.join(columnas_faltantes)}\n\n"
                    f"Columnas requeridas:\n{', '.join(columnas_requeridas)}\n\n"
                    f"Columnas opcionales:\n{', '.join(columnas_opcionales)}"
                )
                return

            # Reemplazar valores NaN por vacío
            df = df.fillna("")

            # Validar que hay datos
            if len(df) == 0:
                QMessageBox.warning(self, "Archivo Vacío", "El archivo Excel no contiene datos para importar.")
                return

            # Confirmar importación
            reply = QMessageBox.question(
                self,
                "Confirmar Importación",
                f"Se encontraron {len(df)} registros en el archivo.\n\n"
                "¿Desea proceder con la importación?\n\n"
                "Los registros duplicados (misma cédula) serán omitidos.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

            # Procesar cada fila
            importados = 0
            omitidos = 0
            errores = []

            for index, row in df.iterrows():
                try:
                    # Extraer datos básicos
                    cedula = str(row["Cedula"]).strip()
                    nombre = str(row["Nombre"]).strip()
                    apellidos = str(row["Apellidos"]).strip()
                    direccion = str(row["Direccion"]).strip()
                    cargo = str(row["Cargo"]).strip()
                    celular = str(row["Celular"]).strip()
                    tarjeta = str(row.get("Tarjeta_Prox", "")).strip()
                    tipo_excepcion = str(row.get("Tipo_Excepcion", "ninguna")).strip().lower()

                    # Validaciones básicas
                    if not cedula or not nombre or not apellidos:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Cédula, Nombre o Apellidos vacíos")
                        continue

                    # Validar formato de cédula (7-10 dígitos)
                    if not cedula.isdigit() or len(cedula) < 7 or len(cedula) > 10:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Cédula inválida '{cedula}' (debe ser 7-10 dígitos)")
                        continue

                    # Validar formato de celular (10 dígitos)
                    if celular and (not celular.isdigit() or len(celular) != 10):
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Celular inválido '{celular}' (debe ser 10 dígitos)")
                        continue

                    # Validar que Cargo sea válido
                    if cargo not in CARGOS_DISPONIBLES:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Cargo inválido '{cargo}' (no existe en el sistema)")
                        continue

                    # Validar que Dirección sea válida
                    if direccion not in DIRECCIONES_DISPONIBLES:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Dirección inválida '{direccion}' (no existe en el sistema)")
                        continue

                    # Procesar tipo de excepción y establecer banderas
                    if tipo_excepcion == "carro_hibrido":
                        permite_compartir = False
                        pico_placa_solidario = False
                        discapacidad = False
                        tiene_parqueadero_exclusivo = False
                        tiene_carro_hibrido = True
                    elif tipo_excepcion == "exclusivo_directivo":
                        permite_compartir = False
                        pico_placa_solidario = False
                        discapacidad = False
                        tiene_parqueadero_exclusivo = True
                        tiene_carro_hibrido = False
                    elif tipo_excepcion == "pico_placa_solidario":
                        permite_compartir = True
                        pico_placa_solidario = True
                        discapacidad = False
                        tiene_parqueadero_exclusivo = False
                        tiene_carro_hibrido = False
                    elif tipo_excepcion == "discapacidad":
                        permite_compartir = True
                        pico_placa_solidario = False
                        discapacidad = True
                        tiene_parqueadero_exclusivo = False
                        tiene_carro_hibrido = False
                    else:  # "ninguna" o cualquier otro valor
                        permite_compartir = True
                        pico_placa_solidario = False
                        discapacidad = False
                        tiene_parqueadero_exclusivo = False
                        tiene_carro_hibrido = False

                    # Intentar crear funcionario
                    exito, error_msg = self.funcionario_model.crear(
                        cedula=cedula,
                        nombre=nombre,
                        apellidos=apellidos,
                        direccion_grupo=direccion,
                        cargo=cargo,
                        celular=celular,
                        tarjeta=tarjeta,
                        permite_compartir=permite_compartir,
                        pico_placa_solidario=pico_placa_solidario,
                        discapacidad=discapacidad,
                        tiene_parqueadero_exclusivo=tiene_parqueadero_exclusivo,
                        tiene_carro_hibrido=tiene_carro_hibrido
                    )

                    if exito:
                        importados += 1
                    else:
                        if "Duplicate entry" in error_msg:
                            omitidos += 1
                            errores.append(f"Fila {index + 2}: Cédula duplicada '{cedula}'")
                        else:
                            omitidos += 1
                            errores.append(f"Fila {index + 2}: {error_msg}")

                except Exception as e:
                    omitidos += 1
                    errores.append(f"Fila {index + 2}: Error inesperado - {str(e)}")

            # Mostrar resultados
            mensaje_resultado = "✅ Importación Completada\n\n"
            mensaje_resultado += f"Registros importados exitosamente: {importados}\n"
            mensaje_resultado += f"Registros omitidos/con errores: {omitidos}\n"

            if errores:
                mensaje_resultado += "\n⚠️ Detalles de errores (primeros 10):\n"
                mensaje_resultado += "\n".join(errores[:10])
                if len(errores) > 10:
                    mensaje_resultado += f"\n\n... y {len(errores) - 10} errores más."

            QMessageBox.information(self, "Importación Completada", mensaje_resultado)

            # Recargar tabla si se importó al menos un funcionario
            if importados > 0:
                self.cargar_funcionarios()
                self.funcionario_creado.emit()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error en Importación",
                f"Ocurrió un error durante la importación:\n\n{str(e)}"
            )


class VerFuncionarioModal(QDialog):
    """Modal para visualizar los detalles de un funcionario"""

    def __init__(self, parent, funcionario_data, datos_relacionados):
        super().__init__(parent)
        self.funcionario_data = funcionario_data
        self.datos_relacionados = datos_relacionados
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        """Configura la interfaz del modal"""
        self.setWindowTitle("Detalles del Funcionario")
        self.setModal(True)
        self.setFixedSize(600, 600)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("👤 Información del Funcionario")
        from PyQt5.QtGui import QFont

        font_titulo = QFont()
        font_titulo.setPointSize(14)
        font_titulo.setBold(True)
        titulo.setFont(font_titulo)
        from PyQt5.QtCore import Qt

        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(titulo)

        # Línea separadora
        from PyQt5.QtWidgets import QFrame

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Grupo de información personal
        grupo_personal = QGroupBox("📋 Información Personal")
        form_personal = QFormLayout()
        form_personal.setSpacing(10)

        self.lbl_cedula = QLabel("")
        self.lbl_cedula.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 3px; font-weight: bold;"
        )
        form_personal.addRow("Cédula:", self.lbl_cedula)

        self.lbl_nombre = QLabel("")
        self.lbl_nombre.setStyleSheet("font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        form_personal.addRow("Nombre completo:", self.lbl_nombre)

        self.lbl_celular = QLabel("")
        self.lbl_celular.setStyleSheet("font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        form_personal.addRow("Celular:", self.lbl_celular)

        grupo_personal.setLayout(form_personal)
        layout.addWidget(grupo_personal)

        # Grupo de información laboral
        grupo_laboral = QGroupBox("💼 Información Laboral")
        form_laboral = QFormLayout()
        form_laboral.setSpacing(10)

        self.lbl_cargo = QLabel("")
        self.lbl_cargo.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px; font-weight: bold;"
        )
        form_laboral.addRow("Cargo:", self.lbl_cargo)

        self.lbl_direccion = QLabel("")
        self.lbl_direccion.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px;"
        )
        form_laboral.addRow("Dirección/Grupo:", self.lbl_direccion)

        self.lbl_tarjeta = QLabel("")
        self.lbl_tarjeta.setStyleSheet("font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px;")
        form_laboral.addRow("Tarjeta Prox:", self.lbl_tarjeta)

        grupo_laboral.setLayout(form_laboral)
        layout.addWidget(grupo_laboral)

        # Grupo de características especiales
        grupo_especial = QGroupBox("⚙️ Características Especiales")
        form_especial = QFormLayout()
        form_especial.setSpacing(10)

        self.lbl_compartir = QLabel("")
        self.lbl_compartir.setStyleSheet("font-size: 12px; padding: 5px; border-radius: 3px; font-weight: bold;")
        form_especial.addRow("Permite compartir parqueadero:", self.lbl_compartir)

        self.lbl_solidario = QLabel("")
        self.lbl_solidario.setStyleSheet("font-size: 12px; padding: 5px; border-radius: 3px; font-weight: bold;")
        form_especial.addRow("Pico y placa solidario:", self.lbl_solidario)

        self.lbl_discapacidad = QLabel("")
        self.lbl_discapacidad.setStyleSheet("font-size: 12px; padding: 5px; border-radius: 3px; font-weight: bold;")
        form_especial.addRow("Discapacidad:", self.lbl_discapacidad)

        grupo_especial.setLayout(form_especial)
        layout.addWidget(grupo_especial)

        # Grupo de vehículos
        grupo_vehiculos = QGroupBox("🚗 Vehículos Registrados")
        vehiculos_layout = QVBoxLayout()

        self.lbl_vehiculos = QLabel("")
        self.lbl_vehiculos.setWordWrap(True)
        self.lbl_vehiculos.setStyleSheet(
            "font-size: 11px; padding: 10px; background-color: #fff9e6; border-radius: 3px;"
        )
        vehiculos_layout.addWidget(self.lbl_vehiculos)

        grupo_vehiculos.setLayout(vehiculos_layout)
        layout.addWidget(grupo_vehiculos)

        # Botón cerrar
        btn_layout = QHBoxLayout()
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.accept)
        self.btn_cerrar.setStyleSheet(
            "QPushButton { background-color: #34495e; color: white; font-weight: bold; padding: 10px 30px; }"
        )
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cerrar)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def cargar_datos(self):
        """Carga los datos del funcionario en el modal"""
        # Información personal
        self.lbl_cedula.setText(self.funcionario_data.get("cedula", "N/A"))
        nombre_completo = f"{self.funcionario_data.get('nombre', '')} {self.funcionario_data.get('apellidos', '')}"
        self.lbl_nombre.setText(nombre_completo)
        self.lbl_celular.setText(self.funcionario_data.get("celular", "N/A"))

        # Información laboral
        self.lbl_cargo.setText(self.funcionario_data.get("cargo", "N/A"))
        self.lbl_direccion.setText(self.funcionario_data.get("direccion_grupo", "N/A"))
        tarjeta = self.funcionario_data.get("no_tarjeta_proximidad", "")
        self.lbl_tarjeta.setText(tarjeta if tarjeta else "No registrada")

        # Características especiales
        permite_compartir = self.funcionario_data.get("permite_compartir", True)
        if permite_compartir:
            self.lbl_compartir.setText("✅ Sí")
            self.lbl_compartir.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #d4edda; color: #155724; border-radius: 3px; font-weight: bold;"
            )
        else:
            self.lbl_compartir.setText("🚫 No (Exclusivo)")
            self.lbl_compartir.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #f8d7da; color: #721c24; border-radius: 3px; font-weight: bold;"
            )

        pico_placa = self.funcionario_data.get("pico_placa_solidario", False)
        if pico_placa:
            self.lbl_solidario.setText("🔄 Sí")
            self.lbl_solidario.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #d1ecf1; color: #0c5460; border-radius: 3px; font-weight: bold;"
            )
        else:
            self.lbl_solidario.setText("❌ No")
            self.lbl_solidario.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #ecf0f1; color: #666; border-radius: 3px; font-weight: bold;"
            )

        discapacidad = self.funcionario_data.get("discapacidad", False)
        if discapacidad:
            self.lbl_discapacidad.setText("♿ Sí")
            self.lbl_discapacidad.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #d4edda; color: #155724; border-radius: 3px; font-weight: bold;"
            )
        else:
            self.lbl_discapacidad.setText("❌ No")
            self.lbl_discapacidad.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #ecf0f1; color: #666; border-radius: 3px; font-weight: bold;"
            )

        # Información de vehículos
        vehiculos = self.datos_relacionados.get("vehiculos", [])
        if vehiculos:
            texto_vehiculos = f"Total de vehículos: {len(vehiculos)}/2\n\n"
            for i, vehiculo in enumerate(vehiculos, 1):
                tipo = vehiculo.get("tipo_vehiculo", "N/A")
                placa = vehiculo.get("placa", "N/A")
                circulacion = vehiculo.get("tipo_circulacion", "N/A")
                tiene_asignacion = vehiculo.get("tiene_asignacion", False)

                estado = (
                    f"Parqueadero {format_numero_parqueadero(vehiculo.get('numero_parqueadero', 0))}" if tiene_asignacion else "Sin asignar"
                )
                texto_vehiculos += f"{i}. {tipo} - Placa: {placa} ({circulacion}) - {estado}\n"

            self.lbl_vehiculos.setText(texto_vehiculos.strip())
        else:
            self.lbl_vehiculos.setText("No tiene vehículos registrados")


class EditarFuncionarioModal(QDialog):
    """Modal para editar datos de un funcionario"""

    def __init__(self, parent, funcionario_data):
        super().__init__(parent)
        self.parent_tab = parent
        self.funcionario_data = funcionario_data
        self.funcionario_model = parent.funcionario_model
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        """Configura la interfaz del modal"""
        self.setWindowTitle("Editar Funcionario")
        self.setModal(True)
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout()

        # Formulario
        form_layout = QFormLayout()

        self.txt_cedula = QLineEdit()
        self.txt_cedula.setValidator(InputValidators.CEDULA)
        self.txt_cedula.setPlaceholderText("Ingrese 7-10 dígitos numéricos")
        self.txt_cedula.setMaxLength(10)
        form_layout.addRow("Cédula:", self.txt_cedula)

        self.txt_nombre = QLineEdit()
        self.txt_nombre.setValidator(InputValidators.NOMBRE)
        self.txt_nombre.setPlaceholderText("Solo letras y espacios")
        form_layout.addRow("Nombre:", self.txt_nombre)

        self.txt_apellidos = QLineEdit()
        self.txt_apellidos.setValidator(InputValidators.APELLIDOS)
        self.txt_apellidos.setPlaceholderText("Solo letras y espacios")
        form_layout.addRow("Apellidos:", self.txt_apellidos)

        # Dirección/Grupo (sin botón +, los items personalizados se cargan automáticamente)
        self.combo_direccion = QComboBox()
        self.combo_direccion.addItem("-- Seleccione --", "")
        self.combo_direccion.addItems(DIRECCIONES_DISPONIBLES)
        form_layout.addRow("Dirección/Grupo:", self.combo_direccion)

        # Cargo (sin botón +, los items personalizados se cargan automáticamente)
        self.combo_cargo = QComboBox()
        self.combo_cargo.addItem("-- Seleccione --", "")
        self.combo_cargo.addItems(CARGOS_DISPONIBLES)
        form_layout.addRow("Cargo:", self.combo_cargo)

        self.txt_celular = QLineEdit()
        self.txt_celular.setValidator(InputValidators.CELULAR)
        self.txt_celular.setPlaceholderText("10 dígitos numéricos (ej: 3001234567)")
        self.txt_celular.setMaxLength(10)
        form_layout.addRow("Celular:", self.txt_celular)

        self.txt_tarjeta = QLineEdit()
        self.txt_tarjeta.setValidator(InputValidators.TARJETA_CLARO)
        self.txt_tarjeta.setPlaceholderText("Alfanumérico, máx 15 caracteres")
        self.txt_tarjeta.setMaxLength(15)
        form_layout.addRow("No.Tarjeta Prox:", self.txt_tarjeta)

        # ===== COMBOBOX DE TIPO DE EXCEPCIÓN =====
        self.combo_tipo_excepcion = QComboBox()
        self.combo_tipo_excepcion.addItem("-- Ninguna --", "ninguna")
        self.combo_tipo_excepcion.addItem("🔄 Pico y Placa Solidario", "pico_placa_solidario")
        self.combo_tipo_excepcion.addItem("♿ Funcionario con Discapacidad", "discapacidad")
        self.combo_tipo_excepcion.addItem("🏢 Exclusivo Directivo (4 carros)", "exclusivo_directivo")
        self.combo_tipo_excepcion.addItem("🌿 Carro Híbrido (Incentivo Ambiental)", "carro_hibrido")

        # Tooltips para cada opción
        self.combo_tipo_excepcion.setItemData(
            1, "Permite usar el parqueadero en días PAR/IMPAR sin restricción", Qt.ToolTipRole
        )
        self.combo_tipo_excepcion.setItemData(2, "Funcionario con condición de discapacidad", Qt.ToolTipRole)
        self.combo_tipo_excepcion.setItemData(
            3,
            "Permite registrar hasta 4 vehículos (solo carros) en el mismo parqueadero. Disponible para cualquier cargo",
            Qt.ToolTipRole,
        )
        self.combo_tipo_excepcion.setItemData(
            4, "Carro híbrido - Uso diario, parqueadero exclusivo (incentivo ambiental)", Qt.ToolTipRole
        )

        # Expandir el ancho del dropdown para mostrar textos largos
        self.combo_tipo_excepcion.view().setMinimumWidth(450)

        form_layout.addRow("Tipo de Excepción:", self.combo_tipo_excepcion)

        layout.addLayout(form_layout)

        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.guardar_cambios)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

        # Cargar items personalizados (cargos y direcciones guardados previamente)
        self.cargar_items_personalizados()

    def cargar_items_personalizados(self):
        """Carga items personalizados desde el archivo JSON"""
        import json
        import os

        try:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
            config_file = os.path.join(config_dir, "custom_items.json")

            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    custom_items = json.load(f)

                # Cargar cargos personalizados
                if "cargos" in custom_items:
                    for cargo in custom_items["cargos"]:
                        if cargo and cargo.strip():
                            self.combo_cargo.addItem(cargo)

                # Cargar direcciones personalizadas
                if "direcciones" in custom_items:
                    for direccion in custom_items["direcciones"]:
                        if direccion and direccion.strip():
                            self.combo_direccion.addItem(direccion)

        except Exception as e:
            print(f"Error al cargar items personalizados en modal: {e}")

    def on_pico_placa_changed(self, state):
        """Cuando se marca Pico y Placa, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_discapacidad.blockSignals(True)
            self.chk_exclusivo_directivo.blockSignals(True)
            self.chk_carro_hibrido.blockSignals(True)
            self.chk_discapacidad.setChecked(False)
            self.chk_exclusivo_directivo.setChecked(False)
            self.chk_carro_hibrido.setChecked(False)
            self.chk_discapacidad.blockSignals(False)
            self.chk_exclusivo_directivo.blockSignals(False)
            self.chk_carro_hibrido.blockSignals(False)

    def on_discapacidad_changed(self, state):
        """Cuando se marca Discapacidad, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_exclusivo_directivo.blockSignals(True)
            self.chk_carro_hibrido.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_exclusivo_directivo.setChecked(False)
            self.chk_carro_hibrido.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_exclusivo_directivo.blockSignals(False)
            self.chk_carro_hibrido.blockSignals(False)

    def on_exclusivo_directivo_changed(self, state):
        """Cuando se marca Exclusivo Directivo en el modal, desmarca las otras opciones y valida el cargo"""
        if state == 2:  # Checked
            # Validar cargo
            from ..config.settings import CARGOS_DIRECTIVOS
            cargo_actual = self.combo_cargo.currentText()

            if cargo_actual not in CARGOS_DIRECTIVOS and cargo_actual != "-- Seleccione --":
                # Bloquear el checkbox y mostrar advertencia
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "Cargo No Permitido",
                    f"El parqueadero exclusivo directivo solo esta disponible para:\n\n"
                    f"- {', '.join(CARGOS_DIRECTIVOS)}\n\n"
                    f"Cargo actual: {cargo_actual}\n\n"
                    f"Por favor, cambie el cargo antes de activar esta opcion."
                )
                self.chk_exclusivo_directivo.blockSignals(True)
                self.chk_exclusivo_directivo.setChecked(False)
                self.chk_exclusivo_directivo.blockSignals(False)
                return

            # Desmarcar las otras opciones
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_discapacidad.blockSignals(True)
            self.chk_carro_hibrido.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_discapacidad.setChecked(False)
            self.chk_carro_hibrido.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_discapacidad.blockSignals(False)
            self.chk_carro_hibrido.blockSignals(False)

    def on_carro_hibrido_changed(self, state):
        """Cuando se marca Carro Hibrido en el modal, desmarca las otras opciones"""
        if state == 2:  # Checked
            # Desmarcar las otras opciones
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_discapacidad.blockSignals(True)
            self.chk_exclusivo_directivo.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_discapacidad.setChecked(False)
            self.chk_exclusivo_directivo.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_discapacidad.blockSignals(False)
            self.chk_exclusivo_directivo.blockSignals(False)

    def on_cargo_changed_modal(self, cargo: str):
        """Validaciones o acciones cuando cambia el cargo"""
        # Si en el futuro se necesitan validaciones específicas por cargo
        pass

    def cargar_datos(self):
        """Carga los datos del funcionario en el formulario"""
        self.txt_cedula.setText(self.funcionario_data.get("cedula", ""))
        self.txt_nombre.setText(self.funcionario_data.get("nombre", ""))
        self.txt_apellidos.setText(self.funcionario_data.get("apellidos", ""))

        direccion = self.funcionario_data.get("direccion_grupo", "")
        index = self.combo_direccion.findText(direccion)
        if index >= 0:
            self.combo_direccion.setCurrentIndex(index)

        cargo = self.funcionario_data.get("cargo", "")
        index = self.combo_cargo.findText(cargo)
        if index >= 0:
            self.combo_cargo.setCurrentIndex(index)

        self.txt_celular.setText(self.funcionario_data.get("celular", ""))
        self.txt_tarjeta.setText(self.funcionario_data.get("no_tarjeta_proximidad", "") or "")

        # Cargar tipo de excepción en el ComboBox (solo uno puede estar activo)
        # Prioridad: carro híbrido > exclusivo directivo > pico placa > discapacidad > ninguna
        if self.funcionario_data.get("tiene_carro_hibrido", False):
            # Carro híbrido tiene máxima prioridad
            index = self.combo_tipo_excepcion.findData("carro_hibrido")
            self.combo_tipo_excepcion.setCurrentIndex(index if index >= 0 else 0)
        elif self.funcionario_data.get("tiene_parqueadero_exclusivo", False):
            # Exclusivo directivo
            index = self.combo_tipo_excepcion.findData("exclusivo_directivo")
            self.combo_tipo_excepcion.setCurrentIndex(index if index >= 0 else 0)
        elif self.funcionario_data.get("pico_placa_solidario", False):
            # Pico y placa solidario
            index = self.combo_tipo_excepcion.findData("pico_placa_solidario")
            self.combo_tipo_excepcion.setCurrentIndex(index if index >= 0 else 0)
        elif self.funcionario_data.get("discapacidad", False):
            # Discapacidad
            index = self.combo_tipo_excepcion.findData("discapacidad")
            self.combo_tipo_excepcion.setCurrentIndex(index if index >= 0 else 0)
        else:
            # Ninguna excepción (funcionario regular)
            self.combo_tipo_excepcion.setCurrentIndex(0)  # "-- Ninguna --"

    def guardar_cambios(self):
        """Guarda los cambios del funcionario"""
        # Obtener y validar todos los campos
        cedula = self.txt_cedula.text().strip()
        nombre = self.txt_nombre.text().strip()
        apellidos = self.txt_apellidos.text().strip()
        celular = self.txt_celular.text().strip()
        tarjeta = self.txt_tarjeta.text().strip()

        # Validar campos obligatorios
        if not cedula or not nombre or not apellidos:
            QMessageBox.warning(self, "⚠️ Validación", "Cédula, nombre y apellidos son obligatorios")
            return

        # Validar formato de cédula
        if not cedula.isdigit():
            QMessageBox.warning(self, "⚠️ Validación", "La cédula solo debe contener números")
            return

        if len(cedula) < 7 or len(cedula) > 10:
            QMessageBox.warning(
                self,
                "⚠️ Validación",
                f"La cédula debe tener entre 7 y 10 dígitos\n" f"Dígitos ingresados: {len(cedula)}",
            )
            return

        # Validar nombre
        if len(nombre) < 2:
            QMessageBox.warning(self, "⚠️ Validación", "El nombre debe tener al menos 2 caracteres")
            return

        # Validar apellidos
        if len(apellidos) < 2:
            QMessageBox.warning(self, "⚠️ Validación", "Los apellidos deben tener al menos 2 caracteres")
            return

        # Validar celular
        if celular and len(celular) != 10:
            QMessageBox.warning(
                self,
                "⚠️ Validación",
                f"El celular debe tener exactamente 10 dígitos\n" f"Dígitos ingresados: {len(celular)}",
            )
            return

        if celular and not celular.isdigit():
            QMessageBox.warning(self, "⚠️ Validación", "El celular solo debe contener números")
            return

        # Validar tarjeta (opcional pero si se ingresa debe ser válida)
        if tarjeta and len(tarjeta) < 3:
            QMessageBox.warning(self, "⚠️ Validación", "La tarjeta de proximidad debe tener al menos 3 caracteres")
            return

        # Determinar los valores de los campos según el tipo de excepción seleccionado
        tipo_excepcion = self.combo_tipo_excepcion.currentData()

        if tipo_excepcion == "carro_hibrido":
            # Carro híbrido (incentivo ambiental)
            permite_compartir = False
            pico_placa_solidario = False
            discapacidad = False
            tiene_parqueadero_exclusivo = False
            tiene_carro_hibrido = True
        elif tipo_excepcion == "exclusivo_directivo":
            # Exclusivo directivo (hasta 4 vehículos)
            permite_compartir = False
            pico_placa_solidario = False
            discapacidad = False
            tiene_parqueadero_exclusivo = True
            tiene_carro_hibrido = False
        elif tipo_excepcion == "pico_placa_solidario":
            # Pico y placa solidario
            permite_compartir = True
            pico_placa_solidario = True
            discapacidad = False
            tiene_parqueadero_exclusivo = False
            tiene_carro_hibrido = False
        elif tipo_excepcion == "discapacidad":
            # Funcionario con discapacidad
            permite_compartir = True
            pico_placa_solidario = False
            discapacidad = True
            tiene_parqueadero_exclusivo = False
            tiene_carro_hibrido = False
        else:  # "ninguna" o cualquier otro valor
            # Ninguno marcado (funcionario regular que comparte)
            permite_compartir = True
            pico_placa_solidario = False
            discapacidad = False
            tiene_parqueadero_exclusivo = False
            tiene_carro_hibrido = False

        exito, error_msg = self.funcionario_model.actualizar(
            funcionario_id=self.funcionario_data["id"],
            cedula=self.txt_cedula.text(),
            nombre=self.txt_nombre.text(),
            apellidos=self.txt_apellidos.text(),
            direccion_grupo=(
                self.combo_direccion.currentText() if self.combo_direccion.currentText() != "-- Seleccione --" else ""
            ),
            cargo=self.combo_cargo.currentText() if self.combo_cargo.currentText() != "-- Seleccione --" else "",
            celular=self.txt_celular.text(),
            tarjeta=self.txt_tarjeta.text(),
            permite_compartir=permite_compartir,
            pico_placa_solidario=pico_placa_solidario,
            discapacidad=discapacidad,
            tiene_parqueadero_exclusivo=tiene_parqueadero_exclusivo,
            tiene_carro_hibrido=tiene_carro_hibrido,
        )

        if exito:
            QMessageBox.information(self, "Éxito", "Funcionario actualizado correctamente")
            self.accept()
        else:
            if "Duplicate entry" in error_msg:
                QMessageBox.critical(
                    self, "Error", f"Ya existe un funcionario con esa cédula: {self.txt_cedula.text()}"
                )
            else:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el funcionario.\n\nError: {error_msg}")
