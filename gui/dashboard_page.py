from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt

from services.stats_service import StatsService


class DashboardPage(QWidget):
    """Page du tableau de bord avec les statistiques."""

    def __init__(self):
        super().__init__()
        self.stats_service = StatsService()
        self._init_ui()
        self.refresh()

    def _init_ui(self):
        """Initialise l'interface du tableau de bord."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        # En-tête
        header_layout = QHBoxLayout()
        title = QLabel("Tableau de bord")
        title.setProperty("class", "title")
        header_layout.addWidget(title)
        header_layout.addStretch()

        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)
        layout.addLayout(header_layout)

        # Cartes de statistiques
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        self.card_products = self._create_card("Nombre de produits", "0")
        self.card_orders = self._create_card("Commandes en cours", "0")
        self.card_revenue = self._create_card("Chiffre d'affaires", "0.00 €")
        self.card_clients = self._create_card("Clients inscrits", "0")

        cards_layout.addWidget(self.card_products["frame"])
        cards_layout.addWidget(self.card_orders["frame"])
        cards_layout.addWidget(self.card_revenue["frame"])
        cards_layout.addWidget(self.card_clients["frame"])

        layout.addLayout(cards_layout)
        layout.addStretch()

    def _create_card(self, title_text, value_text):
        """Crée une carte de statistique."""
        frame = QFrame()
        frame.setObjectName("statCard")
        frame_layout = QVBoxLayout(frame)
        frame_layout.setAlignment(Qt.AlignCenter)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 13px; color: #6D4C41;")
        frame_layout.addWidget(title)

        value = QLabel(value_text)
        value.setProperty("class", "stat-value")
        value.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(value)

        return {"frame": frame, "value": value}

    def refresh(self):
        """Actualise les statistiques depuis la base de données."""
        try:
            stats = self.stats_service.get_dashboard_stats()
            self.card_products["value"].setText(str(stats["nb_products"]))
            self.card_orders["value"].setText(str(stats["nb_orders_in_progress"]))
            self.card_revenue["value"].setText(f"{stats['total_revenue']:.2f} €")
            self.card_clients["value"].setText(str(stats["nb_clients"]))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les statistiques :\n{e}")
