# -*- coding: utf-8 -*-
"""
Estilos CSS para la aplicación del sistema de gestión de parqueadero
"""


class AppStyles:
    """Define los estilos CSS para la aplicación"""

    MAIN_STYLE = """
    QMainWindow {
        background-color: #f5f5f5;
    }

    QTabWidget::pane {
        border: 1px solid #cccccc;
        background-color: white;
        border-radius: 5px;
    }

    QTabBar::tab {
        background-color: #e0e0e0;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
    }

    QTabBar::tab:selected {
        background-color: white;
        border-bottom: 2px solid #2196F3;
    }

    QTabBar::tab:hover {
        background-color: #e3e4e5;
    }

    QPushButton {
        background-color: #2196F3;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        min-width: 100px;
    }

    QPushButton:hover {
        background-color: #1976D2;
    }

    QPushButton:pressed {
        background-color: #0D47A1;
    }

    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }

    QPushButton.danger {
        background-color: #f44336;
    }

    QPushButton.danger:hover {
        background-color: #d32f2f;
    }

    QPushButton.success {
        background-color: #4CAF50;
    }

    QPushButton.success:hover {
        background-color: #388E3C;
    }

    QLineEdit, QSpinBox, QTextEdit {
        padding: 8px;
        border: 1px solid #cccccc;
        border-radius: 4px;
        background-color: white;
        font-size: 14px;
    }

    /* ==============================
       🎨 ESTILO DEL COMBOBOX
       ============================== */
    QComboBox {
        background-color: #ffffff;
        border: 1px solid #b0bec5;
        border-radius: 6px;
        padding: 6px 30px 6px 10px;
        font-size: 14px;
        color: #333;
    }

    /* Sin cambios visuales al pasar el mouse sobre el combobox cerrado */
    QComboBox:hover {
        background-color: #ffffff;
        color: #333;
    }

    /* 🔽 Flechita CSS hacia abajo */
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 25px;
        border-left: 1px solid #b0bec5;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
        background: transparent;
    }

    QComboBox::down-arrow {
        image: none;
        width: 0;
        height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 7px solid #555;
        margin-right: 6px;
    }

    QComboBox::down-arrow:on {
        border-top: 7px solid #2196F3;
    }

    /* ==============================
       📋 MENÚ DESPLEGABLE (LISTA)
       ============================== */
    QComboBox QAbstractItemView {
        background: #ffffff;
        border: 1px solid #2196F3;
        border-radius: 6px;
        padding: 2px;
        outline: none;
    }

    QComboBox QAbstractItemView::item {
        padding: 8px;
        color: #333333;
        background-color: #ffffff;
        min-height: 28px;
        border: none;
    }

    /* 🌈 Hover y selección al desplegar */
    QComboBox QAbstractItemView::item:hover {
        background-color: #42A5F5 !important;
        color: #ffffff !important;
        font-weight: bold;
    }

    QComboBox QAbstractItemView::item:selected {
        background-color: #42A5F5 !important;
        color: #ffffff !important;
        font-weight: bold;
    }

    QLabel {
        color: #333333;
        font-size: 14px;
    }

    QGroupBox {
        font-weight: bold;
        border: 2px solid #cccccc;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        background-color: white;
    }

    QTableWidget {
        border: 1px solid #cccccc;
        border-radius: 5px;
        background-color: white;
        gridline-color: #e0e0e0;
    }

    QTableWidget::item {
        padding: 5px;
        color: #000000;
    }

    QTableWidget::item:selected {
        background-color: #E3F2FD;
        color: #1976D2;
    }

    QHeaderView::section {
        background-color: #2196F3;
        color: white;
        padding: 8px;
        border: none;
        font-weight: bold;
    }

    QMessageBox {
        background-color: white;
    }

    QProgressBar {
        border: 1px solid #cccccc;
        border-radius: 5px;
        text-align: center;
        background-color: #f0f0f0;
    }

    QProgressBar::chunk {
        background-color: #2196F3;
        border-radius: 5px;
    }
    """
