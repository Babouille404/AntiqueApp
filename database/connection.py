import mysql.connector
from mysql.connector import Error


def get_connection():
    """Retourne une connexion à la base de données MySQL."""
    try:
        from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4"
        )
        return connection
    except Error as e:
        raise ConnectionError(f"Erreur de connexion à la base de données : {e}")
