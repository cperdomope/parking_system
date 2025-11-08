# -*- coding: utf-8 -*-
"""
Centralized Dialog Utilities
Replaces 47+ duplicate QMessageBox instances across UI tabs
"""

from PyQt5.QtWidgets import QMessageBox


class UIDialogs:
    """Standardized dialog helpers to reduce code duplication"""

    @staticmethod
    def show_warning(parent, title: str, message: str) -> int:
        """
        Show warning dialog with standardized style

        Args:
            parent: Parent widget
            title: Dialog title
            message: Warning message

        Returns:
            Button clicked (QMessageBox.Ok, etc.)
        """
        return QMessageBox.warning(parent, title, message)

    @staticmethod
    def show_error(parent, title: str, message: str) -> int:
        """
        Show error/critical dialog with standardized style

        Args:
            parent: Parent widget
            title: Dialog title
            message: Error message

        Returns:
            Button clicked
        """
        return QMessageBox.critical(parent, title, message)

    @staticmethod
    def show_success(parent, title: str, message: str) -> int:
        """
        Show success/information dialog with standardized style

        Args:
            parent: Parent widget
            title: Dialog title
            message: Success message

        Returns:
            Button clicked
        """
        return QMessageBox.information(parent, title, message)

    @staticmethod
    def show_question(parent, title: str, message: str) -> int:
        """
        Show yes/no question dialog

        Args:
            parent: Parent widget
            title: Dialog title
            message: Question message

        Returns:
            QMessageBox.Yes or QMessageBox.No
        """
        return QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

    @staticmethod
    def confirm_delete(parent, item_name: str) -> bool:
        """
        Show standardized delete confirmation dialog

        Args:
            parent: Parent widget
            item_name: Name of item to delete

        Returns:
            True if confirmed, False otherwise
        """
        result = QMessageBox.question(
            parent,
            "Confirmar Eliminacion",
            f"Esta seguro que desea eliminar:\n\n{item_name}\n\n"
            "Esta accion no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return result == QMessageBox.Yes

    @staticmethod
    def show_validation_error(parent, errors: list) -> int:
        """
        Show validation errors in standardized format

        Args:
            parent: Parent widget
            errors: List of error messages

        Returns:
            Button clicked
        """
        if not errors:
            return QMessageBox.Ok

        error_text = "\n".join([f"- {error}" for error in errors])
        return QMessageBox.warning(
            parent,
            "Errores de Validacion",
            f"Por favor corrija los siguientes errores:\n\n{error_text}"
        )
