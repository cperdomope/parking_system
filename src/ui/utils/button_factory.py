# -*- coding: utf-8 -*-
"""
Button Factory
Creates standardized buttons to reduce duplication
"""

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize


class ButtonFactory:
    """Factory for creating standardized UI buttons"""

    @staticmethod
    def create_action_button(icon: str, tooltip: str, color: str = "blue",
                            size: int = 28) -> QPushButton:
        """
        Create standardized action button (edit/view/delete icons)

        Args:
            icon: Button icon/emoji text
            tooltip: Hover tooltip text
            color: Color theme (blue/green/red/yellow)
            size: Button size in pixels

        Returns:
            Configured QPushButton
        """
        button = QPushButton(icon)
        button.setToolTip(tooltip)
        button.setFixedSize(QSize(size, size))
        button.setCursor(Qt.PointingHandCursor)

        # Color-specific styles
        color_map = {
            "blue": "rgba(52, 152, 219, 0.1)",
            "green": "rgba(39, 174, 96, 0.1)",
            "red": "rgba(231, 76, 60, 0.1)",
            "yellow": "rgba(243, 156, 18, 0.1)",
        }

        hover_color = color_map.get(color.lower(), color_map["blue"])
        pressed_color = hover_color.replace("0.1", "0.2")

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 16px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border-radius: 4px;
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """)

        return button

    @staticmethod
    def create_pagination_button(text: str, enabled: bool = True) -> QPushButton:
        """
        Create standardized pagination button

        Args:
            text: Button text (e.g., "Primera", "Anterior")
            enabled: Initial enabled state

        Returns:
            Configured QPushButton
        """
        button = QPushButton(text)
        button.setEnabled(enabled)
        button.setCursor(Qt.PointingHandCursor if enabled else Qt.ForbiddenCursor)

        button.setStyleSheet("""
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
        """)

        return button

    @staticmethod
    def create_primary_button(text: str, icon: str = "") -> QPushButton:
        """
        Create primary action button

        Args:
            text: Button text
            icon: Optional emoji/icon prefix

        Returns:
            Configured QPushButton
        """
        button_text = f"{icon} {text}" if icon else text
        button = QPushButton(button_text)
        button.setCursor(Qt.PointingHandCursor)

        button.setStyleSheet("""
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
        """)

        return button

    @staticmethod
    def create_success_button(text: str, icon: str = "") -> QPushButton:
        """
        Create success/confirm button (green)

        Args:
            text: Button text
            icon: Optional emoji/icon prefix

        Returns:
            Configured QPushButton
        """
        button_text = f"{icon} {text}" if icon else text
        button = QPushButton(button_text)
        button.setCursor(Qt.PointingHandCursor)

        button.setStyleSheet("""
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
        """)

        return button

    @staticmethod
    def create_danger_button(text: str, icon: str = "") -> QPushButton:
        """
        Create danger/delete button (red)

        Args:
            text: Button text
            icon: Optional emoji/icon prefix

        Returns:
            Configured QPushButton
        """
        button_text = f"{icon} {text}" if icon else text
        button = QPushButton(button_text)
        button.setCursor(Qt.PointingHandCursor)

        button.setStyleSheet("""
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
        """)

        return button


# Import Qt constants for button factory
from PyQt5.QtCore import Qt
