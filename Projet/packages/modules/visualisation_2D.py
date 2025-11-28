from typing import Union
import pandas as pd
import numpy as np
from packages.modules.methode_acp import MethodeACP
from packages.modules.methode_tsne import MethodeTSNE
from packages.modules.methode_umap import MethodeUMAP
from packages.modules.auto_selector import AutoSelector
import plotly.express as px

class Visualisation_2D:
    def __init__(self, df: Union[pd.DataFrame, np.ndarray, str]):
        self.axes = 2
        self.df = df
    
    def visualisation_2D_acp(self):
        apc_2d_instance = MethodeACP(self.df)

        X_acp = apc_2d_instance.acp_reduction(nombre_dimenssion= self.axes)

        title = "Méthode de réduction de données avec ACP en 2D."
        
        label = {"x": "PC_1", "y": "PC_2"}
        
        df_acp = pd.DataFrame(X_acp, columns=["PC_1: Composante 1", "PC_2: Composante 2"])
        
        df_acp["age"] = self.df["age"].values

        fig = px.scatter(df_acp,
                x="PC_1: Composante 1",
                y= "PC_2: Composante 2",
                color= "age",
                title=title,
                labels=label
            )
        
        #fig.write_image("/home/adama/visualdata/Projet_stage/tests/resultats/img/2D/Reduction_ACP_2D.png", format="png")
        #fig.write_html("/home/adama/visualdata/Projet_stage/tests/resultats/html/2D/Reduction_ACP_2D.html")
        return fig.to_html()
    
    def visualisation_2D_tsne(self):
        chargeur_tsne = MethodeTSNE(self.df)
        X_tsne = chargeur_tsne.tsne_reduction(nombre_de_dimension=self.axes)
        title = "Méthode de réduction de données avec t-SNE en 2D."
        
        label = {"x": "t-SNE_1", "y": "t-SNE_2"}
        
        df_tsne = pd.DataFrame(X_tsne, columns=["t-SNE_1", "t-SNE_2"])
        
        df_tsne["age"] = self.df["age"].values

        fig = px.scatter(df_tsne,
                x="t-SNE_1",
                y= "t-SNE_2",
                color= "age",
                title=title,
                labels=label
            )
        #fig.write_image("/home/adama/visualdata/Projet_stage/tests/resultats/img/2D/Reduction_t-SNE_2D.png", format="png")
        #fig.write_html("/home/adama/visualdata/Projet_stage/tests/resultats/html/2D/Reduction_t-SNE_2D.html")
        return fig.to_html()

    def visualisation_2D_umap(self):
        chargeur_umap = MethodeUMAP(self.df)
        
        X_umap = chargeur_umap.umap_reduction(nombre_de_dimension=self.axes)
        
        title = "Méthode de réduction de données avec UMAP en 2D."
        
        label = {"x": "UMAP_1", "y": "UMAP_2"}
        
        df_umap = pd.DataFrame(X_umap, columns=["UMAP_1", "UMAP_2"])
        
        df_umap["age"] = self.df["age"].values

        fig = px.scatter(df_umap,
                x="UMAP_1",
                y= "UMAP_2",
                color= "age",
                title=title,
                labels=label
            )
        #fig.write_image("/home/adama/visualdata/Projet_stage/tests/resultats/img/2D/Reduction_UMAP_2D.png", format="png")
        #fig.write_html("/home/adama/visualdata/Projet_stage/tests/resultats/html/2D/Reduction_UMAP_2D.html")
        return fig.to_html()

    def visualisation_automatique(self):
        auto = AutoSelector(self.df, nombre_de_dimension=2)
        methode = auto.detecter_methode()
        match methode:
            case 'pca':
                return self.visualisation_2D_acp()
            case 'tsne':
                return self.visualisation_2D_tsne()
            case 'umap':
                return self.visualisation_2D_umap()