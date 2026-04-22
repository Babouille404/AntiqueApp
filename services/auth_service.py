from models.user_model import UserModel
from utils.security import verify_password


class AuthService:
    """Service d'authentification des administrateurs."""

    def __init__(self):
        self.user_model = UserModel()
        self.current_user = None

    def login(self, email, password):
        """Authentifie un administrateur par email et mot de passe."""
        # Recherche de l'utilisateur par email
        user = self.user_model.get_by_email(email)
        if not user:
            raise ValueError("Identifiants incorrects.")

        # Vérification du mot de passe
        if not verify_password(password, user["password"]):
            raise ValueError("Identifiants incorrects.")

        # Vérification du rôle (seuls les employés/administrateurs sont autorisés)
        if user["role"] != "admin":
            raise ValueError("Accès réservé aux administrateurs.")

        # Connexion réussie : on stocke l'utilisateur sans le mot de passe
        user_data = {k: v for k, v in user.items() if k != "password"}
        self.current_user = user_data
        return user_data

    def logout(self):
        """Déconnecte l'utilisateur courant."""
        self.current_user = None
