# -*- coding: utf-8 -*-
"""
Centralized UI Styles for Parking System
Consolidates duplicate stylesheets from funcionarios_tab, vehiculos_tab, and asignaciones_tab
"""


class UIStyles:
    """Centralized stylesheet definitions"""

    # ========== COMBOBOX STYLES ==========
    COMBOBOX = """
        QComboBox {
            padding: 8px;
            border: 2px solid #27ae60;
            border-radius: 5px;
            font-size: 13px;
            min-width: 120px;
            background-color: white;
            min-height: 25px;
        }
        QComboBox:hover {
            border-color: #229954;
        }
        QComboBox:focus {
            border: 2px solid #229954;
            background-color: #e8f8f0;
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 5px;
        }
        QComboBox QAbstractItemView {
            border: 2px solid #27ae60;
            background-color: white;
            selection-background-color: #27ae60;
            selection-color: white;
            outline: none;
        }
    """

    # ========== INPUT FIELD STYLES ==========
    LINEEDIT = """
        QLineEdit {
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            background-color: white;
        }
        QLineEdit:focus {
            border-color: #3498db;
        }
        QLineEdit:disabled {
            background-color: #ecf0f1;
            color: #7f8c8d;
        }
    """

    # ========== BUTTON STYLES ==========
    BUTTON_PRIMARY = """
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
    """

    BUTTON_SUCCESS = """
        QPushButton {
            background-color: #27ae60;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #229954;
        }
        QPushButton:pressed {
            background-color: #1e8449;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
    """

    BUTTON_DANGER = """
        QPushButton {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #c0392b;
        }
        QPushButton:pressed {
            background-color: #a93226;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
    """

    BUTTON_WARNING = """
        QPushButton {
            background-color: #f39c12;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #e67e22;
        }
        QPushButton:pressed {
            background-color: #d35400;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
    """

    BUTTON_PAGINATION = """
        QPushButton {
            background-color: #3498db;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            padding: 8px 15px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #21618c;
        }
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
    """

    BUTTON_ACTION_BLUE = """
        QPushButton {
            background-color: transparent;
            border: none;
            font-size: 16px;
            padding: 4px;
        }
        QPushButton:hover {
            background-color: rgba(52, 152, 219, 0.1);
            border-radius: 4px;
        }
        QPushButton:pressed {
            background-color: rgba(52, 152, 219, 0.2);
        }
    """

    BUTTON_ACTION_GREEN = """
        QPushButton {
            background-color: transparent;
            border: none;
            font-size: 16px;
            padding: 4px;
        }
        QPushButton:hover {
            background-color: rgba(39, 174, 96, 0.1);
            border-radius: 4px;
        }
        QPushButton:pressed {
            background-color: rgba(39, 174, 96, 0.2);
        }
    """

    BUTTON_ACTION_RED = """
        QPushButton {
            background-color: transparent;
            border: none;
            font-size: 16px;
            padding: 4px;
        }
        QPushButton:hover {
            background-color: rgba(231, 76, 60, 0.1);
            border-radius: 4px;
        }
        QPushButton:pressed {
            background-color: rgba(231, 76, 60, 0.2);
        }
    """

    # ========== GROUPBOX STYLES ==========
    @staticmethod
    def groupbox(border_color="#3498db"):
        """Returns groupbox style with customizable border color"""
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid {border_color};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
                background-color: white;
            }}
        """

    GROUPBOX_PRIMARY = groupbox.__func__(border_color="#3498db")
    GROUPBOX_SUCCESS = groupbox.__func__(border_color="#27ae60")
    GROUPBOX_WARNING = groupbox.__func__(border_color="#f39c12")

    # ========== TABLE STYLES ==========
    @staticmethod
    def table(header_bg="#34B5A9", header_text="#FFFFFF",
              alternate_row="#F5F5F5", selection_bg="#3498db"):
        """Returns table style with customizable colors"""
        return f"""
            QTableWidget {{
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: {alternate_row};
                selection-background-color: {selection_bg};
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: {selection_bg};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: {header_text};
                font-weight: bold;
                padding: 8px;
                border: none;
                font-size: 12px;
            }}
            QHeaderView::section:horizontal {{
                border-right: 1px solid #2C9A8F;
            }}
        """

    TABLE_DEFAULT = table.__func__()

    # ========== LABEL STYLES ==========
    LABEL_TITLE = """
        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
        }
    """

    LABEL_SUBTITLE = """
        QLabel {
            font-size: 14px;
            font-weight: bold;
            color: #34495e;
        }
    """

    LABEL_FORM = """
        QLabel {
            font-size: 12px;
            font-weight: bold;
            color: #2c3e50;
        }
    """

    # ========== TEXTAREA STYLES ==========
    TEXTEDIT = """
        QTextEdit {
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            background-color: white;
        }
        QTextEdit:focus {
            border-color: #3498db;
        }
    """

    # ========== CHECKBOX/RADIO STYLES ==========
    CHECKBOX = """
        QCheckBox {
            font-size: 12px;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 3px;
            border: 2px solid #bdc3c7;
        }
        QCheckBox::indicator:checked {
            background-color: #3498db;
            border-color: #3498db;
        }
        QCheckBox::indicator:hover {
            border-color: #3498db;
        }
    """

    # ========== SPINBOX STYLES ==========
    SPINBOX = """
        QSpinBox, QDoubleSpinBox {
            border: 2px solid #bdc3c7;
            border-radius: 6px;
            padding: 6px;
            font-size: 12px;
            background-color: white;
        }
        QSpinBox:focus, QDoubleSpinBox:focus {
            border-color: #3498db;
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            border-left: 1px solid #bdc3c7;
            border-radius: 0 6px 0 0;
            background-color: #ecf0f1;
        }
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            border-left: 1px solid #bdc3c7;
            border-radius: 0 0 6px 0;
            background-color: #ecf0f1;
        }
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
            background-color: #d5dbdb;
        }
    """
