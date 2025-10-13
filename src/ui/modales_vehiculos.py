# -*- coding: utf-8 -*-
"""
Modales para CRUD de vehículos
Incluye modales para editar y eliminar vehículos
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
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
    QVBoxLayout,
)

from ..models.funcionario import FuncionarioModel
from ..models.vehiculo import VehiculoModel


class EditarVehiculoModal(QDialog):
    """Modal para editar un vehículo existente"""

    vehiculo_actualizado = pyqtSignal()

    def __init__(
        self, vehiculo_id: int, vehiculo_model: VehiculoModel, funcionario_model: FuncionarioModel, parent=None
    ):
        super().__init__(parent)
        self.vehiculo_id = vehiculo_id
        self.vehiculo_model = vehiculo_model
        self.funcionario_model = funcionario_model
        self.vehiculo_actual = None

        self.setup_ui()
        self.cargar_datos_vehiculo()
        self.cargar_funcionarios()
        self.conectar_eventos()

    def setup_ui(self):
        """Configura la interfaz del modal"""
        self.setWindowTitle("Editar Vehículo")
        self.setModal(True)
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Editar Vehículo")
        font_titulo = QFont()
        font_titulo.setPointSize(14)
        font_titulo.setBold(True)
        titulo.setFont(font_titulo)
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Información actual del vehículo
        self.grupo_info = QGroupBox("Información Actual")
        info_layout = QGridLayout()

        self.lbl_info_actual = QLabel("")
        self.lbl_info_actual.setWordWrap(True)
        self.lbl_info_actual.setStyleSheet(
            "color: #666; font-size: 11px; padding: 8px; background-color: #f5f5f5; border-radius: 4px;"
        )
        info_layout.addWidget(self.lbl_info_actual, 0, 0, 1, 2)

        self.grupo_info.setLayout(info_layout)
        layout.addWidget(self.grupo_info)

        # Formulario de edición
        form_group = QGroupBox("Nuevos Datos")
        form_layout = QGridLayout()

        # Funcionario
        form_layout.addWidget(QLabel("Funcionario:"), 0, 0)
        self.combo_funcionario = QComboBox()
        form_layout.addWidget(self.combo_funcionario, 0, 1)

        # Tipo de vehículo
        form_layout.addWidget(QLabel("Tipo de Vehículo:"), 1, 0)
        self.combo_tipo_vehiculo = QComboBox()
        self.combo_tipo_vehiculo.addItems(["Carro", "Moto", "Bicicleta"])
        form_layout.addWidget(self.combo_tipo_vehiculo, 1, 1)

        # Placa
        form_layout.addWidget(QLabel("Placa:"), 2, 0)
        self.txt_placa = QLineEdit()
        self.txt_placa.setPlaceholderText("Ej: ABC123")
        form_layout.addWidget(self.txt_placa, 2, 1)

        # Label informativo de pico y placa
        self.lbl_info_pico = QLabel("")
        self.lbl_info_pico.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.lbl_info_pico.setWordWrap(True)
        form_layout.addWidget(self.lbl_info_pico, 3, 0, 1, 2)

        # Label de validación
        self.lbl_validacion = QLabel("")
        self.lbl_validacion.setStyleSheet(
            "font-size: 11px; color: #666; background-color: #f0f8ff; padding: 8px; border-radius: 4px;"
        )
        self.lbl_validacion.setWordWrap(True)
        form_layout.addWidget(self.lbl_validacion, 4, 0, 1, 2)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Botones
        btn_layout = QHBoxLayout()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        self.btn_guardar.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }"
        )

        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def cargar_datos_vehiculo(self):
        """Carga los datos actuales del vehículo"""
        self.vehiculo_actual = self.vehiculo_model.obtener_por_id(self.vehiculo_id)

        if not self.vehiculo_actual:
            QMessageBox.critical(self, "Error", "No se pudo cargar la información del vehículo")
            self.reject()
            return

        # Mostrar información actual
        info_text = f"""
        Funcionario: {self.vehiculo_actual['nombre']} {self.vehiculo_actual['apellidos']} ({self.vehiculo_actual['cedula']})
        Tipo: {self.vehiculo_actual['tipo_vehiculo']}
        Placa Actual: {self.vehiculo_actual['placa']}
        Circulación: {self.vehiculo_actual['tipo_circulacion']}
        Parqueadero: {self.vehiculo_actual.get('numero_parqueadero', 'Sin asignar')}
        """
        self.lbl_info_actual.setText(info_text.strip())

        # Precargar formulario con datos actuales
        self.combo_tipo_vehiculo.setCurrentText(self.vehiculo_actual["tipo_vehiculo"])
        self.txt_placa.setText(self.vehiculo_actual["placa"])

    def cargar_funcionarios(self):
        """Carga el combo de funcionarios"""
        funcionarios = self.funcionario_model.obtener_todos()

        self.combo_funcionario.clear()

        for func in funcionarios:
            texto = f"{func['cedula']} - {func['nombre']} {func['apellidos']}"
            self.combo_funcionario.addItem(texto, func["id"])

            # Seleccionar el funcionario actual
            if func["id"] == self.vehiculo_actual["funcionario_id"]:
                self.combo_funcionario.setCurrentText(texto)

    def conectar_eventos(self):
        """Conecta los eventos del formulario"""
        self.txt_placa.textChanged.connect(self.actualizar_info_pico_placa)
        self.txt_placa.textChanged.connect(self.validar_en_tiempo_real)
        self.combo_funcionario.currentIndexChanged.connect(self.validar_en_tiempo_real)
        self.combo_tipo_vehiculo.currentTextChanged.connect(self.validar_en_tiempo_real)

    def actualizar_info_pico_placa(self):
        """Actualiza la información de pico y placa"""
        placa = self.txt_placa.text()

        if placa and self.combo_tipo_vehiculo.currentText() == "Carro":
            ultimo_digito = placa[-1] if placa else ""

            if ultimo_digito.isdigit() or ultimo_digito == "0":
                if ultimo_digito in "12345":
                    self.lbl_info_pico.setText(
                        f"Placa terminada en {ultimo_digito}: Circula días IMPARES (Tipo: IMPAR)"
                    )
                    self.lbl_info_pico.setStyleSheet("font-weight: bold; color: #FF9800;")
                else:
                    self.lbl_info_pico.setText(f"Placa terminada en {ultimo_digito}: Circula días PARES (Tipo: PAR)")
                    self.lbl_info_pico.setStyleSheet("font-weight: bold; color: #2196F3;")
        else:
            self.lbl_info_pico.clear()

    def validar_en_tiempo_real(self):
        """Valida el vehículo en tiempo real"""
        if self.combo_funcionario.currentData() is None:
            self.lbl_validacion.setText("Seleccione un funcionario")
            self.btn_guardar.setEnabled(False)
            return

        funcionario_id = self.combo_funcionario.currentData()
        tipo_vehiculo = self.combo_tipo_vehiculo.currentText()
        placa = self.txt_placa.text().strip()

        if not placa:
            self.lbl_validacion.setText("Ingrese una placa")
            self.btn_guardar.setEnabled(False)
            return

        # Validar si hay cambios
        hay_cambios = (
            funcionario_id != self.vehiculo_actual["funcionario_id"]
            or tipo_vehiculo != self.vehiculo_actual["tipo_vehiculo"]
            or placa.upper() != self.vehiculo_actual["placa"]
        )

        if not hay_cambios:
            self.lbl_validacion.setText("No hay cambios para guardar")
            self.btn_guardar.setEnabled(False)
            return

        # Validar placa única (excluyendo el vehículo actual)
        es_unica, mensaje_placa = self.vehiculo_model.validar_placa_unica(placa, self.vehiculo_id)
        if not es_unica:
            self.lbl_validacion.setText(f"❌ {mensaje_placa}")
            self.lbl_validacion.setStyleSheet(
                "font-size: 11px; color: #f44336; background-color: #ffebee; padding: 8px; border-radius: 4px;"
            )
            self.btn_guardar.setEnabled(False)
            return

        # Obtener otros vehículos del funcionario (excluyendo el actual)
        vehiculos_funcionario = self.vehiculo_model.obtener_por_funcionario(funcionario_id)
        otros_vehiculos = [v for v in vehiculos_funcionario if v["id"] != self.vehiculo_id]

        # Validar reglas de negocio (excluyendo el vehículo actual)
        from ..utils.validaciones_vehiculos import ValidadorVehiculos

        validador = ValidadorVehiculos()
        es_valido, mensaje = validador.validar_registro_vehiculo(otros_vehiculos, tipo_vehiculo, placa)

        if es_valido:
            self.lbl_validacion.setText("✅ Validación exitosa - Listo para guardar")
            self.lbl_validacion.setStyleSheet(
                "font-size: 11px; color: #4CAF50; background-color: #e8f5e8; padding: 8px; border-radius: 4px;"
            )
            self.btn_guardar.setEnabled(True)
        else:
            self.lbl_validacion.setText(f"❌ {mensaje}")
            self.lbl_validacion.setStyleSheet(
                "font-size: 11px; color: #f44336; background-color: #ffebee; padding: 8px; border-radius: 4px;"
            )
            self.btn_guardar.setEnabled(False)

    def guardar_cambios(self):
        """Guarda los cambios del vehículo"""
        funcionario_id = self.combo_funcionario.currentData()
        tipo_vehiculo = self.combo_tipo_vehiculo.currentText()
        placa = self.txt_placa.text().strip()

        if not funcionario_id or not placa:
            QMessageBox.warning(
                self,
                "📝 Campos Requeridos",
                "🚫 Por favor complete todos los campos obligatorios\n\n"
                f"👤 Funcionario: {'✅' if funcionario_id else '❌'}\n"
                f"🏷️ Placa: {'✅' if placa else '❌'}\n\n"
                "💡 Todos los campos son necesarios para actualizar el vehículo",
            )
            return

        # Intentar actualizar
        exito, mensaje = self.vehiculo_model.actualizar(self.vehiculo_id, funcionario_id, tipo_vehiculo, placa)

        if exito:
            QMessageBox.information(self, "✅ Vehículo Actualizado", mensaje)
            self.vehiculo_actualizado.emit()
            self.accept()
        else:
            QMessageBox.warning(self, "🚫 Error de Validación", mensaje)


class EliminarVehiculoModal(QDialog):
    """Modal para confirmar eliminación de vehículo"""

    vehiculo_eliminado = pyqtSignal()

    def __init__(self, vehiculo_id: int, vehiculo_model: VehiculoModel, parent=None):
        super().__init__(parent)
        self.vehiculo_id = vehiculo_id
        self.vehiculo_model = vehiculo_model
        self.vehiculo_actual = None

        self.setup_ui()
        self.cargar_datos_vehiculo()

    def setup_ui(self):
        """Configura la interfaz del modal"""
        self.setWindowTitle("Eliminar Vehículo")
        self.setModal(True)
        self.setFixedSize(450, 350)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Confirmar Eliminación")
        font_titulo = QFont()
        font_titulo.setPointSize(14)
        font_titulo.setBold(True)
        titulo.setFont(font_titulo)
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #d32f2f;")
        layout.addWidget(titulo)

        # Línea separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Información del vehículo
        self.grupo_info = QGroupBox("Información del Vehículo a Eliminar")
        info_layout = QVBoxLayout()

        self.lbl_info_vehiculo = QLabel("")
        self.lbl_info_vehiculo.setWordWrap(True)
        self.lbl_info_vehiculo.setStyleSheet(
            "font-size: 12px; padding: 12px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;"
        )
        info_layout.addWidget(self.lbl_info_vehiculo)

        self.grupo_info.setLayout(info_layout)
        layout.addWidget(self.grupo_info)

        # Advertencia
        advertencia = QLabel("ADVERTENCIA: Esta accion NO se puede deshacer")
        advertencia.setStyleSheet(
            "color: #d32f2f; font-weight: bold; font-size: 12px; padding: 8px; background-color: #ffebee; border-radius: 4px;"
        )
        advertencia.setAlignment(Qt.AlignCenter)
        layout.addWidget(advertencia)

        # Opciones de eliminación
        opciones_group = QGroupBox("Tipo de Eliminación")
        opciones_layout = QVBoxLayout()

        # Información sobre los tipos
        info_tipos = QLabel(
            """
- Eliminacion Logica: El vehiculo se desactiva pero permanece en la base de datos para historial
- Eliminacion Fisica: El vehiculo se borra completamente de la base de datos
        """
        )
        info_tipos.setStyleSheet("font-size: 10px; color: #666; padding: 8px;")
        opciones_layout.addWidget(info_tipos)

        self.btn_eliminar_logico = QPushButton("Eliminacion Logica (Recomendado)")
        self.btn_eliminar_logico.clicked.connect(self.eliminar_logico)
        self.btn_eliminar_logico.setStyleSheet(
            "QPushButton { background-color: #ff9800; color: white; font-weight: bold; padding: 8px; }"
        )

        self.btn_eliminar_fisico = QPushButton("Eliminacion Fisica (Permanente)")
        self.btn_eliminar_fisico.clicked.connect(self.eliminar_fisico)
        self.btn_eliminar_fisico.setStyleSheet(
            "QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; }"
        )

        opciones_layout.addWidget(self.btn_eliminar_logico)
        opciones_layout.addWidget(self.btn_eliminar_fisico)

        opciones_group.setLayout(opciones_layout)
        layout.addWidget(opciones_group)

        # Botón cancelar
        btn_layout = QHBoxLayout()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_cancelar.setStyleSheet("QPushButton { background-color: #6c757d; color: white; padding: 8px; }")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancelar)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def cargar_datos_vehiculo(self):
        """Carga los datos del vehículo a eliminar"""
        self.vehiculo_actual = self.vehiculo_model.obtener_por_id(self.vehiculo_id)

        if not self.vehiculo_actual:
            QMessageBox.critical(self, "Error", "No se pudo cargar la información del vehículo")
            self.reject()
            return

        # Mostrar información del vehículo
        info_text = f"""
Funcionario: {self.vehiculo_actual['nombre']} {self.vehiculo_actual['apellidos']}
Cédula: {self.vehiculo_actual['cedula']}
Tipo: {self.vehiculo_actual['tipo_vehiculo']}
Placa: {self.vehiculo_actual['placa']}
Circulación: {self.vehiculo_actual['tipo_circulacion']}
Parqueadero: {self.vehiculo_actual.get('numero_parqueadero', 'Sin asignar')}
        """
        self.lbl_info_vehiculo.setText(info_text.strip())

    def eliminar_logico(self):
        """Ejecuta eliminación lógica del vehículo"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminacion Logica",
            f"Esta seguro de que desea eliminar el vehiculo {self.vehiculo_actual['placa']}?\n\n"
            "El vehiculo se desactivara pero permanecera en la base de datos.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if respuesta == QMessageBox.Yes:
            exito, mensaje = self.vehiculo_model.eliminar(self.vehiculo_id)

            if exito:
                QMessageBox.information(self, "✅ Vehículo Eliminado", mensaje)
                self.vehiculo_eliminado.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "🚫 Error de Eliminación", mensaje)

    def eliminar_fisico(self):
        """Ejecuta eliminación física del vehículo"""
        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminacion Fisica",
            f"Esta ABSOLUTAMENTE seguro de que desea eliminar PERMANENTEMENTE el vehiculo {self.vehiculo_actual['placa']}?\n\n"
            "ESTA ACCION NO SE PUEDE DESHACER\n"
            "El vehiculo se borrara completamente de la base de datos.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if respuesta == QMessageBox.Yes:
            # Doble confirmación para eliminación física
            respuesta2 = QMessageBox.question(
                self,
                "ULTIMA CONFIRMACION",
                f"ULTIMA OPORTUNIDAD:\n\n"
                f"Realmente desea BORRAR PERMANENTEMENTE el vehiculo {self.vehiculo_actual['placa']}?\n\n"
                "Esta completamente seguro?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if respuesta2 == QMessageBox.Yes:
                exito, mensaje = self.vehiculo_model.eliminar_fisico(self.vehiculo_id)

                if exito:
                    QMessageBox.information(self, "Exito", mensaje)
                    self.vehiculo_eliminado.emit()
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", mensaje)


class VerVehiculoModal(QDialog):
    """Modal para visualizar los detalles de un vehículo"""

    def __init__(
        self, vehiculo_id: int, vehiculo_model: VehiculoModel, funcionario_model: FuncionarioModel, parent=None
    ):
        super().__init__(parent)
        self.vehiculo_id = vehiculo_id
        self.vehiculo_model = vehiculo_model
        self.funcionario_model = funcionario_model
        self.vehiculo_actual = None

        self.setup_ui()
        self.cargar_datos_vehiculo()

    def setup_ui(self):
        """Configura la interfaz del modal"""
        self.setWindowTitle("Detalles del Vehículo")
        self.setModal(True)
        self.setFixedSize(500, 450)

        layout = QVBoxLayout()

        # Título
        titulo = QLabel("📋 Información del Vehículo")
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

        # Grupo de información del funcionario
        grupo_funcionario = QGroupBox("👤 Información del Propietario")
        form_funcionario = QFormLayout()
        form_funcionario.setSpacing(10)

        self.lbl_nombre = QLabel("")
        self.lbl_nombre.setStyleSheet("font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        form_funcionario.addRow("Nombre completo:", self.lbl_nombre)

        self.lbl_cedula = QLabel("")
        self.lbl_cedula.setStyleSheet("font-size: 12px; padding: 5px; background-color: #ecf0f1; border-radius: 3px;")
        form_funcionario.addRow("Cédula:", self.lbl_cedula)

        grupo_funcionario.setLayout(form_funcionario)
        layout.addWidget(grupo_funcionario)

        # Grupo de información del vehículo
        grupo_vehiculo = QGroupBox("🚗 Información del Vehículo")
        form_vehiculo = QFormLayout()
        form_vehiculo.setSpacing(10)

        self.lbl_tipo = QLabel("")
        self.lbl_tipo.setStyleSheet("font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px;")
        form_vehiculo.addRow("Tipo de vehículo:", self.lbl_tipo)

        self.lbl_placa = QLabel("")
        self.lbl_placa.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px; font-weight: bold;"
        )
        form_vehiculo.addRow("Placa:", self.lbl_placa)

        self.lbl_ultimo_digito = QLabel("")
        self.lbl_ultimo_digito.setStyleSheet(
            "font-size: 12px; padding: 5px; background-color: #e8f5e8; border-radius: 3px;"
        )
        form_vehiculo.addRow("Último dígito:", self.lbl_ultimo_digito)

        self.lbl_circulacion = QLabel("")
        self.lbl_circulacion.setStyleSheet("font-size: 12px; padding: 5px; border-radius: 3px; font-weight: bold;")
        form_vehiculo.addRow("Tipo de circulación:", self.lbl_circulacion)

        grupo_vehiculo.setLayout(form_vehiculo)
        layout.addWidget(grupo_vehiculo)

        # Grupo de información del parqueadero
        grupo_parqueadero = QGroupBox("🅿️ Información del Parqueadero")
        form_parqueadero = QFormLayout()
        form_parqueadero.setSpacing(10)

        self.lbl_parqueadero = QLabel("")
        self.lbl_parqueadero.setStyleSheet("font-size: 12px; padding: 5px; border-radius: 3px; font-weight: bold;")
        form_parqueadero.addRow("Parqueadero asignado:", self.lbl_parqueadero)

        grupo_parqueadero.setLayout(form_parqueadero)
        layout.addWidget(grupo_parqueadero)

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

    def cargar_datos_vehiculo(self):
        """Carga los datos del vehículo"""
        self.vehiculo_actual = self.vehiculo_model.obtener_por_id(self.vehiculo_id)

        if not self.vehiculo_actual:
            QMessageBox.critical(self, "Error", "No se pudo cargar la información del vehículo")
            self.reject()
            return

        # Cargar información del funcionario
        nombre_completo = f"{self.vehiculo_actual['nombre']} {self.vehiculo_actual['apellidos']}"
        self.lbl_nombre.setText(nombre_completo)
        self.lbl_cedula.setText(self.vehiculo_actual["cedula"])

        # Cargar información del vehículo
        self.lbl_tipo.setText(self.vehiculo_actual["tipo_vehiculo"])
        self.lbl_placa.setText(self.vehiculo_actual["placa"])
        self.lbl_ultimo_digito.setText(str(self.vehiculo_actual.get("ultimo_digito", "N/A")))

        # Tipo de circulación con color
        circulacion = self.vehiculo_actual.get("tipo_circulacion", "N/A")
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

        # Información del parqueadero
        parqueadero = self.vehiculo_actual.get("numero_parqueadero")
        if parqueadero:
            self.lbl_parqueadero.setText(f"P-{parqueadero:03d}")
            self.lbl_parqueadero.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #e3f2fd; color: #1976d2; border-radius: 3px; font-weight: bold;"
            )
        else:
            self.lbl_parqueadero.setText("Sin asignar")
            self.lbl_parqueadero.setStyleSheet(
                "font-size: 12px; padding: 5px; background-color: #ffebee; color: #d32f2f; border-radius: 3px; font-weight: bold;"
            )
