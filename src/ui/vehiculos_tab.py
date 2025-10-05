# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Vehículos del sistema de gestión de parqueadero
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QBrush

from ..database.manager import DatabaseManager
from ..models.funcionario import FuncionarioModel
from ..models.vehiculo import VehiculoModel
from .modales_vehiculos import EditarVehiculoModal, EliminarVehiculoModal


class VehiculosTab(QWidget):
    """Pestaña de gestión de vehículos"""

    # Señal que se emite cuando se crea un nuevo vehículo
    vehiculo_creado = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.funcionario_model = FuncionarioModel(self.db)
        self.vehiculo_model = VehiculoModel(self.db)
        self.setup_ui()
        self.cargar_vehiculos()
        self.cargar_combo_funcionarios()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout()

        # Formulario de registro
        form_group = QGroupBox("Registro de Vehículo")
        form_layout = QGridLayout()
        form_layout.setHorizontalSpacing(10)  # Reducir espaciado horizontal entre columnas

        form_layout.addWidget(QLabel("Funcionario:"), 0, 0)
        self.combo_funcionario = QComboBox()
        self.combo_funcionario.setMinimumWidth(280)
        form_layout.addWidget(self.combo_funcionario, 0, 1)

        form_layout.addWidget(QLabel("Tipo de Vehículo:"), 1, 0)
        self.combo_tipo_vehiculo = QComboBox()
        self.combo_tipo_vehiculo.addItems(["Carro", "Moto", "Bicicleta"])
        form_layout.addWidget(self.combo_tipo_vehiculo, 1, 1)

        form_layout.addWidget(QLabel("Placa:"), 2, 0)
        self.txt_placa = QLineEdit()
        self.txt_placa.setPlaceholderText("Ej: ABC123")
        self.txt_placa.setMaximumWidth(150)
        form_layout.addWidget(self.txt_placa, 2, 1)

        # Label informativo de pico y placa
        self.lbl_info_pico = QLabel("")
        self.lbl_info_pico.setStyleSheet("font-weight: bold; color: #2196F3;")
        form_layout.addWidget(self.lbl_info_pico, 3, 0, 1, 4)

        # Label de sugerencias de vehículos
        self.lbl_sugerencias = QLabel("")
        self.lbl_sugerencias.setStyleSheet("font-size: 11px; color: #666; background-color: #f5f5f5; padding: 8px; border-radius: 4px;")
        self.lbl_sugerencias.setWordWrap(True)
        form_layout.addWidget(self.lbl_sugerencias, 4, 0, 1, 4)

        # Conectar eventos
        self.txt_placa.textChanged.connect(self.actualizar_info_pico_placa)
        self.txt_placa.textChanged.connect(self.validar_en_tiempo_real)
        self.combo_funcionario.currentIndexChanged.connect(self.mostrar_sugerencias_vehiculo)
        self.combo_tipo_vehiculo.currentTextChanged.connect(self.validar_en_tiempo_real)

        # Botón Guardar (columna derecha, alineado con la placa)
        self.btn_guardar_vehiculo = QPushButton("Guardar")
        self.btn_guardar_vehiculo.clicked.connect(self.guardar_vehiculo)
        self.btn_guardar_vehiculo.setProperty("class", "success")
        self.btn_guardar_vehiculo.setMinimumHeight(40)
        form_layout.addWidget(self.btn_guardar_vehiculo, 2, 2, 1, 2)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Tabla de vehículos con diseño profesional
        tabla_group = QGroupBox("Lista de Vehículos")
        tabla_layout = QVBoxLayout()

        self.tabla_vehiculos = QTableWidget()
        self.tabla_vehiculos.setColumnCount(7)
        self.tabla_vehiculos.setHorizontalHeaderLabels([
            "Funcionario", "Tipo", "Placa", "Último Dígito", "Circulación", "Parqueadero", "Acciones"
        ])

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
        self.tabla_vehiculos.verticalHeader().setDefaultSectionSize(58)

        # Estilo de encabezados
        self.tabla_vehiculos.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-right: 1px solid #34495e;
                text-align: center;
            }
        """)

        # Estilo general de la tabla
        self.tabla_vehiculos.setStyleSheet("""
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
        """)

        tabla_layout.addWidget(self.tabla_vehiculos)
        tabla_group.setLayout(tabla_layout)
        layout.addWidget(tabla_group)

        self.setLayout(layout)

    def cargar_combo_funcionarios(self):
        """Carga el combo de funcionarios"""
        funcionarios = self.funcionario_model.obtener_todos()

        self.combo_funcionario.clear()
        self.combo_funcionario.addItem("-- Seleccione --", None)

        for func in funcionarios:
            texto = f"{func['cedula']} - {func['nombre']} {func['apellidos']}"
            self.combo_funcionario.addItem(texto, func['id'])

    def guardar_vehiculo(self):
        """Guarda un nuevo vehículo con validaciones de reglas de negocio"""
        if self.combo_funcionario.currentData() is None:
            QMessageBox.warning(self, "🚗 Seleccionar Funcionario",
                              "🚫 Debe seleccionar un funcionario del listado\n\n"
                              "💡 Solución: Escoja un funcionario del combo desplegable")
            return

        tipo_vehiculo = self.combo_tipo_vehiculo.currentText()
        placa = self.txt_placa.text().strip()

        # Validación de placa para carros
        if tipo_vehiculo == "Carro" and not placa:
            QMessageBox.warning(self, "🚗 Placa Requerida",
                              "🚫 La placa es obligatoria para carros\n\n"
                              "📝 Formato válido: ABC123, XYZ789\n"
                              "💡 La placa determina el tipo de circulación (PAR/IMPAR)")
            return

        # Intentar crear el vehículo con validaciones
        exito, mensaje = self.vehiculo_model.crear(
            funcionario_id=self.combo_funcionario.currentData(),
            tipo_vehiculo=tipo_vehiculo,
            placa=placa
        )

        if exito:
            QMessageBox.information(self, "✅ Vehículo Registrado", mensaje)
            self.txt_placa.clear()
            self.lbl_info_pico.clear()
            self.lbl_sugerencias.clear()
            self.cargar_vehiculos()
            # Emitir señal para notificar a otras pestañas
            self.vehiculo_creado.emit()
            # Actualizar sugerencias después del registro exitoso
            self.mostrar_sugerencias_vehiculo()
        else:
            # Los mensajes ya vienen formateados desde el modelo
            QMessageBox.warning(self, "🚫 Validación", mensaje)

    def actualizar_info_pico_placa(self):
        """Actualiza la información de pico y placa según la placa ingresada"""
        placa = self.txt_placa.text()

        if placa and self.combo_tipo_vehiculo.currentText() == "Carro":
            ultimo_digito = placa[-1] if placa else ""

            if ultimo_digito.isdigit() or ultimo_digito == "0":
                if ultimo_digito in "12345":
                    self.lbl_info_pico.setText(f"ℹ️ Placa terminada en {ultimo_digito}: Circula días IMPARES (Tipo: IMPAR)")
                    self.lbl_info_pico.setStyleSheet("font-weight: bold; color: #FF9800;")
                else:
                    self.lbl_info_pico.setText(f"ℹ️ Placa terminada en {ultimo_digito}: Circula días PARES (Tipo: PAR)")
                    self.lbl_info_pico.setStyleSheet("font-weight: bold; color: #2196F3;")
        else:
            self.lbl_info_pico.clear()

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

        self.tabla_vehiculos.setRowCount(len(vehiculos))

        for i, vehiculo in enumerate(vehiculos):
            # Crear items con alineación centrada
            funcionario_item = QTableWidgetItem(vehiculo.get('funcionario', ''))
            funcionario_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter
            self.tabla_vehiculos.setItem(i, 0, funcionario_item)

            tipo_item = QTableWidgetItem(vehiculo.get('tipo_vehiculo', ''))
            tipo_item.setTextAlignment(0x0004 | 0x0080)
            self.tabla_vehiculos.setItem(i, 1, tipo_item)

            placa_item = QTableWidgetItem(vehiculo.get('placa', ''))
            placa_item.setTextAlignment(0x0004 | 0x0080)
            self.tabla_vehiculos.setItem(i, 2, placa_item)

            digito_item = QTableWidgetItem(vehiculo.get('ultimo_digito', ''))
            digito_item.setTextAlignment(0x0004 | 0x0080)
            self.tabla_vehiculos.setItem(i, 3, digito_item)

            # Formato de circulación con color
            circulacion_item = QTableWidgetItem(vehiculo.get('tipo_circulacion', ''))
            circulacion_item.setTextAlignment(0x0004 | 0x0080)
            if vehiculo.get('tipo_circulacion') == 'PAR':
                circulacion_item.setBackground(QBrush(QColor("#e8f5e8")))
                circulacion_item.setForeground(QBrush(QColor("#2e7d32")))
            else:
                circulacion_item.setBackground(QBrush(QColor("#fff3e0")))
                circulacion_item.setForeground(QBrush(QColor("#f57c00")))
            self.tabla_vehiculos.setItem(i, 4, circulacion_item)

            # Información del parqueadero
            parqueadero_info = str(vehiculo.get('numero_parqueadero', '')) if vehiculo.get('numero_parqueadero') else 'Sin asignar'
            if vehiculo.get('numero_parqueadero'):
                parqueadero_info = f"P-{vehiculo.get('numero_parqueadero'):03d}"
            parqueadero_item = QTableWidgetItem(parqueadero_info)
            parqueadero_item.setTextAlignment(0x0004 | 0x0080)
            self.tabla_vehiculos.setItem(i, 5, parqueadero_item)

            # Botones de acción (Editar, Ver, Eliminar)
            btn_widget_acciones = QWidget()
            btn_layout_acciones = QHBoxLayout()
            btn_layout_acciones.setSpacing(5)
            btn_layout_acciones.setContentsMargins(5, 5, 5, 5)

            # Botón Editar
            btn_editar = QPushButton("✏️")
            btn_editar.setFixedSize(40, 40)
            btn_editar.setToolTip("Editar vehículo")
            btn_editar.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
                QPushButton:pressed {
                    background-color: #21618c;
                }
            """)
            btn_editar.clicked.connect(lambda checked, vid=vehiculo['id']: self.abrir_modal_editar(vid))

            # Botón Ver
            btn_ver = QPushButton("👁️")
            btn_ver.setFixedSize(40, 40)
            btn_ver.setToolTip("Ver detalles del vehículo")
            btn_ver.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
                QPushButton:pressed {
                    background-color: #1e8449;
                }
            """)
            btn_ver.clicked.connect(lambda checked, vid=vehiculo['id']: self.abrir_modal_ver(vid))

            # Botón Eliminar
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setFixedSize(40, 40)
            btn_eliminar.setToolTip("Eliminar vehículo")
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
                QPushButton:pressed {
                    background-color: #a93226;
                }
            """)
            btn_eliminar.clicked.connect(lambda checked, vid=vehiculo['id']: self.abrir_modal_eliminar(vid))

            btn_layout_acciones.addWidget(btn_editar)
            btn_layout_acciones.addWidget(btn_ver)
            btn_layout_acciones.addWidget(btn_eliminar)
            btn_layout_acciones.addStretch()

            btn_widget_acciones.setLayout(btn_layout_acciones)
            self.tabla_vehiculos.setCellWidget(i, 6, btn_widget_acciones)

    def actualizar_combo_funcionarios(self):
        """Actualiza el combo de funcionarios cuando se crea uno nuevo"""
        self.cargar_combo_funcionarios()

    def actualizar_vehiculos(self):
        """Actualiza la tabla de vehículos"""
        self.cargar_vehiculos()

    def mostrar_sugerencias_vehiculo(self):
        """Muestra sugerencias sobre qué vehículos puede registrar el funcionario"""
        if self.combo_funcionario.currentData() is None:
            self.lbl_sugerencias.clear()
            return

        funcionario_id = self.combo_funcionario.currentData()
        sugerencias = self.vehiculo_model.obtener_sugerencias_vehiculo(funcionario_id)

        if sugerencias:
            texto_sugerencias = "💡 Sugerencias:\n• " + "\n• ".join(sugerencias)
            self.lbl_sugerencias.setText(texto_sugerencias)
            self.lbl_sugerencias.show()
        else:
            self.lbl_sugerencias.clear()

    def validar_en_tiempo_real(self):
        """Valida el vehículo en tiempo real mientras el usuario ingresa datos"""
        if self.combo_funcionario.currentData() is None:
            return

        funcionario_id = self.combo_funcionario.currentData()
        tipo_vehiculo = self.combo_tipo_vehiculo.currentText()
        placa = self.txt_placa.text()

        # Solo validar si hay datos suficientes
        if tipo_vehiculo and (tipo_vehiculo != "Carro" or placa):
            es_valido, mensaje = self.vehiculo_model.validar_vehiculo_antes_registro(
                funcionario_id, tipo_vehiculo, placa
            )

            if not es_valido:
                # Mostrar advertencia visual
                self.btn_guardar_vehiculo.setEnabled(False)
                self.btn_guardar_vehiculo.setText("❌ No válido")
                self.btn_guardar_vehiculo.setStyleSheet("background-color: #f44336; color: white;")
            else:
                # Restaurar botón normal
                self.btn_guardar_vehiculo.setEnabled(True)
                self.btn_guardar_vehiculo.setText("Guardar")
                self.btn_guardar_vehiculo.setStyleSheet("")
        else:
            # Restaurar botón normal si no hay datos para validar
            self.btn_guardar_vehiculo.setEnabled(True)
            self.btn_guardar_vehiculo.setText("Guardar")
            self.btn_guardar_vehiculo.setStyleSheet("")

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
                    if vehiculo.get('placa') == placa:
                        return vehiculo.get('id')
        return None