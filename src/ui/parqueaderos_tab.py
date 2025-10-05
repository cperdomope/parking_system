# -*- coding: utf-8 -*-
"""
Módulo de la pestaña Parqueaderos del sistema de gestión de parqueadero
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QGridLayout, QScrollArea, QFrame,
    QSplitter, QTextEdit, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt

from ..database.manager import DatabaseManager
from ..models.parqueadero import ParqueaderoModel
from ..widgets.parking_widget import ParkingSpaceWidget
from .modal_detalle_parqueadero import DetalleParqueaderoModal


class ParqueaderosTab(QWidget):
    """Pestaña de visualización de parqueaderos"""

    # Señal que se emite cuando se actualiza la vista de parqueaderos
    parqueaderos_actualizados = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db = db_manager
        self.parqueadero_model = ParqueaderoModel(self.db)
        self.setup_ui()
        self.cargar_filtros_iniciales()
        self.cargar_parqueaderos()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        layout = QVBoxLayout()

        # Header con controles
        header_group = QGroupBox(" Vista de Parqueaderos - Solo Carros")
        header_layout = QGridLayout()

        # Estadísticas rápidas
        self.lbl_total = QLabel("Total: 250")
        self.lbl_disponibles = QLabel("Disponibles: -")
        self.lbl_parciales = QLabel("Parciales: -")
        self.lbl_completos = QLabel("Completos: -")

        # Estilo para estadísticas
        style_stats = "padding: 8px; border-radius: 4px; font-weight: bold;"
        self.lbl_total.setStyleSheet(f"{style_stats} background-color: #E3F2FD; color: #1976D2;")
        self.lbl_disponibles.setStyleSheet(f"{style_stats} background-color: #E8F5E9; color: #2E7D32;")
        self.lbl_parciales.setStyleSheet(f"{style_stats} background-color: #FFF3E0; color: #F57C00;")
        self.lbl_completos.setStyleSheet(f"{style_stats} background-color: #FFEBEE; color: #C62828;")

        header_layout.addWidget(self.lbl_total, 0, 0)
        header_layout.addWidget(self.lbl_disponibles, 0, 1)
        header_layout.addWidget(self.lbl_parciales, 0, 2)
        header_layout.addWidget(self.lbl_completos, 0, 3)

        # Controles de filtrado mejorados
        header_layout.addWidget(QLabel("Sótano:"), 1, 0)

        # Filtro por sótano
        self.combo_filtro_sotano = QComboBox()
        self.combo_filtro_sotano.addItem("Todos los sótanos", None)
        self.combo_filtro_sotano.currentTextChanged.connect(self.aplicar_filtros)
        header_layout.addWidget(self.combo_filtro_sotano, 1, 1)

        header_layout.addWidget(QLabel("Estado:"), 1, 2)

        # Filtro por estado (manteniendo compatibilidad)
        self.combo_filtro_estado = QComboBox()
        self.combo_filtro_estado.addItems(["Todos", "Disponible", "Parcialmente Asignado", "Completo"])
        self.combo_filtro_estado.currentTextChanged.connect(self.aplicar_filtros)
        self.combo_filtro_estado.setToolTip(
            "Estados basados solo en carros:\n"
            "• Disponible: 0 carros\n"
            "• Parcialmente Asignado: 1 carro\n"
            "• Completo: 2 carros\n\n"
            "Nota: Si un funcionario tiene parqueadero\n"
            "exclusivo (permite_compartir=NO), se muestra\n"
            "como 'Completo' aunque tenga solo 1 carro.\n\n"
            "Motos y bicicletas no afectan el estado"
        )
        header_layout.addWidget(self.combo_filtro_estado, 1, 3)

        self.btn_refrescar = QPushButton(" Refrescar")
        self.btn_refrescar.clicked.connect(self.cargar_parqueaderos)
        header_layout.addWidget(self.btn_refrescar, 2, 0)

        # Botón de ayuda
        btn_ayuda = QPushButton("ℹ️ Ayuda")
        btn_ayuda.clicked.connect(self.mostrar_ayuda)
        header_layout.addWidget(btn_ayuda, 2, 1)

        header_group.setLayout(header_layout)
        layout.addWidget(header_group)

        # Área principal con scroll SOLO vertical
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # NO scroll horizontal
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)     # Solo scroll vertical

        # Widget contenedor optimizado para scroll vertical únicamente
        self.parking_container = QWidget()
        self.parking_grid = QGridLayout()
        self.parking_grid.setSpacing(8)

        # Configurar para usar todo el ancho disponible sin scroll horizontal
        self.parking_container.setLayout(self.parking_grid)

        scroll.setWidget(self.parking_container)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def cargar_parqueaderos(self):
        """Carga y muestra todos los parqueaderos de carros organizados en una grilla optimizada

        IMPORTANTE: Esta pestaña solo muestra espacios para carros.
        Los estados reflejan únicamente la ocupación por carros.
        """
        # Solo cargar parqueaderos para carros
        parqueaderos = self.parqueadero_model.obtener_todos(tipo_vehiculo="Carro")

        # Limpiar grilla actual de forma segura
        for i in reversed(range(self.parking_grid.count())):
            item = self.parking_grid.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        # Calcular columnas dinámicamente para evitar scroll horizontal
        # Usar 8 columnas por defecto para garantizar presentación consistente
        if self.width() > 1200:  # Solo ajustar si hay suficiente espacio
            columnas = min(max(8, self.width() // 170), 12)
        else:
            columnas = 8  # Siempre mostrar 8 columnas por defecto

        # Crear widgets de parqueaderos
        self.parqueaderos_data = {}  # Guardar referencia para filtros

        for i, park in enumerate(parqueaderos):
            row = i // columnas
            col = i % columnas

            # Usar estado_display si está disponible (considera permite_compartir)
            estado_mostrar = park.get('estado_display', park['estado'])

            widget = ParkingSpaceWidget(
                parqueadero_id=park['id'],
                numero=park['numero_parqueadero'],
                estado=estado_mostrar,
                asignados=park.get('asignados', '') or ''
            )

            # Conectar señal de clic
            widget.clicked.connect(self.mostrar_detalle_parqueadero)

            self.parking_grid.addWidget(widget, row, col)
            self.parqueaderos_data[park['id']] = park

        # Actualizar estadísticas
        self.actualizar_estadisticas(parqueaderos)

        # Emitir señal de actualización
        self.parqueaderos_actualizados.emit()

    def filtrar_parqueaderos(self):
        """Filtra los parqueaderos según el estado seleccionado"""
        estado_filtro = self.combo_filtro_estado.currentText()

        for i in range(self.parking_grid.count()):
            widget = self.parking_grid.itemAt(i).widget()
            if isinstance(widget, ParkingSpaceWidget):
                if estado_filtro == "Todos":
                    widget.show()
                else:
                    estado_widget = widget.estado.replace("_", " ").title()
                    if estado_widget == estado_filtro:
                        widget.show()
                    else:
                        widget.hide()

    def actualizar_estadisticas(self, parqueaderos):
        """Actualiza las estadísticas mostradas en el header"""
        total = len(parqueaderos)
        # Usar estado_display que considera permite_compartir
        disponibles = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Disponible'])
        parciales = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Parcialmente_Asignado'])
        completos = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Completo'])

        self.lbl_total.setText(f"Total: {total}")
        self.lbl_disponibles.setText(f"Disponibles: {disponibles}")
        self.lbl_parciales.setText(f"Parciales: {parciales}")
        self.lbl_completos.setText(f"Completos: {completos}")

    def mostrar_detalle_parqueadero(self, parqueadero_id, numero_parqueadero):
        """Muestra el modal con el detalle del parqueadero"""
        try:
            # Validar que los datos sean válidos
            if not parqueadero_id or not numero_parqueadero:
                raise ValueError("ID de parqueadero o número no válido")

            # Verificar que el parqueadero existe
            query_validacion = "SELECT id FROM parqueaderos WHERE id = %s"
            resultado = self.db.fetch_one(query_validacion, (parqueadero_id,))

            if not resultado:
                raise ValueError(f"El parqueadero con ID {parqueadero_id} no existe")

            modal = DetalleParqueaderoModal(
                parqueadero_id=parqueadero_id,
                numero_parqueadero=numero_parqueadero,
                db_manager=self.db,
                parent=self
            )
            modal.exec_()
        except Exception as e:
            print(f"Error detallado al mostrar modal: {e}")  # Para debug
            QMessageBox.critical(
                self,
                " Error",
                f"No se pudo cargar la información del parqueadero:\n\n{str(e)}\n\n"
                f"Parqueadero ID: {parqueadero_id}\n"
                f"Número: {numero_parqueadero}"
            )

    def mostrar_ayuda(self):
        """Muestra información de ayuda sobre la vista"""
        QMessageBox.information(
            self,
            " Ayuda - Vista de Parqueaderos (Solo Carros)",
            "<h3>Vista de espacios para carros:</h3>"
            "<ul>"
            "<li><b>Clic en cualquier parqueadero</b> para ver información detallada</li>"
            "<li><b>Filtros disponibles</b>:</li>"
            "  <ul>"
            "    <li><b>Sótano:</b> Filtrar por Sótano-1, Sótano-2 o Sótano-3</li>"
            "    <li><b>Estado:</b> Disponible, Parcialmente Asignado o Completo</li>"
            "  </ul>"
            "<li><b>Colores de estado</b>:</li>"
            "  <ul>"
            "    <li>🟢 Verde: Disponible (0 carros)</li>"
            "    <li>🟡 Naranja: Parcialmente Asignado (1 carro)</li>"
            "    <li> Rojo: Completo (2 carros)</li>"
            "  </ul>"
            "<li><b>Regla de Parqueaderos Exclusivos 🚫:</b></li>"
            "  <ul>"
            "    <li>Si un funcionario tiene <b>permite_compartir = NO</b>,</li>"
            "    <li>el parqueadero se muestra como <b>Completo</b></li>"
            "    <li>aunque solo tenga 1 vehículo asignado.</li>"
            "    <li>Esto previene asignaciones adicionales.</li>"
            "  </ul>"
            "</ul>"
            "<p><b>Importante:</b> Esta pestaña muestra únicamente los 250 espacios para carros.<br>"
            "Los espacios para motos y bicicletas se gestionan en otras secciones.</p>"
        )

    def resizeEvent(self, event):
        """Recalcula la distribución al cambiar el tamaño de la ventana"""
        super().resizeEvent(event)
        # Solo recargar si el cambio de tamaño es significativo para evitar lag
        if hasattr(self, 'parqueaderos_data') and hasattr(self, '_last_width'):
            new_width = self.width()
            if abs(new_width - self._last_width) > 100:  # Solo si cambió más de 100px
                self._last_width = new_width
                self.reorganizar_parqueaderos()
        elif hasattr(self, 'parqueaderos_data'):
            self._last_width = self.width()

    def reorganizar_parqueaderos(self):
        """Reorganiza los widgets existentes sin recargar datos"""
        if not hasattr(self, 'parqueaderos_data') or not self.parqueaderos_data:
            return

        # Obtener widgets existentes
        widgets = []
        for i in range(self.parking_grid.count()):
            item = self.parking_grid.itemAt(i)
            if item and item.widget():
                widgets.append(item.widget())

        # Limpiar grilla de forma segura
        for i in reversed(range(self.parking_grid.count())):
            item = self.parking_grid.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)

        # Recalcular columnas
        columnas = max(1, self.width() // 170) if self.width() > 0 else 8
        columnas = min(columnas, 12)

        # Reorganizar widgets
        for i, widget in enumerate(widgets):
            row = i // columnas
            col = i % columnas
            self.parking_grid.addWidget(widget, row, col)

    def cargar_filtros_iniciales(self):
        """Carga las opciones de filtros desde la base de datos"""
        self.combo_filtro_sotano.clear()
        self.combo_filtro_sotano.addItem("Todos los sótanos", None)

        # Siempre cargar exactamente los 3 sótanos principales (sin duplicaciones)
        sotanos_disponibles = ['Sótano-1', 'Sótano-2', 'Sótano-3']

        for sotano in sotanos_disponibles:
            self.combo_filtro_sotano.addItem(sotano, sotano)

        print(f"Sotanos cargados en parqueaderos: {sotanos_disponibles}")


    def aplicar_filtros(self):
        """Aplica todos los filtros seleccionados"""
        try:
            # Obtener valores de filtros
            sotano_seleccionado = self.combo_filtro_sotano.currentData()
            # Siempre filtrar solo por carros
            tipo_seleccionado = "Carro"

            # Mapear estado seleccionado
            estado_texto = self.combo_filtro_estado.currentText()
            estado_seleccionado = None
            if estado_texto != "Todos":
                if estado_texto == "Parcialmente Asignado":
                    estado_seleccionado = "Parcialmente_Asignado"
                else:
                    estado_seleccionado = estado_texto

            # Cargar parqueaderos con filtros
            self.cargar_parqueaderos_con_filtros(sotano_seleccionado, tipo_seleccionado, estado_seleccionado)

        except Exception as e:
            print(f"Error al aplicar filtros: {e}")
            # Fallback a carga sin filtros
            self.cargar_parqueaderos()

    def cargar_parqueaderos_con_filtros(self, sotano=None, tipo_vehiculo=None, estado=None):
        """Carga parqueaderos con filtros específicos"""
        try:
            parqueaderos = self.parqueadero_model.obtener_todos(
                sotano=sotano,
                tipo_vehiculo=tipo_vehiculo,
                estado=estado
            )

            # Limpiar grilla actual de forma segura
            for i in reversed(range(self.parking_grid.count())):
                item = self.parking_grid.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.setParent(None)

            # Calcular columnas dinámicamente
            columnas = max(1, self.width() // 170) if self.width() > 0 else 8
            columnas = min(columnas, 12)

            # Crear widgets de parqueaderos
            self.parqueaderos_data = {}

            for i, park in enumerate(parqueaderos):
                row = i // columnas
                col = i % columnas

                # Usar estado_display si está disponible (considera permite_compartir)
                estado_mostrar = park.get('estado_display', park['estado'])

                widget = ParkingSpaceWidget(
                    parqueadero_id=park['id'],
                    numero=park['numero_parqueadero'],
                    estado=estado_mostrar,
                    asignados=park.get('asignados', '') or ''
                )

                # Conectar señal de clic
                widget.clicked.connect(self.mostrar_detalle_parqueadero)

                self.parking_grid.addWidget(widget, row, col)
                self.parqueaderos_data[park['id']] = park

            # Actualizar estadísticas con filtros
            self.actualizar_estadisticas_con_filtros(parqueaderos, sotano)

            # Emitir señal de actualización
            self.parqueaderos_actualizados.emit()

        except Exception as e:
            print(f"Error al cargar parqueaderos con filtros: {e}")
            # Fallback a método original
            self.cargar_parqueaderos()

    def actualizar_estadisticas_con_filtros(self, parqueaderos, sotano=None):
        """Actualiza las estadísticas basado en los parqueaderos filtrados"""
        try:
            if sotano:
                # Para estadísticas por sótano, calcular manualmente con estado_display
                total = len(parqueaderos)
                disponibles = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Disponible'])
                parciales = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Parcialmente_Asignado'])
                completos = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Completo'])

                stats = {
                    'total_parqueaderos': total,
                    'disponibles': disponibles,
                    'parcialmente_asignados': parciales,
                    'completos': completos
                }
                prefix = f"{sotano} - "
            else:
                # Estadísticas de los parqueaderos mostrados actualmente
                total = len(parqueaderos)
                disponibles = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Disponible'])
                parciales = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Parcialmente_Asignado'])
                completos = len([p for p in parqueaderos if p.get('estado_display', p['estado']) == 'Completo'])

                stats = {
                    'total_parqueaderos': total,
                    'disponibles': disponibles,
                    'parcialmente_asignados': parciales,
                    'completos': completos
                }
                prefix = "Filtrados - "

            self.lbl_total.setText(f"{prefix}Total: {stats['total_parqueaderos']}")
            self.lbl_disponibles.setText(f"Disponibles: {stats['disponibles']}")
            self.lbl_parciales.setText(f"Parciales: {stats['parcialmente_asignados']}")
            self.lbl_completos.setText(f"Completos: {stats['completos']}")

        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")
            # Estadísticas por defecto
            self.actualizar_estadisticas(parqueaderos)

    def filtrar_parqueaderos(self):
        """Método de compatibilidad - redirige a aplicar_filtros"""
        self.aplicar_filtros()


    def actualizar_parqueaderos(self):
        """Actualiza la vista de parqueaderos"""
        self.cargar_filtros_iniciales()


        self.cargar_parqueaderos()