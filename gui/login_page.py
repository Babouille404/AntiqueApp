from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Signal, Qt


class LoginPage(QWidget):
    """Écran de connexion pour les administrateurs."""

    login_success = Signal(dict)

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("L'Antique — Connexion")
        self.setFixedSize(400, 500)
        self._init_ui()

    def _init_ui(self):
        """Initialise l'interface de connexion."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Espacement en haut
        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Titre
        title = QLabel("L'Antique")
        title.setProperty("class", "title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Sous-titre
        subtitle = QLabel("Espace Administrateur")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #6D4C41; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Champ email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedWidth(280)
        layout.addWidget(self.email_input, alignment=Qt.AlignCenter)

        # Champ mot de passe
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(280)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)

        # Label d'erreur (masqué par défaut)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #C62828; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label, alignment=Qt.AlignCenter)

        # Bouton de connexion
        self.login_button = QPushButton("Se connecter")
        self.login_button.setFixedWidth(280)
        self.login_button.clicked.connect(self._on_login)
        layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        # Espacement en bas
        layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(layout)

        # Connexion sur Entrée
        self.password_input.returnPressed.connect(self._on_login)
        self.email_input.returnPressed.connect(self._on_login)

    def _on_login(self):
        """Tente la connexion avec les identifiants saisis."""
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            self.error_label.setText("Veuillez remplir tous les champs.")
            self.error_label.show()
            return

        try:
            user = self.auth_service.login(email, password)
            self.error_label.hide()
            self.login_success.emit(user)
        except ValueError as e:
            self.error_label.setText(str(e))
            self.error_label.show()

    def show(self):
        """Réinitialise les champs à l'affichage."""
        self.email_input.clear()
        self.password_input.clear()
        self.error_label.hide()
        super().show()
