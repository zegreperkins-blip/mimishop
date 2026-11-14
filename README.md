# MIMISHOP — Boutique de mode féminine

## Installation Windows (PowerShell)

1. Installer Python 3.11 ou plus récent.
2. Ouvrir PowerShell dans le dossier MIMISHOP.
3. Exécuter :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

4. Ouvrir http://127.0.0.1:5000

## Administration
- Adresse : http://127.0.0.1:5000/admin/connexion
- Identifiant initial : `admin`
- Mot de passe initial : `MimiShop2026!`

IMPORTANT : avant toute mise en ligne, définir des variables d'environnement `ADMIN_USERNAME`, `ADMIN_PASSWORD` et `SECRET_KEY` avec des valeurs personnelles fortes. Ne jamais conserver le mot de passe de démonstration en production.

## Base SQL
Le projet utilise SQLite dans le fichier `mimishop.db`, créé automatiquement au premier lancement. Les tables sont `product`, `order` et `admin`.

## Mise en ligne Render
- Créer un dépôt GitHub et y envoyer le contenu du dossier.
- Render > New > Web Service > connecter le dépôt.
- Build command : `pip install -r requirements.txt`
- Start command : `gunicorn app:app`
- Ajouter `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `SECRET_KEY`.
- Pour conserver la base de données et les photos durablement sur Render, configurer un disque persistant et une base PostgreSQL. Le SQLite local est prévu pour les essais et le développement.

## Personnalisation
- Modifier les couleurs dans `static/style.css`.
- Ajouter les produits depuis `/admin`.
- Téléverser les photos dans l'administration ou saisir une URL d'image.
- Le WhatsApp est configuré dans `app.py` (format international sans + : 2250576949824).

## À vérifier avant les vraies ventes
- Confirmer les catégories et les tailles/variantes (notamment lingerie).
- Ajouter les frais et zones de livraison.
- Configurer un stockage persistant et une vraie base PostgreSQL en production.
- Tester une commande complète sur téléphone.
