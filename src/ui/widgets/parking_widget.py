# -*- coding: utf-8 -*-
"""
Widget personalizado para representar un espacio de parqueo con visualización mejorada
Versión 2.0 - Incluye iconos, barra de progreso y tooltips informativos
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QProgressBar

from src.utils.formatters import format_numero_parqueadero


class ParkingSpaceWidget(QFrame):
    """Widget personalizado para representar un espacio de parqueo con información visual enriquecida"""

    # Señal emitida cuando se hace clic en el parqueadero
    clicked = pyqtSignal(int, int)  # parqueadero_id, numero_parqueadero

    def __init__(
        self,
        parqueadero_id: int,
        numero: int,
        estado: str,
        asignados: str = "",
        tipo_espacio: str = "Carro",
        vehiculos_actuales: int = 0,
        capacidad_total: int = 2,
        tipo_ocupacion: str = "Regular",
        vehiculos_detalle: list = None,
        sotano: str = "",
    ):
        super().__init__()
        self.parqueadero_id = parqueadero_id
        self.numero = numero
        self.estado = estado
        self.asignados = asignados
        self.tipo_espacio = tipo_espacio
        self.vehiculos_actuales = vehiculos_actuales
        self.capacidad_total = capacidad_total
        self.tipo_ocupacion = tipo_ocupacion
        self.vehiculos_detalle = vehiculos_detalle or []
        self.sotano = sotano
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del widget con visualización mejorada"""
        self.setFixedSize(180, 130)  # Tamaño aumentado para nueva info
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # === LÍNEA 1: Número del parqueadero con sótano ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(2)

        icono_tipo = self._obtener_icono_tipo_espacio()
        numero_display = format_numero_parqueadero(self.numero)
        self.lbl_numero = QLabel(f"{icono_tipo} {numero_display}")
        self.lbl_numero.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1976D2; padding: 2px;"
        )
        self.lbl_numero.setCursor(QCursor(Qt.PointingHandCursor))
        self.lbl_numero.mousePressEvent = self.on_numero_clicked

        if self.sotano:
            lbl_sotano = QLabel(f"[{self.sotano}]")
            lbl_sotano.setStyleSheet("font-size: 9px; color: #666;")
            header_layout.addWidget(self.lbl_numero)
            header_layout.addWidget(lbl_sotano)
        else:
            header_layout.addWidget(self.lbl_numero)

        header_layout.addStretch()

        # === LÍNEA 2: Iconos de vehículos + Barra de progreso + Contador ===
        ocupacion_layout = QHBoxLayout()
        ocupacion_layout.setSpacing(3)

        # Iconos de vehículos asignados
        iconos_vehiculos = self._obtener_iconos_vehiculos()
        lbl_iconos = QLabel(iconos_vehiculos)
        lbl_iconos.setStyleSheet("font-size: 16px;")
        ocupacion_layout.addWidget(lbl_iconos)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.capacidad_total)
        self.progress_bar.setValue(self.vehiculos_actuales)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(self._get_progressbar_style())
        ocupacion_layout.addWidget(self.progress_bar)

        # Contador
        lbl_contador = QLabel(f"{self.vehiculos_actuales}/{self.capacidad_total}")
        lbl_contador.setStyleSheet("font-size: 11px; font-weight: bold; color: #333;")
        ocupacion_layout.addWidget(lbl_contador)

        # === LÍNEA 3: Etiqueta especial (tipo de ocupación) ===
        etiqueta_especial = self._obtener_etiqueta_especial()
        lbl_etiqueta = QLabel(etiqueta_especial)
        lbl_etiqueta.setAlignment(Qt.AlignCenter)
        lbl_etiqueta.setStyleSheet(
            "font-size: 9px; color: #555; font-style: italic; padding: 2px;"
        )
        lbl_etiqueta.setWordWrap(True)

        # === LÍNEA 4: Estado textual ===
        lbl_estado = QLabel(self.estado.replace("_", " "))
        lbl_estado.setAlignment(Qt.AlignCenter)
        lbl_estado.setStyleSheet(self.get_estado_style())

        # === LÍNEA 5: Indicador de detalles ===
        lbl_info = QLabel("ℹ️ Hover para detalles")
        lbl_info.setAlignment(Qt.AlignCenter)
        lbl_info.setStyleSheet("font-size: 8px; color: #999;")

        # Ensamblar layout
        layout.addLayout(header_layout)
        layout.addLayout(ocupacion_layout)
        layout.addWidget(lbl_etiqueta)
        layout.addWidget(lbl_estado)
        layout.addWidget(lbl_info)
        layout.addStretch()

        self.setLayout(layout)
        self.setStyleSheet(self.get_frame_style())

        # Configurar tooltip enriquecido
        self.setToolTip(self._generar_tooltip())

        # Hacer todo el widget clickeable
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mousePressEvent(self, event):
        """Maneja el clic en cualquier parte del widget"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.parqueadero_id, self.numero)

    def on_numero_clicked(self, event):
        """Maneja el clic específicamente en el número"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.parqueadero_id, self.numero)

    def enterEvent(self, event):
        """Efecto hover"""
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + " QFrame { border-width: 3px; }")
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Quitar efecto hover"""
        self.setStyleSheet(self.get_frame_style())
        super().leaveEvent(event)

    def _obtener_icono_tipo_espacio(self) -> str:
        """Retorna el icono según el tipo de espacio"""
        iconos = {"Carro": "🚗", "Moto": "🏍️", "Bicicleta": "🚲", "Mixto": "🅿️"}
        return iconos.get(self.tipo_espacio, "🅿️")

    def _obtener_iconos_vehiculos(self) -> str:
        """Genera iconos visuales de los vehículos asignados"""
        if self.vehiculos_actuales == 0:
            return "⬜"  # Espacio vacío

        iconos = []
        for vehiculo in self.vehiculos_detalle:
            tipo = vehiculo.get("tipo_vehiculo", "Carro")
            if tipo == "Carro":
                iconos.append("🚗")
            elif tipo == "Moto":
                iconos.append("🏍️")
            elif tipo == "Bicicleta":
                iconos.append("🚲")

        # Si no hay detalles, usar iconos genéricos
        if not iconos:
            icono_tipo = self._obtener_icono_tipo_espacio()
            iconos = [icono_tipo] * min(self.vehiculos_actuales, 4)

        return "".join(iconos[:4])  # Máximo 4 iconos

    def _obtener_etiqueta_especial(self) -> str:
        """Retorna la etiqueta especial según el tipo de ocupación"""
        etiquetas = {
            "Regular (PAR/IMPAR)": "⚡ PAR/IMPAR",
            "Exclusivo Directivo": "🏢 Exclusivo Directivo",
            "Híbrido Ecológico": "⚡ Híbrido (No comparte)",
            "Exclusivo": "🔒 Exclusivo",
            "Pico y Placa Solidario": "🔄 Pico y Placa Solidario",
            "Prioritario (Discapacidad)": "♿ Prioritario",
            "Individual": "📍 Individual",
        }
        return etiquetas.get(self.tipo_ocupacion, "")

    def _get_progressbar_style(self) -> str:
        """Estilo de la barra de progreso según ocupación"""
        # Color según el porcentaje de ocupación
        if self.capacidad_total == 0:
            porcentaje = 0
        else:
            porcentaje = (self.vehiculos_actuales / self.capacidad_total) * 100

        if porcentaje == 0:
            color = "#4CAF50"  # Verde
        elif porcentaje < 100:
            color = "#FF9800"  # Naranja
        else:
            color = "#f44336"  # Rojo

        return f"""
            QProgressBar {{
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: #f0f0f0;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """

    def _generar_tooltip(self) -> str:
        """Genera un tooltip enriquecido con información detallada"""
        numero_display = format_numero_parqueadero(self.numero)
        if self.vehiculos_actuales == 0:
            return (
                f"📊 PARQUEADERO {numero_display}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Estado: Disponible\n"
                f"Capacidad: 0/{self.capacidad_total}\n"
                f"Tipo: {self.tipo_espacio}\n\n"
                f"✅ Espacio libre"
            )

        # Generar información de vehículos asignados
        vehiculos_info = []
        for i, vehiculo in enumerate(self.vehiculos_detalle, 1):
            tipo_icon = "🚗" if vehiculo.get("tipo_vehiculo") == "Carro" else "🏍️" if vehiculo.get("tipo_vehiculo") == "Moto" else "🚲"
            placa = vehiculo.get("placa", "N/A")
            tipo_circ = vehiculo.get("tipo_circulacion", "N/A")
            funcionario = vehiculo.get("funcionario_nombre", "N/A")
            cargo = vehiculo.get("cargo", "N/A")

            # Etiquetas especiales
            etiquetas = []
            if vehiculo.get("tiene_parqueadero_exclusivo"):
                etiquetas.append("🏢 Directivo")
            if vehiculo.get("tiene_carro_hibrido"):
                etiquetas.append("⚡ Híbrido")
            if vehiculo.get("pico_placa_solidario"):
                etiquetas.append("🔄 Solidario")
            if vehiculo.get("discapacidad"):
                etiquetas.append("♿ Discapacidad")

            etiqueta_str = f" [{', '.join(etiquetas)}]" if etiquetas else ""

            vehiculos_info.append(
                f"{tipo_icon} Vehículo {i}:\n"
                f"   Placa: {placa} ({tipo_circ})\n"
                f"   Funcionario: {funcionario}\n"
                f"   Cargo: {cargo}{etiqueta_str}"
            )

        vehiculos_texto = "\n\n".join(vehiculos_info)

        # Estado de ocupación
        if self.vehiculos_actuales >= self.capacidad_total:
            estado_ocupacion = "🔴 Espacio completo"
        elif self.vehiculos_actuales > 0:
            estado_ocupacion = f"🟠 Espacio parcial ({self.capacidad_total - self.vehiculos_actuales} cupo{'s' if self.capacidad_total - self.vehiculos_actuales > 1 else ''} disponible{'s' if self.capacidad_total - self.vehiculos_actuales > 1 else ''})"
        else:
            estado_ocupacion = "🟢 Espacio disponible"

        numero_display = format_numero_parqueadero(self.numero)
        return (
            f"📊 INFORMACIÓN DETALLADA\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Parqueadero: {numero_display}\n"
            f"Sótano: {self.sotano or 'N/A'}\n"
            f"Tipo: {self.tipo_espacio}\n"
            f"Ocupación: {self.vehiculos_actuales}/{self.capacidad_total}\n"
            f"Modalidad: {self.tipo_ocupacion}\n\n"
            f"{vehiculos_texto}\n\n"
            f"{estado_ocupacion}"
        )

    def get_estado_style(self) -> str:
        """Retorna el estilo según el estado"""
        if self.estado == "Disponible":
            return "color: green; font-weight: bold; font-size: 10px;"
        elif self.estado == "Parcialmente_Asignado":
            return "color: orange; font-weight: bold; font-size: 10px;"
        else:
            return "color: red; font-weight: bold; font-size: 10px;"

    def get_frame_style(self) -> str:
        """Retorna el estilo del frame según el estado"""
        base = "QFrame { border-radius: 5px; border-width: 2px; "
        if self.estado == "Disponible":
            return base + "background-color: #E8F5E9; border-color: #4CAF50; } QFrame:hover { border-color: #2E7D32; border-width: 3px; }"
        elif self.estado == "Parcialmente_Asignado":
            return base + "background-color: #FFF3E0; border-color: #FF9800; } QFrame:hover { border-color: #F57C00; border-width: 3px; }"
        else:
            return base + "background-color: #FFEBEE; border-color: #f44336; } QFrame:hover { border-color: #C62828; border-width: 3px; }"
