from models.product_model import ProductModel
from models.order_model import OrderModel
from models.user_model import UserModel


class StatsService:
    """Service de statistiques pour le tableau de bord."""

    def __init__(self):
        self.product_model = ProductModel()
        self.order_model = OrderModel()
        self.user_model = UserModel()

    def get_dashboard_stats(self):
        """Retourne les statistiques du tableau de bord."""
        return {
            "nb_products": self.product_model.count(),
            "nb_orders_in_progress": self.order_model.count_in_progress(),
            "total_revenue": self.order_model.total_revenue(),
            "nb_clients": self.user_model.count_clients(),
        }
