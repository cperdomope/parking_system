# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Vehículos del sistema de gestión de parqueadero
"""

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QComboBox,
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

from ..database.manager import DatabaseManager
from ..models.funcionario import FuncionarioModel
from ..models.vehiculo import VehiculoModel
from .modales_vehiculos import EditarVehiculoModal, EliminarVehiculoModal
from ..utils.formatters import format_numero_parqueadero


class VehiculosTab(QWidget):
    """Pestaña de gestión de vehículos"""

    # Señal que se emite cuando se crea un nuevo vehículo
    vehiculo_creado = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.funcionario_model = FuncionarioModel(self.db)
        self.vehiculo_model = VehiculoModel(self.db)
        self.vehiculos_completos = []  # Lista completa para filtrado
        self.vehiculos_filtrados = []  # Lista filtrada actual
        self.pagina_actual = 1  # Página actual de paginación
        self.filas_por_pagina = 6  # Máximo 6 filas por página
        self.ultimo_mensaje_validacion = None  # Guarda el último mensaje de validación para mostrarlo si el usuario intenta guardar
        self.setup_ui()
        self.cargar_vehiculos()
        self.cargar_combo_funcionarios()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        # Formulario de registro
        form_group = QGroupBox("Registro de Vehículo")
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(10, 10, 10, 10)

        # Primera fila: Labels e Inputs en una sola línea
        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(15)

        # Funcionario (Label + Combo)
        lbl_funcionario = QLabel("Funcionario:")
        lbl_funcionario.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        inputs_layout.addWidget(lbl_funcionario)

        self.combo_funcionario = QComboBox()
        self.combo_funcionario.setFixedWidth(280)
        self.combo_funcionario.setFixedHeight(40)
        self.combo_funcionario.setStyleSheet(
            """
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 10px;
            }
        """
        )
        inputs_layout.addWidget(self.combo_funcionario)

        # Tipo de Vehículo (Label + Combo)
        lbl_tipo = QLabel("Tipo de Vehículo:")
        lbl_tipo.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        inputs_layout.addWidget(lbl_tipo)

        self.combo_tipo_vehiculo = QComboBox()
        self.combo_tipo_vehiculo.addItems(["Carro", "Moto", "Bicicleta"])
        self.combo_tipo_vehiculo.setFixedWidth(180)
        self.combo_tipo_vehiculo.setFixedHeight(40)
        self.combo_tipo_vehiculo.setStyleSheet(
            """
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #7f8c8d;
                margin-right: 10px;
            }
        """
        )
        inputs_layout.addWidget(self.combo_tipo_vehiculo)

        # Placa (Label + Input)
        lbl_placa = QLabel("Placa:")
        lbl_placa.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        inputs_layout.addWidget(lbl_placa)

        self.txt_placa = QLineEdit()
        self.txt_placa.setPlaceholderText("Ej: ABC123")
        self.txt_placa.setFixedWidth(150)
        self.txt_placa.setFixedHeight(40)
        self.txt_placa.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """
        )
        inputs_layout.addWidget(self.txt_placa)

        # Botón Guardar en la misma fila
        self.btn_guardar_vehiculo = QPushButton("💾 Guardar")
        self.btn_guardar_vehiculo.clicked.connect(self.guardar_vehiculo)
        self.btn_guardar_vehiculo.setProperty("class", "success")
        self.btn_guardar_vehiculo.setFixedHeight(40)
        self.btn_guardar_vehiculo.setFixedWidth(150)
        self.btn_guardar_vehiculo.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """
        )
        inputs_layout.addWidget(self.btn_guardar_vehiculo)

        inputs_layout.addStretch()
        form_layout.addLayout(inputs_layout)

        # Conectar eventos
        self.txt_placa.textChanged.connect(self.validar_en_tiempo_real)
        self.combo_funcionario.currentIndexChanged.connect(self.validar_en_tiempo_real)
        self.combo_tipo_vehiculo.currentTextChanged.connect(self.validar_en_tiempo_real)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Tabla de vehículos con diseño profesional
        tabla_group = QGroupBox("Lista de Vehículos")
        tabla_layout = QVBoxLayout()
        tabla_layout.setSpacing(5)
        tabla_layout.setContentsMargins(10, 5, 10, 5)

        # Buscador de placas
        buscar_layout = QHBoxLayout()
        buscar_layout.setSpacing(10)
        buscar_layout.setContentsMargins(0, 0, 0, 5)

        lbl_buscar = QLabel("🔍 Buscar por placa:")
        lbl_buscar.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        buscar_layout.addWidget(lbl_buscar)

        self.txt_buscar_placa = QLineEdit()
        self.txt_buscar_placa.setPlaceholderText("Ingrese placa para filtrar...")
        self.txt_buscar_placa.setFixedWidth(200)
        self.txt_buscar_placa.setFixedHeight(35)
        self.txt_buscar_placa.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 5px 10px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }
        """
        )
        self.txt_buscar_placa.textChanged.connect(self.filtrar_por_placa)
        buscar_layout.addWidget(self.txt_buscar_placa)

        btn_limpiar = QPushButton("🗑️ Limpiar")
        btn_limpiar.setFixedHeight(35)
        btn_limpiar.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #5d6d7e;
            }
        """
        )
        btn_limpiar.clicked.connect(self.limpiar_filtro)
        buscar_layout.addWidget(btn_limpiar)

        buscar_layout.addStretch()
        tabla_layout.addLayout(buscar_layout)

        self.tabla_vehiculos = QTableWidget()
        self.tabla_vehiculos.setColumnCount(7)
        self.tabla_vehiculos.setHorizontalHeaderLabels(
            ["Funcionario", "Tipo", "Placa", "Último Dígito", "Circulación", "Parqueadero", "Acciones"]
        )

        # Configuración visual profesional
        self.tabla_vehiculos.setAlternatingRowColors(True)
        self.tabla_vehiculos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_vehiculos.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_vehiculos.verticalHeader().setVisible(False)

        # Establecer anchos de columna fijos para distribución equitativa
        self.tabla_vehiculos.setColumnWidth(0, 200)  # Funcionario
        self.tabla_vehiculos.setColumnWidth(1, 100)  # Tipo
        self.tabla_vehiculos.setColumnWidth(2, 100)  # Placa
        self.tabla_vehiculos.setColumnWidth(3, 120)  # Último Dígito
        self.tabla_vehiculos.setColumnWidth(4, 110)  # Circulación
        self.tabla_vehiculos.setColumnWidth(5, 130)  # Parqueadero
        self.tabla_vehiculos.setColumnWidth(6, 240)  # Acciones

        # Configurar altura de filas fija
        altura_fila = 50
        self.tabla_vehiculos.verticalHeader().setDefaultSectionSize(altura_fila)

        # Calcular altura exacta para 6 filas + encabezado (sin scroll vertical)
        # Aumentar margen para asegurar que la última fila se vea completa
        altura_encabezado = 35  # Altura fija del encabezado
        altura_total_tabla = (altura_fila * 6) + altura_encabezado + 10  # +10 para bordes y margen adicional
        self.tabla_vehiculos.setMinimumHeight(altura_total_tabla)
        self.tabla_vehiculos.setMaximumHeight(altura_total_tabla)

        # Deshabilitar scroll vertical completamente para forzar visualización exacta de 6 filas
        from PyQt5.QtCore import Qt as QtCore
        self.tabla_vehiculos.setVerticalScrollBarPolicy(QtCore.ScrollBarAlwaysOff)
        self.tabla_vehiculos.setHorizontalScrollBarPolicy(QtCore.ScrollBarAsNeeded)

        # Estilo de encabezados
        self.tabla_vehiculos.horizontalHeader().setStyleSheet(
            """
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-right: 1px solid #34495e;
                text-align: center;
            }
        """
        )

        # Estilo general de la tabla
        self.tabla_vehiculos.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                gridline-color: #bdc3c7;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #e8f6f3;
                color: #2c3e50;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QTableWidget::item:alternate {
                background-color: #f8f9fa;
            }
        """
        )

        tabla_layout.addWidget(self.tabla_vehiculos)

        # Controles de paginación
        paginacion_layout = QHBoxLayout()
        paginacion_layout.setSpacing(8)
        paginacion_layout.setContentsMargins(0, 5, 0, 0)

        # Botón Primera Página
        self.btn_primera_pagina = QPushButton("⏮️ Primera")
        self.btn_primera_pagina.setFixedHeight(35)
        self.btn_primera_pagina.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.btn_primera_pagina.clicked.connect(self.ir_primera_pagina)
        paginacion_layout.addWidget(self.btn_primera_pagina)

        # Botón Página Anterior
        self.btn_pagina_anterior = QPushButton("◀️ Anterior")
        self.btn_pagina_anterior.setFixedHeight(35)
        self.btn_pagina_anterior.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.btn_pagina_anterior.clicked.connect(self.ir_pagina_anterior)
        paginacion_layout.addWidget(self.btn_pagina_anterior)

        # Label de información de página
        self.lbl_info_pagina = QLabel("Página 1 de 1")
        self.lbl_info_pagina.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        self.lbl_info_pagina.setAlignment(Qt.AlignCenter)
        paginacion_layout.addWidget(self.lbl_info_pagina)

        # Botón Página Siguiente
        self.btn_pagina_siguiente = QPushButton("Siguiente ▶️")
        self.btn_pagina_siguiente.setFixedHeight(35)
        self.btn_pagina_siguiente.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.btn_pagina_siguiente.clicked.connect(self.ir_pagina_siguiente)
        paginacion_layout.addWidget(self.btn_pagina_siguiente)

        # Botón Última Página
        self.btn_ultima_pagina = QPushButton("Última ⏭️")
        self.btn_ultima_pagina.setFixedHeight(35)
        self.btn_ultima_pagina.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.btn_ultima_pagina.clicked.connect(self.ir_ultima_pagina)
        paginacion_layout.addWidget(self.btn_ultima_pagina)

        paginacion_layout.addStretch()

        # Label de total de registros
        self.lbl_total_registros = QLabel("Total: 0 vehículos")
        self.lbl_total_registros.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 12px;")
        paginacion_layout.addWidget(self.lbl_total_registros)

        tabla_layout.addLayout(paginacion_layout)
        tabla_group.setLayout(tabla_layout)
        layout.addWidget(tabla_group)

        self.setLayout(layout)

    def cargar_combo_funcionarios(self):
        """Carga el combo de funcionarios que aún tienen cupo disponible para registrar vehículos"""
        from ..config.settings import CARGOS_DIRECTIVOS

        funcionarios = self.funcionario_model.obtener_todos()

        self.combo_funcionario.clear()
        self.combo_funcionario.addItem("-- Seleccione --", None)

        for func in funcionarios:
            funcionario_id = func["id"]
            cargo = func.get("cargo", "")

            # Determinar si es directivo
            es_directivo = cargo in CARGOS_DIRECTIVOS

            # Obtener vehículos registrados del funcionario
            vehiculos = self.vehiculo_model.obtener_por_funcionario(funcionario_id)
            cant_vehiculos = len(vehiculos)

            # Contar vehículos por tipo
            cant_carros = sum(1 for v in vehiculos if v.get('tipo_vehiculo') == 'Carro')
            cant_motos = sum(1 for v in vehiculos if v.get('tipo_vehiculo') == 'Moto')
            cant_bicicletas = sum(1 for v in vehiculos if v.get('tipo_vehiculo') == 'Bicicleta')

            # Lógica de filtrado:
            # - Directivos: SIEMPRE aparecen (vehículos ilimitados)
            # - Regulares: Solo si NO han completado alguna de las 3 combinaciones válidas
            mostrar_funcionario = False

            if es_directivo:
                # Directivos siempre pueden registrar más vehículos
                mostrar_funcionario = True
            else:
                # Regulares: verificar si han completado alguna de las 3 combinaciones válidas:
                # 1. 1 Carro + 1 Moto + 1 Bicicleta
                # 2. 2 Carros + 1 Bicicleta
                # 3. 2 Carros + 1 Moto

                combinacion1_completa = (cant_carros == 1 and cant_motos == 1 and cant_bicicletas == 1)
                combinacion2_completa = (cant_carros == 2 and cant_bicicletas == 1 and cant_motos == 0)
                combinacion3_completa = (cant_carros == 2 and cant_motos == 1 and cant_bicicletas == 0)

                # Solo ocultar si completó alguna de las 3 combinaciones
                if not (combinacion1_completa or combinacion2_completa or combinacion3_completa):
                    mostrar_funcionario = True

            # Agregar al combobox solo si cumple la condición
            if mostrar_funcionario:
                texto = f"{func['cedula']} - {func['nombre']} {func['apellidos']}"
                self.combo_funcionario.addItem(texto, func["id"])

    def guardar_vehiculo(self):
        """Guarda un nuevo vehículo con validaciones de reglas de negocio"""
        if self.combo_funcionario.currentData() is None:
            QMessageBox.warning(
                self,
                "🚗 Seleccionar Funcionario",
                "🚫 Debe seleccionar un funcionario del listado\n\n"
                "💡 Solución: Escoja un funcionario del combo desplegable",
            )
            return

        tipo_vehiculo = self.combo_tipo_vehiculo.currentText()
        placa = self.txt_placa.text().strip()

        # Validación de placa para carros
        if tipo_vehiculo == "Carro" and not placa:
            QMessageBox.warning(
                self,
                "🚗 Placa Requerida",
                "🚫 La placa es obligatoria para carros\n\n"
                "📝 Formato válido: ABC123, XYZ789\n"
                "💡 La placa determina el tipo de circulación (PAR/IMPAR)",
            )
            return

        # Intentar crear el vehículo con validaciones
        exito, mensaje = self.vehiculo_model.crear(
            funcionario_id=self.combo_funcionario.currentData(), tipo_vehiculo=tipo_vehiculo, placa=placa
        )

        if exito:
            QMessageBox.information(self, "✅ Vehículo Registrado", mensaje)
            self.txt_placa.clear()
            self.combo_funcionario.setCurrentIndex(0)
            self.cargar_vehiculos()
            # Recargar combobox para filtrar funcionarios que completaron su cupo
            self.cargar_combo_funcionarios()
            # Emitir señal para notificar a otras pestañas
            self.vehiculo_creado.emit()
        else:
            # Los mensajes ya vienen formateados desde el modelo
            QMessageBox.warning(self, "🚫 Validación", mensaje)

    def cargar_vehiculos(self):
        """Carga todos los vehículos en la tabla con botones de acción"""
        query = """
            SELECT
                v.id,
                CONCAT(f.nombre, ' ', f.apellidos) as funcionario,
                v.tipo_vehiculo,
                v.placa,
                v.ultimo_digito,
                v.tipo_circulacion,
                p.numero_parqueadero
            FROM vehiculos v
            JOIN funcionarios f ON v.funcionario_id = f.id
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            LEFT JOIN parqueaderos p ON a.parqueadero_id = p.id
            WHERE v.activo = TRUE
            ORDER BY f.apellidos, f.nombre
        """

        vehiculos = self.db.fetch_all(query)

        # Guardar lista completa para filtrado
        self.vehiculos_completos = vehiculos

        # Mostrar todos los vehículos
        self.mostrar_vehiculos(vehiculos)

    def mostrar_vehiculos(self, vehiculos):
        """Muestra los vehículos en la tabla con paginación"""
        # Guardar lista filtrada
        self.vehiculos_filtrados = vehiculos

        # Calcular paginación
        total_vehiculos = len(vehiculos)
        total_paginas = (total_vehiculos + self.filas_por_pagina - 1) // self.filas_por_pagina if total_vehiculos > 0 else 1

        # Ajustar página actual si es necesaria
        if self.pagina_actual > total_paginas:
            self.pagina_actual = total_paginas if total_paginas > 0 else 1

        # Calcular índices de vehículos a mostrar
        inicio = (self.pagina_actual - 1) * self.filas_por_pagina
        fin = min(inicio + self.filas_por_pagina, total_vehiculos)

        # Obtener vehículos de la página actual
        vehiculos_pagina = vehiculos[inicio:fin]

        # Actualizar tabla
        self.tabla_vehiculos.setRowCount(len(vehiculos_pagina))

        for i, vehiculo in enumerate(vehiculos_pagina):
            # Crear items con alineación centrada
            funcionario_item = QTableWidgetItem(vehiculo.get("funcionario", ""))
            funcionario_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_vehiculos.setItem(i, 0, funcionario_item)

            tipo_item = QTableWidgetItem(vehiculo.get("tipo_vehiculo", ""))
            tipo_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_vehiculos.setItem(i, 1, tipo_item)

            placa_item = QTableWidgetItem(vehiculo.get("placa", ""))
            placa_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_vehiculos.setItem(i, 2, placa_item)

            digito_item = QTableWidgetItem(vehiculo.get("ultimo_digito", ""))
            digito_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_vehiculos.setItem(i, 3, digito_item)

            # Formato de circulación con color
            circulacion_item = QTableWidgetItem(vehiculo.get("tipo_circulacion", ""))
            circulacion_item.setTextAlignment(Qt.AlignCenter)
            if vehiculo.get("tipo_circulacion") == "PAR":
                circulacion_item.setBackground(QBrush(QColor("#e8f5e8")))
                circulacion_item.setForeground(QBrush(QColor("#2e7d32")))
            else:
                circulacion_item.setBackground(QBrush(QColor("#fff3e0")))
                circulacion_item.setForeground(QBrush(QColor("#f57c00")))
            self.tabla_vehiculos.setItem(i, 4, circulacion_item)

            # Información del parqueadero
            parqueadero_info = (
                str(vehiculo.get("numero_parqueadero", "")) if vehiculo.get("numero_parqueadero") else "Sin asignar"
            )
            if vehiculo.get("numero_parqueadero"):
                parqueadero_info = f"{format_numero_parqueadero(vehiculo.get('numero_parqueadero'))}"
            parqueadero_item = QTableWidgetItem(parqueadero_info)
            parqueadero_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_vehiculos.setItem(i, 5, parqueadero_item)

            # Botones de acción (Editar, Ver, Eliminar) - Solo íconos
            btn_widget_acciones = QWidget()
            btn_layout_acciones = QHBoxLayout()
            btn_layout_acciones.setSpacing(3)
            btn_layout_acciones.setContentsMargins(2, 2, 2, 2)

            # Botón Editar (solo ícono sin fondo)
            btn_editar = QPushButton("✏️")
            btn_editar.setFixedSize(28, 28)
            btn_editar.setToolTip("Editar vehículo")
            btn_editar.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 18px;
                    padding: 0px;
                    color: #3498db;
                }
                QPushButton:hover {
                    background-color: rgba(52, 152, 219, 0.15);
                    border-radius: 3px;
                    color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: rgba(52, 152, 219, 0.3);
                    border-radius: 3px;
                    color: #21618c;
                }
            """
            )
            btn_editar.clicked.connect(lambda checked, vid=vehiculo["id"]: self.abrir_modal_editar(vid))

            # Botón Ver (solo ícono sin fondo)
            btn_ver = QPushButton("👁️")
            btn_ver.setFixedSize(28, 28)
            btn_ver.setToolTip("Ver detalles del vehículo")
            btn_ver.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 16px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(39, 174, 96, 0.1);
                    border-radius: 3px;
                }
                QPushButton:pressed {
                    background-color: rgba(39, 174, 96, 0.2);
                    border-radius: 3px;
                }
            """
            )
            btn_ver.clicked.connect(lambda checked, vid=vehiculo["id"]: self.abrir_modal_ver(vid))

            # Botón Eliminar (solo ícono sin fondo)
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setFixedSize(28, 28)
            btn_eliminar.setToolTip("Eliminar vehículo")
            btn_eliminar.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 16px;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: rgba(231, 76, 60, 0.1);
                    border-radius: 3px;
                }
                QPushButton:pressed {
                    background-color: rgba(231, 76, 60, 0.2);
                    border-radius: 3px;
                }
            """
            )
            btn_eliminar.clicked.connect(lambda checked, vid=vehiculo["id"]: self.abrir_modal_eliminar(vid))

            btn_layout_acciones.addWidget(btn_editar)
            btn_layout_acciones.addSpacing(2)
            btn_layout_acciones.addWidget(btn_ver)
            btn_layout_acciones.addSpacing(2)
            btn_layout_acciones.addWidget(btn_eliminar)
            btn_layout_acciones.addStretch()

            btn_widget_acciones.setLayout(btn_layout_acciones)
            self.tabla_vehiculos.setCellWidget(i, 6, btn_widget_acciones)

        # Actualizar controles de paginación
        self.actualizar_controles_paginacion(total_vehiculos, total_paginas)

    def actualizar_controles_paginacion(self, total_vehiculos, total_paginas):
        """Actualiza los controles de paginación"""
        # Actualizar labels
        self.lbl_info_pagina.setText(f"Página {self.pagina_actual} de {total_paginas}")
        self.lbl_total_registros.setText(f"Total: {total_vehiculos} vehículos")

        # Habilitar/deshabilitar botones
        self.btn_primera_pagina.setEnabled(self.pagina_actual > 1)
        self.btn_pagina_anterior.setEnabled(self.pagina_actual > 1)
        self.btn_pagina_siguiente.setEnabled(self.pagina_actual < total_paginas)
        self.btn_ultima_pagina.setEnabled(self.pagina_actual < total_paginas)

    def ir_primera_pagina(self):
        """Ir a la primera página"""
        self.pagina_actual = 1
        self.mostrar_vehiculos(self.vehiculos_filtrados)

    def ir_pagina_anterior(self):
        """Ir a la página anterior"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.mostrar_vehiculos(self.vehiculos_filtrados)

    def ir_pagina_siguiente(self):
        """Ir a la página siguiente"""
        total_paginas = (len(self.vehiculos_filtrados) + self.filas_por_pagina - 1) // self.filas_por_pagina
        if self.pagina_actual < total_paginas:
            self.pagina_actual += 1
            self.mostrar_vehiculos(self.vehiculos_filtrados)

    def ir_ultima_pagina(self):
        """Ir a la última página"""
        total_paginas = (len(self.vehiculos_filtrados) + self.filas_por_pagina - 1) // self.filas_por_pagina
        self.pagina_actual = total_paginas if total_paginas > 0 else 1
        self.mostrar_vehiculos(self.vehiculos_filtrados)

    def actualizar_combo_funcionarios(self):
        """Actualiza el combo de funcionarios cuando se crea uno nuevo"""
        self.cargar_combo_funcionarios()

    def actualizar_vehiculos(self):
        """Actualiza la tabla de vehículos"""
        self.cargar_vehiculos()

    def validar_en_tiempo_real(self):
        """Valida el vehículo en tiempo real con retroalimentación visual por color del botón"""
        # Si no hay funcionario seleccionado, botón gris neutral
        if self.combo_funcionario.currentData() is None:
            self.btn_guardar_vehiculo.setEnabled(False)
            self.btn_guardar_vehiculo.setText("💾 Guardar")
            self.btn_guardar_vehiculo.setStyleSheet(
                """
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                    border-radius: 8px;
                }
            """
            )
            return

        funcionario_id = self.combo_funcionario.currentData()
        tipo_vehiculo = self.combo_tipo_vehiculo.currentText()
        placa = self.txt_placa.text().strip().upper()

        # Para carros, validar solo si la placa tiene al menos 5 caracteres (formato mínimo: ABC12)
        if tipo_vehiculo == "Carro" and placa and len(placa) < 5:
            # Placa incompleta, botón amarillo indicando que falta información
            self.btn_guardar_vehiculo.setEnabled(True)
            self.btn_guardar_vehiculo.setText("⚠️ Completar placa")
            self.btn_guardar_vehiculo.setStyleSheet(
                """
                QPushButton {
                    background-color: #f39c12;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #e67e22;
                }
            """
            )
            return

        # Solo validar si hay datos suficientes
        if tipo_vehiculo and (tipo_vehiculo != "Carro" or placa):
            es_valido, mensaje = self.vehiculo_model.validar_vehiculo_antes_registro(
                funcionario_id, tipo_vehiculo, placa
            )

            if not es_valido:
                # Guardar el mensaje de error para mostrarlo cuando intente guardar
                self.ultimo_mensaje_validacion = mensaje

                # Botón ROJO - No válido según reglas de negocio
                self.btn_guardar_vehiculo.setEnabled(False)
                self.btn_guardar_vehiculo.setText("🚫 No permitido")
                self.btn_guardar_vehiculo.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        font-weight: bold;
                        font-size: 14px;
                        border: none;
                        border-radius: 8px;
                    }
                """
                )
            else:
                # Limpiar mensaje de error guardado
                self.ultimo_mensaje_validacion = None

                # Botón VERDE - Válido y listo para guardar
                self.btn_guardar_vehiculo.setEnabled(True)
                self.btn_guardar_vehiculo.setText("✅ Guardar")
                self.btn_guardar_vehiculo.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        font-weight: bold;
                        font-size: 14px;
                        border: none;
                        border-radius: 8px;
                    }
                    QPushButton:hover {
                        background-color: #229954;
                    }
                    QPushButton:pressed {
                        background-color: #1e8449;
                    }
                """
                )
        else:
            # Botón gris - Esperando selección de tipo de vehículo
            self.ultimo_mensaje_validacion = None
            self.btn_guardar_vehiculo.setEnabled(False)
            self.btn_guardar_vehiculo.setText("💾 Seleccione tipo")
            self.btn_guardar_vehiculo.setStyleSheet(
                """
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                    border-radius: 8px;
                }
            """
            )

    def mostrar_mensaje_validacion_fallida(self, mensaje_base: str, placa: str, tipo_vehiculo: str, funcionario_id: int):
        """Muestra un mensaje breve y preciso explicando por qué el registro está bloqueado"""
        # Obtener vehículos existentes
        vehiculos = self.vehiculo_model.obtener_por_funcionario(funcionario_id)
        cant_vehiculos = len(vehiculos)

        # Analizar placa para determinar tipo de circulación
        ultimo_digito = ""
        tipo_circulacion = "N/A"

        if tipo_vehiculo == "Carro" and placa:
            for char in reversed(placa):
                if char.isdigit():
                    ultimo_digito = char
                    break

            if ultimo_digito:
                digito_int = int(ultimo_digito)
                tipo_circulacion = "PAR" if digito_int % 2 == 0 else "IMPAR"

        # Construir mensaje breve y preciso
        titulo = "🚫 Registro No Permitido"

        # Determinar razón específica
        razon = ""

        if cant_vehiculos >= 3:
            razon = f"<b>Límite alcanzado:</b> Tiene {cant_vehiculos} vehículos registrados.<br>Funcionarios regulares: máximo 3 vehículos según combinaciones válidas."

        elif tipo_vehiculo == "Carro":
            tiene_carro = any(v.get('tipo_vehiculo') == 'Carro' for v in vehiculos)

            if tiene_carro:
                vehiculo_carro = next(v for v in vehiculos if v.get('tipo_vehiculo') == 'Carro')
                placa_existente = vehiculo_carro.get('placa', 'N/A')
                circulacion_existente = vehiculo_carro.get('tipo_circulacion', 'N/A')

                razon = f"""
<b>Ya tiene un carro registrado:</b> Placa {placa_existente} ({circulacion_existente})<br>
<b>Restricción:</b> Funcionarios regulares solo pueden tener 1 carro.<br>
<b>Puede registrar:</b> Moto o Bicicleta.
                """.strip()

        elif "placa ya registrada" in mensaje_base.lower() or "duplicada" in mensaje_base.lower():
            razon = f"<b>Placa duplicada:</b> La placa {placa} ya está registrada en el sistema."

        else:
            razon = mensaje_base

        mensaje_html = f"""
<div style='font-family: Arial; color: #2c3e50; padding: 10px;'>
    <p style='font-size: 13px; margin-bottom: 10px;'>
        <b>🚗 Vehículo:</b> {tipo_vehiculo} {f'- Placa {placa} ({tipo_circulacion})' if tipo_vehiculo == "Carro" and placa else ''}
    </p>

    <hr style='border: 1px solid #e74c3c; margin: 10px 0;'>

    <p style='font-size: 12px; line-height: 1.6;'>
        {razon}
    </p>
</div>
        """.strip()

        # Mostrar mensaje compacto
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(mensaje_html)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)

        # Estilo compacto
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #2c3e50;
                font-size: 11px;
                min-width: 400px;
                max-width: 450px;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        msg_box.exec_()

    def abrir_modal_editar(self, vehiculo_id: int):
        """Abre el modal para editar un vehículo

        Args:
            vehiculo_id (int): ID del vehículo a editar
        """
        try:
            modal = EditarVehiculoModal(vehiculo_id, self.vehiculo_model, self.funcionario_model, self)

            # Conectar señal para actualizar tabla cuando se edite
            modal.vehiculo_actualizado.connect(self.cargar_vehiculos)
            modal.vehiculo_actualizado.connect(self.vehiculo_creado.emit)  # Para sincronizar otros módulos
            modal.vehiculo_actualizado.connect(self.cargar_combo_funcionarios)  # Actualizar combo

            modal.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir el modal de edición: {str(e)}")

    def abrir_modal_ver(self, vehiculo_id: int):
        """Abre el modal para ver los detalles de un vehículo

        Args:
            vehiculo_id (int): ID del vehículo a visualizar
        """
        try:
            from .modales_vehiculos import VerVehiculoModal

            modal = VerVehiculoModal(vehiculo_id, self.vehiculo_model, self.funcionario_model, self)
            modal.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir el modal de visualización: {str(e)}")

    def abrir_modal_eliminar(self, vehiculo_id: int):
        """Abre el modal para eliminar un vehículo

        Args:
            vehiculo_id (int): ID del vehículo a eliminar
        """
        try:
            modal = EliminarVehiculoModal(vehiculo_id, self.vehiculo_model, self)

            # Conectar señal para actualizar tabla cuando se elimine
            modal.vehiculo_eliminado.connect(self.cargar_vehiculos)
            modal.vehiculo_eliminado.connect(self.vehiculo_creado.emit)  # Para sincronizar otros módulos
            modal.vehiculo_eliminado.connect(self.cargar_combo_funcionarios)  # Actualizar combo

            modal.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al abrir el modal de eliminación: {str(e)}")

    def obtener_vehiculo_seleccionado(self) -> int:
        """Obtiene el ID del vehículo seleccionado en la tabla

        Returns:
            int: ID del vehículo seleccionado o None si no hay selección
        """
        fila_actual = self.tabla_vehiculos.currentRow()
        if fila_actual >= 0:
            # Obtener la placa de la fila seleccionada
            placa_item = self.tabla_vehiculos.item(fila_actual, 2)
            if placa_item:
                placa = placa_item.text()
                # Buscar el vehículo por placa para obtener su ID
                vehiculos = self.vehiculo_model.obtener_todos()
                for vehiculo in vehiculos:
                    if vehiculo.get("placa") == placa:
                        return vehiculo.get("id")
        return None

    def filtrar_por_placa(self):
        """Filtra los vehículos por placa en tiempo real"""
        texto_busqueda = self.txt_buscar_placa.text().strip().upper()

        # Resetear a la primera página al filtrar
        self.pagina_actual = 1

        if not texto_busqueda:
            # Si no hay texto, mostrar todos los vehículos
            self.mostrar_vehiculos(self.vehiculos_completos)
            return

        # Filtrar vehículos que contengan el texto en la placa
        vehiculos_filtrados = [
            vehiculo
            for vehiculo in self.vehiculos_completos
            if texto_busqueda in str(vehiculo.get("placa", "")).upper()
        ]

        self.mostrar_vehiculos(vehiculos_filtrados)

    def limpiar_filtro(self):
        """Limpia el filtro de búsqueda"""
        self.txt_buscar_placa.clear()
        # Resetear a la primera página al limpiar
        self.pagina_actual = 1
        self.mostrar_vehiculos(self.vehiculos_completos)
