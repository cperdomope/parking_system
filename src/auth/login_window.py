# -*- coding: utf-8 -*-
"""
Ventana de login futurista para el sistema de gestión de parqueadero
"""

import sys

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .auth_manager import AuthManager


class FuturisticLoginWindow(QWidget):
    """
    Ventana de login con diseño futurista y profesional
    """

    login_successful = pyqtSignal(dict)  # Señal emitida cuando el login es exitoso

    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.password_visible = False
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configuración de ventana
        self.setWindowTitle("Ssalud Plaza Claro - Acceso al Sistema")
        self.setFixedSize(500, 650)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setAlignment(Qt.AlignCenter)

        # Contenedor principal con bordes redondeados
        self.main_container = QFrame()
        self.main_container.setObjectName("mainContainer")
        self.main_container.setFixedSize(470, 620)

        # Layout del contenedor
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(30, 20, 30, 20)
        container_layout.setSpacing(0)  # Controlaremos spacing manualmente

        # Botón de cerrar
        self.create_close_button(container_layout)

        # Spacer pequeño después del botón cerrar
        container_layout.addSpacing(10)

        # Header con logo y título
        self.create_header(container_layout)

        # Spacer entre header y formulario
        container_layout.addSpacing(35)

        # Formulario de login
        self.create_form(container_layout)

        # Spacer entre formulario y botón
        container_layout.addSpacing(30)

        # Botón de login
        self.create_login_button(container_layout)

        # Spacer entre botón y footer
        container_layout.addSpacing(25)

        # Footer
        self.create_footer(container_layout)

        # Spacer final para balance
        container_layout.addSpacing(15)

        # Agregar al layout principal
        main_layout.addWidget(self.main_container)
        self.setLayout(main_layout)

        # Aplicar estilos
        self.apply_styles()

        # Efectos de sombra
        self.add_shadow_effects()

    def create_close_button(self, layout):
        """Crea el botón de cerrar personalizado"""
        # Contenedor para el botón de cerrar (alineado a la derecha)
        close_container = QHBoxLayout()
        close_container.addStretch()  # Empuja el botón hacia la derecha

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.close_application)

        close_container.addWidget(self.close_btn)
        layout.addLayout(close_container)

    def create_header(self, layout):
        """Crea el header con logo y título"""
        # Logo (placeholder)
        logo_label = QLabel("🏢")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setObjectName("logoLabel")
        layout.addWidget(logo_label)

        # Pequeño espacio entre logo y título
        layout.addSpacing(8)

        # Título principal
        title_label = QLabel("SISTEMA DE PARQUEADERO")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        # Pequeño espacio entre título y subtítulo
        layout.addSpacing(5)

        # Subtítulo
        subtitle_label = QLabel("Ssalud Plaza Claro")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("subtitleLabel")
        layout.addWidget(subtitle_label)

    def create_form(self, layout):
        """Crea el formulario de login"""
        # Contenedor principal del formulario
        form_container = QFrame()
        form_container.setObjectName("formContainer")
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(20)  # Espacio entre campos

        # Campo de usuario
        user_container = QFrame()
        user_container.setObjectName("inputContainer")
        user_layout = QVBoxLayout(user_container)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.setSpacing(8)

        user_label = QLabel("USUARIO")
        user_label.setObjectName("inputLabel")
        user_layout.addWidget(user_label)

        self.user_input = QLineEdit()
        self.user_input.setObjectName("inputField")
        self.user_input.setPlaceholderText("Ingrese su usuario")
        self.user_input.setText("splaza")  # Usuario por defecto para pruebas
        self.user_input.setFixedHeight(45)  # Altura fija para mejor apariencia
        user_layout.addWidget(self.user_input)

        form_layout.addWidget(user_container)

        # Campo de contraseña
        password_container = QFrame()
        password_container.setObjectName("inputContainer")
        password_layout = QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)

        password_label = QLabel("CONTRASEÑA")
        password_label.setObjectName("inputLabel")
        password_layout.addWidget(password_label)

        # Contenedor para input y botón de visibilidad
        password_input_container = QFrame()
        password_input_container.setObjectName("passwordContainer")
        password_input_layout = QHBoxLayout(password_input_container)
        password_input_layout.setContentsMargins(0, 0, 0, 0)
        password_input_layout.setSpacing(2)

        self.password_input = QLineEdit()
        self.password_input.setObjectName("passwordField")
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(45)  # Misma altura que usuario
        password_input_layout.addWidget(self.password_input)

        # Botón para mostrar/ocultar contraseña
        self.toggle_password_btn = QPushButton("👁")
        self.toggle_password_btn.setObjectName("togglePasswordBtn")
        self.toggle_password_btn.setFixedSize(45, 45)  # Mismo alto que input
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_input_layout.addWidget(self.toggle_password_btn)

        password_layout.addWidget(password_input_container)
        form_layout.addWidget(password_container)

        layout.addWidget(form_container)

        # Conectar Enter para hacer login
        self.user_input.returnPressed.connect(self.attempt_login)
        self.password_input.returnPressed.connect(self.attempt_login)

    def create_login_button(self, layout):
        """Crea el botón de login"""
        # Contenedor para centrar el botón
        button_container = QFrame()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.login_btn = QPushButton("INICIAR SESIÓN")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setFixedHeight(50)
        self.login_btn.setMinimumWidth(200)  # Ancho mínimo para mejor apariencia
        self.login_btn.clicked.connect(self.attempt_login)

        button_layout.addWidget(self.login_btn)
        layout.addWidget(button_container)

    def create_footer(self, layout):
        """Crea el footer"""
        footer_label = QLabel("Sistema de Gestión Modular v1.0")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_label.setObjectName("footerLabel")
        layout.addWidget(footer_label)

    def toggle_password_visibility(self):
        """Alterna la visibilidad de la contraseña"""
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_btn.setText("👁")
            self.password_visible = False
        else:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_btn.setText("🙈")
            self.password_visible = True

    def attempt_login(self):
        """Intenta realizar el login"""
        usuario = self.user_input.text().strip()
        contraseña = self.password_input.text()

        if not usuario or not contraseña:
            self.show_error("Por favor complete todos los campos")
            return

        # Deshabilitar botón durante la autenticación
        self.login_btn.setEnabled(False)
        self.login_btn.setText("VALIDANDO...")

        # Simular delay de autenticación para mejor UX
        QTimer.singleShot(1000, lambda: self.process_login(usuario, contraseña))

    def process_login(self, usuario, contraseña):
        """Procesa el login con el manejador de autenticación"""
        try:
            # El nuevo authenticate() retorna (bool, str)
            success, message = self.auth_manager.authenticate(usuario, contraseña)

            if success:
                self.show_success("¡Bienvenido al sistema!")
                user_data = self.auth_manager.get_current_user()

                # Marcar que hay un login exitoso pendiente (no cerrar DB ni aplicación)
                self._login_success_pending = True

                self.login_successful.emit(user_data)
                QTimer.singleShot(1500, self.hide)  # Solo ocultar, no cerrar
            else:
                # Mostrar mensaje específico de error
                self.show_error(message)
        except Exception as e:
            self.show_error(f"Error de conexión: {str(e)}")
        finally:
            # Restaurar botón
            self.login_btn.setEnabled(True)
            self.login_btn.setText("INICIAR SESIÓN")

    def show_error(self, message):
        """Muestra un mensaje de error"""
        self.show_message(message, "error")

    def show_success(self, message):
        """Muestra un mensaje de éxito"""
        self.show_message(message, "success")

    def show_message(self, message, type_msg):
        """Muestra un mensaje temporal en la interfaz"""
        # Por ahora usamos QMessageBox, se puede mejorar con un toast personalizado
        if type_msg == "error":
            QMessageBox.warning(self, "Error de Autenticación", message)
        else:
            QMessageBox.information(self, "Éxito", message)

    def setup_animations(self):
        """Configura animaciones para la interfaz"""
        # Animación de entrada
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)

    def close_application(self):
        """Cierra la aplicación completamente y limpia recursos"""
        try:
            # Solo cerrar la base de datos si no hay login exitoso pendiente
            if not hasattr(self, "_login_success_pending"):
                if hasattr(self.auth_manager, "db") and self.auth_manager.db:
                    self.auth_manager.db.disconnect()
                    print("Conexión a base de datos cerrada - Login cancelado")

            # Cerrar la aplicación
            QApplication.quit()

        except Exception as e:
            print(f"Error al cerrar aplicación: {e}")
            QApplication.quit()

    def close_window_only(self):
        """Cierra solo la ventana sin terminar la aplicación"""
        self.close()

    def closeEvent(self, event):
        """Evento al cerrar la ventana (X del sistema o Alt+F4)"""
        # Solo cerrar aplicación si no es un login exitoso
        if not hasattr(self, "_login_success_pending") or not self._login_success_pending:
            self.close_application()
        event.accept()

    def showEvent(self, event):
        """Evento al mostrar la ventana"""
        super().showEvent(event)
        self.fade_animation.start()

    def add_shadow_effects(self):
        """Agrega efectos de sombra"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 10)
        shadow.setColor(Qt.black)
        self.main_container.setGraphicsEffect(shadow)

    def apply_styles(self):
        """Aplica estilos CSS futuristas"""
        style = """
        QWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000000,
                        stop:0.5 #1A1A2E,
                        stop:1 #000000);
            color: #FFFFFF;
            font-family: 'Segoe UI', Arial, sans-serif;
        }

        #mainContainer {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0F172A,
                        stop:0.5 #1E293B,
                        stop:1 #0F172A);
            border: 2px solid #3B82F6;
            border-radius: 20px;
        }

        #logoLabel {
            font-size: 36px;
            margin: 0px;
            padding: 5px;
        }

        #titleLabel {
            font-size: 22px;
            font-weight: bold;
            color: #3B82F6;
            margin: 0px;
            padding: 2px;
            letter-spacing: 1.5px;
        }

        #subtitleLabel {
            font-size: 15px;
            color: #94A3B8;
            margin: 0px;
            padding: 2px;
            font-weight: 500;
        }

        #formContainer {
            background: transparent;
        }

        #inputContainer {
            background: transparent;
            margin: 0px;
            padding: 0px;
        }

        #passwordContainer {
            background: transparent;
            border-radius: 10px;
        }

        #inputLabel {
            font-size: 13px;
            font-weight: bold;
            color: #8B94A8;
            letter-spacing: 0.8px;
            margin: 0px;
            padding: 0px 2px 5px 2px;
        }

        #inputField, #passwordField {
            background: rgba(30, 41, 59, 0.9);
            border: 2px solid rgba(71, 85, 105, 0.6);
            border-radius: 10px;
            padding: 12px 16px;
            font-size: 15px;
            color: #FFFFFF;
            font-weight: 500;
        }

        #inputField:focus, #passwordField:focus {
            border: 2px solid #3B82F6;
            background: rgba(30, 41, 59, 1.0);
            outline: none;
        }

        #inputField::placeholder, #passwordField::placeholder {
            color: #64748B;
            font-weight: normal;
        }

        #togglePasswordBtn {
            background: rgba(59, 130, 246, 0.25);
            border: 2px solid rgba(59, 130, 246, 0.4);
            border-radius: 10px;
            color: #3B82F6;
            font-size: 18px;
            font-weight: bold;
            margin-left: 2px;
        }

        #togglePasswordBtn:hover {
            background: rgba(59, 130, 246, 0.35);
            border: 2px solid rgba(59, 130, 246, 0.6);
            color: #FFFFFF;
        }

        #togglePasswordBtn:pressed {
            background: rgba(59, 130, 246, 0.5);
            border: 2px solid rgba(59, 130, 246, 0.7);
        }

        #loginButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #3B82F6,
                        stop:0.5 #1D4ED8,
                        stop:1 #3B82F6);
            border: none;
            border-radius: 12px;
            color: #FFFFFF;
            font-size: 16px;
            font-weight: bold;
            letter-spacing: 1.2px;
            margin: 0px;
            padding: 0px;
        }

        #loginButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2563EB,
                        stop:0.5 #1E40AF,
                        stop:1 #2563EB);
        }

        #loginButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1D4ED8,
                        stop:0.5 #1E3A8A,
                        stop:1 #1D4ED8);
        }

        #loginButton:disabled {
            background: rgba(71, 85, 105, 0.6);
            color: rgba(148, 163, 184, 0.8);
        }

        #footerLabel {
            font-size: 12px;
            color: #64748B;
            margin: 0px;
            padding: 5px;
            font-weight: 400;
        }

        #closeButton {
            background: rgba(239, 68, 68, 0.2);
            border: 2px solid rgba(239, 68, 68, 0.3);
            border-radius: 15px;
            color: #EF4444;
            font-size: 16px;
            font-weight: bold;
        }

        #closeButton:hover {
            background: rgba(239, 68, 68, 0.3);
            border: 2px solid rgba(239, 68, 68, 0.5);
            color: #FFFFFF;
        }

        #closeButton:pressed {
            background: rgba(239, 68, 68, 0.4);
            border: 2px solid rgba(239, 68, 68, 0.6);
        }
        """
        self.setStyleSheet(style)

    def mousePressEvent(self, event):
        """Permite arrastrar la ventana"""
        if event.button() == Qt.LeftButton:
            # Solo permitir arrastre si no se hace clic en el botón de cerrar
            if not self.close_btn.geometry().contains(event.pos()):
                self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """Maneja el arrastre de la ventana"""
        if event.buttons() == Qt.LeftButton and hasattr(self, "dragPosition"):
            self.move(event.globalPos() - self.dragPosition)
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_window = FuturisticLoginWindow()
    login_window.show()
    sys.exit(app.exec_())
