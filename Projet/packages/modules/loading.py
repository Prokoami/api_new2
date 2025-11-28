"""_summary_

Raises:
    pd.errors.ParserError: _description_
    pd.errors.ParserError: _description_
    ValueError: _description_
    FileNotFoundError: _description_
    Exception: _description_

Returns:
    _type_: _description_
    """
# data_loader/loading.py
import os
import json
import yaml
import sqlite3
import pandas as pd
import requests
import io
from pathlib import Path
import numpy as np

from PIL import Image
from typing import Union, Optional
from pydantic import BaseModel
from pydantic import field_serializer, field_validator

# import pyarrow.parquet as pq
# from pathlib import Path

class DataLoader(BaseModel):
    df: Optional[pd.DataFrame] = None
    model_config = {"arbitrary_types_allowed": True,"str_max_length": None}

    @field_serializer("df")
    def serialize_df(self, df, _info):
        return df.to_dict(orient="records") if df is not None else None

    @field_validator("df", mode="before")
    def ensure_df(cls, v):
        if isinstance(v, list):
            return pd.DataFrame(v)
        return v

    def load(
        self,
        file_path: str,
        sql_query: str = None,
        db_path: str = None,
        image_as_dataframe: bool = False) -> Union[pd.DataFrame, np.ndarray, str]:
        """
        Charge des données en fonction des fichiers chargés (locaux ou distants).
        ... (args et returns inchangés) ...
        """
        
        # --- MODIFICATION ---
        # Correction du chemin Windows (conservée)
        if "\\" in file_path:
            file_path = "/".join(file_path.split("\\"))

        # --- AJOUT ---
        # Détection si le chemin est une URL
        is_url = file_path.startswith("http://") or file_path.startswith("https://")
        
        # --- AJOUT : Sécurité ---
        # Valider que le chemin local est sécurisé
        if not is_url:
            PROJECT_ROOT = Path(__file__).resolve().parents[3] # Remonte au dossier 'Projet'
            file_path_abs = Path(file_path).resolve()
            
            try:
                file_path_abs.relative_to(PROJECT_ROOT)
            except ValueError:
                raise ValueError("Accès non autorisé : le chemin spécifié est en dehors du répertoire de travail.")

        # --- AJOUT ---
        # Obtenir le type de fichier (suffixe) en utilisant Pathlib
        try:
            file_type = Path(file_path).suffix.lower().replace('.', '')
        except Exception as e:
            raise ValueError(f"Impossible de déterminer le type de fichier depuis le chemin : {e}")

        self.format = file_type

        try:
            # ==========================================================
            # --- CAS 1 : Le chemin est une URL distante ---
            # ==========================================================
            if is_url:
                print(f"Chargement des données depuis une URL distante : {file_path}")

                if file_type in ['csv', 'xls', 'xlsx']:
                    # --- MODIFICATION ---
                    # Pandas peut lire les CSV et Excel directement depuis une URL
                    # C'est la méthode la plus simple et la plus efficace.
                    if file_type == 'csv':
                        self.df = pd.read_csv(file_path)
                    elif file_type in ['xls', 'xlsx']:
                        self.df = pd.read_excel(file_path)
                
                else:
                    # --- AJOUT ---
                    # Pour les autres types (JSON, TXT, etc.), nous devons
                    # télécharger le contenu d'abord avec 'requests'.
                    try:
                        r = requests.get(file_path)
                        r.raise_for_status() # Lève une erreur si 404, 500, etc.
                    except requests.exceptions.RequestException as e:
                        raise Exception(f"Erreur de téléchargement de l'URL '{file_path}': {e}")

                    if file_type == 'json':
                        data = r.json() # Décode le JSON depuis la réponse
                        self.df = pd.json_normalize(data)
                    
                    elif file_type in ['yaml', 'yml']:
                        data = yaml.safe_load(r.content) # Lit depuis les bytes
                        self.df = pd.json_normalize(data)
                    
                    elif file_type == 'txt':
                        self.df = r.text # Renvoie le texte brut
                    
                    # Note : Parquet, SQL, Image depuis une URL ne sont pas implémentés
                    # car ils nécessitent une logique plus complexe (ex: authentification)
                    else:
                        raise ValueError(f"Format de fichier distant non supporté : '{file_type}'")

            # ==========================================================
            # --- CAS 2 : Le chemin est un fichier local ---
            # ==========================================================
            elif os.path.exists(file_path):
                print(f"Chargement des données depuis un chemin local : {file_path}")
                
                # --- MODIFICATION ---
                # Votre logique de détection de séparateur pour CSV (conservée)
                if file_type == 'csv':
                    sepateur_valeurs = [";", "|", "\t", ","]
                    index_sepateur = 0
                    
                    # Lire la première ligne pour deviner le séparateur
                    with open(file=file_path, encoding="utf-8") as contenu_du_fichier:
                        premiere_ligne = contenu_du_fichier.readline()
                    
                    for i, sep in enumerate(sepateur_valeurs):
                        if sep in premiere_ligne:
                            index_sepateur = i
                            break # Trouvé !
                        
                    try:
                        self.df = pd.read_csv(file_path, sep=sepateur_valeurs[index_sepateur])
                    except pd.errors.ParserError:
                        raise pd.errors.ParserError(f"Erreur de parsing CSV. Assurez-vous que le séparateur est l'un de : {sepateur_valeurs}")
                
                # Logique pour les autres fichiers locaux (conservée)
                elif file_type in ['xls', 'xlsx']:
                    self.df = pd.read_excel(file_path)
                elif file_type == 'json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.df = pd.json_normalize(data)
                elif file_type in ['yaml', 'yml']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    self.df = pd.json_normalize(data)
                elif file_type == 'parquet':
                    self.df = pd.read_parquet(file_path)
                elif file_type == 'sql' and db_path and sql_query:
                    conn = sqlite3.connect(db_path)
                    self.df = pd.read_sql_query(sql_query, conn)
                    conn.close()
                elif file_type in ['png', 'jpg', 'jpeg']:
                    image = Image.open(file_path).convert('RGB')
                    img_array = np.array(image)
                    if image_as_dataframe:
                        h, w, c = img_array.shape
                        pixels = img_array.reshape(-1, c)
                        coords = [(x, y) for y in range(h) for x in range(w)]
                        self.df = pd.DataFrame(pixels, columns=["R", "G", "B"])
                        self.df["x"] = [coord[0] for coord in coords]
                        self.df["y"] = [coord[1] for coord in coords]
                    else:
                        self.df = img_array
                elif file_type == 'txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.df = f.read()
                else:
                    raise ValueError(f"Format de fichier local non supporté : '{file_type}'")
            
            else:
                # --- MODIFICATION ---
                # Si ce n'est ni une URL ni un fichier local existant
                raise FileNotFoundError(f"Erreur : Le fichier à l'adresse '{file_path}' est introuvable.")

            # Si tout s'est bien passé
            print(f"\nFichier '{Path(file_path).name}' chargé avec succès.")
            return self.df
        
        # --- MODIFICATION ---
        # Gestion des erreurs plus spécifique
        except FileNotFoundError as e:
            raise e # Laisser FileNotFoundError se propager
        except pd.errors.ParserError as e:
            raise e # Laisser ParserError se propager
        except Exception as e:
            # Attrape toutes les autres erreurs (ex: Erreur de téléchargement, format non supporté)
            raise Exception(f"Une erreur est survenue lors du chargement : {e}")