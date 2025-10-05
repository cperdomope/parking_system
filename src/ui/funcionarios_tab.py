# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Funcionarios del sistema de gestión de parqueadero
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QGroupBox, QGridLayout,
    QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QCheckBox
)
from PyQt5.QtCore import pyqtSignal, QRegExp
from PyQt5.QtGui import QRegExpValidator, QBrush, QColor

from ..database.manager import DatabaseManager
from ..models.funcionario import FuncionarioModel
from ..config.settings import CARGOS_DISPONIBLES, DIRECCIONES_DISPONIBLES


class FuncionariosTab(QWidget):
    """Pestaña de gestión de funcionarios"""

    # Señales que se emiten para sincronizar con otras pestañas
    funcionario_creado = pyqtSignal()
    funcionario_eliminado = pyqtSignal()  # Nueva señal para eliminación en cascada

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.funcionario_model = FuncionarioModel(self.db)
        self.setup_ui()
        self.cargar_funcionarios()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout()

        # Formulario de registro
        form_group = QGroupBox("Registro de Funcionario")
        form_layout = QGridLayout()

        # Campos del formulario
        form_layout.addWidget(QLabel("Cédula:"), 0, 0)
        self.txt_cedula = QLineEdit()
        # Validador para cédula: solo números, entre 7 y 10 dígitos
        cedula_validator = QRegExpValidator(QRegExp("^[0-9]{7,10}$"))
        self.txt_cedula.setValidator(cedula_validator)
        self.txt_cedula.setPlaceholderText("Ingrese 7-10 dígitos numéricos")
        self.txt_cedula.setMaxLength(10)
        form_layout.addWidget(self.txt_cedula, 0, 1)

        form_layout.addWidget(QLabel("Nombre:"), 0, 2)
        self.txt_nombre = QLineEdit()
        # Validador para nombre: solo letras, espacios y tildes
        nombre_validator = QRegExpValidator(QRegExp("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$"))
        self.txt_nombre.setValidator(nombre_validator)
        self.txt_nombre.setPlaceholderText("Solo letras y espacios")
        form_layout.addWidget(self.txt_nombre, 0, 3)

        form_layout.addWidget(QLabel("Apellidos:"), 1, 0)
        self.txt_apellidos = QLineEdit()
        # Validador para apellidos: solo letras, espacios y tildes
        apellidos_validator = QRegExpValidator(QRegExp("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$"))
        self.txt_apellidos.setValidator(apellidos_validator)
        self.txt_apellidos.setPlaceholderText("Solo letras y espacios")
        form_layout.addWidget(self.txt_apellidos, 1, 1)

        form_layout.addWidget(QLabel("Dirección/Grupo:"), 1, 2)
        self.combo_direccion = QComboBox()
        self.combo_direccion.addItem("-- Seleccione --", "")
        self.combo_direccion.addItems(DIRECCIONES_DISPONIBLES)
        form_layout.addWidget(self.combo_direccion, 1, 3)

        form_layout.addWidget(QLabel("Cargo:"), 2, 0)
        self.combo_cargo = QComboBox()
        self.combo_cargo.addItem("-- Seleccione --", "")
        self.combo_cargo.addItems(CARGOS_DISPONIBLES)
        form_layout.addWidget(self.combo_cargo, 2, 1)

        form_layout.addWidget(QLabel("Celular:"), 2, 2)
        self.txt_celular = QLineEdit()
        # Validador para celular: exactamente 10 números
        celular_validator = QRegExpValidator(QRegExp("^[0-9]{10}$"))
        self.txt_celular.setValidator(celular_validator)
        self.txt_celular.setPlaceholderText("10 dígitos numéricos (ej: 3001234567)")
        self.txt_celular.setMaxLength(10)
        form_layout.addWidget(self.txt_celular, 2, 3)

        form_layout.addWidget(QLabel("No.Tarjeta Prox:"), 3, 0)
        self.txt_tarjeta = QLineEdit()
        # Validador para tarjeta: números y letras, máximo 15 caracteres
        tarjeta_validator = QRegExpValidator(QRegExp("^[a-zA-Z0-9]{1,15}$"))
        self.txt_tarjeta.setValidator(tarjeta_validator)
        self.txt_tarjeta.setPlaceholderText("Alfanumérico, máx 15 caracteres")
        self.txt_tarjeta.setMaxLength(15)
        form_layout.addWidget(self.txt_tarjeta, 3, 1)

        # ===== NUEVOS CHECKBOXES - REGLAS DE NEGOCIO (Solo uno puede estar activo) =====
        # Contenedor horizontal para los tres checkboxes
        checkboxes_layout = QHBoxLayout()

        # Checkbox: Pico y Placa Solidario
        self.chk_pico_placa_solidario = QCheckBox("🔄 Pico y Placa Solidario")
        self.chk_pico_placa_solidario.setToolTip(
            "Permite al funcionario usar el parqueadero en días que normalmente no le corresponderían.\n"
            "Ignora restricciones de PAR/IMPAR."
        )
        self.chk_pico_placa_solidario.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #2980b9;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
            }
        """)
        self.chk_pico_placa_solidario.stateChanged.connect(self.on_pico_placa_changed_main)

        # Checkbox: Discapacidad
        self.chk_discapacidad = QCheckBox("♿ Funcionario con Discapacidad")
        self.chk_discapacidad.setToolTip(
            "Marca al funcionario con condición de discapacidad.\n"
            "Tiene prioridad para espacios especiales."
        )
        self.chk_discapacidad.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #27ae60;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #2ecc71;
                border: 2px solid #27ae60;
            }
        """)
        self.chk_discapacidad.stateChanged.connect(self.on_discapacidad_changed_main)

        # Checkbox: Parqueadero Exclusivo (No compartir)
        self.chk_no_compartir = QCheckBox("🚫 Parqueadero Exclusivo (No compartido)")
        self.chk_no_compartir.setToolTip(
            "El funcionario tendrá un parqueadero EXCLUSIVO.\n"
            "Nadie más podrá usar ese espacio."
        )
        self.chk_no_compartir.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #e74c3c;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #e74c3c;
                border: 2px solid #c0392b;
            }
        """)
        self.chk_no_compartir.stateChanged.connect(self.on_no_compartir_changed_main)

        # Agregar los tres checkboxes al layout horizontal
        checkboxes_layout.addWidget(self.chk_pico_placa_solidario)
        checkboxes_layout.addWidget(self.chk_discapacidad)
        checkboxes_layout.addWidget(self.chk_no_compartir)
        checkboxes_layout.addStretch()

        # Agregar el layout horizontal completo al grid en una sola fila
        form_layout.addLayout(checkboxes_layout, 4, 0, 1, 4)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar_funcionario = QPushButton("Guardar")
        self.btn_guardar_funcionario.clicked.connect(self.guardar_funcionario)
        self.btn_guardar_funcionario.setProperty("class", "success")

        self.btn_limpiar_funcionario = QPushButton("Limpiar")
        self.btn_limpiar_funcionario.clicked.connect(self.limpiar_formulario)

        btn_layout.addWidget(self.btn_guardar_funcionario)
        btn_layout.addWidget(self.btn_limpiar_funcionario)
        btn_layout.addStretch()

        form_layout.addLayout(btn_layout, 3, 2, 1, 2)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Tabla de funcionarios con configuración fija y mejorada
        tabla_group = QGroupBox("Lista de Funcionarios")
        tabla_layout = QVBoxLayout()

        self.tabla_funcionarios = QTableWidget()
        self.tabla_funcionarios.setColumnCount(12)
        self.tabla_funcionarios.setHorizontalHeaderLabels([
            "Cédula", "Nombre", "Apellidos", "Dirección", "Cargo", "Celular",
            "Tarjeta Prox", "Vehículos", "Compartir", "Solidario", "Discap.", "Acciones"
        ])

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
        self.tabla_funcionarios.setColumnWidth(7, 80)   # Vehículos
        self.tabla_funcionarios.setColumnWidth(8, 80)   # Compartir
        self.tabla_funcionarios.setColumnWidth(9, 80)   # Solidario
        self.tabla_funcionarios.setColumnWidth(10, 70)  # Discapacidad
        self.tabla_funcionarios.setColumnWidth(11, 240) # Acciones

        # Configurar altura de filas fija
        self.tabla_funcionarios.verticalHeader().setDefaultSectionSize(60)

        # Estilo de encabezados
        self.tabla_funcionarios.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-right: 1px solid #2980b9;
            }
        """)

        # Estilo general de la tabla
        self.tabla_funcionarios.setStyleSheet("""
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
        """)

        tabla_layout.addWidget(self.tabla_funcionarios)
        tabla_group.setLayout(tabla_layout)
        layout.addWidget(tabla_group)

        self.setLayout(layout)

    def on_pico_placa_changed_main(self, state):
        """Cuando se marca Pico y Placa en el formulario principal, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_discapacidad.blockSignals(True)
            self.chk_no_compartir.blockSignals(True)
            self.chk_discapacidad.setChecked(False)
            self.chk_no_compartir.setChecked(False)
            self.chk_discapacidad.blockSignals(False)
            self.chk_no_compartir.blockSignals(False)

    def on_discapacidad_changed_main(self, state):
        """Cuando se marca Discapacidad en el formulario principal, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_no_compartir.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_no_compartir.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_no_compartir.blockSignals(False)

    def on_no_compartir_changed_main(self, state):
        """Cuando se marca Parqueadero Exclusivo en el formulario principal, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_discapacidad.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_discapacidad.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_discapacidad.blockSignals(False)

    def on_cargo_changed(self, cargo: str):
        """Validaciones o acciones cuando cambia el cargo (si es necesario en el futuro)"""
        # Método mantenido para compatibilidad futura si se necesitan validaciones por cargo
        pass

    def guardar_funcionario(self):
        """Guarda un nuevo funcionario en la base de datos"""
        # Validar cédula antes de enviar a la base de datos
        cedula = self.txt_cedula.text().strip()
        nombre = self.txt_nombre.text().strip()
        apellidos = self.txt_apellidos.text().strip()
        celular = self.txt_celular.text().strip()
        tarjeta = self.txt_tarjeta.text().strip()

        # Validación de cédula
        if not cedula:
            QMessageBox.warning(self, "⚠️ Validación", "La cédula es obligatoria")
            return

        if not cedula.isdigit():
            QMessageBox.warning(self, "⚠️ Validación", "La cédula solo debe contener números")
            return

        if len(cedula) < 7 or len(cedula) > 10:
            QMessageBox.warning(self, "⚠️ Validación",
                              f"La cédula debe tener entre 7 y 10 dígitos\n"
                              f"Dígitos ingresados: {len(cedula)}")
            return

        # Validación de nombre
        if not nombre:
            QMessageBox.warning(self, "⚠️ Validación", "El nombre es obligatorio")
            return

        if len(nombre) < 2:
            QMessageBox.warning(self, "⚠️ Validación", "El nombre debe tener al menos 2 caracteres")
            return

        # Validación de apellidos
        if not apellidos:
            QMessageBox.warning(self, "⚠️ Validación", "Los apellidos son obligatorios")
            return

        if len(apellidos) < 2:
            QMessageBox.warning(self, "⚠️ Validación", "Los apellidos deben tener al menos 2 caracteres")
            return

        # Validación de celular
        if celular and len(celular) != 10:
            QMessageBox.warning(self, "⚠️ Validación",
                              f"El celular debe tener exactamente 10 dígitos\n"
                              f"Dígitos ingresados: {len(celular)}")
            return

        if celular and not celular.isdigit():
            QMessageBox.warning(self, "⚠️ Validación", "El celular solo debe contener números")
            return

        # Validación de tarjeta (opcional pero si se ingresa debe ser válida)
        if tarjeta and len(tarjeta) < 3:
            QMessageBox.warning(self, "⚠️ Validación", "La tarjeta de proximidad debe tener al menos 3 caracteres")
            return

        # Determinar los valores de los campos según el checkbox marcado
        if self.chk_no_compartir.isChecked():
            # Parqueadero exclusivo (no compartido)
            permite_compartir = False
            pico_placa_solidario = False
            discapacidad = False
        elif self.chk_pico_placa_solidario.isChecked():
            # Pico y placa solidario
            permite_compartir = True
            pico_placa_solidario = True
            discapacidad = False
        elif self.chk_discapacidad.isChecked():
            # Funcionario con discapacidad
            permite_compartir = True
            pico_placa_solidario = False
            discapacidad = True
        else:
            # Ninguno marcado (funcionario regular que comparte)
            permite_compartir = True
            pico_placa_solidario = False
            discapacidad = False

        exito, mensaje = self.funcionario_model.crear(
            cedula=self.txt_cedula.text(),
            nombre=self.txt_nombre.text(),
            apellidos=self.txt_apellidos.text(),
            direccion_grupo=self.combo_direccion.currentText() if self.combo_direccion.currentText() != "-- Seleccione --" else "",
            cargo=self.combo_cargo.currentText() if self.combo_cargo.currentText() != "-- Seleccione --" else "",
            celular=self.txt_celular.text(),
            tarjeta=self.txt_tarjeta.text(),
            permite_compartir=permite_compartir,
            pico_placa_solidario=pico_placa_solidario,
            discapacidad=discapacidad
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
                QMessageBox.critical(self, "🚫 Error de Base de Datos",
                                   f"{mensaje}\n\n🛠️ Solución: Ejecute el script 'parking_database_schema.sql'")
            elif "estructura de la tabla" in mensaje.lower():
                QMessageBox.critical(self, "🚫 Error de Estructura",
                                   f"{mensaje}\n\n🛠️ Solución: Verifique la estructura de la base de datos")
            else:
                QMessageBox.critical(self, "🚫 Error", mensaje)

    def limpiar_formulario(self):
        """Limpia el formulario de funcionarios"""
        self.txt_cedula.clear()
        self.txt_nombre.clear()
        self.txt_apellidos.clear()
        self.combo_direccion.setCurrentIndex(0)
        self.combo_cargo.setCurrentIndex(0)
        self.txt_celular.clear()
        self.txt_tarjeta.clear()
        # Limpiar checkboxes (ninguno marcado por defecto)
        self.chk_pico_placa_solidario.setChecked(False)
        self.chk_discapacidad.setChecked(False)
        self.chk_no_compartir.setChecked(False)

    def cargar_funcionarios(self):
        """Carga la lista de funcionarios en la tabla"""
        funcionarios = self.funcionario_model.obtener_todos()

        self.tabla_funcionarios.setRowCount(len(funcionarios))

        for i, func in enumerate(funcionarios):
            # Ajustar índices ya que eliminamos la columna ID oculta
            self.tabla_funcionarios.setItem(i, 0, QTableWidgetItem(func.get('cedula', '')))
            self.tabla_funcionarios.setItem(i, 1, QTableWidgetItem(func.get('nombre', '')))
            self.tabla_funcionarios.setItem(i, 2, QTableWidgetItem(func.get('apellidos', '')))
            self.tabla_funcionarios.setItem(i, 3, QTableWidgetItem(func.get('direccion_grupo', '')))
            self.tabla_funcionarios.setItem(i, 4, QTableWidgetItem(func.get('cargo', '')))
            self.tabla_funcionarios.setItem(i, 5, QTableWidgetItem(func.get('celular', '')))
            self.tabla_funcionarios.setItem(i, 6, QTableWidgetItem(func.get('no_tarjeta_proximidad', '') or ''))

            # Formatear número de vehículos con mejor presentación
            total_vehiculos = func.get('total_vehiculos', 0)
            vehiculos_item = QTableWidgetItem(f"{total_vehiculos}/2")
            self.tabla_funcionarios.setItem(i, 7, vehiculos_item)

            # ===== NUEVAS COLUMNAS: Indicadores visuales =====

            # Columna 8: Permite Compartir
            # Mostrar "NO" si tiene marcado cualquiera de las tres opciones:
            # - NO permite_compartir (Parqueadero Exclusivo)
            # - pico_placa_solidario (Pico y Placa Solidario)
            # - discapacidad (Funcionario con Discapacidad)
            permite_compartir = func.get('permite_compartir', True)
            tiene_pico_placa = func.get('pico_placa_solidario', False)
            tiene_discapacidad = func.get('discapacidad', False)

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

            # Botones de acciones (Editar, Ver, Eliminar)
            btn_layout = QHBoxLayout()
            btn_widget = QWidget()
            btn_layout.setSpacing(5)
            btn_layout.setContentsMargins(5, 5, 5, 5)

            # Botón Editar
            btn_editar = QPushButton("✏️")
            btn_editar.setFixedSize(40, 40)
            btn_editar.setToolTip("Editar funcionario")
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
            btn_editar.clicked.connect(lambda _, fid=func.get('id'): self.editar_funcionario(fid))

            # Botón Ver
            btn_ver = QPushButton("👁️")
            btn_ver.setFixedSize(40, 40)
            btn_ver.setToolTip("Ver detalles del funcionario")
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
            btn_ver.clicked.connect(lambda _, fid=func.get('id'): self.ver_funcionario(fid))

            # Botón Eliminar
            btn_eliminar = QPushButton("🗑️")
            btn_eliminar.setFixedSize(40, 40)
            btn_eliminar.setToolTip("Eliminar funcionario")
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
            btn_eliminar.clicked.connect(lambda _, fid=func.get('id'): self.eliminar_funcionario(fid))

            btn_layout.addWidget(btn_editar)
            btn_layout.addWidget(btn_ver)
            btn_layout.addWidget(btn_eliminar)
            btn_layout.addStretch()
            btn_widget.setLayout(btn_layout)

            self.tabla_funcionarios.setCellWidget(i, 11, btn_widget)

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

        vehiculos = datos_relacionados['vehiculos']
        parqueaderos = datos_relacionados['parqueaderos_afectados']

        if vehiculos:
            mensaje += "Se eliminarán los siguientes vehículos:\n"
            for vehiculo in vehiculos:
                estado_asignacion = f" (Parqueadero P-{vehiculo['numero_parqueadero']:03d})" if vehiculo['tiene_asignacion'] else " (Sin asignar)"
                mensaje += f"• {vehiculo['tipo_vehiculo']} - {vehiculo['placa']} - {vehiculo['tipo_circulacion']}{estado_asignacion}\n"
            mensaje += "\n"

        if parqueaderos:
            mensaje += f"Se liberarán {len(parqueaderos)} parqueadero(s):\n"
            for parq in parqueaderos:
                mensaje += f"• P-{parq['numero_parqueadero']:03d} (actualmente {parq['estado'].replace('_', ' ')})\n"
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
                QMessageBox.information(self, "Éxito", "Funcionario y todos sus datos asociados eliminados correctamente.\n\nLos parqueaderos han quedado disponibles.")
                self.cargar_funcionarios()
                # Emitir señal específica para eliminación en cascada
                self.funcionario_eliminado.emit()
                # También emitir la señal general para mantener compatibilidad
                self.funcionario_creado.emit()
            else:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el funcionario.\n\nError: {error_msg}")

    def actualizar_funcionarios(self):
        """Actualiza la lista de funcionarios"""
        self.cargar_funcionarios()


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
        self.lbl_cedula.setStyleSheet("font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 3px; font-weight: bold;")
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
        self.lbl_cargo.setStyleSheet("font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px; font-weight: bold;")
        form_laboral.addRow("Cargo:", self.lbl_cargo)

        self.lbl_direccion = QLabel("")
        self.lbl_direccion.setStyleSheet("font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px;")
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
        self.lbl_vehiculos.setStyleSheet("font-size: 11px; padding: 10px; background-color: #fff9e6; border-radius: 3px;")
        vehiculos_layout.addWidget(self.lbl_vehiculos)

        grupo_vehiculos.setLayout(vehiculos_layout)
        layout.addWidget(grupo_vehiculos)

        # Botón cerrar
        btn_layout = QHBoxLayout()
        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.accept)
        self.btn_cerrar.setStyleSheet("QPushButton { background-color: #34495e; color: white; font-weight: bold; padding: 10px 30px; }")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cerrar)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def cargar_datos(self):
        """Carga los datos del funcionario en el modal"""
        # Información personal
        self.lbl_cedula.setText(self.funcionario_data.get('cedula', 'N/A'))
        nombre_completo = f"{self.funcionario_data.get('nombre', '')} {self.funcionario_data.get('apellidos', '')}"
        self.lbl_nombre.setText(nombre_completo)
        self.lbl_celular.setText(self.funcionario_data.get('celular', 'N/A'))

        # Información laboral
        self.lbl_cargo.setText(self.funcionario_data.get('cargo', 'N/A'))
        self.lbl_direccion.setText(self.funcionario_data.get('direccion_grupo', 'N/A'))
        tarjeta = self.funcionario_data.get('no_tarjeta_proximidad', '')
        self.lbl_tarjeta.setText(tarjeta if tarjeta else 'No registrada')

        # Características especiales
        permite_compartir = self.funcionario_data.get('permite_compartir', True)
        if permite_compartir:
            self.lbl_compartir.setText("✅ Sí")
            self.lbl_compartir.setStyleSheet("font-size: 12px; padding: 5px; background-color: #d4edda; color: #155724; border-radius: 3px; font-weight: bold;")
        else:
            self.lbl_compartir.setText("🚫 No (Exclusivo)")
            self.lbl_compartir.setStyleSheet("font-size: 12px; padding: 5px; background-color: #f8d7da; color: #721c24; border-radius: 3px; font-weight: bold;")

        pico_placa = self.funcionario_data.get('pico_placa_solidario', False)
        if pico_placa:
            self.lbl_solidario.setText("🔄 Sí")
            self.lbl_solidario.setStyleSheet("font-size: 12px; padding: 5px; background-color: #d1ecf1; color: #0c5460; border-radius: 3px; font-weight: bold;")
        else:
            self.lbl_solidario.setText("❌ No")
            self.lbl_solidario.setStyleSheet("font-size: 12px; padding: 5px; background-color: #ecf0f1; color: #666; border-radius: 3px; font-weight: bold;")

        discapacidad = self.funcionario_data.get('discapacidad', False)
        if discapacidad:
            self.lbl_discapacidad.setText("♿ Sí")
            self.lbl_discapacidad.setStyleSheet("font-size: 12px; padding: 5px; background-color: #d4edda; color: #155724; border-radius: 3px; font-weight: bold;")
        else:
            self.lbl_discapacidad.setText("❌ No")
            self.lbl_discapacidad.setStyleSheet("font-size: 12px; padding: 5px; background-color: #ecf0f1; color: #666; border-radius: 3px; font-weight: bold;")

        # Información de vehículos
        vehiculos = self.datos_relacionados.get('vehiculos', [])
        if vehiculos:
            texto_vehiculos = f"Total de vehículos: {len(vehiculos)}/2\n\n"
            for i, vehiculo in enumerate(vehiculos, 1):
                tipo = vehiculo.get('tipo_vehiculo', 'N/A')
                placa = vehiculo.get('placa', 'N/A')
                circulacion = vehiculo.get('tipo_circulacion', 'N/A')
                tiene_asignacion = vehiculo.get('tiene_asignacion', False)

                estado = f"Parqueadero P-{vehiculo.get('numero_parqueadero', 0):03d}" if tiene_asignacion else "Sin asignar"
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
        # Validador para cédula en modal de edición: solo números, entre 7 y 10 dígitos
        cedula_validator = QRegExpValidator(QRegExp("^[0-9]{7,10}$"))
        self.txt_cedula.setValidator(cedula_validator)
        self.txt_cedula.setPlaceholderText("Ingrese 7-10 dígitos numéricos")
        self.txt_cedula.setMaxLength(10)
        form_layout.addRow("Cédula:", self.txt_cedula)

        self.txt_nombre = QLineEdit()
        # Validador para nombre: solo letras, espacios y tildes
        nombre_validator = QRegExpValidator(QRegExp("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$"))
        self.txt_nombre.setValidator(nombre_validator)
        self.txt_nombre.setPlaceholderText("Solo letras y espacios")
        form_layout.addRow("Nombre:", self.txt_nombre)

        self.txt_apellidos = QLineEdit()
        # Validador para apellidos: solo letras, espacios y tildes
        apellidos_validator = QRegExpValidator(QRegExp("^[a-zA-ZáéíóúÁÉÍÓÚñÑ ]+$"))
        self.txt_apellidos.setValidator(apellidos_validator)
        self.txt_apellidos.setPlaceholderText("Solo letras y espacios")
        form_layout.addRow("Apellidos:", self.txt_apellidos)

        self.combo_direccion = QComboBox()
        self.combo_direccion.addItem("-- Seleccione --", "")
        self.combo_direccion.addItems(DIRECCIONES_DISPONIBLES)
        form_layout.addRow("Dirección/Grupo:", self.combo_direccion)

        self.combo_cargo = QComboBox()
        self.combo_cargo.addItem("-- Seleccione --", "")
        self.combo_cargo.addItems(CARGOS_DISPONIBLES)
        form_layout.addRow("Cargo:", self.combo_cargo)

        self.txt_celular = QLineEdit()
        # Validador para celular: exactamente 10 números
        celular_validator = QRegExpValidator(QRegExp("^[0-9]{10}$"))
        self.txt_celular.setValidator(celular_validator)
        self.txt_celular.setPlaceholderText("10 dígitos numéricos (ej: 3001234567)")
        self.txt_celular.setMaxLength(10)
        form_layout.addRow("Celular:", self.txt_celular)

        self.txt_tarjeta = QLineEdit()
        # Validador para tarjeta: números y letras, máximo 15 caracteres
        tarjeta_validator = QRegExpValidator(QRegExp("^[a-zA-Z0-9]{1,15}$"))
        self.txt_tarjeta.setValidator(tarjeta_validator)
        self.txt_tarjeta.setPlaceholderText("Alfanumérico, máx 15 caracteres")
        self.txt_tarjeta.setMaxLength(15)
        form_layout.addRow("No.Tarjeta Prox:", self.txt_tarjeta)

        # ===== CHECKBOXES DE REGLAS DE NEGOCIO (Solo uno puede estar activo) =====

        # Checkbox: Pico y Placa Solidario
        self.chk_pico_placa_solidario = QCheckBox("🔄 Pico y Placa Solidario")
        self.chk_pico_placa_solidario.setToolTip(
            "Permite al funcionario usar el parqueadero en días que normalmente no le corresponderían."
        )
        self.chk_pico_placa_solidario.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #2980b9;
            }
        """)
        self.chk_pico_placa_solidario.stateChanged.connect(self.on_pico_placa_changed)
        form_layout.addRow("", self.chk_pico_placa_solidario)

        # Checkbox: Discapacidad
        self.chk_discapacidad = QCheckBox("♿ Funcionario con Discapacidad")
        self.chk_discapacidad.setToolTip(
            "Marca al funcionario con condición de discapacidad."
        )
        self.chk_discapacidad.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #27ae60;
            }
        """)
        self.chk_discapacidad.stateChanged.connect(self.on_discapacidad_changed)
        form_layout.addRow("", self.chk_discapacidad)

        # Checkbox: Parqueadero Exclusivo (No compartir)
        self.chk_no_compartir = QCheckBox("🚫 Parqueadero Exclusivo (No compartido)")
        self.chk_no_compartir.setToolTip(
            "El funcionario tendrá un parqueadero EXCLUSIVO que no se comparte con otros."
        )
        self.chk_no_compartir.setStyleSheet("""
            QCheckBox {
                font-weight: bold;
                color: #e74c3c;
            }
        """)
        self.chk_no_compartir.stateChanged.connect(self.on_no_compartir_changed)
        form_layout.addRow("", self.chk_no_compartir)

        # Conectar cambio de cargo para validaciones
        self.combo_cargo.currentTextChanged.connect(self.on_cargo_changed_modal)

        layout.addLayout(form_layout)

        # Botones
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.guardar_cambios)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def on_pico_placa_changed(self, state):
        """Cuando se marca Pico y Placa, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_discapacidad.blockSignals(True)
            self.chk_no_compartir.blockSignals(True)
            self.chk_discapacidad.setChecked(False)
            self.chk_no_compartir.setChecked(False)
            self.chk_discapacidad.blockSignals(False)
            self.chk_no_compartir.blockSignals(False)

    def on_discapacidad_changed(self, state):
        """Cuando se marca Discapacidad, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_no_compartir.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_no_compartir.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_no_compartir.blockSignals(False)

    def on_no_compartir_changed(self, state):
        """Cuando se marca Parqueadero Exclusivo, desmarca las otras opciones"""
        if state == 2:  # Checked
            self.chk_pico_placa_solidario.blockSignals(True)
            self.chk_discapacidad.blockSignals(True)
            self.chk_pico_placa_solidario.setChecked(False)
            self.chk_discapacidad.setChecked(False)
            self.chk_pico_placa_solidario.blockSignals(False)
            self.chk_discapacidad.blockSignals(False)

    def on_cargo_changed_modal(self, cargo: str):
        """Validaciones o acciones cuando cambia el cargo"""
        # Si en el futuro se necesitan validaciones específicas por cargo
        pass

    def cargar_datos(self):
        """Carga los datos del funcionario en el formulario"""
        self.txt_cedula.setText(self.funcionario_data.get('cedula', ''))
        self.txt_nombre.setText(self.funcionario_data.get('nombre', ''))
        self.txt_apellidos.setText(self.funcionario_data.get('apellidos', ''))

        direccion = self.funcionario_data.get('direccion_grupo', '')
        index = self.combo_direccion.findText(direccion)
        if index >= 0:
            self.combo_direccion.setCurrentIndex(index)

        cargo = self.funcionario_data.get('cargo', '')
        index = self.combo_cargo.findText(cargo)
        if index >= 0:
            self.combo_cargo.setCurrentIndex(index)

        self.txt_celular.setText(self.funcionario_data.get('celular', ''))
        self.txt_tarjeta.setText(self.funcionario_data.get('no_tarjeta_proximidad', '') or '')

        # Cargar valores de checkboxes (solo uno puede estar marcado)
        # Bloquear señales temporalmente para evitar conflictos
        self.chk_pico_placa_solidario.blockSignals(True)
        self.chk_discapacidad.blockSignals(True)
        self.chk_no_compartir.blockSignals(True)

        # Desmarcar todos primero
        self.chk_pico_placa_solidario.setChecked(False)
        self.chk_discapacidad.setChecked(False)
        self.chk_no_compartir.setChecked(False)

        # Marcar solo el que corresponde
        if self.funcionario_data.get('pico_placa_solidario', False):
            self.chk_pico_placa_solidario.setChecked(True)
        elif self.funcionario_data.get('discapacidad', False):
            self.chk_discapacidad.setChecked(True)
        elif not self.funcionario_data.get('permite_compartir', True):
            # Si permite_compartir es False, significa parqueadero exclusivo
            self.chk_no_compartir.setChecked(True)

        # Reactivar señales
        self.chk_pico_placa_solidario.blockSignals(False)
        self.chk_discapacidad.blockSignals(False)
        self.chk_no_compartir.blockSignals(False)

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
            QMessageBox.warning(self, "⚠️ Validación",
                              f"La cédula debe tener entre 7 y 10 dígitos\n"
                              f"Dígitos ingresados: {len(cedula)}")
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
            QMessageBox.warning(self, "⚠️ Validación",
                              f"El celular debe tener exactamente 10 dígitos\n"
                              f"Dígitos ingresados: {len(celular)}")
            return

        if celular and not celular.isdigit():
            QMessageBox.warning(self, "⚠️ Validación", "El celular solo debe contener números")
            return

        # Validar tarjeta (opcional pero si se ingresa debe ser válida)
        if tarjeta and len(tarjeta) < 3:
            QMessageBox.warning(self, "⚠️ Validación", "La tarjeta de proximidad debe tener al menos 3 caracteres")
            return

        # Determinar los valores de los campos según el checkbox marcado
        if self.chk_no_compartir.isChecked():
            # Parqueadero exclusivo (no compartido)
            permite_compartir = False
            pico_placa_solidario = False
            discapacidad = False
        elif self.chk_pico_placa_solidario.isChecked():
            # Pico y placa solidario
            permite_compartir = True
            pico_placa_solidario = True
            discapacidad = False
        elif self.chk_discapacidad.isChecked():
            # Funcionario con discapacidad
            permite_compartir = True
            pico_placa_solidario = False
            discapacidad = True
        else:
            # Ninguno marcado (funcionario regular que comparte)
            permite_compartir = True
            pico_placa_solidario = False
            discapacidad = False

        exito, error_msg = self.funcionario_model.actualizar(
            funcionario_id=self.funcionario_data['id'],
            cedula=self.txt_cedula.text(),
            nombre=self.txt_nombre.text(),
            apellidos=self.txt_apellidos.text(),
            direccion_grupo=self.combo_direccion.currentText() if self.combo_direccion.currentText() != "-- Seleccione --" else "",
            cargo=self.combo_cargo.currentText() if self.combo_cargo.currentText() != "-- Seleccione --" else "",
            celular=self.txt_celular.text(),
            tarjeta=self.txt_tarjeta.text(),
            permite_compartir=permite_compartir,
            pico_placa_solidario=pico_placa_solidario,
            discapacidad=discapacidad
        )

        if exito:
            QMessageBox.information(self, "Éxito", "Funcionario actualizado correctamente")
            self.accept()
        else:
            if "Duplicate entry" in error_msg:
                QMessageBox.critical(self, "Error", f"Ya existe un funcionario con esa cédula: {self.txt_cedula.text()}")
            else:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar el funcionario.\n\nError: {error_msg}")