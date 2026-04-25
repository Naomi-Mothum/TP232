# EduAnalysis - Suivi et Analyse des Performances des Étudiants

Une application web complète conçue pour collecter les données de performance des étudiants et fournir des informations avancées grâce au machine learning.

## Fonctionnalités
- **Collecte de Données** : Formulaire de saisie manuelle et support d'importation CSV.
- **Analyse Avancée** : 
  - Régression Linéaire Simple et Multiple.
  - Analyse en Composantes Principales (PCA) pour la réduction de dimension.
  - Régression Logistique pour la prédiction de réussite/échec.
  - Clustering K-Means pour la segmentation des profils d'étudiants.
- **Tableau de Bord Dynamique** : Interface responsive avec visualisations Chart.js (lignes de régression, graphiques de clusters, projection PCA).
- **Base de Données SQLite** : Stockage persistant avec données pré-chargées (60+ enregistrements).

## Prérequis
- Python 3.8+
- Dépendances listées dans `requirements.txt`

## Installation et Lancement Local

1. **Cloner le dépôt** (ou naviguer dans le répertoire du projet).
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancer l'application** :
   ```bash
   python main.py
   ```
4. **Accéder au tableau de bord** :
   Ouvrez [http://localhost:8000](http://localhost:8000) dans votre navigateur.

## Structure du Projet
- `app/` : Logique backend (FastAPI, SQLAlchemy, Scikit-learn).
- `static/` : Actifs frontend (Vanilla CSS, JS).
- `templates/` : Modèle HTML du tableau de bord.
- `main.py` : Point d'entrée de l'application.
- `seed.py` : Utilitaire pour peupler la base de données.

## Déploiement
Cette application est prête pour le déploiement sur toute plateforme supportant Python. Assurez-vous que `requirements.txt` est à jour.
