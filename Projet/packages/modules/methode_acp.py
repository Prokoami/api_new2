#methode_acp.py

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Union
import numpy as np
import pandas as pd


class MethodeACP:
    """Réduction de dimenssion avec l'ACP."""
    
    def __init__(self, df: Union[pd.DataFrame, np.ndarray, str]):
        self.df = df
    
    def acp_reduction(self, nombre_dimenssion = 1):

            normalisation = StandardScaler()

            X_normaliser = normalisation.fit_transform(self.df)
            
            acp = PCA(n_components=nombre_dimenssion) # n_components mentionne les axes (dimensions)

            X_acp = acp.fit_transform(X_normaliser)

            X_reconstructed = acp.inverse_transform(X_acp)

            return X_acp
    