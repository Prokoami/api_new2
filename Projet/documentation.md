
# API d'Analyse et de Visualisation de Données

**Version:** 4.2

## 1. Vue d'ensemble

Cette API, construite avec **FastAPI**, fournit un ensemble d'outils puissants pour l'analyse exploratoire de données. Elle permet de téléverser des jeux de données (CSV, Excel), de les nettoyer, d'en extraire des statistiques descriptives, et surtout, de les visualiser en 2D ou 3D en utilisant des techniques de réduction de dimensionnalité de pointe comme l'**ACP**, **t-SNE** et **UMAP**.

Les visualisations générées sont des graphiques interactifs créés avec Plotly, sauvegardés sur le serveur et accessibles via une URL unique.

## 2. Démarrage Rapide

### Prérequis

- Python 3.8+
- `pip`

### Installation

1.  Clonez le dépôt du projet.
2.  Naviguez jusqu'au répertoire racine (`API_code`)
3.  Installez les dépendances requises :

    ```bash
    pip install -r requirement.txt
    ```

### Lancement du Serveur

Le serveur est propulsé par Uvicorn. Pour le lancer en mode développement (avec rechargement automatique) depuis le répertoire `API_code`, exécutez :

```bash
uvicorn Projet.api:app --reload
```

L'API sera alors accessible à l'adresse [http://127.0.0.1:8000](http://127.0.0.1:8000).

## 3. Structure du Projet

```
API_code/
├── Projet/
│   ├── api.py              # Fichier principal de l'API (endpoints FastAPI)
│   ├── main.py             # Script pour des tests locaux (non utilisé par l'API)
│   ├── packages/
│   │   ├── modules/        # Logique métier (chargement, nettoyage, analyse, etc.)
│   │   └── data/           # Données CSV d'exemple
│   ├── storage/
│   │   ├── renders/        # Stockage des visualisations HTML générées
│   │   └── ma_base.db      # Base de données SQLite par défaut
│   ├── Dockerfile          # Instructions pour la conteneurisation
│   └── ...
└── requirement.txt         # Dépendances Python
```

## 4. Endpoints de l'API

L'API est organisée en deux catégories principales : **"Gérer les Données"** et **"Visualisation"**.

---

### 4.1. Gérer les Données

#### **`POST /donnees/decrire`**

Charge un fichier (CSV/Excel) et retourne un résumé complet (dimensions, colonnes, types, valeurs manquantes) ainsi que des statistiques descriptives.

-   **Paramètres:**
    -   `fichier`: Le fichier de données à téléverser.
-   **Exemple d'utilisation (`curl`):**

    ```bash
    curl -X POST "http://127.0.0.1:8000/donnees/decrire" \
         -F "fichier=@/chemin/vers/vos/donnees.csv"
    ```

-   **Réponse (succès):**

    ```json
    {
      "statut": "success",
      "resume": {
        "shape": [150, 5],
        "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"],
        "types": { "...": "float64", "...": "object" },
        "missing_values": { "...": 0 },
        "duplicates": 0
      },
      "statistiques": {
        "sepal_length": { "count": 150.0, "mean": 5.84, ... },
        "species": { "count": 150, "unique": 3, "top": "setosa", ... }
      }
    }
    ```

#### **`POST /nettoyer-donnees`**

Applique des opérations de nettoyage sur un jeu de données téléversé (suppression des doublons, gestion des valeurs manquantes).

-   **Paramètres:**
    -   `fichier`: Le fichier de données à téléverser.
    -   `parametres_json`: Une chaîne JSON contenant les options de nettoyage.
-   **Options de `parametres_json`:**
    -   `supprimer_na` (bool): Si `true`, supprime les lignes avec des valeurs manquantes.
    -   `supprimer_doublons` (bool): Si `true`, supprime les lignes dupliquées.
    -   `strategie_imputation` (str): Si `supprimer_na` est `false`, peut être `"mean"`, `"median"` ou `"fill"` pour imputer les valeurs manquantes.
-   **Exemple d'utilisation (`curl`):**

    ```bash
    curl -X POST "http://127.0.0.1:8000/nettoyer-donnees" \
         -F "fichier=@/chemin/vers/vos/donnees.csv" \
         -F "parametres_json={\"supprimer_doublons\": true, \"strategie_imputation\": \"median\"}"
    ```

-   **Réponse (succès):**

    ```json
    {
        "statut": "success",
        "message": "Nettoyage terminé.",
        "donnees_nettoyees": [
            { "col1": 1, "col2": "A" },
            { "col1": 2, "col2": "B" }
        ]
    }
    ```

#### **`POST /donnees/sauvegarde-en-bdd`**

Charge un fichier et sauvegarde son contenu dans une table d'une base de données SQLite.

-   **Paramètres:**
    -   `fichier`: Le fichier de données à téléverser.
    -   `parametres_json`: Une chaîne JSON contenant les options de sauvegarde.
-   **Options de `parametres_json`:**
    -   `chemin_bdd` (str): Chemin vers le fichier de la base de données (ex: `storage/ma_base.db`).
    -   `nom_table` (str): Nom de la table où insérer les données.
    -   `si_existe` (str): Action si la table existe déjà : `"fail"` (défaut), `"replace"`, ou `"append"`.
-   **Exemple d'utilisation (`curl`):**

    ```bash
    curl -X POST "http://127.0.0.1:8000/donnees/sauvegarde-en-bdd" \
         -F "fichier=@/chemin/vers/vos/donnees.csv" \
         -F "parametres_json={\"chemin_bdd\": \"storage/ma_base.db\", \"nom_table\": \"donnees_clients\", \"si_existe\": \"replace\"}"
    ```

---

### 4.2. Visualisation

Ces endpoints sont le cœur de l'API. Ils prennent un fichier de données, une méthode de réduction et des paramètres de visualisation, puis retournent une visualisation interactive.

#### **`POST /reduire-visualiser-2d`**
#### **`POST /reduire-visualiser-3d`**

-   **Paramètres:**
    -   `methode` (str): La méthode de réduction à utiliser. Valeurs possibles : `"acp"`, `"tsne"`, `"umap"`, `"auto"`.
    -   `fichier`: Le fichier de données à téléverser.
    -   `parametres_json`: Une chaîne JSON contenant les options de visualisation.

-   **Options de `parametres_json`:**
    -   `colonne_couleur` (str, optionnel): Nom de la colonne à utiliser pour colorer les points du graphique.
    -   `titre` (str): Titre du graphique.
    -   `perplexite` (int, pour `tsne`): Perplexité de l'algorithme t-SNE (défaut: 5).
    -   `n_neighbor` (int, pour `umap`): Nombre de voisins pour l'algorithme UMAP (défaut: 10).
    -   `dist_min` (float, pour `umap`): Distance minimale pour l'algorithme UMAP (défaut: 0.1).

-   **Exemple d'utilisation (`curl` pour une visualisation 3D UMAP):**

    ```bash
    curl -X POST "http://127.0.0.1:8000/reduire-visualiser-3d" \
         -F "methode=umap" \
         -F "fichier=@/chemin/vers/vos/donnees.csv" \
         -F "parametres_json={\"colonne_couleur\": \"target_variable\", \"titre\": \"UMAP 3D des Clusters\", \"n_voisins\": 20}"
    ```

-   **Réponse (succès):**

    ```json
    {
      "statut": "success",
      "methode_utilisee": "umap",
      "message": "Rendu 3D UMAP créé avec succès.",
      "url_rendu": "http://127.0.0.1:8000/static/renders/rendu_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.html",
      "contenu_html": "<!DOCTYPE html><html><head>..."
    }
    ```
    La `url_rendu` peut être ouverte directement dans un navigateur pour voir le graphique interactif. Le `contenu_html` peut être utilisé pour embarquer le graphique directement dans une application front-end.

## 5. Flux de travail typique

Un utilisateur souhaitant explorer un nouveau jeu de données suivrait généralement ces étapes :

1.  **Décrire les données** : Appeler `POST /donnees/decrire` pour obtenir un aperçu rapide du fichier, identifier les colonnes pertinentes et les problèmes potentiels (valeurs manquantes, etc.).
2.  **Nettoyer (si nécessaire)** : Appeler `POST /nettoyer-donnees` pour corriger les problèmes identifiés.
3.  **Visualiser** : Appeler `POST /reduire-visualiser-3d` avec le fichier (nettoyé ou non), en choisissant une méthode (`umap` est un bon point de départ) et en spécifiant une colonne catégorielle comme `colonne_couleur` pour identifier des clusters visuels.
4.  **Analyser le résultat** : Ouvrir la `url_rendu` retournée par l'API pour explorer le graphique 3D interactif, zoomer, et inspecter les points de données.
