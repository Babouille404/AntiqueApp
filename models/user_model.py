from database.connection import get_connection


class UserModel:
    """Accès à la table users."""

    def get_by_email(self, email):
        """Retourne un utilisateur par son email."""
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    def get_by_id(self, user_id):
        """Retourne un utilisateur par son ID."""
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user

    def get_all_clients(self):
        """Retourne tous les clients (role = 'client'), triés par date d'inscription décroissante."""
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, email, first_name, last_name, created_at "
            "FROM users WHERE role = 'client' ORDER BY created_at DESC"
        )
        clients = cursor.fetchall()
        cursor.close()
        connection.close()
        return clients

    def create(self, email, password_hash, first_name, last_name, role="client"):
        """Crée un nouvel utilisateur."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (email, password, first_name, last_name, role) "
            "VALUES (%s, %s, %s, %s, %s)",
            (email, password_hash, first_name, last_name, role)
        )
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return new_id

    def update(self, user_id, email, first_name, last_name):
        """Met à jour un utilisateur (sans modifier le mot de passe)."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET email = %s, first_name = %s, last_name = %s WHERE id = %s",
            (email, first_name, last_name, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

    def delete(self, user_id):
        """Supprime un utilisateur par son ID."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        cursor.close()
        connection.close()

    def count_clients(self):
        """Retourne le nombre de clients inscrits."""
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'client'")
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return count
