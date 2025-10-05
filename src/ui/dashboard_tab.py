# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Dashboard del sistema de gestión de parqueadero.
Diseño renovado para mayor claridad y eficiencia.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from ..database.manager import DatabaseManager
from ..models.parqueadero import ParqueaderoModel

class DashboardWidget(QWidget):
    """
    Widget del panel de control principal con un diseño profesional y enfocado
    en indicadores clave.
    """

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.parqueadero_model = ParqueaderoModel(self.db)

        self.setup_ui()

        # Timer para actualizar las estadísticas cada 30 segundos
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_statistics)
        self.timer.start(30000)

    def setup_ui(self):
        """Configura la interfaz de usuario del dashboard."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(12)

        # Aplicar estilo de fondo directamente al widget principal
        self.setStyleSheet("background-color: #BAD8B6;")

        # Título del Dashboard
        title_label = QLabel("Dashboard de Ocupación")
        title_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #222222;
            margin-bottom: 5px;
        """)
        main_layout.addWidget(title_label)

        # Grid para las tarjetas de KPIs principales
        kpi_grid_layout = QGridLayout()
        kpi_grid_layout.setSpacing(12)

        self.total_card = self._crear_kpi_card("Total Parqueaderos Carros ", "0", "🅿️", "#6366F1")
        self.ocupacion_card = self._crear_kpi_card("Ocupación Total", "0%", "📊", "#3B82F6")
        self.disponibles_card = self._crear_kpi_card("Espacios Disponibles", "0", "✅", "#10B981")
        self.vehiculos_card = self._crear_kpi_card("Vehículos Estacionados", "0", "🚗", "#F59E0B")

        kpi_grid_layout.addWidget(self.total_card, 0, 0)
        kpi_grid_layout.addWidget(self.ocupacion_card, 0, 1)
        kpi_grid_layout.addWidget(self.disponibles_card, 0, 2)
        kpi_grid_layout.addWidget(self.vehiculos_card, 0, 3)

        main_layout.addLayout(kpi_grid_layout)

        # Layout de dos columnas para detalles
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(12)

        # Columna Izquierda: Ocupación por Sótano
        sotanos_section_frame, sotanos_content_frame = self._crear_seccion_frame("Ocupación por Sótano")
        self.sotanos_layout = QVBoxLayout(sotanos_content_frame)
        self.sotanos_layout.setContentsMargins(0, 0, 0, 0)
        self.sotanos_layout.setSpacing(8)
        columns_layout.addWidget(sotanos_section_frame, 2)

        # Columna Derecha: Ocupación por Tipo de Vehículo
        tipos_section_frame, tipos_content_frame = self._crear_seccion_frame("Ocupación por Tipo de Vehículo")
        self.tipos_layout = QVBoxLayout(tipos_content_frame)
        self.tipos_layout.setContentsMargins(0, 0, 0, 0)
        self.tipos_layout.setSpacing(8)
        columns_layout.addWidget(tipos_section_frame, 1)

        main_layout.addLayout(columns_layout)

    def _crear_kpi_card(self, title, value, icon, color):
        """Crea una tarjeta de indicador clave (KPI) con un diseño mejorado."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #EFEFEF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
                min-height: 80px;
            }}
            QFrame:hover {{
                border: 1px solid {color};
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; color: #6B7280; font-weight: 500;")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)

        value_layout = QHBoxLayout()
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 28px; color: {color};")
        icon_label.setAlignment(Qt.AlignCenter)

        value_layout.addStretch()
        value_layout.addWidget(value_label)
        value_layout.addWidget(icon_label)
        value_layout.addStretch()

        card_layout.addWidget(title_label)
        card_layout.addLayout(value_layout)

        card.value_label = value_label
        return card

    def _crear_seccion_frame(self, title):
        """Crea un frame contenedor para una sección del dashboard."""
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: #EFEFEF;
                border-radius: 12px;
                border: 1px solid #E5E7EB;
            }
        """)
        section_layout = QVBoxLayout(section_frame)
        section_layout.setContentsMargins(12, 8, 12, 8)
        section_layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #374151;
            padding-bottom: 5px;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        section_layout.addWidget(title_label)

        content_frame = QFrame()
        content_frame.setStyleSheet("border: none;")
        section_layout.addWidget(content_frame)

        return section_frame, content_frame

    def _crear_detalle_card(self, title, value, total, color):
        """Crea una tarjeta de detalle para sótanos o tipos de vehículo."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 10px;
                border: 1px solid #E5E7EB;
                min-height: 60px;
            }
        """)
        main_layout = QVBoxLayout(card)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(6)

        # Layout superior con título y valor
        top_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #374151;")
        title_label.setWordWrap(True)

        value_label = QLabel(f"{value} / {total}")
        value_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {color};")

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(value_label)

        # Barra de progreso
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(int(total) if total > 0 else 1)
        progress_bar.setValue(int(value))
        progress_bar.setTextVisible(False)
        progress_bar.setMaximumHeight(6)

        # Calcular porcentaje para el color
        percentage = (int(value) / int(total) * 100) if total > 0 else 0

        # Definir color según porcentaje
        if percentage >= 90:
            bar_color = "#EF4444"  # Rojo
        elif percentage >= 70:
            bar_color = "#F59E0B"  # Amarillo
        else:
            bar_color = "#10B981"  # Verde

        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 3px;
                background-color: #E5E7EB;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 3px;
            }}
        """)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(progress_bar)

        card.value_label = value_label
        card.progress_bar = progress_bar
        return card

    def load_initial_data(self):
        """Carga los datos iniciales del dashboard."""
        self.update_statistics()
        self.update_sotanos_details()
        self.update_tipos_details()

    def update_statistics(self):
        """Actualiza los KPIs principales."""
        try:
            stats = self.parqueadero_model.obtener_estadisticas_generales()

            total = stats.get('total_espacios', 0)
            espacios_ocupados = stats.get('ocupados', 0)  # Parqueaderos ocupados
            vehiculos_estacionados = stats.get('vehiculos_estacionados', 0)  # Vehículos totales
            espacios_disponibles = total - espacios_ocupados

            tasa_ocupacion = (espacios_ocupados / total * 100) if total > 0 else 0

            self.total_card.value_label.setText(str(total))
            self.ocupacion_card.value_label.setText(f"{tasa_ocupacion:.1f}%")
            self.disponibles_card.value_label.setText(str(espacios_disponibles))
            self.vehiculos_card.value_label.setText(str(vehiculos_estacionados))

        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")

    def update_sotanos_details(self):
        """Actualiza los detalles de ocupación por sótano."""
        try:
            sotanos_data = self.parqueadero_model.obtener_ocupacion_por_sotano()

            # Limpiar layout anterior
            while self.sotanos_layout.count():
                item = self.sotanos_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

            for sotano in sorted(sotanos_data.keys()):
                data = sotanos_data[sotano]
                total = data['total']
                ocupados = data['ocupados']
                color = "#EF4444" if ocupados / total > 0.9 else "#F59E0B" if ocupados / total > 0.6 else "#10B981"

                card = self._crear_detalle_card(sotano, ocupados, total, color)
                self.sotanos_layout.addWidget(card)

            self.sotanos_layout.addStretch()

        except Exception as e:
            print(f"Error al actualizar detalles de sótanos: {e}")

    def update_tipos_details(self):
        """Actualiza los detalles de ocupación por tipo de vehículo."""
        try:
            tipos_data = self.parqueadero_model.obtener_ocupacion_por_tipo_vehiculo()

            # Limpiar layout anterior
            while self.tipos_layout.count():
                item = self.tipos_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

            colores = {"Carro": "#3B82F6", "Moto": "#8B5CF6", "Bicicleta": "#10B981"}

            for tipo in ["Carro", "Moto", "Bicicleta"]:
                data = tipos_data.get(tipo, {'ocupados': 0, 'total': 0})
                ocupados = data['ocupados']
                total = data['total']
                color = colores.get(tipo, "#6B7280")

                card = self._crear_detalle_card(tipo, ocupados, total, color)
                self.tipos_layout.addWidget(card)

            self.tipos_layout.addStretch()

        except Exception as e:
            print(f"Error al actualizar detalles de tipos: {e}")

    def actualizar_dashboard(self):
        """Slot público para actualizar el dashboard desde otras pestañas."""
        self.load_initial_data()

    def showEvent(self, event):
        """Se activa cuando el widget se muestra."""
        super().showEvent(event)
        self.load_initial_data()
        self.timer.start(30000)

    def hideEvent(self, event):
        """Se activa cuando el widget se oculta."""
        super().hideEvent(event)
        self.timer.stop()