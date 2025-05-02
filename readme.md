APP ECOMMERCE 1.0.0

Plateforme e-commerce complète avec backend API Django REST Framework et frontend React TypeScript.

## Fonctionnalités principales

### Backend (Django REST Framework)

- ✅ Système d'authentification utilisateur (JWT)
- ✅ Gestion des produits avec catégories et tags
- ✅ Panier d'achat et gestion des commandes
- ✅ Système d'évaluation et de commentaires
- ✅ Recherche et filtrage avancé
- ✅ Administration Django personnalisée
- ✅ Paiement avec Stripe/PayPal


## Prérequis
- Python 3.10+
- PostgreSQL/MySQL (recommandé pour la production)
- Redis (pour le cache, optionnel)

## Installation

### 1. Cloner le dépôt
git clone : https://github.com/TCHUINDJANG/Ecommerce_Api_App.git
cd ecommerce-project

2. Configuration backend
Créer un environnement virtuel : 
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

Installer les dépendances :
pip install -r requirements.txt

Appliquer les migrations :
python manage.py migrate
python manage.py createsuperuser

Exécution:
python manage.py runserver

Accès à :
API : http://localhost:8000/api/
Admin : http://localhost:8000/admin/

Tests
Lancer les tests backend : python manage.py test