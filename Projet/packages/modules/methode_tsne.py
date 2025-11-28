#methode_tsne.py
from typing import Union
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE

class MethodeTSNE:
    def __init__(self, df: Union[pd.DataFrame, np.ndarray, str]):
        self.df = df

    def tsne_reduction(self, nombre_de_dimension = 1, perplexity=5) -> np.ndarray:
        tsne = TSNE(n_components=nombre_de_dimension, perplexity=perplexity)
        X_tsne = tsne.fit_transform(self.df)
        return X_tsne
 #mes parametres : nombre_de_dimension, perplexity=5 par defaut       