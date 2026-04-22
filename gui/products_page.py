from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QDoubleSpinBox, QSpinBox, QDialogButtonBox, QHeaderView
)
from PySide6.QtCore import Qt

from services.product_service import ProductService


class ProductDialog(QDialog):
    """Dialogue d'ajout ou de modification d'un produit."""

    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Modifier le produit" if product else "Ajouter un produit")
        self.setMinimumWidth(400)
        self._init_ui()

    def _init_ui(self):
        """Initialise les champs du formulaire."""
        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        layout.addRow("Nom :", self.name_input)

        self.category_input = QLineEdit()
        layout.addRow("Catégorie :", self.category_input)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        layout.addRow("Description :", self.description_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 99999.99)
        self.price_input.setDecimals(2)
        self.price_input.setSuffix(" €")
        layout.addRow("Prix :", self.price_input)

        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 99999)
        layout.addRow("Stock :", self.stock_input)

        self.image_input = QLineEdit()
        self.image_input.setPlaceholderText("URL ou chemin de l'image")
        layout.addRow("Image :", self.image_input)

        # Pré-remplissage en mode modification
        if self.product:
            self.name_input.setText(self.product.get("name", ""))
            self.category_input.setText(self.product.get("category", "") or "")
            self.description_input.setPlainText(self.product.get("description", "") or "")
            self.price_input.setValue(float(self.product.get("price", 0)))
            self.stock_input.setValue(int(self.product.get("stock", 0)))
            self.image_input.setText(self.product.get("image", "") or "")

        # Boutons OK / Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        """Retourne les données saisies."""
        return {
            "name": self.name_input.text().strip(),
            "category": self.category_input.text().strip() or None,
            "description": self.description_input.toPlainText().strip() or None,
            "price": self.price_input.value(),
            "stock": self.stock_input.value(),
            "image": self.image_input.text().strip() or None,
        }


class ProductsPage(QWidget):
    """Page de gestion des produits."""

    def __init__(self):
        super().__init__()
        self.product_service = ProductService()
        self._init_ui()

    def _init_ui(self):
        """Initialise l'interface de gestion des produits."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        # En-tête
        header_layout = QHBoxLayout()
        title = QLabel("Gestion des produits")
        title.setProperty("class", "title")
        header_layout.addWidget(title)
        header_layout.addStretch()

        btn_add = QPushButton("Ajouter")
        btn_add.clicked.connect(self._on_add)
        header_layout.addWidget(btn_add)

        btn_edit = QPushButton("Modifier")
        btn_edit.clicked.connect(self._on_edit)
        header_layout.addWidget(btn_edit)

        btn_delete = QPushButton("Supprimer")
        btn_delete.clicked.connect(self._on_delete)
        header_layout.addWidget(btn_delete)

        btn_refresh = QPushButton("Actualiser")
        btn_refresh.clicked.connect(self.refresh)
        header_layout.addWidget(btn_refresh)

        layout.addLayout(header_layout)

        # Tableau des produits
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nom", "Catégorie", "Prix", "Stock"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        """Recharge la liste des produits."""
        try:
            products = self.product_service.list_products()
            self.table.setRowCount(len(products))
            for row, product in enumerate(products):
                self.table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(product["name"]))
                self.table.setItem(row, 2, QTableWidgetItem(product.get("category") or ""))
                self.table.setItem(row, 3, QTableWidgetItem(f"{float(product['price']):.2f} €"))
                self.table.setItem(row, 4, QTableWidgetItem(str(product["stock"])))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les produits :\n{e}")

    def _get_selected_product_id(self):
        """Retourne l'ID du produit sélectionné ou None."""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un produit.")
            return None
        return int(self.table.item(selected, 0).text())

    def _on_add(self):
        """Ouvre le dialogue d'ajout d'un produit."""
        dialog = ProductDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.product_service.create_product(**data)
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def _on_edit(self):
        """Ouvre le dialogue de modification du produit sélectionné."""
        product_id = self._get_selected_product_id()
        if product_id is None:
            return
        product = self.product_service.get_product(product_id)
        if not product:
            QMessageBox.warning(self, "Erreur", "Produit introuvable.")
            return

        dialog = ProductDialog(self, product)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.product_service.update_product(product_id, **data)
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def _on_delete(self):
        """Supprime le produit sélectionné après confirmation."""
        product_id = self._get_selected_product_id()
        if product_id is None:
            return

        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment supprimer ce produit ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.product_service.delete_product(product_id)
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", str(e))
