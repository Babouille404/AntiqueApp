from models.order_model import OrderModel


class OrderService:
    """Service de gestion des commandes."""

    # Libellés d'affichage des statuts
    STATUS_LABELS = {
        "en_attente": "En attente",
        "validee": "Validée",
        "expediee": "Expédiée",
        "annulee": "Annulée",
    }

    def __init__(self):
        self.order_model = OrderModel()

    def list_orders(self):
        """Retourne la liste de toutes les commandes."""
        return self.order_model.get_all()

    def get_order_details(self, order_id):
        """Retourne les détails d'une commande (infos + articles)."""
        order = self.order_model.get_by_id(order_id)
        items = self.order_model.get_items(order_id)
        return {"order": order, "items": items}

    def change_status(self, order_id, new_status):
        """Change le statut d'une commande."""
        if new_status not in self.STATUS_LABELS:
            raise ValueError(f"Statut invalide : {new_status}")
        self.order_model.update_status(order_id, new_status)
