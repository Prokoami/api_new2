# API d'Analyse et de Visualisation de Données

Cette documentation décrit l'API construite avec FastAPI, ses fonctionnalités, son architecture et la manière de l'utiliser.

## 1. Objectif

L'objectif de cette API est de fournir une plateforme **stateless** et accessible via HTTP pour l'**analyse exploratoire de données (EDA)**. Elle transforme des opérations complexes (nettoyage, visualisation, réduction de dimension) en services web simples et réutilisables.

**Principes clés :**
- **Accessibilité** : Interagissez avec l'API depuis n'importe quelle application cliente via des requêtes HTTP.
- **Standardisation** : Offre une méthode unifiée pour effectuer des tâches d'analyse courantes.
- **Rapidité** : Obtenez rapidement des insights visuels sur un jeu de données sans configurer un environnement local complet.
- **Intégration** : Peut servir de backend pour des applications de tableaux de bord interactifs.

## 2. Outils utilisés 

L'API est construite sur un écosystème Python moderne et robuste.

| categorie   | outils  | Rôle |
|---|---|---|
| **Framework Web** | `FastAPI` | Construction d'API haute performance, validation de données, documentation automatique. |
| **Serveur ASGI** | `Uvicorn` | Exécution de l'application FastAPI. |
| **Validation** | `Pydantic` | Définition de schémas de données, validation des requêtes et sérialisation des réponses. |
| **Data Science** | `Pandas`, `NumPy` | Manipulation de données tabulaires et calculs numériques. |
| **Visualisation** | `Plotly`, `Matplotlib`, `Seaborn` | Création de graphiques interactifs (Plotly) et statiques. |
| **Machine Learning**| `Scikit-learn`, `UMAP-learn` | Algorithmes de réduction de dimension (ACP, t-SNE, UMAP). |
| **Autres** | `Pillow`, `WordCloud` | Traitement d'images et génération de nuages de mots. |

La structure du projet est modulaire, organisée en `packages` et `modules` (`loading`, `netoyage`, `analysis`, etc.), favorisant la maintenabilité et l'extensibilité.

## 3. Installation et Lancement

### 3.1. Prérequis
- Python 3.8+

### 3.2. Installation des dépendances
Il est recommandé de créer un fichier `requirements.txt` à la racine de votre projet avec le contenu suivant, puis de l'installer.

```txt
# requirements.txt
fastapi
gunicorn # Ajouté pour le déploiement en production
uvicorn[standard]
pandas
numpy
matplotlib
seaborn
plotly
scikit-learn
umap-learn
python-multipart
Pillow
opencv-python-headless
wordcloud
pyarrow
openpyxl
```

Installez les dépendances avec `pip` :
```bash
pip install -r requirements.txt
```

### 3.3. Lancement du serveur
Ouvrez un terminal à la racine du projet (où se trouve `api.py`) et exécutez la commande :

```bash
uvicorn api:app --reload 
```

- `api`: Fait référence au fichier `api.py`.
- `app`: Fait référence à l'objet `FastAPI` créé dans le fichier (`app = FastAPI(...)`).
- `--reload`: Redémarre le serveur automatiquement après chaque modification du code (idéal pour le développement).

L'API sera alors accessible à l'adresse < http://127.0.0.1:8000.>

## 4. Utilisation de l'API

La meilleure façon d'explorer et de tester l'API est d'utiliser la documentation interactive générée automatiquement.

- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc
- **Interfaces de test locales** :
  - [Testeur de Réduction](file:///c:/Users/User/Desktop/development/API_code/Projet/testes/tester_reduction.html)
  - [Testeur de Nettoyage](file:///c:/Users/User/Desktop/development/API_code/Projet/testes/tester_nettoyage.html)
  - [Testeur de Nuage de Mots](file:///c:/Users/User/Desktop/development/API_code/Projet/testes/tester_nuage_de_mots.html)
  - [Testeur de Visualisation](file:///c:/Users/User/Desktop/development/API_code/Projet/testes/tester_visualisation.html)

### 4.1. Les Modèles de Requête

L'API utilise deux modèles de requête principaux, adaptés à différents cas d'usage.

#### Modèle 1 : Requête JSON unique (pour le pipeline complet)

L'endpoint `/analyser-et-visualiser/` utilise un **unique corps de requête JSON**. Ce modèle est puissant pour les interactions de service à service, où les données peuvent être envoyées directement en JSON ou encodées en Base64.

La source des données est spécifiée via un objet `DataSource`, qui peut prendre l'une des formes suivantes :

| Champ | Type | Description |
|---|---|---|
| `donnees_brutes` | `List[Dict]` | Données directement fournies en JSON (tableau d'objets). |
| `chemin_fichier` | `str` | Chemin vers un fichier de données sur le serveur. |
| `contenu_base64`| `str` | Contenu d'un fichier (CSV/Excel) encodé en Base64. |
| `nom_fichier` | `str` | **Requis si `contenu_base64` est utilisé.** Permet de déterminer le type de fichier (ex: 'data.csv'). |

> **Note** : Une seule de ces sources doit être fournie par requête.

#### Modèle 2 : Requête `multipart/form-data` (pour les endpoints interactifs)

La plupart des autres endpoints (`/reduire-dimension`, `/nettoyer-donnees`, `/visualiser/...`) sont conçus pour des clients interactifs (comme une page web). Ils utilisent le format `multipart/form-data`, qui permet d'envoyer un **fichier** et des **paramètres** dans la même requête.

- **Source de données** : Un champ de formulaire de type `file` pour téléverser un fichier (CSV, Excel, image, etc.).
- **Paramètres** : Des champs de formulaire textuels. Pour les paramètres complexes (comme ceux de la réduction de dimension), ils sont envoyés sous forme de chaîne JSON dans un champ unique (ex: `params_json`).

Ce modèle est celui utilisé par les interfaces de test HTML fournies.

### 4.2. Détail des Endpoints

Voici un aperçu des endpoints les plus importants.

#### Pipeline Complet
- **Endpoint** : `POST /analyser-et-visualiser/` (Modèle JSON unique)
- **Description** : Exécute un pipeline complet : chargement, nettoyage (optionnel) et réduction de dimension. C'est l'endpoint le plus puissant et recommandé.
- **Exemple de requête** (`application/json`) :
  ```json
  {
    "source_donnees": {
      "donnees_brutes": [
        {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2, "species": "setosa"},
        {"sepal_length": 7.0, "sepal_width": 3.2, "petal_length": 4.7, "petal_width": 1.4, "species": "versicolor"}
      ]
    },
    "parametres_nettoyage": {
      "supprimer_doublons": true
    },
    "parametres_reduction": {
      "methode": "umap",
      "n_components": 2,
      "color_by_col": "species",
      "n_neighbors": 10
    }
  }
  ```

#### Réduction de Dimension
- **Endpoint** : `POST /reduire-dimension/`
- **Description** : Applique une technique de réduction de dimension (ACP, UMAP, ou t-SNE) sur un jeu de données.
- **Exemple de requête** (`application/json`) :
  ```json
  {
    "source_donnees": {
      "chemin_fichier": "/path/to/your/data.csv"
    },
    "parametres_reduction": {
      "methode": "acp",
      "n_components": 3,
      "color_by_col": "target"
    }
  }
  ```

#### Nettoyage de Données
- **Endpoint** : `POST /nettoyer-donnees/`
- **Description** : Applique diverses étapes de nettoyage à un jeu de données.
- **Exemple de requête** (`application/json`) :
  ```json
  {
    "source_donnees": {
      "contenu_base64": "c2VwYWxfbGVuZ3RoLH...",
      "nom_fichier": "my_data.csv"
    },
    "parametres_nettoyage": {
      "supprimer_lignes_na": true,
      "strategie_imputation": "mean",
      "colonnes_imputation": ["age"]
    }
  }
  ```

## 5. Concepts Architecturaux Clés

- **Injection de Dépendances (`Depends`)** : FastAPI est utilisé pour centraliser la logique réutilisable, comme le chargement et la validation des données, rendant les endpoints plus propres et plus lisibles.
- **Modèles Pydantic Avancés** : L'utilisation de `Union` et `Literal` (par exemple dans `ReductionParams`) permet de créer une API auto-documentée et fortement typée, où les paramètres disponibles s'adaptent dynamiquement au choix de l'utilisateur.
- **Gestion des Retours** : Pour les opérations complexes comme la réduction de dimension, l'API retourne non seulement une image (`image_data`) mais aussi les données transformées (`reduced_data`), permettant une réutilisation côté client.
- **Gestion des Erreurs** : L'API utilise `HTTPException` pour retourner des erreurs claires avec des codes de statut HTTP appropriés (ex: `400` pour une mauvaise requête, `404` pour un fichier non trouvé), ce qui est une bonne pratique pour les API RESTful.
