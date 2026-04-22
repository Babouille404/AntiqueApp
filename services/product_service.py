from models.product_model import ProductModel


class ProductService:
    """Service de gestion des produits."""

    def __init__(self):
        self.product_model = ProductModel()

    def list_products(self):
        """Retourne la liste de tous les produits."""
        return self.product_model.get_all()

    def get_product(self, product_id):
        """Retourne un produit par son ID."""
        return self.product_model.get_by_id(product_id)

    def create_product(self, name, description, price, stock, image, category):
        """Crée un nouveau produit avec validations."""
        if not name or not name.strip():
            raise ValueError("Le nom du produit est obligatoire.")
        if price is None or price <= 0:
            raise ValueError("Le prix doit être supérieur à 0.")
        if stock is None or stock < 0:
            raise ValueError("Le stock ne peut pas être négatif.")

        return self.product_model.create(
            name.strip(), description, price, stock, image, category
        )

    def update_product(self, product_id, name, description, price, stock, image, category):
        """Met à jour un produit existant avec validations."""
        if not name or not name.strip():
            raise ValueError("Le nom du produit est obligatoire.")
        if price is None or price <= 0:
            raise ValueError("Le prix doit être supérieur à 0.")
        if stock is None or stock < 0:
            raise ValueError("Le stock ne peut pas être négatif.")

        self.product_model.update(
            product_id, name.strip(), description, price, stock, image, category
        )

    def delete_product(self, product_id):
        """Supprime un produit."""
        try:
            self.product_model.delete(product_id)
        except ValueError:
            raise ValueError("Impossible de supprimer ce produit : il est référencé dans des commandes.")
