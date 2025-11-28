from typing import Union
import pandas as pd
import numpy as np
#from packages.modules.numeric_data import Numeric_data


class Netoyage:
    def __init__(self, df: Union[pd.DataFrame, np.ndarray, str]):
        self.df = df
    
    def gerer_les_valeurs_manquantes(self, strategy: str = 'mean', column: str = None) -> pd.DataFrame:
        """
        Gère les valeurs manquantes d'un tableau de données.
        
        Args:
            df (pd.DataFrame) : Le tableau à traiter.
            strategy (str) : La manière dont il faut remplir les valeurs manquantes, la valeur par défaut est `mean` et les valeurs possibles sont: `mean`, `drop`, `median` et `fill`.
            column (str) : Les colonnes sur lesquelles doit se faire le remplissage des valeurs manquantes.
            
        Return:
            pd.DataFrame: Une nouvelle tableau sans des valeurs manquantes s'il y avait.
        """
        if not isinstance(self.df, pd.DataFrame):
            print("L'opération n'est applicable qu'aux DataFrames.")
            return self.df

        df_copy = self.df.copy() # On travaille sur une copie pour ne pas modifier l'original

        if strategy == 'drop':
            df_copy.dropna(inplace=True)
            print("Les lignes avec des valeurs manquantes ont été supprimées.")
        else:
            columns_to_handle = [column] if column else df_copy.select_dtypes(include=np.number).columns
            if not columns_to_handle.empty:
                for col in columns_to_handle:
                    if strategy == 'mean':
                        fill_value = df_copy[col].mean()
                    elif strategy == 'median':
                        fill_value = df_copy[col].median()
                    elif strategy == 'fill':
                        fill_value = 0
                    else:
                        print("Stratégie de changement non valide.")
                        return self.df
                    df_copy[col].fillna(fill_value, inplace=True)
                    print(f"\nValeurs manquantes de la colonne '{col}' changée avec la stratégie '{strategy}'.\n")
            else:
                print("\nAucune colonne numérique trouvée pour le changement.\n")
        return df_copy
    
    def gerer_les_valeurs_duplicates(self) -> pd.DataFrame:
        """
        Supprime les lignes dupliquées d'un tableau s'il y a.
        
        Args:
            df (pd.DataFrame) : Prend le tableau des données.
        
        Return:
            pd.DataFrame: Renvoi un nouveau tableau sans des lignes dupliquées s'il y avant au départ.
        """
        
        if not isinstance(self.df, pd.DataFrame):
            print("L'opération n'est applicable qu'aux DataFrames.")
            return self.df

        initial_rows = len(self.df)
        df_copy = self.df.drop_duplicates().copy()
        dropped_rows = initial_rows - len(df_copy)
        print(f"{dropped_rows} lignes dupliquées ont été supprimées.")
        return df_copy