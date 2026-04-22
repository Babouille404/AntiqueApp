from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QHeaderView
)
from PySide6.QtCore import Qt

from services.user_service import UserService


class UserDialog(QDialog):
    """Dialogue d'ajout ou de modification d'un client."""

    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Modifier le client" if user else "Ajouter un client")
        self.setMinimumWidth(380)
        self._init_ui()

    def _init_ui(self):
        """Initialise les champs du formulaire."""
        layout = QFormLayout(self)

        self.first_name_input = QLineEdit()
        layout.addRow("Prénom :", self.first_name_input)

        self.last_name_input = QLineEdit()
        layout.addRow("Nom :", self.last_name_input)

        self.email_input = QLineEdit()
        layout.addRow("Email :", self.email_input)

        # Mot de passe visible uniquement en création
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if self.user:
            self.password_input.hide()
            self.password_label = QLabel("")
            self.password_label.hide()
        else:
            layout.addRow("Mot de passe :", self.password_input)

        # Pré-remplissage en mode modification
        if self.user:
            self.first_name_input.setText(self.user.get("first_name", ""))
            self.last_name_input.setText(self.user.get("last_name", ""))
            self.email_input.setText(self.user.get("email", ""))

        # Boutons OK / Annuler
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        """Retourne les données saisies."""
        data = {
            "first_name": self.first_name_input.text().strip(),
            "last_name": self.last_name_input.text().strip(),
            "email": self.email_input.text().strip(),
        }
        if not self.user:
            data["password"] = self.password_input.text()
        return data


class UsersPage(QWidget):
    """Page de gestion des clients."""

    def __init__(self):
        super().__init__()
        self.user_service = UserService()
        self._init_ui()

    def _init_ui(self):
        """Initialise l'interface de gestion des clients."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)

        # En-tête
        header_layout = QHBoxLayout()
        title = QLabel("Gestion des clients")
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

        # Tableau des clients
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Prénom", "Nom", "Email", "Inscrit le"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        """Recharge la liste des clients."""
        try:
            clients = self.user_service.list_clients()
            self.table.setRowCount(len(clients))
            for row, client in enumerate(clients):
                self.table.setItem(row, 0, QTableWidgetItem(str(client["id"])))
                self.table.setItem(row, 1, QTableWidgetItem(client["first_name"]))
                self.table.setItem(row, 2, QTableWidgetItem(client["last_name"]))
                self.table.setItem(row, 3, QTableWidgetItem(client["email"]))
                self.table.setItem(row, 4, QTableWidgetItem(str(client["created_at"])))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger les clients :\n{e}")

    def _get_selected_user_id(self):
        """Retourne l'ID du client sélectionné ou None."""
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un client.")
            return None
        return int(self.table.item(selected, 0).text())

    def _on_add(self):
        """Ouvre le dialogue d'ajout d'un client."""
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.user_service.create_client(
                    data["email"], data["password"], data["first_name"], data["last_name"]
                )
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def _on_edit(self):
        """Ouvre le dialogue de modification du client sélectionné."""
        user_id = self._get_selected_user_id()
        if user_id is None:
            return

        # Récupérer les données actuelles depuis le tableau
        row = self.table.currentRow()
        user_data = {
            "first_name": self.table.item(row, 1).text(),
            "last_name": self.table.item(row, 2).text(),
            "email": self.table.item(row, 3).text(),
        }

        dialog = UserDialog(self, user_data)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.user_service.update_client(user_id, data["email"], data["first_name"], data["last_name"])
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def _on_delete(self):
        """Supprime le client sélectionné après confirmation."""
        user_id = self._get_selected_user_id()
        if user_id is None:
            return

        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment supprimer ce client ?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.user_service.delete_client(user_id)
                self.refresh()
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", str(e))
