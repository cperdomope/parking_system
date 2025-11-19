# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Asignaciones del sistema de gestión de parqueadero
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..database.manager import DatabaseManager
from ..models.parqueadero import ParqueaderoModel
from ..models.vehiculo import VehiculoModel
from ..utils.formatters import format_numero_parqueadero

# Nuevas utilidades de refactorización
from .utils import UIDialogs


class EditarAsignacionDialog(QDialog):
    """Diálogo para editar una asignación existente"""

    def __init__(self, asignacion_data, db_manager, parqueadero_model, parent=None):
        super().__init__(parent)
        self.asignacion_data = asignacion_data
        self.db = db_manager
        self.parqueadero_model = parqueadero_model
        self.setup_ui()
        self.cargar_datos_actuales()
        self.cargar_sotanos()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        self.setWindowTitle("✏️ Editar Asignación")
        self.setFixedSize(600, 500)
        self.setModal(True)

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)

        # Título
        title_label = QLabel("📝 Editar Asignación de Parqueadero")
        title_label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
                text-align: center;
            }
        """
        )
        layout.addWidget(title_label)

        # Información del funcionario (solo lectura)
        info_group = QGroupBox("👤 Información del Funcionario")
        info_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #95a5a6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """
        )

        info_layout = QGridLayout()
        info_layout.setSpacing(10)

        # Labels de información
        info_layout.addWidget(QLabel("Funcionario:"), 0, 0)
        self.lbl_funcionario = QLabel()
        self.lbl_funcionario.setStyleSheet("font-weight: normal; color: #34495e;")
        info_layout.addWidget(self.lbl_funcionario, 0, 1)

        info_layout.addWidget(QLabel("Cédula:"), 0, 2)
        self.lbl_cedula = QLabel()
        self.lbl_cedula.setStyleSheet("font-weight: normal; color: #34495e;")
        info_layout.addWidget(self.lbl_cedula, 0, 3)

        info_layout.addWidget(QLabel("Vehículo:"), 1, 0)
        self.lbl_vehiculo = QLabel()
        self.lbl_vehiculo.setStyleSheet("font-weight: normal; color: #34495e;")
        info_layout.addWidget(self.lbl_vehiculo, 1, 1)

        info_layout.addWidget(QLabel("Placa:"), 1, 2)
        self.lbl_placa = QLabel()
        self.lbl_placa.setStyleSheet("font-weight: normal; color: #34495e;")
        info_layout.addWidget(self.lbl_placa, 1, 3)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Sección de edición
        edit_group = QGroupBox("🏢 Cambiar Ubicación")
        edit_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """
        )

        edit_layout = QGridLayout()
        edit_layout.setSpacing(15)

        # Sótano actual y nuevo
        edit_layout.addWidget(QLabel("Sótano actual:"), 0, 0)
        self.lbl_sotano_actual = QLabel()
        self.lbl_sotano_actual.setStyleSheet("font-weight: bold; color: #e74c3c;")
        edit_layout.addWidget(self.lbl_sotano_actual, 0, 1)

        edit_layout.addWidget(QLabel("Nuevo sótano:"), 0, 2)
        self.combo_nuevo_sotano = QComboBox()
        self.combo_nuevo_sotano.setFixedHeight(35)
        self.combo_nuevo_sotano.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #bcbcbc;
                border-radius: 3px;
                padding: 2px 25px 2px 8px;
                min-height: 22px;
                font-size: 13px;
                color: #000000;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #bcbcbc;
                background-color: #e0e0e0;
            }
            QComboBox::drop-down:hover {
                background-color: #34B5A9;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #333333;
                margin-top: 2px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #34B5A9;
                background-color: #ffffff;
                selection-background-color: #34B5A9 !important;
                selection-color: #ffffff !important;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                color: #000000;
                background-color: #ffffff;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
        """
        )
        self.combo_nuevo_sotano.currentTextChanged.connect(self.cargar_parqueaderos_disponibles)
        edit_layout.addWidget(self.combo_nuevo_sotano, 0, 3)

        # Parqueadero actual y nuevo
        edit_layout.addWidget(QLabel("Parqueadero actual:"), 1, 0)
        self.lbl_parqueadero_actual = QLabel()
        self.lbl_parqueadero_actual.setStyleSheet("font-weight: bold; color: #e74c3c;")
        edit_layout.addWidget(self.lbl_parqueadero_actual, 1, 1)

        edit_layout.addWidget(QLabel("Nuevo parqueadero:"), 1, 2)
        self.combo_nuevo_parqueadero = QComboBox()
        self.combo_nuevo_parqueadero.setFixedHeight(35)
        self.combo_nuevo_parqueadero.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #bcbcbc;
                border-radius: 3px;
                padding: 2px 25px 2px 8px;
                min-height: 22px;
                font-size: 13px;
                color: #000000;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #bcbcbc;
                background-color: #e0e0e0;
            }
            QComboBox::drop-down:hover {
                background-color: #34B5A9;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #333333;
                margin-top: 2px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #34B5A9;
                background-color: #ffffff;
                selection-background-color: #34B5A9 !important;
                selection-color: #ffffff !important;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                color: #000000;
                background-color: #ffffff;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
        """
        )
        edit_layout.addWidget(self.combo_nuevo_parqueadero, 1, 3)

        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)

        # Observaciones
        obs_group = QGroupBox("📝 Observaciones")
        obs_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """
        )

        obs_layout = QVBoxLayout()
        self.txt_observaciones = QTextEdit()
        self.txt_observaciones.setFixedHeight(80)
        self.txt_observaciones.setPlaceholderText("Agregar o modificar observaciones sobre esta asignación...")
        self.txt_observaciones.setStyleSheet(
            """
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit:focus {
                border-color: #27ae60;
                background-color: #f8f9fa;
            }
        """
        )
        obs_layout.addWidget(self.txt_observaciones)
        obs_group.setLayout(obs_layout)
        layout.addWidget(obs_group)

        # Botones
        btn_guardar = QPushButton("💾 Guardar Cambios")
        btn_guardar.setFixedSize(150, 40)
        btn_guardar.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #229954, stop:1 #27ae60);
            }
        """
        )
        btn_guardar.clicked.connect(self.guardar_cambios)

        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setFixedSize(120, 40)
        btn_cancelar.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """
        )
        btn_cancelar.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(btn_guardar)
        button_layout.addWidget(btn_cancelar)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def cargar_datos_actuales(self):
        """Carga los datos actuales de la asignación"""
        self.lbl_funcionario.setText(self.asignacion_data["funcionario"])
        self.lbl_cedula.setText(self.asignacion_data["cedula"])
        self.lbl_vehiculo.setText(
            f"{self.asignacion_data['tipo_vehiculo']} - {self.asignacion_data['tipo_circulacion']}"
        )
        self.lbl_placa.setText(self.asignacion_data["placa"])
        self.lbl_sotano_actual.setText(self.asignacion_data["sotano"])
        self.lbl_parqueadero_actual.setText(f"{format_numero_parqueadero(self.asignacion_data['numero_parqueadero'])}")

        # Cargar observaciones actuales
        observaciones_actuales = self.asignacion_data.get("observaciones", "") or ""
        self.txt_observaciones.setPlainText(observaciones_actuales)

    def cargar_sotanos(self):
        """Carga los sótanos disponibles"""
        try:
            sotanos = self.parqueadero_model.obtener_sotanos_disponibles()
            self.combo_nuevo_sotano.clear()
            self.combo_nuevo_sotano.addItem("-- Seleccione sótano --", None)

            for sotano in sotanos:
                self.combo_nuevo_sotano.addItem(sotano, sotano)

            # Pre-seleccionar sótano actual
            current_sotano = self.asignacion_data["sotano"]
            index = self.combo_nuevo_sotano.findText(current_sotano)
            if index >= 0:
                self.combo_nuevo_sotano.setCurrentIndex(index)

        except Exception as e:
            print(f"Error al cargar sótanos: {e}")

    def cargar_parqueaderos_disponibles(self):
        """Carga los parqueaderos disponibles del sótano seleccionado"""
        try:
            sotano_seleccionado = self.combo_nuevo_sotano.currentData()
            self.combo_nuevo_parqueadero.clear()
            self.combo_nuevo_parqueadero.addItem("-- Seleccione parqueadero --", None)

            if sotano_seleccionado:
                # Obtener parqueaderos disponibles del sótano
                parqueaderos_disponibles = self.parqueadero_model.obtener_todos(
                    sotano=sotano_seleccionado, tipo_vehiculo="Carro", estado="Disponible"
                )

                # Incluir también el parqueadero actual como opción
                parqueadero_actual = {
                    "id": None,  # Se establecerá después
                    "numero_parqueadero": self.asignacion_data["numero_parqueadero"],
                    "estado": "Actual",
                }

                # Agregar parqueadero actual si es del mismo sótano
                if sotano_seleccionado == self.asignacion_data["sotano"]:
                    texto_actual = f"{format_numero_parqueadero(parqueadero_actual['numero_parqueadero'])} (ACTUAL)"
                    self.combo_nuevo_parqueadero.addItem(texto_actual, parqueadero_actual["numero_parqueadero"])

                # Agregar parqueaderos disponibles
                for park in sorted(parqueaderos_disponibles, key=lambda x: x["numero_parqueadero"]):
                    texto = f"{format_numero_parqueadero(park['numero_parqueadero'])} ({park['estado'].replace('_', ' ')})"
                    self.combo_nuevo_parqueadero.addItem(texto, park["id"])

        except Exception as e:
            print(f"Error al cargar parqueaderos: {e}")

    def guardar_cambios(self):
        """Guarda los cambios realizados"""
        try:
            nuevo_sotano = self.combo_nuevo_sotano.currentData()
            nuevo_parqueadero_id = self.combo_nuevo_parqueadero.currentData()
            nuevas_observaciones = self.txt_observaciones.toPlainText().strip()

            # Verificar si hay cambios
            cambios_realizados = False

            # Si cambió de sótano o parqueadero
            if nuevo_sotano != self.asignacion_data["sotano"] or (
                nuevo_parqueadero_id and isinstance(nuevo_parqueadero_id, int)
            ):

                if not nuevo_sotano or not nuevo_parqueadero_id:
                    UIDialogs.show_warning(
                        self, "Datos Incompletos", "Debe seleccionar tanto el sotano como el parqueadero."
                    )
                    return

                # Realizar cambio de ubicación
                vehiculo_id = self.asignacion_data["vehiculo_id"]

                # Primero liberar la asignación actual
                success_liberar = self.parqueadero_model.liberar_asignacion(vehiculo_id)
                if not success_liberar:
                    UIDialogs.show_error(self, "Error", "No se pudo liberar la asignacion actual.")
                    return

                # Luego crear nueva asignación
                exito, mensaje = self.parqueadero_model.asignar_vehiculo(
                    vehiculo_id, nuevo_parqueadero_id, nuevas_observaciones
                )
                if not exito:
                    UIDialogs.show_error(self, "Error", f"No se pudo crear la nueva asignacion: {mensaje}")
                    return

                cambios_realizados = True

            else:
                # Solo actualizar observaciones
                observaciones_actuales = self.asignacion_data.get("observaciones", "") or ""
                if nuevas_observaciones != observaciones_actuales:
                    vehiculo_id = self.asignacion_data["vehiculo_id"]
                    update_query = """
                        UPDATE asignaciones
                        SET observaciones = %s
                        WHERE vehiculo_id = %s AND activo = TRUE
                    """
                    success, error = self.db.execute_query(update_query, (nuevas_observaciones, vehiculo_id))
                    if not success:
                        UIDialogs.show_error(self, "Error", f"No se pudieron actualizar las observaciones: {error}")
                        return
                    cambios_realizados = True

            if cambios_realizados:
                UIDialogs.show_success(self, "Exito", "Los cambios se han guardado correctamente.")
                self.accept()
            else:
                UIDialogs.show_success(self, "Sin Cambios", "No se detectaron cambios para guardar.")

        except Exception as e:
            UIDialogs.show_error(self, "Error", f"Error al guardar cambios: {str(e)}")


class VerAsignacionModal(QDialog):
    """Modal para visualizar los detalles de una asignación"""

    def __init__(self, asignacion_data, parent=None):
        super().__init__(parent)
        self.asignacion_data = asignacion_data
        self.setup_ui()
        self.cargar_datos()

    def setup_ui(self):
        """Configura la interfaz del modal"""
        self.setWindowTitle("Detalles de la Asignación")
        self.setModal(True)
        self.setFixedSize(600, 550)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("🅿️ Información de la Asignación")
        font_titulo = QFont()
        font_titulo.setPointSize(14)
        font_titulo.setBold(True)
        titulo.setFont(font_titulo)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(titulo)

        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Grupo de información del parqueadero
        grupo_parqueadero = QGroupBox("🅿️ Información del Parqueadero")
        form_parqueadero = QFormLayout()
        form_parqueadero.setSpacing(10)

        self.lbl_sotano = QLabel("")
        self.lbl_sotano.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #e3f2fd; border-radius: 3px; font-weight: bold;"
        )
        form_parqueadero.addRow("Sótano:", self.lbl_sotano)

        self.lbl_numero = QLabel("")
        self.lbl_numero.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #e3f2fd; border-radius: 3px; font-weight: bold;"
        )
        form_parqueadero.addRow("Número de parqueadero:", self.lbl_numero)

        grupo_parqueadero.setLayout(form_parqueadero)
        layout.addWidget(grupo_parqueadero)

        # Grupo de información del funcionario
        grupo_funcionario = QGroupBox("👤 Información del Funcionario")
        form_funcionario = QFormLayout()
        form_funcionario.setSpacing(10)

        self.lbl_funcionario = QLabel("")
        self.lbl_funcionario.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 3px;"
        )
        form_funcionario.addRow("Nombre completo:", self.lbl_funcionario)

        self.lbl_cedula = QLabel("")
        self.lbl_cedula.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 3px; font-weight: bold;"
        )
        form_funcionario.addRow("Cédula:", self.lbl_cedula)

        grupo_funcionario.setLayout(form_funcionario)
        layout.addWidget(grupo_funcionario)

        # Grupo de información del vehículo
        grupo_vehiculo = QGroupBox("🚗 Información del Vehículo")
        form_vehiculo = QFormLayout()
        form_vehiculo.setSpacing(10)

        self.lbl_tipo_vehiculo = QLabel("")
        self.lbl_tipo_vehiculo.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px;"
        )
        form_vehiculo.addRow("Tipo de vehículo:", self.lbl_tipo_vehiculo)

        self.lbl_placa = QLabel("")
        self.lbl_placa.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px; font-weight: bold;"
        )
        form_vehiculo.addRow("Placa:", self.lbl_placa)

        self.lbl_circulacion = QLabel("")
        self.lbl_circulacion.setStyleSheet("font-size: 12px; padding: 5px; border-radius: 3px; font-weight: bold;")
        form_vehiculo.addRow("Tipo de circulación:", self.lbl_circulacion)

        grupo_vehiculo.setLayout(form_vehiculo)
        layout.addWidget(grupo_vehiculo)

        # Grupo de detalles de la asignación
        grupo_detalles = QGroupBox("📝 Detalles de la Asignación")
        form_detalles = QFormLayout()
        form_detalles.setSpacing(10)

        self.lbl_fecha_asignacion = QLabel("")
        self.lbl_fecha_asignacion.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #fff9e6; border-radius: 3px;"
        )
        form_detalles.addRow("Fecha de asignación:", self.lbl_fecha_asignacion)

        self.lbl_observaciones = QLabel("")
        self.lbl_observaciones.setWordWrap(True)
        self.lbl_observaciones.setStyleSheet(
            "font-size: 11px; padding: 8px; background-color: #fff9e6; border-radius: 3px;"
        )
        form_detalles.addRow("Observaciones:", self.lbl_observaciones)

        grupo_detalles.setLayout(form_detalles)
        layout.addWidget(grupo_detalles)

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
        """Carga los datos de la asignación"""
        # Información del parqueadero
        self.lbl_sotano.setText(self.asignacion_data.get("sotano", "N/A"))
        numero_parqueadero = self.asignacion_data.get("numero_parqueadero", 0)
        self.lbl_numero.setText(f"{format_numero_parqueadero(numero_parqueadero)}")

        # Información del funcionario
        self.lbl_funcionario.setText(self.asignacion_data.get("funcionario", "N/A"))
        self.lbl_cedula.setText(self.asignacion_data.get("cedula", "N/A"))

        # Información del vehículo
        self.lbl_tipo_vehiculo.setText(self.asignacion_data.get("tipo_vehiculo", "N/A"))
        self.lbl_placa.setText(self.asignacion_data.get("placa", "N/A"))

        # Tipo de circulación con color
        circulacion = self.asignacion_data.get("tipo_circulacion", "N/A")
        self.lbl_circulacion.setText(circulacion)
        if circulacion == "PAR":
            self.lbl_circulacion.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #e8f5e8; color: #2e7d32; border-radius: 3px; font-weight: bold;"
            )
        elif circulacion == "IMPAR":
            self.lbl_circulacion.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #fff3e0; color: #f57c00; border-radius: 3px; font-weight: bold;"
            )
        else:
            self.lbl_circulacion.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #ecf0f1; color: #666; border-radius: 3px; font-weight: bold;"
            )

        # Detalles de la asignación
        fecha_asignacion = self.asignacion_data.get("fecha_asignacion", "N/A")
        if fecha_asignacion and fecha_asignacion != "N/A":
            try:
                from datetime import datetime

                if isinstance(fecha_asignacion, str):
                    fecha_obj = datetime.strptime(str(fecha_asignacion)[:19], "%Y-%m-%d %H:%M:%S")
                else:
                    fecha_obj = fecha_asignacion
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y %H:%M")
                self.lbl_fecha_asignacion.setText(fecha_formateada)
            except Exception as e:
                print(f"Advertencia al formatear fecha: {e}")
                self.lbl_fecha_asignacion.setText(str(fecha_asignacion))
        else:
            self.lbl_fecha_asignacion.setText("N/A")

        observaciones = self.asignacion_data.get("observaciones", "")
        if observaciones:
            self.lbl_observaciones.setText(observaciones)
        else:
            self.lbl_observaciones.setText("Sin observaciones")


class AsignacionesTab(QWidget):
    """Pestaña de gestión de asignaciones"""

    # Señal que se emite cuando se realiza o libera una asignación
    asignacion_actualizada = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.vehiculo_model = VehiculoModel(self.db)
        self.parqueadero_model = ParqueaderoModel(self.db)
        self.setup_ui()
        self.cargar_sotanos()
        self.cargar_asignaciones()
        self.cargar_vehiculos_sin_asignar()

    def setup_ui(self):
        """Configura la interfaz de usuario - Diseño reorganizado profesionalmente"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ============= SECCIÓN SUPERIOR: Filtros y Nueva Asignación en horizontal =============
        top_section = QWidget()
        top_section_layout = QHBoxLayout(top_section)
        top_section_layout.setSpacing(15)
        top_section_layout.setContentsMargins(0, 0, 0, 0)

        # ===== PANEL IZQUIERDO: Filtro de Búsqueda =====
        filter_group = QGroupBox("🔍 Filtrar Asignaciones")
        filter_group.setMaximumWidth(350)
        filter_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """
        )

        filter_layout = QVBoxLayout()
        filter_layout.setSpacing(10)
        filter_layout.setContentsMargins(15, 15, 15, 15)

        lbl_cedula = QLabel("Buscar por Cédula:")
        lbl_cedula.setStyleSheet("font-weight: bold; color: #34495e; font-size: 12px;")
        filter_layout.addWidget(lbl_cedula)

        self.cedula_filter = QLineEdit()
        self.cedula_filter.setPlaceholderText("Ingrese cédula...")
        self.cedula_filter.setFixedHeight(38)
        self.cedula_filter.setStyleSheet(
            """
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }
        """
        )
        self.cedula_filter.textChanged.connect(self.filtrar_por_cedula)
        filter_layout.addWidget(self.cedula_filter)

        btn_limpiar_filtro = QPushButton("🗑️ Limpiar Filtro")
        btn_limpiar_filtro.setFixedHeight(38)
        btn_limpiar_filtro.setStyleSheet(
            """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #5d6d7e;
            }
        """
        )
        btn_limpiar_filtro.clicked.connect(self.limpiar_filtro)
        filter_layout.addWidget(btn_limpiar_filtro)

        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        top_section_layout.addWidget(filter_group)

        # ===== PANEL DERECHO: Nueva Asignación =====
        assign_group = QGroupBox("✨ Nueva Asignación de Parqueadero")
        assign_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }
        """
        )

        assign_layout = QGridLayout()
        assign_layout.setSpacing(10)
        assign_layout.setContentsMargins(15, 15, 15, 15)

        # ========== FILA 1: Vehículo, Sótano y Parqueadero en una sola fila ==========

        # Vehículo
        lbl_vehiculo = QLabel("🚗 Vehículo:")
        lbl_vehiculo.setStyleSheet("font-weight: bold; color: #34495e; font-size: 12px;")
        assign_layout.addWidget(lbl_vehiculo, 0, 0)

        self.combo_vehiculo_sin_asignar = QComboBox()
        self.combo_vehiculo_sin_asignar.setMinimumWidth(550)
        self.combo_vehiculo_sin_asignar.setFixedHeight(38)
        self.combo_vehiculo_sin_asignar.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #bcbcbc;
                border-radius: 3px;
                padding: 2px 25px 2px 8px;
                min-height: 22px;
                font-size: 13px;
                color: #000000;
                min-width: 250px;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #bcbcbc;
                background-color: #e0e0e0;
            }
            QComboBox::drop-down:hover {
                background-color: #34B5A9;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #333333;
                margin-top: 2px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #34B5A9;
                background-color: #ffffff;
                selection-background-color: #34B5A9 !important;
                selection-color: #ffffff !important;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                color: #000000;
                background-color: #ffffff;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
        """
        )
        assign_layout.addWidget(self.combo_vehiculo_sin_asignar, 0, 1)

        # Sótano
        lbl_sotano = QLabel("🏢 Sótano:")
        lbl_sotano.setStyleSheet("font-weight: bold; color: #34495e; font-size: 12px;")
        assign_layout.addWidget(lbl_sotano, 0, 2)

        self.combo_sotano = QComboBox()
        self.combo_sotano.setFixedHeight(38)
        self.combo_sotano.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #bcbcbc;
                border-radius: 3px;
                padding: 2px 25px 2px 8px;
                min-height: 22px;
                font-size: 13px;
                color: #000000;
                min-width: 120px;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #bcbcbc;
                background-color: #e0e0e0;
            }
            QComboBox::drop-down:hover {
                background-color: #34B5A9;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #333333;
                margin-top: 2px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #34B5A9;
                background-color: #ffffff;
                selection-background-color: #34B5A9 !important;
                selection-color: #ffffff !important;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                color: #000000;
                background-color: #ffffff;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
        """
        )
        self.combo_sotano.currentTextChanged.connect(self.cargar_parqueaderos_por_sotano)
        assign_layout.addWidget(self.combo_sotano, 0, 3)

        # Parqueadero
        lbl_parqueadero = QLabel("🅿️ Parqueadero:")
        lbl_parqueadero.setStyleSheet("font-weight: bold; color: #34495e; font-size: 12px;")
        assign_layout.addWidget(lbl_parqueadero, 0, 4)

        self.combo_parqueadero_disponible = QComboBox()
        self.combo_parqueadero_disponible.setFixedHeight(38)
        self.combo_parqueadero_disponible.setStyleSheet(
            """
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #bcbcbc;
                border-radius: 3px;
                padding: 2px 25px 2px 8px;
                min-height: 22px;
                font-size: 13px;
                color: #000000;
                min-width: 180px;
            }
            QComboBox:focus {
                border: 1px solid #0078d7;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #bcbcbc;
                background-color: #e0e0e0;
            }
            QComboBox::drop-down:hover {
                background-color: #34B5A9;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #333333;
                margin-top: 2px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #34B5A9;
                background-color: #ffffff;
                selection-background-color: #34B5A9 !important;
                selection-color: #ffffff !important;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                color: #000000;
                background-color: #ffffff;
                min-height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #34B5A9 !important;
                color: #ffffff !important;
                font-weight: bold;
            }
        """
        )
        assign_layout.addWidget(self.combo_parqueadero_disponible, 0, 5)

        # Conectar evento para cargar parqueaderos cuando se selecciona un vehículo
        self.combo_vehiculo_sin_asignar.currentTextChanged.connect(self.cargar_parqueaderos_por_sotano)

        # ========== FILA 2: Observaciones y Botón de Asignar en la misma fila ==========
        lbl_observaciones = QLabel("📝 Observaciones:")
        lbl_observaciones.setStyleSheet("font-weight: bold; color: #34495e; font-size: 12px;")
        assign_layout.addWidget(lbl_observaciones, 1, 0)

        self.txt_observaciones = QTextEdit()
        self.txt_observaciones.setFixedHeight(60)
        self.txt_observaciones.setPlaceholderText("Ingrese observaciones sobre esta asignación (opcional)...")
        self.txt_observaciones.setStyleSheet(
            """
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit:focus {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """
        )
        assign_layout.addWidget(self.txt_observaciones, 1, 1, 1, 4)

        # Botón de Asignar Parqueadero en la misma fila que Observaciones
        self.btn_asignar = QPushButton("✅ Asignar Parqueadero")
        self.btn_asignar.setFixedSize(180, 38)
        self.btn_asignar.setStyleSheet(
            """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:1 #2ecc71);
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                letter-spacing: 0.3px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #229954, stop:1 #27ae60);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e8449, stop:1 #229954);
            }
        """
        )
        self.btn_asignar.clicked.connect(self.realizar_asignacion)

        # Contenedor para centrar verticalmente el botón con las observaciones
        btn_container = QWidget()
        btn_container_layout = QVBoxLayout(btn_container)
        btn_container_layout.setContentsMargins(0, 11, 0, 11)
        btn_container_layout.addWidget(self.btn_asignar)

        assign_layout.addWidget(btn_container, 1, 5)

        assign_group.setLayout(assign_layout)
        top_section_layout.addWidget(assign_group)

        # Agregar la sección superior al layout principal
        main_layout.addWidget(top_section)

        # ============= SECCIÓN INFERIOR: Tabla de Asignaciones (Ancho completo) =============

        tabla_group = QGroupBox("📋 Asignaciones Actuales")
        tabla_group.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #e67e22;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """
        )
        tabla_layout = QVBoxLayout()
        tabla_layout.setContentsMargins(15, 20, 15, 15)

        self.tabla_asignaciones = QTableWidget()
        self.tabla_asignaciones.setColumnCount(9)  # Agregamos columna para observaciones
        self.tabla_asignaciones.setHorizontalHeaderLabels(
            [
                "Sótano",
                "Parqueadero",
                "Funcionario",
                "Cédula",
                "Vehículo",
                "Placa",
                "Circulación",
                "Observaciones",
                "Acciones",
            ]
        )

        # Configuración visual profesional
        self.tabla_asignaciones.setAlternatingRowColors(True)
        self.tabla_asignaciones.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_asignaciones.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla_asignaciones.verticalHeader().setVisible(False)

        # Establecer anchos de columna optimizados
        self.tabla_asignaciones.setColumnWidth(0, 100)  # Sótano
        self.tabla_asignaciones.setColumnWidth(1, 120)  # Parqueadero
        self.tabla_asignaciones.setColumnWidth(2, 200)  # Funcionario
        self.tabla_asignaciones.setColumnWidth(3, 120)  # Cédula
        self.tabla_asignaciones.setColumnWidth(4, 100)  # Vehículo
        self.tabla_asignaciones.setColumnWidth(5, 100)  # Placa
        self.tabla_asignaciones.setColumnWidth(6, 100)  # Circulación
        self.tabla_asignaciones.setColumnWidth(7, 180)  # Observaciones
        self.tabla_asignaciones.setColumnWidth(8, 160)  # Acciones

        # Configurar altura de filas fija para acomodar los botones
        self.tabla_asignaciones.verticalHeader().setDefaultSectionSize(52)

        # Deshabilitar scroll vertical (paginación manual)
        self.tabla_asignaciones.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Altura fija para mostrar exactamente 6 filas + encabezado
        # 6 filas * 52px + encabezado (34px) + borde superior/inferior (4px)
        self.tabla_asignaciones.setFixedHeight(6 * 52 + 34 + 4)

        # Estilo de encabezados - Color corporativo (altura reducida)
        self.tabla_asignaciones.horizontalHeader().setStyleSheet(
            """
            QHeaderView::section {
                background-color: #34B5A9;
                color: white;
                font-weight: bold;
                padding: 6px;
                border: none;
                border-right: 1px solid #2D9B8F;
                text-align: center;
                height: 34px;
            }
        """
        )

        # Ajustar altura del encabezado
        self.tabla_asignaciones.horizontalHeader().setFixedHeight(34)

        # Estilo general de la tabla
        self.tabla_asignaciones.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                gridline-color: #bdc3c7;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 11px;
            }
            QTableWidget::item {
                padding: 5px 5px;
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

        tabla_layout.addWidget(self.tabla_asignaciones)

        # ========== CONTROLES DE PAGINACIÓN ==========
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(0, 15, 0, 5)
        pagination_layout.setSpacing(10)

        # Botón Primera Página
        self.btn_primera_pagina = QPushButton("⏮ Primera")
        self.btn_primera_pagina.setFixedSize(100, 32)
        self.btn_primera_pagina.setStyleSheet(
            """
            QPushButton {
                background-color: #34B5A9;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2D9B8F;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.btn_primera_pagina.clicked.connect(self.ir_primera_pagina)

        # Botón Anterior
        self.btn_anterior = QPushButton("◀ Anterior")
        self.btn_anterior.setFixedSize(100, 32)
        self.btn_anterior.setStyleSheet(
            """
            QPushButton {
                background-color: #34B5A9;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2D9B8F;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.btn_anterior.clicked.connect(self.pagina_anterior)

        # Label de información de página
        self.lbl_info_pagina = QLabel("Página 1 de 1")
        self.lbl_info_pagina.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                padding: 5px 15px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """
        )
        self.lbl_info_pagina.setAlignment(Qt.AlignCenter)
        self.lbl_info_pagina.setFixedWidth(150)

        # Botón Siguiente
        self.btn_siguiente = QPushButton("Siguiente ▶")
        self.btn_siguiente.setFixedSize(100, 32)
        self.btn_siguiente.setStyleSheet(
            """
            QPushButton {
                background-color: #34B5A9;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2D9B8F;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.btn_siguiente.clicked.connect(self.pagina_siguiente)

        # Botón Última Página
        self.btn_ultima_pagina = QPushButton("Última ⏭")
        self.btn_ultima_pagina.setFixedSize(100, 32)
        self.btn_ultima_pagina.setStyleSheet(
            """
            QPushButton {
                background-color: #34B5A9;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2D9B8F;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """
        )
        self.btn_ultima_pagina.clicked.connect(self.ir_ultima_pagina)

        # Label de total de registros
        self.lbl_total_registros = QLabel("Total: 0 asignaciones")
        self.lbl_total_registros.setStyleSheet(
            """
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                padding: 5px;
            }
        """
        )

        # Agregar widgets al layout de paginación
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.btn_primera_pagina)
        pagination_layout.addWidget(self.btn_anterior)
        pagination_layout.addWidget(self.lbl_info_pagina)
        pagination_layout.addWidget(self.btn_siguiente)
        pagination_layout.addWidget(self.btn_ultima_pagina)
        pagination_layout.addSpacing(20)
        pagination_layout.addWidget(self.lbl_total_registros)
        pagination_layout.addStretch()

        tabla_layout.addWidget(pagination_widget)
        tabla_group.setLayout(tabla_layout)

        # Agregar la tabla directamente al layout principal (ocupa todo el ancho)
        main_layout.addWidget(tabla_group, 1)  # El '1' es el stretch factor para que ocupe más espacio

        self.setLayout(main_layout)

        # Variables para paginación y filtrado
        self.asignaciones_completas = []  # Lista completa sin filtrar
        self.asignaciones_para_mostrar = []  # Lista que se está mostrando actualmente
        self.pagina_actual = 1
        self.filas_por_pagina = 6
        self.total_paginas = 1

    def cargar_vehiculos_sin_asignar(self):
        """Carga TODOS los vehículos sin asignar (Carros, Motos y Bicicletas)"""
        # Query personalizada para obtener vehículos con información del funcionario
        query = """
            SELECT v.*,
                   f.nombre, f.apellidos, f.cedula, f.cargo,
                   f.permite_compartir, f.pico_placa_solidario, f.discapacidad,
                   f.tiene_parqueadero_exclusivo, f.tiene_carro_hibrido
            FROM vehiculos v
            JOIN funcionarios f ON v.funcionario_id = f.id
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            WHERE v.activo = TRUE AND a.id IS NULL
            ORDER BY v.tipo_vehiculo, f.apellidos, f.nombre
        """
        vehiculos = self.db.fetch_all(query)

        # DEBUG: Verificar TODOS los vehículos activos (con y sin asignar)
        query_all = """
            SELECT v.placa, v.tipo_vehiculo,
                   CASE WHEN a.id IS NULL THEN 'SIN_ASIGNAR' ELSE 'ASIGNADO' END as estado
            FROM vehiculos v
            LEFT JOIN asignaciones a ON v.id = a.vehiculo_id AND a.activo = TRUE
            WHERE v.activo = TRUE
            ORDER BY v.id DESC
            LIMIT 10
        """
        todos = self.db.fetch_all(query_all)
        for vh in todos:
            pass  # Debug loop - mantener para compatibilidad

        self.combo_vehiculo_sin_asignar.clear()
        self.combo_vehiculo_sin_asignar.addItem("-- Seleccione vehículo --", None)

        for vehiculo in vehiculos:
            # Icono según tipo de vehículo
            icono_tipo = {"Carro": "🚗", "Moto": "🏍️", "Bicicleta": "🚲"}.get(
                vehiculo.get("tipo_vehiculo", "Carro"), "🚗"
            )

            # Construir iconos de excepciones del funcionario
            iconos = []
            if vehiculo.get("tiene_parqueadero_exclusivo"):
                iconos.append("🏢")
            if vehiculo.get("tiene_carro_hibrido"):
                iconos.append("🌿")
            if vehiculo.get("pico_placa_solidario"):
                iconos.append("🔄")
            if vehiculo.get("discapacidad"):
                iconos.append("♿")

            iconos_str = " " + " ".join(iconos) if iconos else ""

            # Formato: [ICONO] PLACA - NOMBRE (CIRCULACIÓN) [ICONOS]
            tipo_circ = vehiculo.get("tipo_circulacion", "N/A")
            circulacion_str = f" ({tipo_circ})" if tipo_circ != "N/A" else ""
            texto = f"{icono_tipo} {vehiculo['placa']} - {vehiculo['nombre']} {vehiculo['apellidos']}{circulacion_str}{iconos_str}"
            self.combo_vehiculo_sin_asignar.addItem(texto, vehiculo)

    def cargar_sotanos(self):
        """Carga los sótanos disponibles en el combo"""
        try:
            sotanos = self.parqueadero_model.obtener_sotanos_disponibles()
            self.combo_sotano.clear()
            self.combo_sotano.addItem("-- Seleccione sótano --", None)

            for sotano in sotanos:
                self.combo_sotano.addItem(sotano, sotano)

        except Exception as e:
            print(f"Error al cargar sótanos: {e}")
            # Valores por defecto
            self.combo_sotano.clear()
            self.combo_sotano.addItem("-- Seleccione sótano --", None)
            self.combo_sotano.addItem("Sótano-1", "Sótano-1")
            self.combo_sotano.addItem("Sótano-2", "Sótano-2")
            self.combo_sotano.addItem("Sótano-3", "Sótano-3")

    def cargar_parqueaderos_por_sotano(self):
        """Carga los parqueaderos disponibles del sótano seleccionado según el tipo de vehículo"""
        try:
            vehiculo_data = self.combo_vehiculo_sin_asignar.currentData()
            sotano_seleccionado = self.combo_sotano.currentData()

            self.combo_parqueadero_disponible.clear()
            self.combo_parqueadero_disponible.addItem("-- Seleccione parqueadero --", None)

            if vehiculo_data and sotano_seleccionado:
                tipo_vehiculo = vehiculo_data.get("tipo_vehiculo", "Carro")
                funcionario_id = vehiculo_data.get("funcionario_id")

                # Para CARROS: buscar disponibles y parcialmente asignados con complemento
                if tipo_vehiculo == "Carro":
                    # VERIFICAR EXCEPCIONES DE PICO Y PLACA
                    # Vehículos con excepciones SOLO pueden usar parqueaderos 100% DISPONIBLES
                    pico_placa_solidario = vehiculo_data.get("pico_placa_solidario", False)
                    discapacidad = vehiculo_data.get("discapacidad", False)
                    es_hibrido = vehiculo_data.get("tipo_circulacion", "") == "HÍBRIDO"

                    # Verificar si el funcionario tiene parqueadero exclusivo directivo
                    query_check_exclusivo = """
                        SELECT tiene_parqueadero_exclusivo, cargo
                        FROM funcionarios
                        WHERE id = %s AND activo = TRUE
                    """
                    func_data = self.db.fetch_one(query_check_exclusivo, (funcionario_id,))
                    tiene_exclusivo = func_data and func_data.get("tiene_parqueadero_exclusivo", False)
                    # Si tiene parqueadero exclusivo, es directivo exclusivo (sin restricción de cargo)
                    es_directivo_exclusivo = tiene_exclusivo

                    # REGLA CRÍTICA: Vehículos con CUALQUIER excepción NO comparten parqueadero
                    tiene_excepcion_pico_placa = (
                        pico_placa_solidario or
                        discapacidad or
                        es_hibrido or
                        es_directivo_exclusivo
                    )

                    # Obtener parqueaderos disponibles para carros
                    # NOTA: "Disponible" puede incluir parqueaderos con 1 carro (parcialmente asignado para carros)
                    parqueaderos_disponibles = self.parqueadero_model.obtener_todos(
                        sotano=sotano_seleccionado, tipo_vehiculo="Carro", estado="Disponible"
                    )

                    todos_parqueaderos = {p["id"]: p for p in parqueaderos_disponibles}

                    # APLICAR RESTRICCIONES SEGÚN EXCEPCIONES
                    if tiene_excepcion_pico_placa and es_directivo_exclusivo:
                        # CASO ESPECIAL: Directivo con parqueadero exclusivo
                        # Buscar parqueaderos que ya tienen vehículos de este directivo
                        query_parqueaderos_directivo = """
                            SELECT DISTINCT p.id, p.numero_parqueadero, p.estado,
                                   COALESCE(p.sotano, 'Sótano-1') as sotano,
                                   COUNT(a.id) as vehiculos_asignados
                            FROM parqueaderos p
                            JOIN asignaciones a ON p.id = a.parqueadero_id AND a.activo = TRUE
                            JOIN vehiculos v ON a.vehiculo_id = v.id
                            WHERE v.funcionario_id = %s
                            AND COALESCE(p.sotano, 'Sótano-1') = %s
                            GROUP BY p.id, p.numero_parqueadero, p.estado, p.sotano
                            HAVING COUNT(a.id) < 4
                        """
                        parqueaderos_directivo = self.db.fetch_all(
                            query_parqueaderos_directivo, (funcionario_id, sotano_seleccionado)
                        )

                        # Agregar parqueaderos del directivo que aún tienen espacio
                        for park in parqueaderos_directivo:
                            park["estado_display"] = f"Parcial ({park['vehiculos_asignados']}/4)"
                            todos_parqueaderos[park["id"]] = park

                    elif tiene_excepcion_pico_placa:
                        # VEHÍCULOS CON EXCEPCIÓN (Híbrido, Discapacidad, Pico y Placa Solidario)
                        # REGLA: SOLO parqueaderos SIN CARROS (pueden tener motos/bicicletas)
                        if pico_placa_solidario:
                            pass  # Excepción detectada
                        if discapacidad:
                            pass  # Excepción detectada
                        if es_hibrido:
                            pass  # Excepción detectada

                        # FILTRAR parqueaderos que tengan CARROS
                        parqueaderos_sin_carros = []
                        for p in parqueaderos_disponibles:
                            query_count_carros = """
                                SELECT COUNT(*) as total_carros
                                FROM asignaciones a
                                JOIN vehiculos v ON a.vehiculo_id = v.id
                                WHERE a.parqueadero_id = %s
                                AND a.activo = TRUE
                                AND v.tipo_vehiculo = 'Carro'
                            """
                            count_result = self.db.fetch_one(query_count_carros, (p["id"],))
                            total_carros = count_result.get("total_carros", 0) if count_result else 0

                            # Solo agregar si NO tiene NINGÚN CARRO asignado
                            if total_carros == 0:
                                parqueaderos_sin_carros.append(p)
                            else:
                                pass  # Parqueadero con carros, no agregar

                        # Reemplazar todos_parqueaderos con los que no tienen carros
                        todos_parqueaderos = {p["id"]: p for p in parqueaderos_sin_carros}
                        # NO agregar parqueaderos parcialmente asignados con carros

                    else:
                        # Funcionarios regulares SIN excepción: pueden usar parcialmente asignados con complemento PAR/IMPAR
                        parqueaderos_complemento = self.parqueadero_model.obtener_disponibles(
                            vehiculo_data["tipo_circulacion"]
                        )

                        # Filtrar por sótano y VALIDAR que solo tengan 1 carro asignado
                        parqueaderos_complemento_sotano = []
                        for p in parqueaderos_complemento:
                            if p.get("sotano", "Sótano-1") == sotano_seleccionado:
                                # VALIDACIÓN 1: Contar cuántos carros hay asignados
                                query_count_carros = """
                                    SELECT COUNT(*) as total_carros
                                    FROM asignaciones a
                                    JOIN vehiculos v ON a.vehiculo_id = v.id
                                    WHERE a.parqueadero_id = %s
                                    AND a.activo = TRUE
                                    AND v.tipo_vehiculo = 'Carro'
                                """
                                count_result = self.db.fetch_one(query_count_carros, (p["id"],))
                                total_carros = count_result.get("total_carros", 0) if count_result else 0

                                # Solo continuar si tiene EXACTAMENTE 1 carro (no 2 o más)
                                if total_carros == 1:
                                    # VALIDACIÓN 2 (CRÍTICA): Verificar que el carro asignado NO tenga excepción
                                    # Si el parqueadero tiene un vehículo con excepción, NO debe mostrarse a nadie más
                                    query_check_excepcion = """
                                        SELECT v.tipo_circulacion,
                                               f.pico_placa_solidario,
                                               f.discapacidad,
                                               f.tiene_parqueadero_exclusivo
                                        FROM asignaciones a
                                        JOIN vehiculos v ON a.vehiculo_id = v.id
                                        JOIN funcionarios f ON v.funcionario_id = f.id
                                        WHERE a.parqueadero_id = %s
                                        AND a.activo = TRUE
                                        AND v.tipo_vehiculo = 'Carro'
                                        LIMIT 1
                                    """
                                    vehiculo_en_parqueadero = self.db.fetch_one(query_check_excepcion, (p["id"],))

                                    if vehiculo_en_parqueadero:
                                        tiene_excepcion_en_parqueadero = (
                                            vehiculo_en_parqueadero.get("pico_placa_solidario", False) or
                                            vehiculo_en_parqueadero.get("discapacidad", False) or
                                            vehiculo_en_parqueadero.get("tipo_circulacion") == "HÍBRIDO" or
                                            vehiculo_en_parqueadero.get("tiene_parqueadero_exclusivo", False)
                                        )

                                        # Si el vehículo en el parqueadero tiene excepción, NO agregar este parqueadero
                                        if not tiene_excepcion_en_parqueadero:
                                            parqueaderos_complemento_sotano.append(p)
                                        else:
                                            pass  # Parqueadero con vehiculo con excepcion, no agregar

                        todos_parqueaderos.update({p["id"]: p for p in parqueaderos_complemento_sotano})

                # Para MOTOS y BICICLETAS: solo buscar completamente disponibles
                else:
                    # Motos y bicicletas solo ocupan parqueaderos disponibles (estado='Disponible')
                    parqueaderos_disponibles = self.parqueadero_model.obtener_todos(
                        sotano=sotano_seleccionado, tipo_vehiculo=tipo_vehiculo, estado="Disponible"
                    )
                    todos_parqueaderos = {p["id"]: p for p in parqueaderos_disponibles}

                # Llenar el combo con los parqueaderos encontrados
                for park in sorted(todos_parqueaderos.values(), key=lambda x: x["numero_parqueadero"]):
                    estado_str = park.get("estado_display", park["estado"]).replace("_", " ")
                    texto = f"{format_numero_parqueadero(park['numero_parqueadero'])} ({estado_str})"
                    self.combo_parqueadero_disponible.addItem(texto, park["id"])

        except Exception as e:
            print(f"Error al cargar parqueaderos por sótano: {e}")

    def mostrar_info_vehiculo_seleccionado(self):
        """Carga parqueaderos cuando se selecciona un vehículo (mantiene compatibilidad)"""
        # Cargar parqueaderos si ya hay un sótano seleccionado
        if self.combo_sotano.currentData():
            self.cargar_parqueaderos_por_sotano()
        else:
            self.combo_parqueadero_disponible.clear()

    def cargar_parqueaderos_disponibles(self, tipo_circulacion: str):
        """Carga los parqueaderos disponibles para el tipo de circulación

        Busca:
        1. Parqueaderos completamente disponibles
        2. Parqueaderos parcialmente asignados que necesiten el complemento PAR/IMPAR

        Los estados se basan únicamente en la ocupación por carros.
        """
        # Obtener parqueaderos disponibles o que necesiten el complemento
        parqueaderos_disponibles = self.parqueadero_model.obtener_disponibles()
        parqueaderos_complemento = self.parqueadero_model.obtener_disponibles(tipo_circulacion)

        # Combinar listas sin duplicados
        todos_parqueaderos = {p["id"]: p for p in parqueaderos_disponibles}
        todos_parqueaderos.update({p["id"]: p for p in parqueaderos_complemento})

        self.combo_parqueadero_disponible.clear()
        self.combo_parqueadero_disponible.addItem("-- Seleccione --", None)

        for park in sorted(todos_parqueaderos.values(), key=lambda x: x["numero_parqueadero"]):
            texto = f"{format_numero_parqueadero(park['numero_parqueadero'])} ({park['estado'].replace('_', ' ')})"
            self.combo_parqueadero_disponible.addItem(texto, park["id"])

    def realizar_asignacion(self):
        """Realiza la asignación del vehículo al parqueadero con validaciones de permite_compartir"""
        vehiculo_data = self.combo_vehiculo_sin_asignar.currentData()
        parqueadero_id = self.combo_parqueadero_disponible.currentData()
        sotano_seleccionado = self.combo_sotano.currentData()
        observaciones = self.txt_observaciones.toPlainText().strip()

        print(f"  Vehículo data: {vehiculo_data}")
        print(f"  Sótano: {sotano_seleccionado}")

        if not vehiculo_data or not parqueadero_id or not sotano_seleccionado:
            UIDialogs.show_warning(
                self,
                "Asignacion de Parqueadero",
                "Debe seleccionar un vehiculo, un sotano y un parqueadero\n\n"
                "Solo los carros requieren asignacion de parqueadero\n"
                "Motos y bicicletas no ocupan espacios de parqueadero",
            )
            return

        # ========== OBTENER DATOS DEL FUNCIONARIO ==========
        pico_placa_solidario = vehiculo_data.get("pico_placa_solidario", False)
        discapacidad = vehiculo_data.get("discapacidad", False)

        # Realizar asignación usando el modelo (validaciones adicionales en modelo)
        exito, mensaje = self.parqueadero_model.asignar_vehiculo(vehiculo_data["id"], parqueadero_id, observaciones)

        if exito:
            # Agregar indicadores al mensaje si aplica
            msg_extra = []
            if pico_placa_solidario:
                msg_extra.append("🔄 Pico y placa solidario activado")
            if discapacidad:
                msg_extra.append("♿ Funcionario con discapacidad")

            mensaje_final = mensaje
            if msg_extra:
                mensaje_final += "\n\nℹ️ Información adicional:\n" + "\n".join(f"   • {info}" for info in msg_extra)

            # Limpiar campos después de asignación exitosa
            self.txt_observaciones.clear()
            UIDialogs.show_success(self, "Asignacion Exitosa", mensaje_final)
            self.cargar_vehiculos_sin_asignar()
            self.cargar_asignaciones()
            self.cargar_parqueaderos_por_sotano()  # Actualizar parqueaderos disponibles del sótano
            # Emitir señal para actualizar otros módulos
            self.asignacion_actualizada.emit()
        else:
            UIDialogs.show_error(self, "Error en Asignacion", mensaje)

    def cargar_asignaciones(self):
        """Carga las asignaciones actuales en la tabla"""
        try:
            # Forzar reconexión para ver commits frescos de otros threads
            self.db.force_reconnect()

            # Verificar si existe la columna sotano
            check_query = "SHOW COLUMNS FROM parqueaderos LIKE 'sotano'"
            column_exists = self.db.fetch_one(check_query) is not None

            if column_exists:
                query = """
                    SELECT
                        COALESCE(p.sotano, 'Sótano-1') as sotano,
                        p.numero_parqueadero,
                        p.estado as estado_parqueadero,
                        CONCAT(f.nombre, ' ', f.apellidos) as funcionario,
                        f.cedula,
                        f.cargo,
                        f.pico_placa_solidario,
                        f.discapacidad,
                        v.tipo_vehiculo,
                        v.placa,
                        v.tipo_circulacion,
                        COALESCE(a.observaciones, '') as observaciones,
                        a.estado_manual,
                        v.id as vehiculo_id
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    JOIN funcionarios f ON v.funcionario_id = f.id
                    JOIN parqueaderos p ON a.parqueadero_id = p.id
                    WHERE a.activo = TRUE
                    ORDER BY COALESCE(p.sotano, 'Sótano-1'), p.numero_parqueadero, v.tipo_circulacion
                """
            else:
                query = """
                    SELECT
                        'Sótano-1' as sotano,
                        p.numero_parqueadero,
                        p.estado as estado_parqueadero,
                        CONCAT(f.nombre, ' ', f.apellidos) as funcionario,
                        f.cedula,
                        f.cargo,
                        f.pico_placa_solidario,
                        f.discapacidad,
                        v.tipo_vehiculo,
                        v.placa,
                        v.tipo_circulacion,
                        COALESCE(a.observaciones, '') as observaciones,
                        NULL as estado_manual,
                        v.id as vehiculo_id
                    FROM asignaciones a
                    JOIN vehiculos v ON a.vehiculo_id = v.id
                    JOIN funcionarios f ON v.funcionario_id = f.id
                    JOIN parqueaderos p ON a.parqueadero_id = p.id
                    WHERE a.activo = TRUE
                    ORDER BY p.numero_parqueadero, v.tipo_circulacion
                """

            asignaciones = self.db.fetch_all(query)
            self.asignaciones_completas = asignaciones  # Guardar lista completa
            self.mostrar_asignaciones(asignaciones)

        except Exception as e:
            print(f"Error al cargar asignaciones: {e}")
            # Fallback con estructura anterior
            asignaciones = []
            self.asignaciones_completas = []
            self.tabla_asignaciones.setRowCount(0)

    def mostrar_asignaciones(self, asignaciones):
        """Muestra las asignaciones en la tabla con paginación"""
        # Guardar todas las asignaciones para paginación
        self.asignaciones_para_mostrar = asignaciones

        # Calcular total de páginas
        total_asignaciones = len(asignaciones)
        self.total_paginas = max(1, (total_asignaciones + self.filas_por_pagina - 1) // self.filas_por_pagina)

        # Ajustar página actual si es necesario
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = max(1, self.total_paginas)

        # Calcular índices para la página actual
        inicio = (self.pagina_actual - 1) * self.filas_por_pagina
        fin = min(inicio + self.filas_por_pagina, total_asignaciones)

        # Obtener asignaciones de la página actual
        asignaciones_pagina = asignaciones[inicio:fin]

        # Actualizar información de paginación
        self.actualizar_info_paginacion()

        # Mostrar solo las asignaciones de la página actual
        self.tabla_asignaciones.setRowCount(len(asignaciones_pagina))

        for i, asig in enumerate(asignaciones_pagina):
            # Crear items con alineación centrada y formato mejorado
            sotano_item = QTableWidgetItem(asig["sotano"])
            sotano_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter
            self.tabla_asignaciones.setItem(i, 0, sotano_item)

            # Indicador de parqueadero con estado manual si aplica
            parqueadero_texto = f"{format_numero_parqueadero(asig['numero_parqueadero'])}"
            if asig.get("estado_manual") == "Completo":
                parqueadero_texto += " 🚫"  # Indicador de exclusivo

            parqueadero_item = QTableWidgetItem(parqueadero_texto)
            parqueadero_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter

            # Colorear si es parqueadero completo por estado manual
            if asig.get("estado_parqueadero") == "Completo" and asig.get("estado_manual"):
                parqueadero_item.setBackground(QBrush(QColor("#fadbd8")))
                parqueadero_item.setForeground(QBrush(QColor("#c0392b")))

            self.tabla_asignaciones.setItem(i, 1, parqueadero_item)

            # Agregar indicadores visuales al nombre del funcionario
            funcionario_texto = asig["funcionario"]
            indicadores = []
            if asig.get("pico_placa_solidario"):
                indicadores.append("🔄")
            if asig.get("discapacidad"):
                indicadores.append("♿")

            if indicadores:
                funcionario_texto = f"{funcionario_texto} {' '.join(indicadores)}"

            funcionario_item = QTableWidgetItem(funcionario_texto)
            funcionario_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter

            self.tabla_asignaciones.setItem(i, 2, funcionario_item)

            cedula_item = QTableWidgetItem(asig["cedula"])
            cedula_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter
            self.tabla_asignaciones.setItem(i, 3, cedula_item)

            vehiculo_item = QTableWidgetItem(asig["tipo_vehiculo"])
            vehiculo_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter
            self.tabla_asignaciones.setItem(i, 4, vehiculo_item)

            placa_item = QTableWidgetItem(asig["placa"])
            placa_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter
            self.tabla_asignaciones.setItem(i, 5, placa_item)

            # Formato de circulación con color
            circulacion_item = QTableWidgetItem(asig["tipo_circulacion"])
            circulacion_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter

            if asig["tipo_circulacion"] == "PAR":
                circulacion_item.setBackground(QBrush(QColor("#e8f5e8")))
                circulacion_item.setForeground(QBrush(QColor("#2e7d32")))
            else:
                circulacion_item.setBackground(QBrush(QColor("#fff3e0")))
                circulacion_item.setForeground(QBrush(QColor("#f57c00")))
            self.tabla_asignaciones.setItem(i, 6, circulacion_item)

            # Columna de observaciones
            observaciones_text = asig.get("observaciones", "") or "Sin observaciones"
            observaciones_item = QTableWidgetItem(observaciones_text)
            observaciones_item.setTextAlignment(0x0004 | 0x0080)  # Qt.AlignCenter
            if observaciones_text == "Sin observaciones":
                observaciones_item.setForeground(QBrush(QColor("#95a5a6")))
                # No se puede usar setStyleSheet en QTableWidgetItem
            else:
                observaciones_item.setForeground(QBrush(QColor("#2c3e50")))
            self.tabla_asignaciones.setItem(i, 7, observaciones_item)

            # Botones de acción (Ver y Liberar) - Solo íconos compactos
            btn_widget = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(2)
            btn_layout.setContentsMargins(3, 3, 3, 3)

            # Botón Ver (solo ícono sin fondo)
            btn_ver = QPushButton("👁️")
            btn_ver.setFixedSize(26, 26)
            btn_ver.setToolTip("Ver detalles de la asignación")
            btn_ver.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
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
            btn_ver.clicked.connect(lambda _, asig_data=asig: self.ver_asignacion(asig_data))

            # Botón Liberar (solo ícono sin fondo)
            btn_liberar = QPushButton("🔓")
            btn_liberar.setFixedSize(26, 26)
            btn_liberar.setToolTip("Liberar asignación")
            btn_liberar.setStyleSheet(
                """
                QPushButton {
                    background-color: transparent;
                    border: none;
                    font-size: 14px;
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
            btn_liberar.clicked.connect(lambda _, vid=asig["vehiculo_id"]: self.liberar_asignacion(vid))

            btn_layout.addWidget(btn_ver)
            btn_layout.addSpacing(2)
            btn_layout.addWidget(btn_liberar)
            btn_layout.addStretch()
            btn_widget.setLayout(btn_layout)

            self.tabla_asignaciones.setCellWidget(i, 8, btn_widget)

    def filtrar_por_cedula(self):
        """Filtra las asignaciones por número de cédula"""
        cedula_buscar = self.cedula_filter.text().strip().lower()

        # Resetear a la primera página al filtrar
        self.pagina_actual = 1

        if not cedula_buscar:
            # Si no hay filtro, mostrar todas las asignaciones
            self.mostrar_asignaciones(self.asignaciones_completas)
            return

        # Filtrar asignaciones que contengan la cédula buscada
        asignaciones_filtradas = [
            asig for asig in self.asignaciones_completas if cedula_buscar in str(asig.get("cedula", "")).lower()
        ]

        self.mostrar_asignaciones(asignaciones_filtradas)

    def limpiar_filtro(self):
        """Limpia el filtro de búsqueda"""
        self.cedula_filter.clear()
        self.pagina_actual = 1
        self.mostrar_asignaciones(self.asignaciones_completas)

    def ver_asignacion(self, asignacion_data):
        """Abre el modal para ver los detalles de una asignación"""
        try:
            modal = VerAsignacionModal(asignacion_data, self)
            modal.exec_()
        except Exception as e:
            UIDialogs.show_error(self, "Error", f"Error al abrir el modal de visualizacion: {str(e)}")

    def liberar_asignacion(self, vehiculo_id: int):
        """Libera la asignación de un vehículo"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Liberar Asignación")
        msg_box.setText("¿Está seguro de que desea liberar esta asignación?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Sí")
        msg_box.button(QMessageBox.No).setText("No")
        msg_box.setDefaultButton(QMessageBox.No)

        if msg_box.exec_() == QMessageBox.Yes:
            if self.parqueadero_model.liberar_asignacion(vehiculo_id):
                UIDialogs.show_success(self, "Exito", "Asignacion liberada correctamente")
                self.cargar_asignaciones()
                self.cargar_vehiculos_sin_asignar()
                self.cargar_parqueaderos_por_sotano()  # Actualizar parqueaderos disponibles
                # Emitir señal para actualizar otros módulos
                self.asignacion_actualizada.emit()
            else:
                UIDialogs.show_error(self, "Error", "No se pudo liberar la asignacion")

    def actualizar_vehiculos_sin_asignar(self):
        """Actualiza la lista de vehículos sin asignar cuando se actualicen los datos"""
        # FORZAR reconexión para ver commits de otros threads
        self.db.force_reconnect()
        self.cargar_vehiculos_sin_asignar()

    def editar_asignacion(self, asignacion_data):
        """Abre el diálogo de edición para una asignación"""
        try:
            dialog = EditarAsignacionDialog(asignacion_data, self.db, self.parqueadero_model, self)
            if dialog.exec_() == QDialog.Accepted:
                # Actualizar la tabla después de los cambios
                self.cargar_asignaciones()
                self.cargar_vehiculos_sin_asignar()
                # Emitir señal para actualizar otros módulos
                self.asignacion_actualizada.emit()

        except Exception as e:
            UIDialogs.show_error(self, "Error", f"Error al abrir editor: {str(e)}")

    def actualizar_asignaciones(self):
        """Actualiza completamente la pestaña de asignaciones"""
        self.cargar_vehiculos_sin_asignar()
        self.cargar_asignaciones()
        # Limpiar campos
        self.txt_observaciones.clear()
        self.cedula_filter.clear()

    # ========== FUNCIONES DE PAGINACIÓN ==========

    def actualizar_info_paginacion(self):
        """Actualiza los labels y botones de paginación"""
        total_asignaciones = len(self.asignaciones_para_mostrar) if hasattr(self, 'asignaciones_para_mostrar') else 0

        # Actualizar label de página
        self.lbl_info_pagina.setText(f"Página {self.pagina_actual} de {self.total_paginas}")

        # Actualizar label de total
        self.lbl_total_registros.setText(f"Total: {total_asignaciones} asignaciones")

        # Habilitar/deshabilitar botones según la página actual
        self.btn_primera_pagina.setEnabled(self.pagina_actual > 1)
        self.btn_anterior.setEnabled(self.pagina_actual > 1)
        self.btn_siguiente.setEnabled(self.pagina_actual < self.total_paginas)
        self.btn_ultima_pagina.setEnabled(self.pagina_actual < self.total_paginas)

    def pagina_anterior(self):
        """Navega a la página anterior"""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.mostrar_asignaciones(self.asignaciones_para_mostrar)

    def pagina_siguiente(self):
        """Navega a la página siguiente"""
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.mostrar_asignaciones(self.asignaciones_para_mostrar)

    def ir_primera_pagina(self):
        """Navega a la primera página"""
        if self.pagina_actual != 1:
            self.pagina_actual = 1
            self.mostrar_asignaciones(self.asignaciones_para_mostrar)

    def ir_ultima_pagina(self):
        """Navega a la última página"""
        if self.pagina_actual != self.total_paginas:
            self.pagina_actual = self.total_paginas
            self.mostrar_asignaciones(self.asignaciones_para_mostrar)
