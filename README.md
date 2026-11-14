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


## Stockage permanent des photos avec Cloudinary

Les photos ajoutées dans l'administration sont maintenant envoyées vers Cloudinary. Leur URL HTTPS est enregistrée dans la base de données : elles sont donc visibles sur tous les appareils et ne dépendent pas du disque temporaire de Render.

### Configuration obligatoire sur Render

1. Créez un compte sur https://cloudinary.com/ et ouvrez le tableau de bord (Dashboard).
2. Dans Render, ouvrez le service MIMISHOP puis **Environment**.
3. Ajoutez ces trois variables avec les valeurs affichées dans le Dashboard Cloudinary :
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
4. Enregistrez les changements et laissez Render redéployer le site.
5. Testez en ajoutant un nouveau produit avec une photo, puis ouvrez le site depuis un autre téléphone.

Ne communiquez jamais la valeur de `CLOUDINARY_API_SECRET` publiquement ou dans une conversation. Saisissez-la uniquement dans les variables d'environnement privées de Render.

**Important :** les anciennes photos déjà enregistrées sous `/static/uploads/` ne sont pas transférées automatiquement. Après configuration, ouvrez chaque ancien produit dans l'administration et ajoutez à nouveau sa photo (ou fournissez une URL d'image publique).
