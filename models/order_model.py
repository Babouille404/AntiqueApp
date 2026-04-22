from database.connection import get_connection


class OrderModel:
    """Accès aux tables orders et order_items."""

    # Statuts valides pour les commandes
    VALID_STATUSES = ("en_attente", "validee", "expediee", "annulee")

    def get_all(self):
        """Retourne toutes les commandes avec les infos du client."""
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT o.id, o.user_id, o.total, o.status, o.created_at, "
            "u.first_name, u.last_name, u.email "
            "FROM orders o "
            "JOIN users u ON o.user_id = u.id "
            "ORDER BY o.created_at DESC"
        )
        orders = cursor.fetchall()
        cursor.close()
        connection.close()
        return orders

    def get_by_id(self, order_id):
        """Retourne une commande avec les infos du client."""
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT o.id, o.user_id, o.total, o.status, o.created_at, "
            "u.first_name, u.last_name, u.email "
            "FROM orders o "
            "JOIN users u ON o.user_id = u.id "
            "WHERE o.id = %s",
            (order_id,)
        )
        order = cursor.fetchone()
        cursor.close()
        connection.close()
        return order

    def get_items(self, order_id):
        """Retourne les articles d'une commande avec le nom du produit."""
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT oi.id, oi.order_id, oi.product_id, oi.quantity, oi.unit_price, "
            "p.name AS product_name "
            "FROM order_items oi "
            "JOIN products p ON oi.product_id = p.id "
            "WHERE oi.order_id = %s",
            (order_id,)
        )
        items = cursor.fetchall()
        cursor.close()
        connection.close()
        return items

    def update_status(self, order_id, status):
        """Met à jour le statut d'une commande."""
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Statut invalide : {status}")
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE orders SET status = %s WHERE id = %s",
            (status, order_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

    def count_in_progress(self):
        """Retourne le nombre de commandes en cours (en attente ou validées)."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM orders WHERE status IN ('en_attente', 'validee')"
        )
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return count

    def total_revenue(self):
        """Retourne le chiffre d'affaires (commandes validées et expédiées)."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT SUM(total) FROM orders WHERE status IN ('validee', 'expediee')"
        )
        result = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return float(result) if result else 0.0
