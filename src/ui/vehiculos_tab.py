# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Vehículos del sistema de gestión de parqueadero
"""

from PyQt5.QtCore import pyqtSignal, Qt, QThread, pyqtSlot
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
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
    QApplication,
)

from ..database.manager import DatabaseManager
from ..models.funcionario import FuncionarioModel
from ..models.vehiculo import VehiculoModel
from .modales_vehiculos import EditarVehiculoModal, EliminarVehiculoModal
from ..utils.formatters import format_numero_parqueadero

# Nuevas utilidades de refactorización
from .styles import UIStyles
from .utils import UIDialogs, TableUtils, ButtonFactory


# ============================================================================
# WORKER THREADS PARA OPERACIONES ASÍNCRONAS
# ============================================================================

class GuardarVehiculoWorker(QThread):
    """Worker thread para guardar vehículo sin bloquear UI"""

    finished = pyqtSignal(bool, str)  # (exito, mensaje)

    def __init__(self, db_config, funcionario_id, tipo_vehiculo, placa):
        super().__init__()
        self.db_config = db_config
        self.funcionario_id = funcionario_id
        self.tipo_vehiculo = tipo_vehiculo
        self.placa = placa

    def run(self):
        """Ejecuta el guardado en background con conexión propia"""
        import mysql.connector

        connection = None
        try:
            # Crear conexión MySQL directa (no usar DatabaseManager por ser Singleton)
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)

            # Crear un objeto temporal tipo DatabaseManager para el modelo
            class TempDB:
                def __init__(self, conn, cur, db_cfg):
                    self.connection = conn
                    self.cursor = cur
                    # Crear objeto config con los atributos necesarios
                    self.config = type('obj', (object,), db_cfg)()

                def fetch_all(self, query, params=None):
                    self.cursor.execute(query, params or ())
                    return self.cursor.fetchall()

                def fetch_one(self, query, params=None):
                    self.cursor.execute(query, params or ())
                    return self.cursor.fetchone()

                def execute_query(self, query, params=None):
                    try:
                        self.cursor.execute(query, params or ())
                        self.connection.commit()
                        return (True, None)
                    except Exception as e:
                        self.connection.rollback()
                        return (False, str(e))

            temp_db = TempDB(connection, cursor, self.db_config)
            vehiculo_model = VehiculoModel(temp_db)

            exito, mensaje = vehiculo_model.crear(
                funcionario_id=self.funcionario_id,
                tipo_vehiculo=self.tipo_vehiculo,
                placa=self.placa
            )
            self.finished.emit(exito, mensaje)

        except Exception as e:
            self.finished.emit(False, f"Error en worker: {str(e)}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()


class CargarVehiculosWorker(QThread):
    """Worker thread para cargar vehículos sin bloquear UI"""

    finished = pyqtSignal(list)  # lista de vehículos

    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config

    def run(self):
        """Ejecuta la consulta en background con conexión propia"""
        import mysql.connector

        connection = None
        try:
            # Crear conexión MySQL directa (no usar DatabaseManager por ser Singleton)
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT
                    v.id,
                    CONCAT(f.nombre, ' ', f.apellidos) as funcionario,
                    f.cedula,
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
            cursor.execute(query)
            vehiculos = cursor.fetchall()
            self.finished.emit(vehiculos)

        except Exception:
            self.finished.emit([])
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()


class CargarComboFuncionariosWorker(QThread):
    """Worker thread optimizado para cargar funcionarios con query única"""

    finished = pyqtSignal(list)  # lista de (texto, funcionario_id)

    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config

    def run(self):
        """Ejecuta consulta optimizada en background - SIN N+1 con conexión propia"""
        import mysql.connector

        connection = None
        try:
            # Crear conexión MySQL directa (no usar DatabaseManager por ser Singleton)
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor(dictionary=True)

            # Query optimizada que obtiene TODO en una sola consulta (incluye TODOS los tipos de excepción)
            query = """
                SELECT
                    f.id,
                    f.cedula,
                    f.nombre,
                    f.apellidos,
                    f.tiene_parqueadero_exclusivo,
                    f.tiene_carro_hibrido,
                    f.pico_placa_solidario,
                    f.discapacidad,
                    f.permite_compartir,
                    COUNT(CASE WHEN v.tipo_vehiculo = 'Carro' THEN 1 END) as cant_carros,
                    COUNT(CASE WHEN v.tipo_vehiculo = 'Moto' THEN 1 END) as cant_motos,
                    COUNT(CASE WHEN v.tipo_vehiculo = 'Bicicleta' THEN 1 END) as cant_bicicletas
                FROM funcionarios f
                LEFT JOIN vehiculos v ON f.id = v.funcionario_id AND v.activo = TRUE
                WHERE f.activo = TRUE
                GROUP BY f.id, f.cedula, f.nombre, f.apellidos, f.tiene_parqueadero_exclusivo,
                         f.tiene_carro_hibrido, f.pico_placa_solidario, f.discapacidad, f.permite_compartir
                ORDER BY f.apellidos, f.nombre
            """

            cursor.execute(query)
            funcionarios_data = cursor.fetchall()

            # Filtrar en Python (rápido en memoria)
            resultado = []

            for func in funcionarios_data:
                funcionario_id = func["id"]

                # Obtener tipos de excepción
                tiene_exclusivo_directivo = func.get("tiene_parqueadero_exclusivo", 0) == 1
                tiene_carro_hibrido = func.get("tiene_carro_hibrido", 0) == 1
                pico_placa_solidario = func.get("pico_placa_solidario", 0) == 1
                discapacidad = func.get("discapacidad", 0) == 1
                permite_compartir = func.get("permite_compartir", 1)

                # Contadores de vehículos
                cant_carros = func.get("cant_carros", 0)
                cant_motos = func.get("cant_motos", 0)
                cant_bicicletas = func.get("cant_bicicletas", 0)
                total_vehiculos = cant_carros + cant_motos + cant_bicicletas

                # Por defecto, NO mostrar (solo mostrar si NO ha alcanzado su límite)
                mostrar_funcionario = False

                # REGLA 1: Exclusivo Directivo - Máximo 6 vehículos (4 carros + 1 moto + 1 bicicleta)
                if tiene_exclusivo_directivo:
                    # Mostrar solo si tiene menos de 6 vehículos total
                    if total_vehiculos < 6:
                        mostrar_funcionario = True

                # REGLA 2: Carro Híbrido, Pico y Placa Solidario, Discapacidad, No permite compartir
                # Estos pueden tener máximo 3 vehículos (1 carro + 1 moto + 1 bicicleta)
                elif tiene_carro_hibrido or pico_placa_solidario or discapacidad or (permite_compartir == 0):
                    # Mostrar solo si tiene menos de 3 vehículos total
                    if total_vehiculos < 3:
                        mostrar_funcionario = True

                # REGLA 3: Funcionarios regulares (sin excepciones)
                # Máximo 3 vehículos con combinaciones válidas: 1C+1M+1B, 2C+1B, o 2C+1M
                else:
                    # Mostrar solo si tiene menos de 3 vehículos total
                    if total_vehiculos < 3:
                        mostrar_funcionario = True

                if mostrar_funcionario:
                    # Construir iconos de excepciones
                    iconos = []
                    if tiene_exclusivo_directivo:
                        iconos.append('🏢')
                    if tiene_carro_hibrido:
                        iconos.append('🌿')
                    if pico_placa_solidario:
                        iconos.append('🔄')
                    if discapacidad:
                        iconos.append('♿')

                    iconos_str = ' '.join(iconos) + ' ' if iconos else ''
                    texto = f"{func['cedula']} - {func['nombre']} {func['apellidos']} {iconos_str}"
                    resultado.append((texto, funcionario_id))

            self.finished.emit(resultado)

        except Exception:
            self.finished.emit([])
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()


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

        # Guardar configuración de DB para workers (cada worker necesita su propia conexión)
        self.db_config = {
            'host': db_manager.config.host,
            'user': db_manager.config.user,
            'password': db_manager.config.password,
            'database': db_manager.config.database,
            'port': db_manager.config.port
        }

        # Workers para operaciones asíncronas
        self.guardar_worker = None
        self.cargar_vehiculos_worker = None
        self.cargar_combo_worker = None

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
        self.combo_funcionario.setFixedWidth(450)
        self.combo_funcionario.setFixedHeight(40)
        self.combo_funcionario.setStyleSheet(UIStyles.COMBOBOX)
        inputs_layout.addWidget(self.combo_funcionario)

        # Tipo de Vehículo (Label + Combo)
        lbl_tipo = QLabel("Tipo de Vehículo:")
        lbl_tipo.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        inputs_layout.addWidget(lbl_tipo)

        self.combo_tipo_vehiculo = QComboBox()
        self.combo_tipo_vehiculo.addItems(["Carro", "Moto", "Bicicleta"])
        self.combo_tipo_vehiculo.setFixedWidth(180)
        self.combo_tipo_vehiculo.setFixedHeight(40)
        self.combo_tipo_vehiculo.setStyleSheet(UIStyles.COMBOBOX)
        inputs_layout.addWidget(self.combo_tipo_vehiculo)

        # Placa (Label + Input)
        lbl_placa = QLabel("Placa:")
        lbl_placa.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        inputs_layout.addWidget(lbl_placa)

        self.txt_placa = QLineEdit()
        self.txt_placa.setPlaceholderText("Ej: ABC123")
        self.txt_placa.setFixedWidth(150)
        self.txt_placa.setFixedHeight(40)
        self.txt_placa.setStyleSheet(UIStyles.LINEEDIT)
        inputs_layout.addWidget(self.txt_placa)

        # Botón Guardar en la misma fila
        self.btn_guardar_vehiculo = ButtonFactory.create_success_button("Guardar")
        self.btn_guardar_vehiculo.clicked.connect(self.guardar_vehiculo)
        self.btn_guardar_vehiculo.setFixedHeight(40)
        self.btn_guardar_vehiculo.setFixedWidth(150)
        inputs_layout.addWidget(self.btn_guardar_vehiculo)

        inputs_layout.addStretch()
        form_layout.addLayout(inputs_layout)

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

        # Botón Importar desde Excel
        btn_importar = QPushButton("📊 Importar")
        btn_importar.setFixedHeight(35)
        btn_importar.setToolTip("Importar vehículos desde archivo Excel")
        btn_importar.setStyleSheet(
            """
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
            QPushButton:pressed {
                background-color: #117a65;
            }
        """
        )
        btn_importar.clicked.connect(self.importar_desde_excel)
        buscar_layout.addWidget(btn_importar)

        buscar_layout.addStretch()
        tabla_layout.addLayout(buscar_layout)

        self.tabla_vehiculos = QTableWidget()

        # Configurar tabla usando TableUtils
        columns = ["Funcionario", "Tipo", "Placa", "Último Dígito", "Circulación", "Parqueadero", "Acciones"]
        widths = [200, 100, 100, 120, 110, 130, 240]
        TableUtils.setup_table(self.tabla_vehiculos, columns, widths, row_height=50, stretch_last=False)

        # Configurar altura de filas fija
        altura_fila = 50

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

        # Aplicar estilo centralizado
        TableUtils.apply_default_style(self.tabla_vehiculos, header_bg="#34B5A9")

        tabla_layout.addWidget(self.tabla_vehiculos)

        # Controles de paginación
        paginacion_layout = QHBoxLayout()
        paginacion_layout.setSpacing(8)
        paginacion_layout.setContentsMargins(0, 5, 0, 0)

        # Botón Primera Página
        self.btn_primera_pagina = ButtonFactory.create_pagination_button("⏮️ Primera")
        self.btn_primera_pagina.setFixedHeight(35)
        self.btn_primera_pagina.clicked.connect(self.ir_primera_pagina)
        paginacion_layout.addWidget(self.btn_primera_pagina)

        # Botón Página Anterior
        self.btn_pagina_anterior = ButtonFactory.create_pagination_button("◀️ Anterior")
        self.btn_pagina_anterior.setFixedHeight(35)
        self.btn_pagina_anterior.clicked.connect(self.ir_pagina_anterior)
        paginacion_layout.addWidget(self.btn_pagina_anterior)

        # Label de información de página
        self.lbl_info_pagina = QLabel("Página 1 de 1")
        self.lbl_info_pagina.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        self.lbl_info_pagina.setAlignment(Qt.AlignCenter)
        paginacion_layout.addWidget(self.lbl_info_pagina)

        # Botón Página Siguiente
        self.btn_pagina_siguiente = ButtonFactory.create_pagination_button("Siguiente ▶️")
        self.btn_pagina_siguiente.setFixedHeight(35)
        self.btn_pagina_siguiente.clicked.connect(self.ir_pagina_siguiente)
        paginacion_layout.addWidget(self.btn_pagina_siguiente)

        # Botón Última Página
        self.btn_ultima_pagina = ButtonFactory.create_pagination_button("Última ⏭️")
        self.btn_ultima_pagina.setFixedHeight(35)
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
        """Carga el combo de funcionarios de forma asíncrona (Optimizado - SIN N+1)"""
        # Evitar múltiples cargas simultáneas
        if self.cargar_combo_worker and self.cargar_combo_worker.isRunning():
            return

        # Crear y ejecutar worker thread optimizado
        self.cargar_combo_worker = CargarComboFuncionariosWorker(self.db_config)
        self.cargar_combo_worker.finished.connect(self.on_combo_funcionarios_cargado)
        self.cargar_combo_worker.start()

    @pyqtSlot(list)
    def on_combo_funcionarios_cargado(self, funcionarios_lista):
        """Callback cuando termina de cargar el combo de funcionarios"""
        # Limpiar y llenar combo
        self.combo_funcionario.clear()
        self.combo_funcionario.addItem("-- Seleccione --", None)

        for texto, funcionario_id in funcionarios_lista:
            self.combo_funcionario.addItem(texto, funcionario_id)

        # Limpiar worker
        if self.cargar_combo_worker:
            self.cargar_combo_worker.deleteLater()
            self.cargar_combo_worker = None

    def guardar_vehiculo(self):
        """Guarda un nuevo vehículo con validaciones de reglas de negocio (Optimizado - Asíncrono)"""
        # Validación 1: Funcionario seleccionado
        if self.combo_funcionario.currentData() is None:
            UIDialogs.show_warning(
                self,
                "Seleccionar Funcionario",
                "Debe seleccionar un funcionario del listado.\n\n"
                "Solución: Escoja un funcionario del combo desplegable.",
            )
            return

        funcionario_id = self.combo_funcionario.currentData()
        tipo_vehiculo = self.combo_tipo_vehiculo.currentText()
        placa = self.txt_placa.text().strip().upper()

        # Validación 2: Tipo de vehículo seleccionado
        if not tipo_vehiculo:
            UIDialogs.show_warning(
                self,
                "Seleccionar Tipo de Vehículo",
                "Debe seleccionar el tipo de vehículo.\n\n"
                "Solución: Escoja Carro, Moto o Bicicleta del combo desplegable.",
            )
            return

        # Validación 3: Bicicletas NO deben tener placa
        if tipo_vehiculo == "Bicicleta" and placa:
            UIDialogs.show_warning(
                self,
                "Placa No Permitida",
                "Las bicicletas NO requieren placa.\n\n"
                "Solución: Deje el campo de placa vacío.",
            )
            return

        # Validación 4: Placa requerida para Carros y Motos
        if tipo_vehiculo in ("Carro", "Moto") and not placa:
            UIDialogs.show_warning(
                self,
                "Placa Requerida",
                f"La placa es obligatoria para vehículos tipo {tipo_vehiculo}.\n\n"
                "Formatos válidos:\n"
                "  • Carro: ABC123 (6 caracteres)\n"
                "  • Moto: XYZ12 o XYZ12A (5-6 caracteres)\n\n"
                "Solución: Ingrese la placa del vehículo.",
            )
            return

        # Validación 5: Formato de placa para Carros (3 letras + 3 números)
        if tipo_vehiculo == "Carro" and placa:
            if len(placa) != 6:
                UIDialogs.show_warning(
                    self,
                    "Formato de Placa Inválido",
                    "La placa de Carro debe tener exactamente 6 caracteres.\n\n"
                    "Formato válido: ABC123 (3 letras + 3 números)\n\n"
                    "Solución: Verifique la placa del vehículo.",
                )
                return

            # Validar patrón: 3 letras + 3 números
            if not (placa[:3].isalpha() and placa[3:].isdigit()):
                UIDialogs.show_warning(
                    self,
                    "Formato de Placa Inválido",
                    "La placa de Carro debe seguir el patrón:\n"
                    "3 letras + 3 números\n\n"
                    "Ejemplo: ABC123\n\n"
                    "Solución: Verifique que sean 3 letras seguidas de 3 números.",
                )
                return

        # Validación para Motos (3 letras + 2 números ó 3 letras + 2 números + 1 letra)
        if tipo_vehiculo == "Moto" and placa:
            valido = False

            # Patrón 1: XYZ12 (3 letras + 2 números)
            if len(placa) == 5 and placa[:3].isalpha() and placa[3:].isdigit():
                valido = True

            # Patrón 2: XYZ12A (3 letras + 2 números + 1 letra)
            elif len(placa) == 6 and placa[:3].isalpha() and placa[3:5].isdigit() and placa[5].isalpha():
                valido = True

            if not valido:
                UIDialogs.show_warning(
                    self,
                    "Formato de Placa Inválido",
                    "La placa de Moto debe seguir uno de estos patrones:\n\n"
                    "  • XYZ12 (3 letras + 2 números)\n"
                    "  • XYZ12A (3 letras + 2 números + 1 letra)\n\n"
                    "Solución: Verifique el formato de la placa.",
                )
                return

        # Validación 6: Reglas de negocio (límites de vehículos, combinaciones permitidas)
        es_valido, mensaje = self.vehiculo_model.validar_vehiculo_antes_registro(
            funcionario_id, tipo_vehiculo, placa
        )

        if not es_valido:
            UIDialogs.show_warning(
                self,
                "No se puede registrar el vehículo",
                mensaje
            )
            return

        # Todas las validaciones pasaron, proceder a guardar
        self.btn_guardar_vehiculo.setEnabled(False)
        self.btn_guardar_vehiculo.setText("Guardando...")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Crear y ejecutar worker thread para guardar
        self.guardar_worker = GuardarVehiculoWorker(
            self.db_config,
            funcionario_id,
            tipo_vehiculo,
            placa
        )
        self.guardar_worker.finished.connect(self.on_vehiculo_guardado)
        self.guardar_worker.start()

    @pyqtSlot(bool, str)
    def on_vehiculo_guardado(self, exito, mensaje):
        """Callback cuando termina el guardado en background"""
        # Restaurar cursor y botón
        QApplication.restoreOverrideCursor()
        self.btn_guardar_vehiculo.setEnabled(True)
        self.btn_guardar_vehiculo.setText("Guardar")

        if exito:
            UIDialogs.show_success(self, "Vehículo Registrado", mensaje)
            self.txt_placa.clear()
            self.combo_funcionario.setCurrentIndex(0)

            # CRÍTICO: FORZAR reconexión para ver commits del worker
            # El worker hizo commit en su propia conexión MySQL.
            # Por aislamiento de transacciones, esta conexión NO verá esos datos
            # hasta que se cierre y reabra (force_reconnect).
            self.db.force_reconnect()

            # Refrescar esta pestaña de forma asíncrona
            self.cargar_vehiculos_async()
            self.cargar_combo_funcionarios()

            # Emitir señal INMEDIATAMENTE (sin delay)
            # Ya no necesitamos QTimer porque force_reconnect() garantiza visibilidad
            self.vehiculo_creado.emit()
        else:
            # Los mensajes ya vienen formateados desde el modelo
            UIDialogs.show_warning(self, "Error al Guardar", mensaje)

        # Limpiar worker
        if self.guardar_worker:
            self.guardar_worker.deleteLater()
            self.guardar_worker = None

    def cargar_vehiculos(self):
        """Carga todos los vehículos en la tabla con botones de acción (Síncrono - solo para init)"""
        query = """
            SELECT
                v.id,
                CONCAT(f.nombre, ' ', f.apellidos) as funcionario,
                f.cedula,
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

    def cargar_vehiculos_async(self):
        """Carga vehículos de forma asíncrona (Optimizado - no bloquea UI)"""
        # Evitar múltiples cargas simultáneas
        if self.cargar_vehiculos_worker and self.cargar_vehiculos_worker.isRunning():
            return

        # Crear y ejecutar worker thread
        self.cargar_vehiculos_worker = CargarVehiculosWorker(self.db_config)
        self.cargar_vehiculos_worker.finished.connect(self.on_vehiculos_cargados)
        self.cargar_vehiculos_worker.start()

    @pyqtSlot(list)
    def on_vehiculos_cargados(self, vehiculos):
        """Callback cuando terminan de cargar los vehículos"""
        # Guardar lista completa para filtrado
        self.vehiculos_completos = vehiculos

        # Mostrar todos los vehículos
        self.mostrar_vehiculos(vehiculos)

        # Limpiar worker
        if self.cargar_vehiculos_worker:
            self.cargar_vehiculos_worker.deleteLater()
            self.cargar_vehiculos_worker = None

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
            btn_eliminar.clicked.connect(lambda checked, v=vehiculo: self.abrir_modal_eliminar_optimizado(v))

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
        """Actualiza la tabla de vehículos (Optimizado - Asíncrono)"""
        self.cargar_vehiculos_async()

    def abrir_modal_editar(self, vehiculo_id: int):
        """Abre el modal para editar un vehículo

        Args:
            vehiculo_id (int): ID del vehículo a editar
        """
        try:
            modal = EditarVehiculoModal(vehiculo_id, self.vehiculo_model, self.funcionario_model, self)

            # Conectar señal para actualizar tabla cuando se edite (Optimizado - Asíncrono)
            modal.vehiculo_actualizado.connect(self.cargar_vehiculos_async)
            modal.vehiculo_actualizado.connect(self.vehiculo_creado.emit)  # Para sincronizar otros módulos
            modal.vehiculo_actualizado.connect(self.cargar_combo_funcionarios)  # Actualizar combo

            modal.exec_()

        except Exception as e:
            UIDialogs.show_error(self, "Error", f"Error al abrir el modal de edicion: {str(e)}")

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
            UIDialogs.show_error(self, "Error", f"Error al abrir el modal de visualizacion: {str(e)}")

    def abrir_modal_eliminar_optimizado(self, vehiculo_data: dict):
        """Abre el modal para eliminar un vehículo (OPTIMIZADO - sin consulta adicional)

        Args:
            vehiculo_data (dict): Datos completos del vehículo desde la tabla
        """
        import time
        try:

            # Crear modal pasando los datos directamente (SIN consulta a BD)
            t_modal = time.time()
            modal = EliminarVehiculoModal(
                vehiculo_id=vehiculo_data["id"],
                vehiculo_model=self.vehiculo_model,
                parent=self,
                vehiculo_data=vehiculo_data  # Pasar datos directamente
            )

            # Conectar señal para actualizar tabla cuando se elimine (Optimizado - Asíncrono)
            t_connect = time.time()
            modal.vehiculo_eliminado.connect(self.cargar_vehiculos_async)
            modal.vehiculo_eliminado.connect(self.vehiculo_creado.emit)  # Para sincronizar otros módulos
            modal.vehiculo_eliminado.connect(self.cargar_combo_funcionarios)  # Actualizar combo

            t_exec = time.time()
            resultado = modal.exec_()

            # Mostrar mensaje de éxito DESPUÉS de cerrar el modal (evita diálogos simultáneos)
            if resultado == QDialog.Accepted and hasattr(modal, 'mensaje_exito'):
                UIDialogs.show_success(self, "✅ Vehículo Eliminado", modal.mensaje_exito)


        except Exception as e:
            UIDialogs.show_error(self, "Error", f"Error al abrir el modal de eliminacion: {str(e)}")

    def abrir_modal_eliminar(self, vehiculo_id: int):
        """Abre el modal para eliminar un vehículo (LEGACY - mantener por compatibilidad)

        Args:
            vehiculo_id (int): ID del vehículo a eliminar
        """
        try:
            modal = EliminarVehiculoModal(vehiculo_id, self.vehiculo_model, self)

            # Conectar señal para actualizar tabla cuando se elimine (Optimizado - Asíncrono)
            modal.vehiculo_eliminado.connect(self.cargar_vehiculos_async)
            modal.vehiculo_eliminado.connect(self.vehiculo_creado.emit)  # Para sincronizar otros módulos
            modal.vehiculo_eliminado.connect(self.cargar_combo_funcionarios)  # Actualizar combo

            resultado = modal.exec_()

            # Mostrar mensaje de éxito DESPUÉS de cerrar el modal (evita diálogos simultáneos)
            if resultado == QDialog.Accepted and hasattr(modal, 'mensaje_exito'):
                UIDialogs.show_success(self, "✅ Vehículo Eliminado", modal.mensaje_exito)

        except Exception as e:
            UIDialogs.show_error(self, "Error", f"Error al abrir el modal de eliminacion: {str(e)}")

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

    def importar_desde_excel(self):
        """Importa vehículos masivamente desde un archivo Excel (.xlsx o .xls)"""
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
                "Seleccionar archivo Excel de vehículos",
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
            columnas_requeridas = ["Cedula", "Tipo_Vehiculo", "Placa"]
            columnas_opcionales = ["Numero_Parqueadero"]

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
                "Los vehículos duplicados (misma placa) serán omitidos.\n"
                "Las cédulas de funcionarios deben existir en la base de datos.",
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
                    tipo_vehiculo = str(row["Tipo_Vehiculo"]).strip()
                    placa = str(row["Placa"]).strip().upper()
                    numero_parqueadero = str(row.get("Numero_Parqueadero", "")).strip()

                    # Validaciones básicas
                    if not cedula or not tipo_vehiculo:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Cédula o Tipo de Vehículo vacíos")
                        continue

                    # Validar tipo de vehículo
                    if tipo_vehiculo not in ["Carro", "Moto", "Bicicleta"]:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Tipo de vehículo inválido '{tipo_vehiculo}' (debe ser Carro, Moto o Bicicleta)")
                        continue

                    # Validar que la cédula exista en la BD
                    query_funcionario = "SELECT id FROM funcionarios WHERE cedula = %s AND activo = TRUE"
                    funcionario = self.db.fetch_one(query_funcionario, (cedula,))

                    if not funcionario:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Funcionario con cédula '{cedula}' no existe en el sistema")
                        continue

                    funcionario_id = funcionario["id"]

                    # Validar placa según tipo de vehículo
                    if tipo_vehiculo == "Bicicleta":
                        # Bicicletas NO deben tener placa
                        if placa:
                            omitidos += 1
                            errores.append(f"Fila {index + 2}: Las bicicletas NO deben tener placa")
                            continue
                        placa = None  # Establecer como None para bicicletas
                    else:
                        # Carros y Motos SÍ requieren placa
                        if not placa:
                            omitidos += 1
                            errores.append(f"Fila {index + 2}: La placa es obligatoria para {tipo_vehiculo}")
                            continue

                        # Validar formato de placa para Carros
                        if tipo_vehiculo == "Carro":
                            if len(placa) != 6 or not (placa[:3].isalpha() and placa[3:].isdigit()):
                                omitidos += 1
                                errores.append(f"Fila {index + 2}: Formato de placa inválido para Carro '{placa}' (debe ser ABC123)")
                                continue

                        # Validar formato de placa para Motos
                        if tipo_vehiculo == "Moto":
                            valido = False
                            # Patrón 1: ABC12 (3 letras + 2 números)
                            if len(placa) == 5 and placa[:3].isalpha() and placa[3:].isdigit():
                                valido = True
                            # Patrón 2: ABC12D (3 letras + 2 números + 1 letra)
                            elif len(placa) == 6 and placa[:3].isalpha() and placa[3:5].isdigit() and placa[5].isalpha():
                                valido = True

                            if not valido:
                                omitidos += 1
                                errores.append(f"Fila {index + 2}: Formato de placa inválido para Moto '{placa}' (debe ser ABC12 o ABC12D)")
                                continue

                        # Verificar si la placa ya existe
                        query_placa = "SELECT id FROM vehiculos WHERE placa = %s AND activo = TRUE"
                        vehiculo_existente = self.db.fetch_one(query_placa, (placa,))

                        if vehiculo_existente:
                            omitidos += 1
                            errores.append(f"Fila {index + 2}: La placa '{placa}' ya está registrada")
                            continue

                    # Validar reglas de negocio antes de insertar
                    es_valido, mensaje = self.vehiculo_model.validar_vehiculo_antes_registro(
                        funcionario_id, tipo_vehiculo, placa
                    )

                    if not es_valido:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: {mensaje}")
                        continue

                    # Insertar vehículo
                    exito, mensaje_insercion = self.vehiculo_model.crear(
                        funcionario_id=funcionario_id,
                        tipo_vehiculo=tipo_vehiculo,
                        placa=placa
                    )

                    if not exito:
                        omitidos += 1
                        errores.append(f"Fila {index + 2}: Error al insertar vehículo - {mensaje_insercion}")
                        continue

                    # Si se especificó un parqueadero, crear asignación
                    if numero_parqueadero:
                        try:
                            num_parq = int(numero_parqueadero)

                            # Verificar que el parqueadero existe
                            query_parq = "SELECT id FROM parqueaderos WHERE numero_parqueadero = %s AND activo = TRUE"
                            parqueadero = self.db.fetch_one(query_parq, (num_parq,))

                            if parqueadero:
                                # Obtener el ID del vehículo recién creado
                                query_vehiculo = "SELECT id FROM vehiculos WHERE placa = %s AND activo = TRUE" if placa else \
                                                 "SELECT id FROM vehiculos WHERE funcionario_id = %s AND tipo_vehiculo = %s AND activo = TRUE ORDER BY id DESC LIMIT 1"
                                params = (placa,) if placa else (funcionario_id, tipo_vehiculo)
                                vehiculo_nuevo = self.db.fetch_one(query_vehiculo, params)

                                if vehiculo_nuevo:
                                    # Crear asignación
                                    query_asignacion = """
                                        INSERT INTO asignaciones (parqueadero_id, vehiculo_id, activo)
                                        VALUES (%s, %s, TRUE)
                                    """
                                    self.db.execute_query(query_asignacion, (parqueadero["id"], vehiculo_nuevo["id"]))
                        except ValueError:
                            # Número de parqueadero inválido, ignorar asignación pero el vehículo ya se creó
                            pass

                    importados += 1

                except Exception as e:
                    omitidos += 1
                    errores.append(f"Fila {index + 2}: Error inesperado - {str(e)}")

            # Mostrar reporte final
            mensaje_final = f"Importación completada:\n\n"
            mensaje_final += f"✅ Vehículos importados: {importados}\n"
            mensaje_final += f"⚠️ Vehículos omitidos: {omitidos}\n\n"

            if errores:
                mensaje_final += "Detalles de errores:\n"
                # Mostrar solo los primeros 10 errores para no saturar el diálogo
                for error in errores[:10]:
                    mensaje_final += f"  • {error}\n"

                if len(errores) > 10:
                    mensaje_final += f"\n... y {len(errores) - 10} errores más."

            if importados > 0:
                QMessageBox.information(self, "Importación Completada", mensaje_final)
                # Recargar vehículos
                self.db.force_reconnect()
                self.cargar_vehiculos_async()
                self.cargar_combo_funcionarios()
                self.vehiculo_creado.emit()
            else:
                QMessageBox.warning(self, "Importación Sin Éxito", mensaje_final)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Crítico",
                f"Ocurrió un error inesperado durante la importación:\n\n{str(e)}"
            )
