from typing import Union
import pandas as pd
import numpy as np

class Analyse:
    """
    Analyse des données chargées dans la classe `DataLoad` depuis le fichier `loading.py`.
    """
    def summarize(self, data: Union[pd.DataFrame, np.ndarray, str] = None) -> dict:
        """
        Retourne un résumé statistique de la donnée chargée.
        
        Args:
            data (pd.DataFrame | np.ndarray | str) : Les données à résumer (valeur par défaut est `None`).
            
        Return:
            dict: L'ensemble des informations résumé dans un dictionnaire.
        """
        if data is None:
            raise ValueError("Aucune donnée chargée.")

        if isinstance(data, pd.DataFrame):
            return {
                'shape': data.shape,
                'columns': list(data.columns),
                'types': data.dtypes.astype(str).to_dict(),
                'missing_values': data.isnull().sum().to_dict(),
                'duplicates': data.duplicated().sum()
            }
        elif isinstance(data, np.ndarray):
            return {
                'type': 'image',
                'shape': data.shape,
                'dtype': str(data.dtype)
            }
        elif isinstance(data, str):
            return {
                'type': 'text',
                'length': len(data),
                'lines': data.count('\n') + 1
            }
        else:
            raise TypeError("Type de données non supporté pour le résumé.")

    def get_descriptive_stats(self,df: pd.DataFrame) -> pd.DataFrame:
        """
        Retourne des statistiques descriptives pour les colonnes numériques et catégorielles d'un DataFrame.
        
        Args:
            df (pd.DataFrame) : Prend un DataFrame sur lequel l'on verra des informations statistiques.
        
        Return:
            pd.DataFrame: Retourne un DataFrame montrant de façon distinct les données catégorielles et numérique.
        """
    
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Les données ne sont pas tabulaires (DataFrame).")
        
        numeric_stats = df.describe(include=np.number).transpose()
        categorical_stats = df.describe(include='object').transpose()
  
        # --- FIX ROBUSTESSE CONTRE L'ERREUR "No objects to concatenate" ---
        # Crée une liste contenant uniquement les DataFrames qui NE SONT PAS vides.
        stats_list = []
        
        if not numeric_stats.empty:
            stats_list.append(numeric_stats)
        
        if not categorical_stats.empty:
            stats_list.append(categorical_stats)
            
        if not stats_list:
            # Si aucune colonne n'a pu être décrite, renvoyer un DataFrame informatif
            return pd.DataFrame({'Statut': ['Aucune colonne à décrire trouvée.']})

        # Concaténation sécurisée (la fonction corrigée n'échouera plus ici)
        return pd.concat(stats_list)