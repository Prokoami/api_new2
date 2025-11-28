"""
Module : auto_selector.py
But : Détecter automatiquement la meilleure méthode de réduction de dimension (ACP, t-SNE, UMAP)
selon la nature et la structure du jeu de données.
"""

from typing import Union
import pandas as pd
import numpy as np
from sklearn.metrics import pairwise_distances
from sklearn.preprocessing import StandardScaler
import warnings

# Import des méthodes de réduction
from packages.modules.methode_acp import MethodeACP
from packages.modules.methode_tsne import MethodeTSNE
from packages.modules.methode_umap import MethodeUMAP

warnings.filterwarnings("ignore")

class AutoSelector:
    def __init__(self, df: Union[pd.DataFrame, np.ndarray], nombre_de_dimension: int, sample_size: int = 1000):
        """
        :param df: Jeu de données (DataFrame ou ndarray)
        :param sample_size: Taille maximale de l'échantillon pour l'évaluation rapide
        """
        self.df = pd.DataFrame(df) if isinstance(df, np.ndarray) else df
        self.sample_size = min(sample_size, len(self.df))
        self.nombre_de_dimension = nombre_de_dimension

    def _echantillonner(self):
        """Échantillonne une portion du jeu de données pour accélérer la détection."""
        return self.df.sample(n=self.sample_size, random_state=42).reset_index(drop=True)

    def _calculer_score_linearite(self, df_num: pd.DataFrame) -> float:
        """Calcule un score de linéarité moyen basé sur la corrélation absolue."""
        corr = abs(df_num.corr()).values
        moyenne_corr = np.mean(corr[np.triu_indices_from(corr, k=1)])
        return moyenne_corr

    def _score_structure(self, X_proj: np.ndarray, X_original: np.ndarray) -> float:
        """
        Calcule une mesure de qualité structurelle entre distances dans l’espace original et réduit.
        Plus la corrélation est proche de 1, plus la structure est bien préservée.
        """
        idx = np.random.choice(len(X_original), size=min(300, len(X_original)), replace=False)
        dist_orig = pairwise_distances(X_original[idx])
        dist_proj = pairwise_distances(X_proj[idx])
        corr = np.corrcoef(dist_orig.flatten(), dist_proj.flatten())[0, 1]
        return corr

    def detecter_methode(self) -> str:
        """
        Détermine automatiquement la meilleure méthode selon :
          - le nombre de colonnes
          - la linéarité
          - un score de préservation de la structure après réduction
        """
        df_sample = self._echantillonner()
        df_num = df_sample.select_dtypes(include=[np.number])
        X = StandardScaler().fit_transform(df_num.values)

        n, p = X.shape
        score_linearite = self._calculer_score_linearite(df_num)

        print(f"Données : {n} échantillons, {p} variables")
        print(f"Score de linéarité moyenne : {score_linearite:.3f}")

        # Étape 1 — Choix initial heuristique
        if p <= 20 and score_linearite > 0.6:
            methode = "acp"
        elif (20 < p <= 100 and 0.3 <= score_linearite <= 0.6) or n < 10000:
            methode = "tsne"
        else:
            methode = "umap"

        print(f"Méthode initialement pressentie : {methode.upper()}")

        # Étape 2 — Validation par score de qualité structurelle (test rapide)
        resultats = {}
        try:
            # ACP
            X_acp = MethodeACP(df_num).acp_reduction(nombre_dimenssion=self.nombre_de_dimension)
            resultats["acp"] = self._score_structure(X_acp, X)

            # t-SNE (échantillon plus petit si dataset volumineux)
            X_small = X[: min(700, len(X))]
            X_tsne = MethodeTSNE(pd.DataFrame(X_small)).tsne_reduction(nombre_de_dimension=self.nombre_de_dimension)
            resultats["tsne"] = self._score_structure(X_tsne, X_small)

            # UMAP
            X_umap = MethodeUMAP(df_num).umap_reduction(nombre_de_dimension=2)
            resultats["umap"] = self._score_structure(X_umap, X)
        except Exception as e:
            print(f"Erreur durant l’évaluation structurelle : {e}")

        if resultats:
            meilleure_methode = max(resultats, key=resultats.get)
            print(f"Scores structurels : {resultats}")
            print(f"Méthode sélectionnée : {meilleure_methode.upper()}")
            return meilleure_methode

        return methode