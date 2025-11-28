from typing import Union
import pandas as pd
from pandas.api.types import is_numeric_dtype # Vérifie si une déonnée est de type numérique (int, float etc)
import numpy as np

class Numeric_data:
    def __init__(self, df: Union[pd.DataFrame, np.ndarray, str]):
        self.df = df
    
    def num_col(self) -> Union[pd.DataFrame, np.ndarray, str]:
        # Sélection des données de type numérique (int, float etc) dans un dictionnaire
        data = {col: self.df[col] for col in self.df.columns if is_numeric_dtype(self.df[col])}
        return pd.DataFrame(data=data)