from database.connection import get_connection
from mysql.connector import IntegrityError


class ProductModel:
    """Accès à la table products."""

    def get_all(self):
        """Retourne tous les produits, triés par date de création décroissante."""
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products ORDER BY created_at DESC")
        products = cursor.fetchall()
        cursor.close()
        connection.close()
        return products

    def get_by_id(self, product_id):
        """Retourne un produit par son ID."""
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()
        connection.close()
        return product

    def create(self, name, description, price, stock, image, category):
        """Crée un nouveau produit."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO products (name, description, price, stock, image, category) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (name, description, price, stock, image, category)
        )
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return new_id

    def update(self, product_id, name, description, price, stock, image, category):
        """Met à jour un produit existant."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE products SET name = %s, description = %s, price = %s, "
            "stock = %s, image = %s, category = %s WHERE id = %s",
            (name, description, price, stock, image, category, product_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

    def delete(self, product_id):
        """Supprime un produit. Lève une erreur si le produit est référencé dans des commandes."""
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            connection.commit()
        except IntegrityError:
            raise ValueError(
                "Impossible de supprimer ce produit : il est référencé dans des commandes."
            )
        finally:
            cursor.close()
            connection.close()

    def count(self):
        """Retourne le nombre total de produits."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return count
