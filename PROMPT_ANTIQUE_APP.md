# Prompt Claude Code — Génération de L'Antique App (Client Lourd)

Tu vas générer l'intégralité du projet **L'Antique App**, une application de bureau Python/PySide6 pour l'administration d'une boutique de café. Ce projet est réalisé dans le cadre du BTS SIO SLAM (épreuve E6). Il doit être **simple, lisible et fidèle au cahier des charges ci-dessous**, car il sera présenté à un jury et modifié en direct pendant l'oral.

---

## 1. Contexte

L'entreprise **L'Antique** (vente de café) dispose déjà d'un site web PHP (L'Antique Web, client léger) utilisé par ses clients et ses employés. Elle souhaite maintenant un **logiciel de bureau** réservé aux administrateurs pour piloter son activité : catalogue, commandes, comptes utilisateurs.

L'application partage la **même base MySQL** (`antique_db`) que le site web. La BDD existe déjà ; **ne pas créer de script SQL d'initialisation**.

> **Vocabulaire** : dans la BDD, le rôle des utilisateurs habilités s'appelle `employe` (héritage du site web qui parle d'employés de l'entreprise). Dans l'interface de cette application, on les désigne par le terme **"Administrateur"** (conforme au dossier E6). Le filtre SQL se fait donc sur `role = 'employe'`, mais tous les libellés visibles dans l'UI disent "Administrateur".

---

## 2. Stack technique imposée

- **Python 3.10+**
- **PySide6** (interface graphique)
- **mysql-connector-python** (accès BDD)
- **bcrypt** (compatible avec `password_hash()` de PHP qui produit des hashs `$2y$`)
- **QSS** pour le style
- Git / GitHub pour le versionning

**Aucune autre dépendance.** Pas de SQLAlchemy, pas d'ORM, pas de framework MVVM.

---

## 3. Architecture en couches (IMPORTANT)

Le projet suit une **architecture en 3 couches** strictes :

| Couche | Rôle | Dossier |
|--------|------|---------|
| **Modèles** | Accès BDD (SQL uniquement) | `models/` |
| **Services** | Logique métier, validations, orchestration | `services/` |
| **GUI** | Affichage et interactions PySide6 | `gui/` |

**Règle d'or** : la GUI n'appelle **jamais** directement un modèle. Elle passe toujours par un service. Les services appellent les modèles.

---

## 4. Structure du projet

```
AntiqueApp/
├── .gitignore
├── requirements.txt
├── README.md
├── main.py                     # Point d'entrée
├── config.py                   # Paramètres BDD (IGNORÉ par git)
├── config.example.py           # Modèle à copier
├── database/
│   ├── __init__.py
│   └── connection.py           # Connexion MySQL
├── models/
│   ├── __init__.py
│   ├── user_model.py
│   ├── product_model.py
│   └── order_model.py
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── user_service.py
│   ├── product_service.py
│   ├── order_service.py
│   └── stats_service.py
├── gui/
│   ├── __init__.py
│   ├── login_page.py           # Écran de connexion
│   ├── main_window.py          # Fenêtre principale (après login)
│   ├── dashboard_page.py
│   ├── products_page.py
│   ├── orders_page.py
│   └── users_page.py
├── utils/
│   ├── __init__.py
│   └── security.py             # hash_password / verify_password
└── resources/
    └── styles.qss              # Thème café
```

---

## 5. Base de données (existante, partagée avec le site web)

Nom de la BDD : **`antique_db`**. Elle contient 5 tables. Le client lourd utilise **4 d'entre elles** (la table `cart_items` est réservée au site web).

### Table `users`
| Colonne | Type |
|---------|------|
| id | INT AUTO_INCREMENT PK |
| email | VARCHAR(255) NOT NULL UNIQUE |
| password | VARCHAR(255) NOT NULL — hash bcrypt format `$2y$` |
| first_name | VARCHAR(100) NOT NULL |
| last_name | VARCHAR(100) NOT NULL |
| role | ENUM('client', 'employe') DEFAULT 'client' |
| created_at | DATETIME DEFAULT CURRENT_TIMESTAMP |

### Table `products`
| Colonne | Type |
|---------|------|
| id | INT AUTO_INCREMENT PK |
| name | VARCHAR(255) NOT NULL |
| description | TEXT |
| price | DECIMAL(10,2) NOT NULL |
| stock | INT NOT NULL DEFAULT 0 |
| image | VARCHAR(255) nullable |
| category | VARCHAR(100) nullable |
| created_at | DATETIME DEFAULT CURRENT_TIMESTAMP |

### Table `orders`
| Colonne | Type |
|---------|------|
| id | INT AUTO_INCREMENT PK |
| user_id | INT NOT NULL, FK → users(id) ON DELETE CASCADE |
| total | DECIMAL(10,2) NOT NULL |
| status | ENUM('en_attente', 'validee', 'expediee', 'annulee') DEFAULT 'en_attente' |
| created_at | DATETIME DEFAULT CURRENT_TIMESTAMP |

### Table `order_items`
| Colonne | Type |
|---------|------|
| id | INT AUTO_INCREMENT PK |
| order_id | INT NOT NULL, FK → orders(id) ON DELETE CASCADE |
| product_id | INT NOT NULL, FK → products(id) ON DELETE RESTRICT |
| quantity | INT NOT NULL |
| unit_price | DECIMAL(10,2) NOT NULL |

> Les noms de colonnes ci-dessus sont **exacts** — la BDD existe déjà, il ne faut rien renommer.

---

## 6. Fonctionnalités attendues (strictement celles du dossier E6)

1. **Authentification** par email + mot de passe. **Seuls les comptes `role = 'employe'` sont autorisés.** Un compte client qui tente de se connecter reçoit un message d'erreur clair : "Accès réservé aux administrateurs."
2. **Tableau de bord** avec 4 statistiques :
   - **Nombre de produits** : `COUNT(*)` sur `products`
   - **Commandes en cours** : `COUNT(*)` sur `orders` avec `status IN ('en_attente', 'validee')` (non expédiées, non annulées)
   - **Chiffre d'affaires** : `SUM(total)` sur `orders` avec `status IN ('validee', 'expediee')` (commandes honorées)
   - **Clients inscrits** : `COUNT(*)` sur `users` avec `role = 'client'`
3. **Gestion des produits** : CRUD complet + mise à jour des stocks + gestion du champ `category`.
4. **Gestion des commandes** : consultation, détail des articles (order_items), changement de statut parmi les 4 valeurs de l'ENUM, historique.
5. **Gestion des utilisateurs** : consultation, ajout, modification, suppression des comptes **clients** uniquement (`role = 'client'`). Les comptes administrateurs ne sont pas gérables via cette application (sécurité : évite qu'un admin en supprime un autre par erreur).

**Fonctionnalités à NE PAS implémenter** (évolutions futures mentionnées dans la conclusion du dossier) : export CSV, filtres de recherche avancés.

---

## 7. Détail des fichiers à générer

### 7.1 `config.example.py`
```python
# Copier ce fichier en config.py et renseigner les vraies valeurs.
# config.py est ignoré par git pour ne pas exposer les identifiants.

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "antique_db"
```

### 7.2 `.gitignore`
Doit inclure : `config.py`, `__pycache__/`, `*.pyc`, `.idea/`, `.vscode/`, `venv/`, `.env`, `*.log`.

### 7.3 `requirements.txt`
```
PySide6==6.7.0
mysql-connector-python==9.0.0
bcrypt==4.2.0
```

### 7.4 `database/connection.py`
- Fonction `get_connection()` qui retourne une connexion `mysql.connector` en lisant les paramètres de `config.py` (ajouter `charset='utf8mb4'`).
- Gérer `mysql.connector.Error` avec un message clair.
- Pas de singleton complexe : ouvrir/fermer la connexion dans chaque méthode de modèle. Simplicité avant tout.

### 7.5 `utils/security.py`

Deux fonctions :

```python
def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt (format $2b$)."""

def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie un mot de passe. Gère la compatibilité $2y$ (PHP) ↔ $2b$ (Python)."""
```

**IMPORTANT pour la compatibilité PHP** : les hashs générés par `password_hash()` de PHP commencent par `$2y$`, alors que `bcrypt` Python utilise `$2b$`. Les deux formats sont algorithmiquement identiques. Dans `verify_password`, remplacer le préfixe `$2y$` par `$2b$` avant d'appeler `bcrypt.checkpw` :

```python
import bcrypt

def verify_password(password: str, password_hash: str) -> bool:
    # Compatibilité avec les hashs PHP ($2y$) qui fonctionnent comme $2b$
    if password_hash.startswith("$2y$"):
        password_hash = "$2b$" + password_hash[4:]
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False
```

### 7.6 Modèles

Chaque modèle est une **classe** dont toutes les méthodes ouvrent une connexion, exécutent la requête **paramétrée** (`%s`), puis ferment. Retour : `dict` ou `list[dict]` via `cursor(dictionary=True)`.

**`models/user_model.py`** — classe `UserModel` :
- `get_by_email(email)` → retourne le user complet (pour le login)
- `get_by_id(user_id)`
- `get_all_clients()` → `SELECT id, email, first_name, last_name, created_at FROM users WHERE role = 'client' ORDER BY created_at DESC`
- `create(email, password_hash, first_name, last_name, role='client')`
- `update(user_id, email, first_name, last_name)`
- `delete(user_id)`
- `count_clients()` → `SELECT COUNT(*) FROM users WHERE role = 'client'`

**`models/product_model.py`** — classe `ProductModel` :
- `get_all()` → tri par `created_at DESC`
- `get_by_id(product_id)`
- `create(name, description, price, stock, image, category)`
- `update(product_id, name, description, price, stock, image, category)`
- `delete(product_id)` — gérer l'erreur `IntegrityError` si le produit est référencé par des `order_items` (ON DELETE RESTRICT) et remonter un message clair
- `count()` → `SELECT COUNT(*) FROM products`

**`models/order_model.py`** — classe `OrderModel` :
- `get_all()` → avec `JOIN users` pour récupérer `first_name`, `last_name`, `email` du client
- `get_by_id(order_id)` → infos commande + client
- `get_items(order_id)` → `JOIN products` pour récupérer `product_name` (alias de `products.name`)
- `update_status(order_id, status)` — vérifier côté modèle que `status IN ('en_attente', 'validee', 'expediee', 'annulee')`
- `count_in_progress()` → `status IN ('en_attente', 'validee')`
- `total_revenue()` → `SUM(total) WHERE status IN ('validee', 'expediee')`, retour `float` (0.0 si NULL)

### 7.7 Services

Chaque service encapsule le modèle et **ajoute les validations métier**. Ils lèvent des `ValueError` avec des messages clairs en français — ces messages seront affichés à l'utilisateur.

**`services/auth_service.py`** — classe `AuthService` :
- Attribut `current_user` (dict ou None)
- `login(email, password)` :
  1. Récupère le user par email. S'il n'existe pas → `ValueError("Identifiants incorrects.")`
  2. Vérifie le mot de passe via `verify_password`. Échec → même `ValueError("Identifiants incorrects.")`
  3. Vérifie `role == 'employe'`. Sinon → `ValueError("Accès réservé aux administrateurs.")`
  4. Stocke dans `current_user` et retourne le dict (sans le mot de passe).
- `logout()` : remet `current_user` à `None`.

**`services/user_service.py`** (gestion des clients uniquement) :
- `list_clients()`
- `create_client(email, password, first_name, last_name)` : valide email (regex simple), valide mot de passe non vide (min 6 caractères), valide prénom/nom non vides, hache le mot de passe, appelle le modèle avec `role='client'`.
- `update_client(user_id, email, first_name, last_name)` (ne modifie pas le mot de passe)
- `delete_client(user_id)`

**`services/product_service.py`** :
- `list_products()`, `get_product(id)`
- `create_product(name, description, price, stock, image, category)` : vérifie `price > 0`, `stock >= 0`, nom non vide.
- `update_product(...)` (mêmes validations)
- `delete_product(id)` : attrape l'erreur remontée du modèle et la reformule en `ValueError("Impossible de supprimer ce produit : il est référencé dans des commandes.")`

**`services/order_service.py`** :
- `list_orders()`, `get_order_details(id)` (retourne `{"order": ..., "items": [...]}`)
- `change_status(order_id, new_status)` : vérifie que `new_status` est dans `('en_attente', 'validee', 'expediee', 'annulee')`.
- Constante de classe `STATUS_LABELS` pour l'affichage :
  ```python
  STATUS_LABELS = {
      "en_attente": "En attente",
      "validee": "Validée",
      "expediee": "Expédiée",
      "annulee": "Annulée",
  }
  ```

**`services/stats_service.py`** :
- `get_dashboard_stats()` retourne :
```python
{
    "nb_products": int,
    "nb_orders_in_progress": int,
    "total_revenue": float,
    "nb_clients": int
}
```

### 7.8 GUI

Chaque page hérite de `QWidget` et expose un layout propre. Utiliser `QMessageBox` pour les erreurs et confirmations. Toujours capturer les `ValueError` des services pour les transformer en `QMessageBox.warning`.

**`gui/login_page.py`** — classe `LoginPage(QWidget)` :
- Layout centré : titre "L'Antique", sous-titre "Espace Administrateur"
- `QLineEdit` email + `QLineEdit` mot de passe (mode `Password`)
- `QPushButton` "Se connecter" (déclenche aussi sur `Entrée`)
- `QLabel` d'erreur (rouge, masqué par défaut)
- Signal `login_success = Signal(dict)` émis quand la connexion réussit
- Appelle `AuthService.login()` dans un try/except ; en cas de `ValueError`, affiche le message dans le label d'erreur

**`gui/main_window.py`** — classe `MainWindow(QMainWindow)` :
- Signal `logout_requested = Signal()`
- Barre latérale gauche (objectName `mainSidebar`) avec 5 boutons :
  - 🏠 Tableau de bord
  - 📦 Produits
  - 🛒 Commandes
  - 👥 Clients
  - 🚪 Déconnexion
- `QStackedWidget` central contenant les 4 pages
- En haut à droite : label "Connecté : {first_name} {last_name}"
- Méthode `set_user(user)` qui met à jour l'affichage
- Clic sur "Déconnexion" → `QMessageBox.question` de confirmation, puis appel `AuthService.logout()` et émission du signal

**`gui/dashboard_page.py`** :
- 4 "cartes" (`QFrame` stylisée, objectName `statCard`) affichant :
  - Nombre de produits
  - Commandes en cours
  - Chiffre d'affaires (formaté `{:.2f} €`)
  - Clients inscrits
- `QPushButton` "Actualiser" en haut qui recharge via `StatsService`
- Appeler `refresh()` à l'initialisation

**`gui/products_page.py`** :
- `QTableWidget` (non éditable, sélection ligne) : colonnes ID, Nom, Catégorie, Prix, Stock
- Boutons : "Ajouter", "Modifier", "Supprimer", "Actualiser"
- `QDialog` interne `ProductDialog` avec champs : nom, catégorie, description (`QTextEdit`), prix (`QDoubleSpinBox`), stock (`QSpinBox`), image (`QLineEdit` pour l'URL/chemin)
- Confirmation avant suppression (`QMessageBox.question`)

**`gui/orders_page.py`** :
- `QTableWidget` : colonnes ID, Client, Email, Date, Statut (libellé), Total
- Au clic sur une ligne, panneau de détails à droite :
  - Infos client
  - Liste des articles (`QTableWidget` : Produit, Quantité, Prix unitaire, Sous-total)
  - `QComboBox` avec les 4 statuts (libellés humains) + bouton "Mettre à jour"
- Bouton "Actualiser" en haut

**`gui/users_page.py`** :
- `QTableWidget` : colonnes ID, Prénom, Nom, Email, Inscrit le
- Boutons : "Ajouter", "Modifier", "Supprimer", "Actualiser"
- `QDialog` `UserDialog` avec champs : prénom, nom, email, mot de passe (visible uniquement en création)
- Confirmation avant suppression

### 7.9 `resources/styles.qss` — Thème café

Palette à utiliser :
- Fond principal : `#FFF8E7` (crème)
- Fond des cartes et tableaux : `#FFFFFF`
- Texte principal : `#3E2723` (marron foncé)
- Boutons : fond `#6D4C41`, texte blanc, hover `#8D6E63`
- Bordures : `#D7CCC8`
- Accent / sélection : `#A1887F`
- Erreur : `#C62828`
- Barre latérale : fond `#3E2723`, texte `#FFF8E7`

Styliser au minimum :
- `QMainWindow`, `QWidget` (fond, police)
- `QPushButton` (padding 8-12px, border-radius 6px, hover)
- `QLineEdit`, `QTextEdit`, `QComboBox`, `QSpinBox`, `QDoubleSpinBox` (bordure fine, focus marron)
- `QTableWidget` (header marron foncé texte blanc, lignes alternées `#F5F1E8`)
- `QLabel[class="title"]` (taille 20px, bold)
- `QLabel[class="stat-value"]` (taille 28px, bold, marron)
- `QFrame#statCard` (fond blanc, border-radius 8px, bordure `#D7CCC8`, padding)
- `QWidget#mainSidebar` (fond `#3E2723`, boutons en texte blanc à plat, hover `#5D4037`)

Police suggérée : `"Segoe UI", "Arial", sans-serif`.

### 7.10 `main.py`

```python
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from gui.login_page import LoginPage
from gui.main_window import MainWindow
from services.auth_service import AuthService


def main():
    app = QApplication(sys.argv)

    # Chargement du thème
    qss_path = Path(__file__).parent / "resources" / "styles.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    auth = AuthService()
    login = LoginPage(auth)
    main_window = MainWindow(auth)

    def on_login_success(user):
        main_window.set_user(user)
        main_window.show()
        login.close()

    def on_logout():
        main_window.close()
        login.show()

    login.login_success.connect(on_login_success)
    main_window.logout_requested.connect(on_logout)

    login.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

### 7.11 `README.md`

Contenu attendu (en français) :
1. **Présentation** : contexte BTS E6, complément du site web L'Antique Web, partage de la BDD `antique_db`.
2. **Prérequis** : Python 3.10+, MySQL avec la BDD `antique_db` déjà installée (depuis les scripts `database.sql` et `seed.sql` du site web).
3. **Installation** :
   ```
   git clone https://github.com/Babouille404/AntiqueApp.git
   cd AntiqueApp
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # Linux/Mac
   pip install -r requirements.txt
   copy config.example.py config.py     # Windows
   # cp config.example.py config.py     # Linux/Mac
   # puis éditer config.py avec les identifiants MySQL
   ```
4. **Lancement** : `python main.py`
5. **Identifiants de test** (issus du seed du site web) :
   - Email : `employe@antique.fr`
   - Mot de passe : `password123`
6. **Structure du projet** (arborescence commentée)
7. **Architecture en couches** (paragraphe court sur models / services / gui)
8. **Sécurité** : requêtes paramétrées, bcrypt (compatible PHP `$2y$`), `config.py` ignoré par git
9. **Notes BTS** : mention de l'épreuve E6 et du projet jumeau L'Antique Web

---

## 8. Règles de qualité (non négociables)

1. **Tous les commentaires et messages d'erreur sont en français.**
2. **Toutes les requêtes SQL utilisent `%s` paramétré** — jamais de f-string ni de concaténation dans le SQL.
3. **Les mots de passe sont toujours hachés** avant insertion en BDD.
4. **Pas de `print()` dans le code livré** — utiliser `QMessageBox` pour informer l'utilisateur.
5. **Pas de design patterns complexes** (pas d'injection de dépendance, pas de factory, pas de métaclasses). Le jury doit comprendre le code à la lecture.
6. **Gestion d'erreurs** : les services lèvent des `ValueError` ; la GUI les attrape et affiche un `QMessageBox.warning`.
7. **Signaux Qt** pour communiquer entre fenêtres/pages (pas de variables globales).
8. **Noms de classes en anglais**, noms de variables et commentaires en français acceptés.
9. **Aucun fichier de plus** que ceux listés dans la structure — le jury doit retrouver l'arborescence annoncée.
10. **Le mot `admin` n'apparaît jamais dans les requêtes SQL** : c'est toujours `role = 'employe'`. Inversement, le mot `employe` n'apparaît pas dans les libellés visibles par l'utilisateur (on dit "Administrateur").

---

## 9. Ordre de génération

Génère les fichiers **dans cet ordre précis**, chacun complet et fonctionnel avant de passer au suivant :

1. `.gitignore`, `requirements.txt`, `config.example.py`, `README.md`
2. `database/__init__.py`, `database/connection.py`
3. `utils/__init__.py`, `utils/security.py`
4. `models/__init__.py`, puis les 3 modèles
5. `services/__init__.py`, puis les 5 services
6. `gui/__init__.py`, puis `login_page.py`, `main_window.py`, puis les 4 pages
7. `resources/styles.qss`
8. `main.py`

À la fin, affiche un court récapitulatif avec :
- Les étapes d'installation
- La commande pour lancer l'application
- Les identifiants de test (`employe@antique.fr` / `password123`)
