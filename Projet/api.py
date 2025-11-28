# api.py (Version 4.2 - Finale, Robuste et Nettoyée)

# --- Importations des biblioothèques de base ---
import csv
import io
import pandas as pd
import numpy as np
import plotly.express as px
import json
import uuid
import os
import markdown
from io import StringIO
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal, Union
from fastapi import FastAPI, Request, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# --- Importation des Outils Backend ---
from packages.modules.loading import DataLoader
from packages.modules.netoyage import Netoyage
from packages.modules.analysis import Analyse
from packages.modules.numeric_data import Numeric_data
from packages.modules.methode_acp import MethodeACP
from packages.modules.methode_tsne import MethodeTSNE
from packages.modules.methode_umap import MethodeUMAP
from packages.modules.auto_selector import AutoSelector
from packages.modules.clean_dataframe_for_json import CleanDataframeForJson
from packages.modules.sauvegarde_bdd import SauvegardeBDD

# --- Configuration de l'Application ---
app = FastAPI(
    title="API d'Analyse et Visualisation de Données v4.2",
    description="Une API robuste et cohérente pour l'analyse et la visualisation."
)

# Configuration CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
    "*"  # Permet toutes les origines pour le développement
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Répertoire de Stockage pour les Renders HTML ---
DOSSIER_STOCKAGE = Path("storage/renders")
DOSSIER_STOCKAGE.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory="storage"), name="static")


# ==============================================================================
# 1. MODÈLES PYDANTIC (Le "Contrat" de l'API)
# ==============================================================================

class ParametresNettoyage(BaseModel):
    supprimer_na: bool = Field(False, description="Supprimer les lignes avec NA.")
    supprimer_doublons: bool = Field(False, description="Supprimer les doublons.")
    strategie_imputation: Optional[Literal['mean', 'median', 'fill']] = Field(None)

class ParametresVisualisation(BaseModel):
    """Paramètres pour une visualisation (ACP, UMAP, t-SNE)"""
    colonne_couleur: Optional[str] = Field(None, description="Nom de la colonne pour la couleur.")
    titre: str = Field("Visualisation Interactive", description="Titre du graphique.")
    perplexite: int = Field(30, ge=1, description="[t-SNE] Perplexité.")
    n_voisins: int = Field(15, ge=2, description="[UMAP] Nombre de voisins.")
    dist_min: float = Field(0.1, ge=0.0, description="[UMAP] Distance minimale.")

class ParametresSauvegardeBdd(BaseModel):
    chemin_bdd: str = Field(..., description="Chemin du fichier BDD (ex: 'storage/ma_base.db').")
    nom_table: str = Field(..., description="Nom de la table à créer (ex: 'resultats_nettoyes').")
    si_existe: Literal['fail', 'replace', 'append'] = Field('fail', description="Action si la table existe.")

# --- Modèles de Réponse ---

class ReponseSauvegarde(BaseModel):
    statut: str = "success"
    message: str
    chemin_bdd: str
    nom_table: str

class ReponseDescription(BaseModel):
    statut: str = "success"
    resume: Dict[str, Any]
    statistiques: Dict[str, Dict[str, Any]] # Clés = colonnes

class SourceDistante(BaseModel):
    chemin_source: str = Field(..., description="Chemin local (/app/data.csv) ou URL (https://...)")

class ReponseNettoyage(BaseModel):
    statut: str = "success"
    message: str
    donnees_nettoyees: List[Dict[str, Any]]

class ReponseVisualisation(BaseModel):
    statut: str = "success"
    methode_utilisee: str
    message: str
    url_rendu: str # URL pour accéder au fichier HTML stocké
    contenu_html: str # Le HTML lui-même, pour un affichage direct


# ==============================================================================
# 2. SERVICES & HELPERS (Le "Chef d'Orchestre")
# ==============================================================================

# --- Dépendances (Injection) ---
def obtenir_chargeur_donnees():
    """Injecte une instance du DataLoader."""
    return DataLoader()

def obtenir_nettoyeur_json():
    """Injecte le nettoyeur JSON."""
    return CleanDataframeForJson()

# --- Helpers ---
def obtenir_df_depuis_televersement(fichier: UploadFile) -> pd.DataFrame:
    """Charge un DataFrame depuis un fichier téléversé en mémoire (robuste)."""
    if not (fichier.filename.endswith('.csv') or fichier.filename.endswith('.xlsx')):
        raise HTTPException(status_code=400, detail="Format de fichier non supporté (CSV ou XLSX requis).")

    # Lire le contenu une seule fois
    contenu = fichier.file.read() 
    
    try:
        if fichier.filename.endswith('.csv'):
            # Gestion de l'encodage
            try:
                contenu_decode = contenu.decode('utf-8')
            except UnicodeDecodeError:
                contenu_decode = contenu.decode('latin-1')

            # Détection automatique du séparateur
            echantillon = contenu_decode[:1000]
            try:
                dialecte = csv.Sniffer().sniff(echantillon)
                separateur = dialecte.delimiter
            except Exception:
                separateur = ',' # valeur par défaut

            # Lecture du CSV avec pandas
            return pd.read_csv(StringIO(contenu_decode), sep=separateur)

        else: # .xlsx
            # Lire à partir de la variable 'contenu' (bytes)
            return pd.read_excel(io.BytesIO(contenu)) 

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de lecture du fichier: {e}")

def sauvegarder_rendu_html(contenu_html: str, url_base_requete: str) -> str:
    """Sauvegarde le HTML et retourne l'URL d'accès public."""
    nom_fichier = f"rendu_{uuid.uuid4()}.html"
    chemin_fichier = DOSSIER_STOCKAGE / nom_fichier
    
    with open(chemin_fichier, "w", encoding="utf-8") as f:
        f.write(contenu_html)
    
    return f"{str(url_base_requete).rstrip('/')}/static/renders/{nom_fichier}"

# --- Fonction d'Orchestration pour la Visualisation ---
def creer_graphique_interactif(
    donnees_brutes: pd.DataFrame, 
    methode: Literal['acp', 'tsne', 'umap', 'auto'],
    n_composantes: Literal[2, 3],
    parametres: ParametresVisualisation
) -> tuple[str, str]:
    """
    Orchestre la réduction et la création de graphique.
    Retourne (contenu_html, methode_utilisee)
    """
    
    # 1. Préparation et Nettoyage des données (CRITIQUE POUR ÉVITER LES ERREURS 500)
    try:
        # Nettoyage préventif des NaN (SOLUTION À L'ERREUR 'Input X contains NaN')
        nettoyeur = Netoyage(donnees_brutes)
        donnees_propres = nettoyeur.gerer_les_valeurs_manquantes(strategy='drop')
    
        donnees_numeriques = Numeric_data(donnees_propres).num_col()
        if donnees_numeriques.empty:
            raise ValueError("Aucune colonne numérique trouvée ou données vides après nettoyage.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de préparation des données: {e}")

    # 2. Gérer la colonne de couleur
    donnees_couleur = None
    if parametres.colonne_couleur:
        if parametres.colonne_couleur not in donnees_brutes.columns:
            raise HTTPException(status_code=404, detail=f"Colonne de couleur '{parametres.colonne_couleur}' introuvable.")
        # On extrait les couleurs alignées avec les données numériques (après nettoyage)
        donnees_couleur = donnees_propres.loc[donnees_numeriques.index, parametres.colonne_couleur]

    # 3. Sélectionner la méthode
    nom_methode = methode
    donnees_reduites = None
    
    if methode == 'auto':
        selecteur = AutoSelector(donnees_numeriques, nombre_de_dimension=n_composantes)
        nom_methode = selecteur.selection_methode()
        print(f"[INFO] AutoSelector a choisi: {nom_methode.upper()}")

    # 4. Exécuter la Réduction
    try:
        if nom_methode == 'acp':
            donnees_reduites = MethodeACP(donnees_numeriques).acp_reduction(n_composantes)
            noms_colonnes = [f"PC_{i+1}" for i in range(n_composantes)]
        
        elif nom_methode == 'tsne':
            # Utilise le paramètre perplexity (supporté par le backend mis à jour)
            donnees_reduites = MethodeTSNE(donnees_numeriques).tsne_reduction(
                nombre_de_dimension=n_composantes,
                perplexity=parametres.perplexite 
            )
            noms_colonnes = [f"TSNE_{i+1}" for i in range(n_composantes)]
        
        elif nom_methode == 'umap':
            # Utilise les paramètres n_neighbors et min_dist (supportés par le backend mis à jour)
            donnees_reduites = MethodeUMAP(donnees_numeriques).umap_reduction(
                nombre_de_dimension=n_composantes,
                n_neighbors=parametres.n_voisins, 
                min_dist=parametres.dist_min      
            )
            noms_colonnes = [f"UMAP_{i+1}" for i in range(n_composantes)]
            
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution de {nom_methode.upper()}: {e}")

    # 5. Préparer le DataFrame pour Plotly
    if donnees_reduites is None:
        raise HTTPException(status_code=500, detail="Échec de la réduction de dimension.")

    donnees_graphique = pd.DataFrame(donnees_reduites, columns=noms_colonnes, index=donnees_numeriques.index)
    
    # Gestion robuste du hover_name (convertit en string pour éviter les erreurs)
    donnees_graphique['hover_name'] = donnees_graphique.index.astype(str)
    
    if donnees_couleur is not None:
        donnees_graphique[parametres.colonne_couleur] = donnees_couleur

    # 6. Générer le graphique interactif Plotly
    args_graphique = {
        "title": f"{parametres.titre} ({nom_methode.upper()} {n_composantes}D)",
        "color": parametres.colonne_couleur,
        "hover_name": "hover_name"
    }

    if n_composantes == 2:
        fig = px.scatter(donnees_graphique, x=noms_colonnes[0], y=noms_colonnes[1], **args_graphique)
    else:
        fig = px.scatter_3d(donnees_graphique, x=noms_colonnes[0], y=noms_colonnes[1], z=noms_colonnes[2], **args_graphique)

    return fig.to_html(full_html=True, include_plotlyjs='cdn'), nom_methode

# ==============================================================================
# 3. ENDPOINTS (Les "Portes" de l'API)
# ==============================================================================

# --- Endpoints d'Accueil et Documentation (Réintégrés) ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home():
    """Page d'accueil HTML de l'API."""
    return """
    <html>
        <head><title>VISUALDATA API</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #f9f9f9; }
                h1 { color: #2c3e50; } p { font-size: 18px; color: #555; }
                .btn { display: inline-block; margin: 10px; padding: 12px 25px; font-size: 16px; color: white; text-decoration: none; border-radius: 8px; transition: 0.3s; }
                .swagger { background-color: #3498db; } .swagger:hover { background-color: #2980b9; }
                .redoc { background-color: #27ae60; } .redoc:hover { background-color: #1e8449; }
            </style>
        </head>
        <body>
            <h1>🚀 Bienvenue sur l'API de VisualData</h1>
            <p>Cette API permet la réduction et la visualisation de données.</p>
            <a href="/docs" class="btn swagger">📘 Swagger UI</a>
            <a href="/redoc" class="btn redoc">📗 ReDoc</a>
            <a href="/api-documentation" class="btn redoc" style="background-color: #f39c12;">📙 Documentation API</a>
        </body>
    </html>
    """

@app.get(
    "/api-documentation",
    response_class=HTMLResponse,
    tags=["Documentation"],
    summary="Documentation complète du projet")
def get_api_documentation():
    """Affiche le fichier doc_api.md converti en HTML."""
    try:
        with open("documentation.md", "r", encoding="utf-8") as f:
            md_content = f.read()
        html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
        styled_html = f"""
        <!DOCTYPE html>
        <html>
            <head><title>Documentation de l'API</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; padding: 20px 40px; max-width: 900px; margin: 20px auto; color: #333; }}
                    h1, h2, h3 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    code {{ background-color: #f6f8fa; padding: 0.2em 0.4em; margin: 0; font-size: 85%; border-radius: 3px; }}
                    pre {{ background-color: #f6f8fa; padding: 16px; overflow: auto; border-radius: 3px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>{html_content}</body>
        </html>
        """
        return HTMLResponse(content=styled_html)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Le fichier de documentation 'doc_api.md' n'a pas été trouvé.")


@app.post("/donnees/decrire", 
          tags=["1. Gérer les Données"], 
          response_model=ReponseDescription,
          summary="Décrit un jeu de données (depuis téléversement)")
async def decrire_donnees(
    fichier: UploadFile = File(...),
    nettoyeur: CleanDataframeForJson = Depends(obtenir_nettoyeur_json)
):
    """
    Prend un fichier (CSV/Excel) téléversé, le charge et renvoie son résumé 
    et ses statistiques descriptives.
    Args:
        fichier (UploadFile): Le fichier téléversé contenant les données.
    Returns:
        ReponseDescription: Résumé et statistiques descriptives du jeu de données.

    """
    donnees = obtenir_df_depuis_televersement(fichier)
    
    # --- RÉSILIENCE DES TYPES (Pour éviter les erreurs dues aux strings mal formatées) ---
    # Nous conservons cette boucle, car elle est nécessaire pour que pd.describe() 
    # ne plante pas sur les colonnes qui contiennent des caractères non-numériques.
    donnees_resilientes = donnees.copy()
    for col in donnees_resilientes.columns:
        try:
            donnees_resilientes[col] = pd.to_numeric(donnees_resilientes[col], errors='coerce')
        except:
            pass
            
    try:
        service_analyse = Analyse()
        
        # Le backend corrigé peut être appelé directement
        resume = service_analyse.summarize(donnees_resilientes)
        df_statistiques = service_analyse.get_descriptive_stats(donnees_resilientes) 
        
        df_statistiques_nettoye = nettoyeur.clean_dataframe_for_json(df_statistiques)
        
        return ReponseDescription(
            statut="success",
            resume=resume,
            statistiques=df_statistiques_nettoye.to_dict('index')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse: {e}")





@app.post("/donnees/decrire-distant",
          tags=["1. Gérer les Données"],
          response_model=ReponseDescription,
          summary="Décrit un jeu de données (depuis URL ou chemin)")
async def decrire_donnees_distantes(
    source: SourceDistante,
    nettoyeur: CleanDataframeForJson = Depends(obtenir_nettoyeur_json),
    chargeur: DataLoader = Depends(obtenir_chargeur_donnees)
):
    """
    Prend un chemin de fichier (local sur serveur ou URL), le charge, 
    et renvoie son résumé et ses statistiques.

    Args:
        source (SourceDistante): Contient le chemin ou l'URL de la source de données.
    Returns:
        ReponseDescription: Résumé et statistiques descriptives du jeu de données.

    """
    try:
        donnees = chargeur.load(file_path=source.chemin_source)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Échec du chargement de la source : {e}")
    
    service_analyse = Analyse()
    resume = service_analyse.summarize(donnees)
    df_statistiques = service_analyse.get_descriptive_stats(donnees)
    df_statistiques_nettoye = nettoyeur.clean_dataframe_for_json(df_statistiques)
    
    return ReponseDescription(
        statut="success",
        resume=resume,
        statistiques=df_statistiques_nettoye.to_dict('index')
    )

@app.post("/nettoyer-donnees", 
          tags=["1. Gérer les Données"], 
          response_model=ReponseNettoyage,
          summary="Nettoie un jeu de données (depuis téléversement)")
async def nettoyer_donnees(
    fichier: UploadFile = File(...),
    parametres_json: str = Form(ParametresNettoyage().model_dump_json(), description="Paramètres de nettoyage en JSON"),
    nettoyeur_json: CleanDataframeForJson = Depends(obtenir_nettoyeur_json)
):
    """
    Prend un fichier téléversé et des paramètres de nettoyage. 
    Renvoie le DataFrame nettoyé en JSON.

    *strategie_imputation prend les valeurs: "mean", "median", "fill" (valeur fixe).
    1. "mean" : remplit les NaN par la moyenne de la colonne
    2. "median" : remplit les NaN par la médiane de la colonne
    3. "fill" : remplit les NaN par une valeur fixe (ici 0)
    4. None : ne fait rien sur les NaN (si supprimer_na est False)

    *supprimer_na : si True, supprime les lignes avec NaN  avant toute imputation.
    *supprimer_doublons : si True, supprime les lignes dupliquées.

    """
    donnees = obtenir_df_depuis_televersement(fichier)
    try:
        parametres = ParametresNettoyage.model_validate_json(parametres_json)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erreur de validation des paramètres: {e}")
    try:
        service_nettoyage = Netoyage(donnees)
        if parametres.supprimer_doublons:
            donnees = service_nettoyage.gerer_les_valeurs_duplicates()
        if parametres.supprimer_na:
            donnees = Netoyage(donnees).gerer_les_valeurs_manquantes(strategy='drop')
        elif parametres.strategie_imputation:
            donnees = Netoyage(donnees).gerer_les_valeurs_manquantes(strategy=parametres.strategie_imputation)
        
        donnees_propres = nettoyeur_json.clean_dataframe_for_json(donnees)
        return ReponseNettoyage(
            statut="success",
            message="Nettoyage terminé.",
            donnees_nettoyees=donnees_propres.to_dict('records')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de nettoyage: {e}")

@app.post("/donnees/sauvegarde-en-bdd", 
          tags=["1. Gérer les Données"], 
          response_model=ReponseSauvegarde,
          summary="Sauvegarde un fichier téléversé dans une BDD")
async def donnees_sauvegarde_en_bdd(
    fichier: UploadFile = File(..., description="Fichier CSV/Excel à charger et sauvegarder."),
    parametres_json: str = Form(ParametresSauvegardeBdd(chemin_bdd="storage/ma_base.db", nom_table="mes_donnees").model_dump_json(), 
                           description="Paramètres de sauvegarde BDD en JSON"),
):
    """
    Prend un fichier (CSV/Excel), le charge, et le sauvegarde 
    dans une table d'une base de données SQLite.
    Args:
        fichier (UploadFile): Le fichier téléversé contenant les données.
        parametres_json (str): Paramètres de sauvegarde en JSON.
    Returns:
        ReponseSauvegarde: Détails de la sauvegarde effectuée.
    """
    donnees = obtenir_df_depuis_televersement(fichier)
    try:
        parametres = ParametresSauvegardeBdd.model_validate_json(parametres_json)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erreur de validation des paramètres de sauvegarde: {e}")
    try:
        service_sauvegarde = SauvegardeBDD(donnees)
        resultat = service_sauvegarde.sauvegarder_en_sqlite(
            chemin_bdd=parametres.chemin_bdd,
            nom_table=parametres.nom_table,
            si_existe=parametres.si_existe
        )
        return ReponseSauvegarde(
            statut="success",
            message=resultat["message"],
            chemin_bdd=parametres.chemin_bdd,
            nom_table=parametres.nom_table
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde en BDD : {e}")


# --- Endpoints "2. Visualisation"---

@app.post("/reduire-visualiser-2d", 
          tags=["2. Visualisation"], 
          response_model=ReponseVisualisation,
          summary="Réduction et visualisation en 2D")
async def reduire_visualiser_2d(
    requete: Request,
    methode: Literal['acp', 'tsne', 'umap', 'auto'] = Form(..., description="Méthode de réduction."),
    fichier: UploadFile = File(...),
    parametres_json: str = Form(ParametresVisualisation().model_dump_json(), description="Paramètres de visualisation en JSON")
):
    """
    Endpoint unique pour toutes les visualisations 2D.

    *Le parametre de visualisation JSON doit ressembler a quelque chose comme :
    
    1.Pour ACP ----> {"colonne_couleur":"AGE","titre":"Visualisation Interactive"},
    2.Pour UMAP----> {"colonne_couleur":"AGE","titre":"Visualisation Interactive","n_voisins":15,"dist_min":0.1},
    3.Pour TSNE----> {"colonne_couleur":"AGE","titre":"Visualisation Interactive","perplexite":8,"n_voisins":15,"dist_min":0.1}
    
    Args:
        requete (Request): La requête HTTP entrante.
        methode (Literal): Méthode de réduction de dimensionnalité.
        fichier (UploadFile): Le fichier téléversé contenant les données.
        parametres_json (str): Paramètres de visualisation en JSON.

    Returns:
        ReponseVisualisation: Détails du rendu créé.

    """
    donnees = obtenir_df_depuis_televersement(fichier)
    try:
        parametres = ParametresVisualisation.model_validate_json(parametres_json)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erreur de validation des paramètres: {e}")

    # Appel du service d'orchestration en forçant n_composantes = 2
    contenu_html, methode_utilisee = creer_graphique_interactif(donnees, methode, 2, parametres)
    
    # Stockage du fichier HTML
    url_rendu = sauvegarder_rendu_html(contenu_html, str(requete.base_url))
    
    return ReponseVisualisation(
        statut="success",
        methode_utilisee=methode_utilisee,
        message=f"Rendu 2D {methode_utilisee.upper()} créé avec succès.",
        url_rendu=url_rendu,
        contenu_html=contenu_html
    )

@app.post("/reduire-visualiser-3d", 
          tags=["2. Visualisation"], 
          response_model=ReponseVisualisation,
          summary="Réduction et visualisation en 3D")
async def reduire_visualiser_3d(
    requete: Request,
    methode: Literal['acp', 'tsne', 'umap', 'auto'] = Form(..., description="Méthode de réduction."),
    fichier: UploadFile = File(...),
    parametres_json: str = Form(ParametresVisualisation().model_dump_json(), description="Paramètres de visualisation en JSON")
):
    """
    Endpoint unique pour toutes les visualisations 3D.
    *Le parametre de visualisation JSON doit ressembler a quelque chose comme :

    1.Pour ACP ----> {"colonne_couleur":"AGE","titre":"Visualisation Interactive"}
    2.Pour UMAP----> {"colonne_couleur":"AGE","titre":"Visualisation Interactive","n_voisins":15,"dist_min":0.1}
    3.Pour TSNE----> {"colonne_couleur":"AGE","titre":"Visualisation Interactive","perplexite":8,"n_voisins":15,"dist_min":0.1}

    Args:
        requete (Request): La requête HTTP entrante.
        methode (Literal): Méthode de réduction de dimensionnalité.
        fichier (UploadFile): Le fichier téléversé contenant les données.
        parametres_json (str): Paramètres de visualisation en JSON.
    """
    donnees = obtenir_df_depuis_televersement(fichier)
    try:
        parametres = ParametresVisualisation.model_validate_json(parametres_json)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erreur de validation des paramètres: {e}")

    # Appel du service d'orchestration en forçant n_composantes = 3
    contenu_html, methode_utilisee = creer_graphique_interactif(donnees, methode, 3, parametres)
    
    # Stockage du fichier HTML
    url_rendu = sauvegarder_rendu_html(contenu_html, str(requete.base_url))
    
    return ReponseVisualisation(
        statut="success",
        methode_utilisee=methode_utilisee,
        message=f"Rendu 3D {methode_utilisee.upper()} créé avec succès.",
        url_rendu=url_rendu,
        contenu_html=contenu_html
    )