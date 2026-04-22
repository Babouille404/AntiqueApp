from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QMessageBox
)
from PySide6.QtCore import Signal, Qt

from gui.dashboard_page import DashboardPage
from gui.products_page import ProductsPage
from gui.orders_page import OrdersPage
from gui.users_page import UsersPage


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application après connexion."""

    logout_requested = Signal()

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("L'Antique — Administration")
        self.setMinimumSize(1100, 700)
        self._init_ui()

    def _init_ui(self):
        """Initialise l'interface principale avec barre latérale et pages."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Barre latérale ---
        sidebar = QWidget()
        sidebar.setObjectName("mainSidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Titre dans la barre latérale
        sidebar_title = QLabel("L'Antique")
        sidebar_title.setAlignment(Qt.AlignCenter)
        sidebar_title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #FFF8E7; padding: 25px 10px;"
        )
        sidebar_layout.addWidget(sidebar_title)

        # Boutons de navigation
        self.nav_buttons = []
        nav_items = [
            ("\U0001F3E0  Tableau de bord", 0),
            ("\U0001F4E6  Produits", 1),
            ("\U0001F6D2  Commandes", 2),
            ("\U0001F465  Clients", 3),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setObjectName("sidebarButton")
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Bouton déconnexion
        logout_btn = QPushButton("\U0001F6AA  Déconnexion")
        logout_btn.setObjectName("sidebarButton")
        logout_btn.clicked.connect(self._on_logout)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(sidebar)

        # --- Zone de contenu ---
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Barre supérieure avec info utilisateur
        top_bar = QWidget()
        top_bar.setFixedHeight(50)
        top_bar.setStyleSheet("background-color: #FFFFFF; border-bottom: 1px solid #D7CCC8;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 0, 20, 0)

        top_bar_layout.addStretch()
        self.user_label = QLabel("Connecté : —")
        self.user_label.setStyleSheet("color: #3E2723; font-size: 13px;")
        top_bar_layout.addWidget(self.user_label)

        content_layout.addWidget(top_bar)

        # Pages empilées
        self.stacked_widget = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.products_page = ProductsPage()
        self.orders_page = OrdersPage()
        self.users_page = UsersPage()

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.products_page)
        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.addWidget(self.users_page)

        content_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_widget)

        # Sélection par défaut : tableau de bord
        self._switch_page(0)

    def _switch_page(self, index):
        """Change la page affichée et met à jour les boutons."""
        self.stacked_widget.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # Rafraîchir la page affichée
        current_page = self.stacked_widget.currentWidget()
        if hasattr(current_page, "refresh"):
            current_page.refresh()

    def _on_logout(self):
        """Demande confirmation puis déconnecte."""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.auth_service.logout()
            self.logout_requested.emit()

    def set_user(self, user):
        """Met à jour l'affichage avec les informations de l'utilisateur connecté."""
        self.user_label.setText(f"Connecté : {user['first_name']} {user['last_name']}")
