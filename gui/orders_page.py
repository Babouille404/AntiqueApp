from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QComboBox, QFrame, QHeaderView, QSplitter
)
from PySide6.QtCore import Qt

from services.order_service import OrderService


class OrdersPage(QWidget):
    """Page de gestion des commandes."""

    def __init__(self):
        super().__init__()
        self.order_service = OrderService()
        self._init_ui()

    def _init_ui(self):
        """Initialise l'interface de gestion des commandes."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        # En-tête
        header_layout = QHBoxLayout()
        title = QLabel("Gestion des commandes")
        title.setProperty("class", "title")
        header_layout.addWidget(title)
        header_layout.addStretch()

        btn_refresh = QPushButton("Actualiser")
        btn_refresh.clicked.connect(self.refresh)
        header_layout.addWidget(btn_refresh)
        layout.addLayout(header_layout)

        # Splitter : tableau à gauche, détails à droite
        splitter = QSplitter(Qt.Horizontal)

        # --- Tableau des commandes ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Client", "Email", "Date", "Statut", "Total"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.currentCellChanged.connect(self._on_order_selected)
        splitter.addWidget(self.table)

        # --- Panneau de détails ---
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(15, 10, 15, 10)

        detail_title = QLabel("Détails de la commande")
        detail_title.setProperty("class", "title")
        detail_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        detail_layout.addWidget(detail_title)

        # Infos client
        self.detail_client_label = QLabel("Client : —")
        detail_layout.addWidget(self.detail_client_label)

        self.detail_email_label = QLabel("Email : —")
        detail_layout.addWidget(self.detail_email_label)

        self.detail_date_label = QLabel("Date : —")
        detail_layout.addWidget(self.detail_date_label)

        self.detail_total_label = QLabel("Total : —")
        detail_layout.addWidget(self.detail_total_label)

        # Tableau des articles
        articles_label = QLabel("Articles :")
        articles_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        detail_layout.addWidget(articles_label)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Produit", "Quantité", "Prix unitaire", "Sous-total"])
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.items_table.setAlternatingRowColors(True)
        detail_layout.addWidget(self.items_table)

        # Changement de statut
        status_layout = QHBoxLayout()
        status_label = QLabel("Statut :")
        status_layout.addWidget(status_label)

        self.status_combo = QComboBox()
        for key, label in OrderService.STATUS_LABELS.items():
            self.status_combo.addItem(label, key)
        status_layout.addWidget(self.status_combo)

        btn_update_status = QPushButton("Mettre à jour")
        btn_update_status.clicked.connect(self._on_update_status)
        status_layout.addWidget(btn_update_status)

        detail_layout.addLayout(status_layout)

        splitter.addWidget(detail_widget)
        splitter.setSizes([550, 450])

        layout.addWidget(splitter)

    def refresh(self):
        """Recharge la liste des commandes."""
        try:
            orders = self.order_service.list_orders()
            self.table.setRowCount(len(orders))
            for row, order in enumerate(orders):
                self.table.setItem(row, 0, QTableWidgetItem(str(order["id"])))
                client_name = f"{order['first_name']} {order['last_name']}"
                self.table.setItem(row, 1, QTableWidgetItem(client_name))
                self.table.setItem(row, 2, QTableWidgetItem(order["email"]))
                date_str = str(order["created_at"])
                self.table.setItem(row, 3, QTableWidgetItem(date_str))
                status_label = OrderService.STATUS_LABELS.get(order["status"], order["status"])
                self.table.setItem(row, 4, QTableWidgetItem(status_label))
                self.table.setItem(row, 5, QTableWidgetItem(f"{float(order['total']):.2f} €"))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les commandes :\n{e}")

    def _on_order_selected(self, current_row):
        """Affiche les détails de la commande sélectionnée."""
        if current_row < 0:
            return

        order_id_item = self.table.item(current_row, 0)
        if not order_id_item:
            return

        order_id = int(order_id_item.text())
        try:
            details = self.order_service.get_order_details(order_id)
            order = details["order"]
            items = details["items"]

            # Mise à jour des infos
            self.detail_client_label.setText(
                f"Client : {order['first_name']} {order['last_name']}"
            )
            self.detail_email_label.setText(f"Email : {order['email']}")
            self.detail_date_label.setText(f"Date : {order['created_at']}")
            self.detail_total_label.setText(f"Total : {float(order['total']):.2f} €")

            # Mise à jour du combo de statut
            index = self.status_combo.findData(order["status"])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)

            # Mise à jour du tableau des articles
            self.items_table.setRowCount(len(items))
            for row, item in enumerate(items):
                self.items_table.setItem(row, 0, QTableWidgetItem(item["product_name"]))
                self.items_table.setItem(row, 1, QTableWidgetItem(str(item["quantity"])))
                self.items_table.setItem(row, 2, QTableWidgetItem(f"{float(item['unit_price']):.2f} €"))
                subtotal = item["quantity"] * float(item["unit_price"])
                self.items_table.setItem(row, 3, QTableWidgetItem(f"{subtotal:.2f} €"))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les détails :\n{e}")

    def _on_update_status(self):
        """Met à jour le statut de la commande sélectionnée."""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner une commande.")
            return

        order_id = int(self.table.item(selected, 0).text())
        new_status = self.status_combo.currentData()

        try:
            self.order_service.change_status(order_id, new_status)
            self.refresh()
            QMessageBox.information(self, "Succès", "Statut mis à jour avec succès.")
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))
