# L'Antique App — Client Lourd (BTS SIO SLAM - E6)

## Présentation

L'Antique App est une application de bureau développée en Python avec PySide6, destinée aux administrateurs de la boutique de café **L'Antique**. Elle complète le site web **L'Antique Web** (client léger PHP) en offrant une interface d'administration pour gérer le catalogue, les commandes et les comptes clients.

L'application partage la même base de données MySQL (`antique_db`) que le site web. Ce projet s'inscrit dans le cadre de l'épreuve E6 du BTS SIO option SLAM.

## Prérequis

- **Python 3.10+**
- **MySQL** avec la base de données `antique_db` déjà installée (via les scripts `database.sql` et `seed.sql` du projet L'Antique Web)

## Installation

```bash
git clone https://github.com/Babouille404/AntiqueApp.git
cd AntiqueApp
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
copy config.py config.py     # Windows
# cp config.py config.py     # Linux/Mac
# puis éditer config.py avec les identifiants MySQL
```

## Lancement

```bash
python main.py
```

## Identifiants de test

Ces identifiants sont issus du seed du site web :

- **Email** : `employe@antique.fr`
- **Mot de passe** : `password123`

## Structure du projet

```
AntiqueApp/
├── .gitignore
├── requirements.txt
├── README.md
├── main.py                     # Point d'entrée
├── config.py                   # Paramètres BDD (ignoré par git)
├── config.example.py           # Modèle à copier
├── database/
│   ├── __init__.py
│   └── connection.py           # Connexion MySQL
├── models/
│   ├── __init__.py
│   ├── user_model.py           # Accès table users
│   ├── product_model.py        # Accès table products
│   └── order_model.py          # Accès tables orders / order_items
├── services/
│   ├── __init__.py
│   ├── auth_service.py         # Authentification
│   ├── user_service.py         # Gestion des clients
│   ├── product_service.py      # Gestion des produits
│   ├── order_service.py        # Gestion des commandes
│   └── stats_service.py        # Statistiques du tableau de bord
├── gui/
│   ├── __init__.py
│   ├── login_page.py           # Écran de connexion
│   ├── main_window.py          # Fenêtre principale (après login)
│   ├── dashboard_page.py       # Tableau de bord
│   ├── products_page.py        # Gestion des produits
│   ├── orders_page.py          # Gestion des commandes
│   └── users_page.py           # Gestion des clients
├── utils/
│   ├── __init__.py
│   └── security.py             # Hachage et vérification des mots de passe
└── resources/
    └── styles.qss              # Thème café
```

## Architecture en couches

Le projet suit une architecture en **3 couches** strictes :

- **Modèles** (`models/`) : accès à la base de données via des requêtes SQL paramétrées. Chaque méthode ouvre et ferme sa propre connexion.
- **Services** (`services/`) : logique métier, validations et orchestration. Les services appellent les modèles et lèvent des `ValueError` avec des messages clairs en français.
- **GUI** (`gui/`) : interface graphique PySide6. La GUI n'appelle jamais directement un modèle, elle passe toujours par un service.

## Sécurité

- **Requêtes SQL paramétrées** (`%s`) : aucune concaténation ni f-string dans les requêtes SQL.
- **Mots de passe hachés avec bcrypt** : compatibilité avec les hashs PHP (`$2y$` → `$2b$`).
- **`config.py` ignoré par git** : les identifiants de connexion à la BDD ne sont pas versionnés.

## Notes BTS

Ce projet constitue la réalisation technique présentée lors de l'épreuve E6 du BTS SIO option SLAM. Il est le complément « client lourd » du projet **L'Antique Web** (client léger PHP/MySQL).
