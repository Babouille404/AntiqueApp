import bcrypt


def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt (format $2b$)."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie un mot de passe. Gère la compatibilité $2y$ (PHP) ↔ $2b$ (Python)."""
    # Compatibilité avec les hashs PHP ($2y$) qui fonctionnent comme $2b$
    if password_hash.startswith("$2y$"):
        password_hash = "$2b$" + password_hash[4:]
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False
