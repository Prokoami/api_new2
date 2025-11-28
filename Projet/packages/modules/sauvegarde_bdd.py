import pandas as pd
from sqlalchemy import create_engine
from typing import Literal

class SauvegardeBDD:
    """
    Classe pour sauvegarder un DataFrame Pandas dans une base de données.
    Utilise SQLAlchemy pour la connexion.
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialise avec le DataFrame à sauvegarder.

        Args:
            df (pd.DataFrame): Le DataFrame contenant les données.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("L'entrée doit être un DataFrame pandas.")
        self.df = df

    def sauvegarder_en_sqlite(
        self, 
        chemin_bdd: str, 
        nom_table: str, 
        si_existe: Literal['fail', 'replace', 'append'] = 'fail'
    ):
        """
        Sauvegarde le DataFrame dans une base de données SQLite.

        Args:
            chemin_bdd (str): Le chemin vers le fichier de la base de données 
                              (ex: "storage/ma_base.db").
            nom_table (str): Le nom de la table où enregistrer les données.
            si_existe (Literal): Comportement si la table existe déjà:
                - 'fail': (Défaut) Lève une erreur.
                - 'replace': Supprime l'ancienne table et la remplace.
                - 'append': Ajoute les données à la table existante.
        
        Returns:
            dict: Un message de succès.
        """
        try:
            # Crée l'URL de connexion pour SQLite
            # 'sqlite:///storage/ma_base.db'
            url_connexion = f"sqlite:///{chemin_bdd}"
            
            # Crée le "moteur" de base de données
            moteur = create_engine(url_connexion)
            
            print(f"[INFO] Sauvegarde de {len(self.df)} lignes dans la table '{nom_table}' de '{chemin_bdd}'...")

            # Utilise pandas pour écrire dans la base de données
            self.df.to_sql(
                nom_table, 
                con=moteur, 
                if_exists=si_existe,
                index=False # Ne pas inclure l'index pandas comme colonne
            )
            
            message = f"Succès : {len(self.df)} lignes sauvegardées dans la table '{nom_table}'."
            print(f"[INFO] {message}")
            return {"status": "success", "message": message}

        except Exception as e:
            # Gérer les erreurs (ex: la table existe déjà et si_existe='fail')
            print(f"[ERREUR] Échec de la sauvegarde BDD : {e}")
            raise e