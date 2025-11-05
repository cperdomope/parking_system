# -*- coding: utf-8 -*-
"""
Modal para mostrar información detallada de un parqueadero
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..database.manager import DatabaseManager
from ..models.parqueadero import ParqueaderoModel
from ..utils.formatters import format_numero_parqueadero


class DetalleParqueaderoModal(QDialog):
    """Modal para mostrar información detallada de un parqueadero"""

    def __init__(self, parqueadero_id: int, numero_parqueadero=None, db_manager: DatabaseManager = None, parent=None):
        super().__init__(parent)

        # Validaciones de inicialización
        if not parqueadero_id or not db_manager:
            raise ValueError("Parámetros de inicialización inválidos")

        self.parqueadero_id = parqueadero_id
        self.db = db_manager
        self.parqueadero_model = ParqueaderoModel(self.db)
        self.info_parqueadero = None

        # SIEMPRE obtener numero_parqueadero de la BD (ignorar parámetro)
        # Esto evita problemas con formato inconsistente
        try:
            query = "SELECT numero_parqueadero FROM parqueaderos WHERE id = %s"
            result = self.db.fetch_one(query, (self.parqueadero_id,))
            if result:
                self.numero_parqueadero = result['numero_parqueadero']
            else:
                self.numero_parqueadero = "N/A"

            self.setup_ui()
            self.cargar_informacion()
        except Exception as e:
            print(f"Error en inicialización del modal: {e}")
            raise

    def setup_ui(self):
        """Configura la interfaz del modal"""
        self.setWindowTitle(f"📊 Detalle Parqueadero {format_numero_parqueadero(self.numero_parqueadero)}")
        self.setModal(True)

        # Aplicar estilo base para asegurar texto negro en todo el modal
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f5f5f5;
            }
            QTableWidget::item {
                color: #000000 !important;
            }
        """
        )

        # Tamaño optimizado para pantalla sin scroll
        self.resize(900, 650)

        # Centrar en pantalla
        if self.parent():
            parent_geom = self.parent().geometry()
            x = parent_geom.x() + (parent_geom.width() - 900) // 2
            y = parent_geom.y() + (parent_geom.height() - 650) // 2
            self.move(x, y)

        # Layout principal con márgenes compactos
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header con información principal
        header_group = self.crear_header()
        layout.addWidget(header_group)

        # Tabs con información detallada
        tabs = QTabWidget()

        # Tab 1: Ocupación Actual
        self.tab_ocupacion = self.crear_tab_ocupacion()
        tabs.addTab(self.tab_ocupacion, "🚗 Ocupación Actual")

        # Tab 2: Historial
        self.tab_historial = self.crear_tab_historial()
        tabs.addTab(self.tab_historial, "📅 Historial")

        layout.addWidget(tabs)

        # Botones mejorados
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        # Botón de actualizar todo
        btn_actualizar_todo = QPushButton("🔄 Actualizar Todo")
        btn_actualizar_todo.clicked.connect(self.cargar_informacion)
        btn_actualizar_todo.setStyleSheet(
            "padding: 10px 20px; background-color: #34B5A9; color: white; "
            "border: none; border-radius: 6px; font-weight: bold; font-size: 14px;"
        )
        btn_layout.addWidget(btn_actualizar_todo)

        # Botón de cerrar
        btn_cerrar = QPushButton("❌ Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setStyleSheet(
            "padding: 10px 20px; background-color: #757575; color: white; "
            "border: none; border-radius: 6px; font-weight: bold; font-size: 14px;"
        )
        btn_layout.addWidget(btn_cerrar)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def crear_header(self):
        """Crea el header con información principal"""
        group = QGroupBox("📍 Información General del Parqueadero")
        group.setStyleSheet(
            "QGroupBox { "
            "font-size: 16px; font-weight: bold; "
            "border: 2px solid #267A70; "
            "border-radius: 8px; "
            "margin-top: 10px; "
            "padding-top: 10px; "
            "} "
            "QGroupBox::title { "
            "subcontrol-origin: margin; "
            "left: 15px; "
            "padding: 0 8px 0 8px; "
            "color: #267A70; "
            "}"
        )

        layout = QGridLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Número del parqueadero - más prominente
        lbl_numero_label = QLabel("Parqueadero:")
        lbl_numero_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_numero_label, 0, 0)

        lbl_numero = QLabel(f"{format_numero_parqueadero(self.numero_parqueadero)}")
        lbl_numero.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #267A70; "
            "padding: 6px 12px; background-color: #E3F2FD; "
            "border-radius: 6px; border: 2px solid #267A70;"
        )
        layout.addWidget(lbl_numero, 0, 1)

        # Estado con mejor visualización
        lbl_estado_label = QLabel("Estado Actual:")
        lbl_estado_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(lbl_estado_label, 0, 2)

        self.lbl_estado = QLabel("Cargando...")
        self.lbl_estado.setStyleSheet("font-size: 18px; font-weight: bold; " "padding: 8px 12px; border-radius: 6px;")
        layout.addWidget(self.lbl_estado, 0, 3)

        # Sótano
        lbl_sotano_label = QLabel("Sótano:")
        lbl_sotano_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_sotano_label, 1, 0)

        self.lbl_sotano = QLabel("Cargando...")
        self.lbl_sotano.setStyleSheet(
            "font-size: 14px; padding: 6px; font-weight: bold; "
            "background-color: #F0F7FF; border-radius: 4px; color: #0D47A1;"
        )
        layout.addWidget(self.lbl_sotano, 1, 1)

        # Tipo de espacio
        lbl_tipo_label = QLabel("Tipo de Espacio:")
        lbl_tipo_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_tipo_label, 1, 2)

        self.lbl_tipo_espacio = QLabel("Cargando...")
        self.lbl_tipo_espacio.setStyleSheet(
            "font-size: 14px; padding: 6px; " "background-color: #F5F5F5; border-radius: 4px;"
        )
        layout.addWidget(self.lbl_tipo_espacio, 1, 3)

        # Ocupación actual con ícono (FILA 2 para evitar sobreescritura)
        lbl_ocupacion_label = QLabel("Ocupación Actual:")
        lbl_ocupacion_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_ocupacion_label, 2, 0)

        self.lbl_ocupacion = QLabel("Cargando...")
        self.lbl_ocupacion.setStyleSheet(
            "font-size: 16px; font-weight: bold; " "padding: 6px 12px; border-radius: 4px;"
        )
        layout.addWidget(self.lbl_ocupacion, 2, 1, 1, 3)  # Expandir a lo largo de 3 columnas

        group.setLayout(layout)
        return group

    def crear_tab_ocupacion(self):
        """Crea el tab de ocupación actual"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Scroll area para los vehículos con configuración optimizada
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setMinimumHeight(250)  # Altura compacta para vehículos

        # Widget contenedor para vehículos con inicialización segura
        self.vehiculos_container = QWidget()
        self.layout_vehiculos = QVBoxLayout()
        self.layout_vehiculos.setSpacing(8)
        self.layout_vehiculos.setContentsMargins(5, 5, 5, 5)

        # Configurar el contenedor desde el inicio
        self.vehiculos_container.setLayout(self.layout_vehiculos)
        scroll_area.setWidget(self.vehiculos_container)

        # El contenido se cargará en cargar_vehiculos_asignados()

        layout.addWidget(scroll_area)
        widget.setLayout(layout)
        return widget

    def crear_tab_historial(self):
        """Crea el tab de historial"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header del historial
        header_layout = QHBoxLayout()
        lbl_titulo = QLabel("📋 Historial de Asignaciones")
        lbl_titulo.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #267A70; "
            "padding: 10px; background-color: #E3F2FD; border-radius: 6px;"
        )
        header_layout.addWidget(lbl_titulo)
        header_layout.addStretch()

        # Botón de actualizar historial
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.clicked.connect(self.cargar_historial)
        btn_actualizar.setStyleSheet(
            "padding: 8px 15px; background-color: #4CAF50; color: white; "
            "border: none; border-radius: 4px; font-weight: bold;"
        )
        header_layout.addWidget(btn_actualizar)
        layout.addLayout(header_layout)

        # Tabla de historial mejorada
        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(7)
        self.tabla_historial.setHorizontalHeaderLabels(
            ["Fecha Inicio", "Fecha Fin", "Duración", "Funcionario", "Vehículo", "Placa", "Estado"]
        )

        # Configurar tabla con mejor apariencia
        header = self.tabla_historial.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Fecha Inicio
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Fecha Fin
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Duración
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Funcionario
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Vehículo
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Placa
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Estado

        self.tabla_historial.setAlternatingRowColors(True)
        self.tabla_historial.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_historial.setGridStyle(Qt.SolidLine)
        self.tabla_historial.setStyleSheet(
            "QTableWidget { "
            "gridline-color: #E0E0E0; "
            "font-size: 12px; "
            "background-color: white; "
            "} "
            "QTableWidget::item { "
            "padding: 8px; "
            "background-color: white; "
            "} "
            "QTableWidget::item:alternate { "
            "background-color: #f9f9f9; "
            "} "
            "QHeaderView::section { "
            "background-color: #2b2b2b; "
            "color: white; "
            "font-weight: bold; "
            "border: 1px solid #555555; "
            "padding: 8px; "
            "}"
        )

        # Área con scroll para la tabla con mejor configuración
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.tabla_historial)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(220)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        layout.addWidget(scroll_area)

        # Pie del historial con información adicional
        footer_layout = QHBoxLayout()
        self.lbl_total_registros = QLabel("Total de registros: 0")
        self.lbl_total_registros.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        footer_layout.addWidget(self.lbl_total_registros)
        footer_layout.addStretch()

        lbl_nota = QLabel("Nota: Se muestran los últimos 100 registros")
        lbl_nota.setStyleSheet("color: #999; font-size: 11px; font-style: italic;")
        footer_layout.addWidget(lbl_nota)
        layout.addLayout(footer_layout)

        widget.setLayout(layout)
        return widget

    def cargar_informacion(self):
        """Carga la información del parqueadero"""
        try:
            # Verificar si existe la columna sotano
            try:
                check_query = "SHOW COLUMNS FROM parqueaderos LIKE 'sotano'"
                column_exists = self.db.fetch_one(check_query) is not None
            except Exception as e:
                print(f"Advertencia al verificar columna 'sotano': {e}")
                column_exists = False

            # Obtener información actual adaptable
            if column_exists:
                query_actual = """
                    SELECT
                        p.estado,
                        p.tipo_espacio,
                        COALESCE(p.sotano, 'Sótano-1') as sotano,
                        COUNT(CASE WHEN a.activo = TRUE AND v.tipo_vehiculo = 'Carro' THEN 1 END) as carros_asignados,
                        COUNT(CASE WHEN a.activo = TRUE AND v.tipo_vehiculo = 'Moto' THEN 1 END) as motos_asignadas,
                        COUNT(CASE WHEN a.activo = TRUE AND v.tipo_vehiculo = 'Bicicleta' THEN 1 END) as bicicletas_asignadas
                    FROM parqueaderos p
                    LEFT JOIN asignaciones a ON p.id = a.parqueadero_id
                    LEFT JOIN vehiculos v ON a.vehiculo_id = v.id
                    WHERE p.id = %s
                    GROUP BY p.id
                """
            else:
                query_actual = """
                    SELECT
                        p.estado,
                        p.tipo_espacio,
                        'Sótano-1' as sotano,
                        COUNT(CASE WHEN a.activo = TRUE AND v.tipo_vehiculo = 'Carro' THEN 1 END) as carros_asignados,
                        0 as motos_asignadas,
                        0 as bicicletas_asignadas
                    FROM parqueaderos p
                    LEFT JOIN asignaciones a ON p.id = a.parqueadero_id
                    LEFT JOIN vehiculos v ON a.vehiculo_id = v.id
                    WHERE p.id = %s
                    GROUP BY p.id
                """
            info_general = self.db.fetch_one(query_actual, (self.parqueadero_id,))

            if info_general:
                self.actualizar_header(info_general)
            else:
                raise Exception(f"No se encontró información para el parqueadero ID: {self.parqueadero_id}")

            # Cargar vehículos asignados
            self.cargar_vehiculos_asignados()

            # Cargar historial
            self.cargar_historial()

        except Exception as e:
            print(f"Error al cargar información del parqueadero: {e}")
            # Mostrar estado por defecto
            self.lbl_estado.setText("Error al cargar")
            self.lbl_ocupacion.setText("Error al cargar")
            raise

    def actualizar_header(self, info):
        """Actualiza la información del header"""
        tipo_espacio = info["tipo_espacio"]
        sotano = info["sotano"]
        carros_asignados = info.get("carros_asignados", 0)
        motos_asignadas = info.get("motos_asignadas", 0)
        bicicletas_asignadas = info.get("bicicletas_asignadas", 0)

        # Actualizar sótano
        self.lbl_sotano.setText(sotano)

        # Actualizar tipo de espacio con ícono
        iconos_tipo = {"Carro": "🚗", "Moto": "🏍️", "Bicicleta": "🚲", "Mixto": "🚗🏍️"}
        icono_tipo = iconos_tipo.get(tipo_espacio, "🚗")
        self.lbl_tipo_espacio.setText(f"{icono_tipo} {tipo_espacio}")

        # CALCULAR ESTADO CORRECTO según tipo de vehículo y asignaciones
        total_asignaciones = carros_asignados + motos_asignadas + bicicletas_asignadas

        if tipo_espacio == "Moto":
            # Motos: 0 asignaciones = Disponible, ≥1 = Completo
            if motos_asignadas == 0:
                estado = "Disponible"
            else:
                estado = "Completo"
        elif tipo_espacio == "Bicicleta":
            # Bicicletas: 0 asignaciones = Disponible, ≥1 = Completo
            if bicicletas_asignadas == 0:
                estado = "Disponible"
            else:
                estado = "Completo"
        elif tipo_espacio == "Carro":
            # Carros: lógica normal (0=Disponible, 1=Parcial, 2=Completo)
            if carros_asignados == 0:
                estado = "Disponible"
            elif carros_asignados == 1:
                estado = "Parcialmente_Asignado"
            else:
                estado = "Completo"
        else:  # Mixto
            if total_asignaciones == 0:
                estado = "Disponible"
            else:
                estado = "Completo"

        # Actualizar estado con color y fondo
        color_estado, bg_color = self.get_colors_estado(estado)
        estado_texto = estado.replace("_", " ")
        self.lbl_estado.setText(estado_texto)
        self.lbl_estado.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {color_estado}; "
            f"background-color: {bg_color}; padding: 8px 12px; border-radius: 6px; "
            f"border: 2px solid {color_estado};"
        )

        # Actualizar ocupación basada en el tipo de espacio
        if tipo_espacio == "Carro":
            # Lógica original para carros
            porcentaje = (carros_asignados / 2) * 100
            if carros_asignados == 0:
                color_ocupacion = "#4CAF50"
                bg_ocupacion = "#E8F5E9"
                icono = "🟢"
            elif carros_asignados == 1:
                color_ocupacion = "#FF9800"
                bg_ocupacion = "#FFF3E0"
                icono = "🟡"
            else:
                color_ocupacion = "#F44336"
                bg_ocupacion = "#FFEBEE"
                icono = "🔴"
            texto_ocupacion = f"{icono} {carros_asignados}/2 carros ({porcentaje:.0f}%)"

        elif tipo_espacio == "Moto":
            # Para motos (capacidad ilimitada prácticamente)
            color_ocupacion = "#4CAF50" if motos_asignadas == 0 else "#34B5A9"
            bg_ocupacion = "#E8F5E9" if motos_asignadas == 0 else "#E3F2FD"
            icono = "🟢" if motos_asignadas == 0 else "🔵"
            texto_ocupacion = f"{icono} {motos_asignadas} motos asignadas"

        elif tipo_espacio == "Bicicleta":
            # Para bicicletas (capacidad ilimitada prácticamente)
            color_ocupacion = "#4CAF50" if bicicletas_asignadas == 0 else "#9C27B0"
            bg_ocupacion = "#E8F5E9" if bicicletas_asignadas == 0 else "#F3E5F5"
            icono = "🟢" if bicicletas_asignadas == 0 else "🟣"
            texto_ocupacion = f"{icono} {bicicletas_asignadas} bicicletas asignadas"

        else:  # Mixto
            total = carros_asignados + motos_asignadas + bicicletas_asignadas
            if total == 0:
                color_ocupacion = "#4CAF50"
                bg_ocupacion = "#E8F5E9"
                icono = "🟢"
            else:
                color_ocupacion = "#34B5A9"
                bg_ocupacion = "#E3F2FD"
                icono = "🔵"
            texto_ocupacion = f"{icono} {carros_asignados}🚗 {motos_asignadas}🏍️ {bicicletas_asignadas}🚲"

        self.lbl_ocupacion.setText(texto_ocupacion)
        self.lbl_ocupacion.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {color_ocupacion}; "
            f"background-color: {bg_ocupacion}; padding: 6px 12px; border-radius: 4px;"
        )

    def get_colors_estado(self, estado):
        """Retorna el color de texto y fondo según el estado"""
        if estado == "Disponible":
            return "#2E7D32", "#E8F5E9"  # Verde oscuro, fondo verde claro
        elif estado == "Parcialmente_Asignado":
            return "#F57C00", "#FFF3E0"  # Naranja oscuro, fondo naranja claro
        else:
            return "#C62828", "#FFEBEE"  # Rojo oscuro, fondo rojo claro

    def cargar_vehiculos_asignados(self):
        """Carga los vehículos actualmente asignados"""
        try:
            query = """
                SELECT
                    f.nombre, f.apellidos, f.cedula, f.cargo, f.direccion_grupo, f.celular,
                    v.tipo_vehiculo, v.placa, v.tipo_circulacion, v.ultimo_digito,
                    a.fecha_asignacion, a.observaciones
                FROM asignaciones a
                JOIN vehiculos v ON a.vehiculo_id = v.id
                JOIN funcionarios f ON v.funcionario_id = f.id
                WHERE a.parqueadero_id = %s AND a.activo = TRUE
                ORDER BY v.tipo_vehiculo, a.fecha_asignacion
            """
            vehiculos = self.db.fetch_all(query, (self.parqueadero_id,))
        except Exception as e:
            print(f"Error al cargar vehículos asignados: {e}")
            vehiculos = []

        # Limpiar layout de forma segura
        for i in reversed(range(self.layout_vehiculos.count())):
            item = self.layout_vehiculos.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        if not vehiculos:
            lbl_sin_vehiculos = QLabel("💚 Parqueadero disponible - No hay vehículos asignados")
            lbl_sin_vehiculos.setAlignment(Qt.AlignCenter)
            lbl_sin_vehiculos.setStyleSheet(
                "color: #4CAF50; font-size: 14px; font-weight: bold; "
                "padding: 30px; background-color: #E8F5E9; border-radius: 8px;"
            )
            self.layout_vehiculos.addWidget(lbl_sin_vehiculos)
        else:
            for i, vehiculo in enumerate(vehiculos):
                widget_vehiculo = self.crear_widget_vehiculo(vehiculo, i + 1)
                self.layout_vehiculos.addWidget(widget_vehiculo)

        # Agregar stretch al final para que los elementos se alineen arriba
        self.layout_vehiculos.addStretch()

    def crear_widget_vehiculo(self, vehiculo, posicion):
        """Crea un widget con información de un vehículo"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet(
            "QFrame { "
            "background-color: #FAFAFA; "
            "border: 2px solid #E0E0E0; "
            "border-radius: 12px; "
            "padding: 15px; "
            "margin: 8px; "
            "}"
        )
        frame.setMinimumHeight(220)  # Altura compacta optimizada

        # Layout principal vertical compacto
        main_layout = QVBoxLayout()
        main_layout.setSpacing(6)

        # Header del vehículo con ícono dinámico
        header_layout = QHBoxLayout()
        iconos_vehiculo = {"Carro": "🚗", "Moto": "🏍️", "Bicicleta": "🚲"}
        icono = iconos_vehiculo.get(vehiculo["tipo_vehiculo"], "🚗")
        header = QLabel(f"{icono} {vehiculo['tipo_vehiculo']} {posicion}")
        header.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #267A70; "
            "padding: 8px; background-color: #E3F2FD; border-radius: 6px;"
        )
        header_layout.addWidget(header)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Sección de información del vehículo
        vehiculo_group = QGroupBox("🚗 Información del Vehículo")
        vehiculo_layout = QGridLayout()
        vehiculo_layout.setSpacing(4)

        # Placa destacada
        vehiculo_layout.addWidget(QLabel("Placa:"), 0, 0)
        lbl_placa = QLabel(vehiculo["placa"])
        lbl_placa.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #2E7D32; "
            "padding: 4px 8px; background-color: #E8F5E9; border-radius: 4px;"
        )
        vehiculo_layout.addWidget(lbl_placa, 0, 1)

        # Tipo de circulación destacado (solo para carros)
        vehiculo_layout.addWidget(QLabel("Circulación:"), 0, 2)
        tipo_circulacion = vehiculo["tipo_circulacion"] or "N/A"

        # Configurar colores según tipo de circulación
        if tipo_circulacion == "IMPAR":
            color_bg = "#FFEBEE"
            color_text = "#C62828"
        elif tipo_circulacion == "PAR":
            color_bg = "#E8EAF6"
            color_text = "#3F51B5"
        else:  # N/A para motos y bicicletas
            color_bg = "#F5F5F5"
            color_text = "#757575"

        lbl_circulacion = QLabel(tipo_circulacion)
        lbl_circulacion.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {color_text}; "
            f"padding: 4px 8px; background-color: {color_bg}; border-radius: 4px;"
        )
        vehiculo_layout.addWidget(lbl_circulacion, 0, 3)

        # Último dígito
        vehiculo_layout.addWidget(QLabel("Último dígito:"), 1, 0)
        vehiculo_layout.addWidget(QLabel(str(vehiculo["ultimo_digito"]) if vehiculo["ultimo_digito"] else "N/A"), 1, 1)

        # Fecha de asignación
        vehiculo_layout.addWidget(QLabel("Fecha asignación:"), 1, 2)
        fecha_asignacion = (
            vehiculo["fecha_asignacion"].strftime("%d/%m/%Y %H:%M") if vehiculo["fecha_asignacion"] else "No disponible"
        )
        vehiculo_layout.addWidget(QLabel(fecha_asignacion), 1, 3)

        vehiculo_group.setLayout(vehiculo_layout)
        main_layout.addWidget(vehiculo_group)

        # Sección de información del funcionario
        funcionario_group = QGroupBox("👤 Información del Funcionario")
        funcionario_layout = QGridLayout()
        funcionario_layout.setSpacing(4)

        # Nombre completo destacado
        funcionario_layout.addWidget(QLabel("Nombre:"), 0, 0)
        lbl_nombre = QLabel(f"{vehiculo['nombre']} {vehiculo['apellidos']}")
        lbl_nombre.setStyleSheet("font-size: 15px; font-weight: bold; color: #267A70;")
        funcionario_layout.addWidget(lbl_nombre, 0, 1, 1, 3)

        # Cédula
        funcionario_layout.addWidget(QLabel("Cédula:"), 1, 0)
        funcionario_layout.addWidget(QLabel(vehiculo["cedula"]), 1, 1)

        # Cargo
        funcionario_layout.addWidget(QLabel("Cargo:"), 1, 2)
        funcionario_layout.addWidget(QLabel(vehiculo["cargo"] or "No especificado"), 1, 3)

        # Dirección/Grupo
        funcionario_layout.addWidget(QLabel("Dirección:"), 2, 0)
        lbl_direccion = QLabel(vehiculo["direccion_grupo"] or "No especificada")
        lbl_direccion.setWordWrap(True)
        funcionario_layout.addWidget(lbl_direccion, 2, 1, 1, 2)

        # Celular en fila separada para evitar solapamiento
        funcionario_layout.addWidget(QLabel("Celular:"), 3, 0)
        funcionario_layout.addWidget(QLabel(vehiculo["celular"] or "No registrado"), 3, 1)

        funcionario_group.setLayout(funcionario_layout)
        main_layout.addWidget(funcionario_group)

        # Observaciones (si existen)
        if vehiculo["observaciones"]:
            obs_group = QGroupBox("📝 Observaciones")
            obs_layout = QVBoxLayout()
            lbl_obs = QLabel(vehiculo["observaciones"])
            lbl_obs.setWordWrap(True)
            lbl_obs.setStyleSheet("padding: 8px; background-color: #FFF3E0; " "border-radius: 4px; color: #E65100;")
            obs_layout.addWidget(lbl_obs)
            obs_group.setLayout(obs_layout)
            main_layout.addWidget(obs_group)

        main_layout.addStretch()
        frame.setLayout(main_layout)
        return frame

    def cargar_historial(self):
        """Carga el historial de asignaciones"""
        query = """
            SELECT
                a.fecha_asignacion,
                a.fecha_fin_asignacion,
                CONCAT(f.nombre, ' ', f.apellidos) as funcionario,
                f.cedula,
                v.tipo_vehiculo,
                v.placa,
                v.tipo_circulacion,
                CASE
                    WHEN a.activo = TRUE THEN 'Activo'
                    ELSE 'Finalizado'
                END as estado,
                a.observaciones
            FROM asignaciones a
            JOIN vehiculos v ON a.vehiculo_id = v.id
            JOIN funcionarios f ON v.funcionario_id = f.id
            WHERE a.parqueadero_id = %s
            ORDER BY a.fecha_asignacion DESC
            LIMIT 100
        """
        historial = self.db.fetch_all(query, (self.parqueadero_id,))

        self.tabla_historial.setRowCount(len(historial))

        for row, registro in enumerate(historial):
            # Fecha inicio
            fecha_inicio = (
                registro["fecha_asignacion"].strftime("%d/%m/%Y\n%H:%M") if registro["fecha_asignacion"] else "N/A"
            )
            item_inicio = QTableWidgetItem(fecha_inicio)
            item_inicio.setTextAlignment(Qt.AlignCenter)
            item_inicio.setForeground(QBrush(QColor(0, 0, 0)))
            self.tabla_historial.setItem(row, 0, item_inicio)

            # Fecha fin
            fecha_fin = (
                registro["fecha_fin_asignacion"].strftime("%d/%m/%Y\n%H:%M")
                if registro["fecha_fin_asignacion"]
                else "Activo"
            )
            item_fin = QTableWidgetItem(fecha_fin)
            item_fin.setTextAlignment(Qt.AlignCenter)
            if fecha_fin == "Activo":
                item_fin.setBackground(QColor("#E8F5E9"))
                item_fin.setForeground(QBrush(QColor(46, 125, 50)))
            else:
                item_fin.setForeground(QBrush(QColor(0, 0, 0)))
            self.tabla_historial.setItem(row, 1, item_fin)

            # Duración
            if registro["fecha_asignacion"]:
                fecha_fin_calc = registro["fecha_fin_asignacion"] if registro["fecha_fin_asignacion"] else None
                if fecha_fin_calc:
                    duracion = fecha_fin_calc - registro["fecha_asignacion"]
                    dias = duracion.days
                    horas = duracion.seconds // 3600
                    if dias > 0:
                        duracion_texto = f"{dias}d {horas}h"
                    else:
                        duracion_texto = f"{horas}h"
                else:
                    # Calcular duración hasta ahora
                    from datetime import datetime

                    duracion = datetime.now() - registro["fecha_asignacion"]
                    dias = duracion.days
                    duracion_texto = f"{dias}d" if dias > 0 else "< 1d"
            else:
                duracion_texto = "N/A"

            item_duracion = QTableWidgetItem(duracion_texto)
            item_duracion.setTextAlignment(Qt.AlignCenter)
            item_duracion.setForeground(QBrush(QColor(0, 0, 0)))
            self.tabla_historial.setItem(row, 2, item_duracion)

            # Funcionario con cédula
            funcionario_texto = f"{registro['funcionario']}\n(C.C. {registro['cedula']})"
            item_funcionario = QTableWidgetItem(funcionario_texto)
            item_funcionario.setForeground(QBrush(QColor(0, 0, 0)))
            self.tabla_historial.setItem(row, 3, item_funcionario)

            # Vehículo con ícono
            iconos_vehiculo = {"Carro": "🚗", "Moto": "🏍️", "Bicicleta": "🚲"}
            icono_veh = iconos_vehiculo.get(registro["tipo_vehiculo"], "")
            item_vehiculo = QTableWidgetItem(f"{icono_veh} {registro['tipo_vehiculo']}")
            item_vehiculo.setTextAlignment(Qt.AlignCenter)
            item_vehiculo.setForeground(QBrush(QColor(0, 0, 0)))
            # Color por tipo de vehículo
            if registro["tipo_vehiculo"] == "Carro":
                item_vehiculo.setBackground(QColor("#E3F2FD"))
            elif registro["tipo_vehiculo"] == "Moto":
                item_vehiculo.setBackground(QColor("#F3E5F5"))
            elif registro["tipo_vehiculo"] == "Bicicleta":
                item_vehiculo.setBackground(QColor("#E8F5E9"))
            self.tabla_historial.setItem(row, 4, item_vehiculo)

            # Placa con tipo de circulación
            tipo_circ = registro["tipo_circulacion"] or "N/A"
            placa_texto = f"{registro['placa']}\n({tipo_circ})"
            item_placa = QTableWidgetItem(placa_texto)
            item_placa.setTextAlignment(Qt.AlignCenter)
            item_placa.setForeground(QBrush(QColor(0, 0, 0)))
            # Color por tipo de circulación
            if tipo_circ == "IMPAR":
                item_placa.setBackground(QColor("#FFEBEE"))
            elif tipo_circ == "PAR":
                item_placa.setBackground(QColor("#E8EAF6"))
            elif tipo_circ == "N/A":
                item_placa.setBackground(QColor("#F5F5F5"))
            self.tabla_historial.setItem(row, 5, item_placa)

            # Estado con color mejorado
            item_estado = QTableWidgetItem(registro["estado"])
            item_estado.setTextAlignment(Qt.AlignCenter)
            if registro["estado"] == "Activo":
                item_estado.setBackground(QColor("#E8F5E9"))
                item_estado.setForeground(QBrush(QColor(46, 125, 50)))
                item_estado.setFont(QFont("Arial", 10, QFont.Bold))
            else:
                item_estado.setBackground(QColor("#FFEBEE"))
                item_estado.setForeground(QBrush(QColor(198, 40, 40)))
            self.tabla_historial.setItem(row, 6, item_estado)

            # Tooltip con observaciones si existen
            if registro["observaciones"]:
                item_funcionario.setToolTip(f"Observaciones: {registro['observaciones']}")

        # Actualizar contador
        self.lbl_total_registros.setText(f"Total de registros: {len(historial)}")

        # Ajustar altura de filas para ser más compacto
        for row in range(len(historial)):
            self.tabla_historial.setRowHeight(row, 35)
