# -*- coding: utf-8 -*-
"""
Widget personalizado para representar un espacio de parqueo
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor


class ParkingSpaceWidget(QFrame):
    """Widget personalizado para representar un espacio de parqueo"""

    # Señal emitida cuando se hace clic en el parqueadero
    clicked = pyqtSignal(int, int)  # parqueadero_id, numero_parqueadero

    def __init__(self, parqueadero_id: int, numero: int, estado: str, asignados: str = ""):
        super().__init__()
        self.parqueadero_id = parqueadero_id
        self.numero = numero
        self.estado = estado
        self.asignados = asignados
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del widget"""
        self.setFixedSize(150, 100)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)

        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Número del parqueadero (clickeable)
        self.lbl_numero = QLabel(f"P-{self.numero:03d}")
        self.lbl_numero.setAlignment(Qt.AlignCenter)
        self.lbl_numero.setStyleSheet(
            "font-size: 16px; font-weight: bold; "
            "color: #1976D2; "
            "padding: 5px; border-radius: 3px;"
        )
        self.lbl_numero.setCursor(QCursor(Qt.PointingHandCursor))
        self.lbl_numero.mousePressEvent = self.on_numero_clicked

        # Estado
        lbl_estado = QLabel(self.estado.replace("_", " "))
        lbl_estado.setAlignment(Qt.AlignCenter)
        lbl_estado.setStyleSheet(self.get_estado_style())

        # Asignados
        lbl_asignados = QLabel(self.asignados[:30] + "..." if len(self.asignados) > 30 else self.asignados)
        lbl_asignados.setWordWrap(True)
        lbl_asignados.setStyleSheet("font-size: 10px;")

        layout.addWidget(self.lbl_numero)
        layout.addWidget(lbl_estado)
        layout.addWidget(lbl_asignados)
        layout.addStretch()

        self.setLayout(layout)
        self.setStyleSheet(self.get_frame_style())

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

    def get_estado_style(self) -> str:
        """Retorna el estilo según el estado"""
        if self.estado == "Disponible":
            return "color: green; font-weight: bold;"
        elif self.estado == "Parcialmente_Asignado":
            return "color: orange; font-weight: bold;"
        else:
            return "color: red; font-weight: bold;"

    def get_frame_style(self) -> str:
        """Retorna el estilo del frame según el estado"""
        base = "QFrame { border-radius: 5px; border-width: 2px; "
        if self.estado == "Disponible":
            return base + "background-color: #E8F5E9; border-color: #4CAF50; } QFrame:hover { border-color: #2E7D32; }"
        elif self.estado == "Parcialmente_Asignado":
            return base + "background-color: #FFF3E0; border-color: #FF9800; } QFrame:hover { border-color: #F57C00; }"
        else:
            return base + "background-color: #FFEBEE; border-color: #f44336; } QFrame:hover { border-color: #C62828; }"