import re

from models.user_model import UserModel
from utils.security import hash_password


class UserService:
    """Service de gestion des clients."""

    def __init__(self):
        self.user_model = UserModel()

    def list_clients(self):
        """Retourne la liste de tous les clients."""
        return self.user_model.get_all_clients()

    def create_client(self, email, password, first_name, last_name):
        """Crée un nouveau compte client avec validations."""
        # Validation du prénom et du nom
        if not first_name or not first_name.strip():
            raise ValueError("Le prénom est obligatoire.")
        if not last_name or not last_name.strip():
            raise ValueError("Le nom est obligatoire.")

        # Validation de l'email
        if not email or not email.strip():
            raise ValueError("L'email est obligatoire.")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValueError("L'adresse email n'est pas valide.")

        # Validation du mot de passe
        if not password or len(password) < 6:
            raise ValueError("Le mot de passe doit contenir au moins 6 caractères.")

        # Hachage du mot de passe et création
        password_hash = hash_password(password)
        return self.user_model.create(email, password_hash, first_name.strip(), last_name.strip(), role="client")

    def update_client(self, user_id, email, first_name, last_name):
        """Met à jour un compte client (sans modifier le mot de passe)."""
        if not first_name or not first_name.strip():
            raise ValueError("Le prénom est obligatoire.")
        if not last_name or not last_name.strip():
            raise ValueError("Le nom est obligatoire.")
        if not email or not email.strip():
            raise ValueError("L'email est obligatoire.")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValueError("L'adresse email n'est pas valide.")

        self.user_model.update(user_id, email.strip(), first_name.strip(), last_name.strip())

    def delete_client(self, user_id):
        """Supprime un compte client."""
        self.user_model.delete(user_id)
