# -*- coding: utf-8 -*-
"""
Table Utilities
Helpers for standardized table setup and manipulation
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView


class TableUtils:
    """Reusable utilities for QTableWidget operations"""

    @staticmethod
    def setup_table(table: QTableWidget, columns: list, widths: list = None,
                    row_height: int = 50, stretch_last: bool = True):
        """
        Standardized table setup to avoid duplication

        Args:
            table: QTableWidget instance
            columns: List of column header names
            widths: List of column widths (optional, auto-size if None)
            row_height: Default row height
            stretch_last: Whether to stretch last column to fill space
        """
        # Basic setup
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(row_height)

        # Set column widths
        if widths:
            if len(widths) != len(columns):
                raise ValueError("Column widths must match number of columns")
            for i, width in enumerate(widths):
                table.setColumnWidth(i, width)
        else:
            # Auto-resize columns to content
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Stretch last column if requested
        if stretch_last:
            table.horizontalHeader().setStretchLastSection(True)

    @staticmethod
    def create_centered_item(text: str) -> QTableWidgetItem:
        """
        Create table item with centered alignment

        Args:
            text: Item text

        Returns:
            QTableWidgetItem with center alignment
        """
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignCenter)
        return item

    @staticmethod
    def create_readonly_item(text: str, centered: bool = True) -> QTableWidgetItem:
        """
        Create read-only table item

        Args:
            text: Item text
            centered: Whether to center-align text

        Returns:
            QTableWidgetItem that is non-editable
        """
        item = QTableWidgetItem(str(text))
        if centered:
            item.setTextAlignment(Qt.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    @staticmethod
    def clear_table(table: QTableWidget):
        """
        Clear all rows from table while keeping headers

        Args:
            table: QTableWidget instance
        """
        table.setRowCount(0)

    @staticmethod
    def populate_table(table: QTableWidget, data: list, cell_factory=None):
        """
        Populate table with data rows

        Args:
            table: QTableWidget instance
            data: List of row data (each row is a list/dict)
            cell_factory: Optional function to create custom cell items
                         Signature: cell_factory(row_index, col_index, value) -> QTableWidgetItem
        """
        TableUtils.clear_table(table)
        table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            # Handle both list and dict row data
            if isinstance(row_data, dict):
                row_data = list(row_data.values())

            for col_idx, value in enumerate(row_data):
                if cell_factory:
                    item = cell_factory(row_idx, col_idx, value)
                else:
                    item = TableUtils.create_centered_item(value)
                table.setItem(row_idx, col_idx, item)

    @staticmethod
    def get_selected_row_data(table: QTableWidget) -> list:
        """
        Get data from currently selected row

        Args:
            table: QTableWidget instance

        Returns:
            List of cell values from selected row, or empty list if none selected
        """
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            return []

        row_index = selected_rows[0].row()
        row_data = []

        for col in range(table.columnCount()):
            item = table.item(row_index, col)
            row_data.append(item.text() if item else "")

        return row_data

    @staticmethod
    def apply_default_style(table: QTableWidget, header_bg: str = "#34B5A9"):
        """
        Apply standardized table stylesheet

        Args:
            table: QTableWidget instance
            header_bg: Header background color
        """
        stylesheet = f"""
            QTableWidget {{
                gridline-color: #d0d0d0;
                background-color: white;
                alternate-background-color: #F5F5F5;
                selection-background-color: #d5e8f7;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QTableWidget::item:selected {{
                background-color: #d5e8f7;
                color: #2c3e50;
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: #FFFFFF;
                font-weight: bold;
                padding: 8px;
                border: none;
                font-size: 12px;
            }}
            QHeaderView::section:horizontal {{
                border-right: 1px solid #2C9A8F;
            }}
        """
        table.setStyleSheet(stylesheet)
