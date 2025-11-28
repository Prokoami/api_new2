from typing import Union
import pandas as pd
import numpy as np
from packages.modules.methode_acp import MethodeACP
from packages.modules.methode_tsne import MethodeTSNE
from packages.modules.methode_umap import MethodeUMAP
from packages.modules.auto_selector import AutoSelector
import plotly.express as px

class Visualisation_3D:
    def __init__(self, df: Union[pd.DataFrame, np.ndarray, str]):
        self.axes = 3
        self.df = df
    
    def visualisation_3D_acp(self):
        apc_3d_instance = MethodeACP(self.df)

        X_acp = apc_3d_instance.acp_reduction(nombre_dimenssion=self.axes)
        
        df_acp = pd.DataFrame(X_acp, columns=["PC_1","PC_2","PC_3"])
        
        df_acp["age"] = self.df["age"].values

        title = "Méthode de réduction de données ACP en 3D(Interactif)."
        
        label = {"x": "PC_1: Composant 1", "y": "PC_2: Composant 2", "z": "PC_3: Composant 3"}

        # Graphiques interactifs 3D
        fig = px.scatter_3d(df_acp,
                x= X_acp[:, 0],
                y= X_acp[:, 1],
                z= X_acp[:, 2],
                color= "age",
                title=title,
                labels=label
                )
        
        #fig.write_image("/home/adama/visualdata/Projet_stage/tests/resultats/img/3D/Reduction_ACP_3D.png", format="png")
        #fig.write_html("/home/adama/visualdata/Projet_stage/tests/resultats/html/3D/Reduction_ACP_3D.html")
        return fig.to_html()
    def visualisation_3D_tsne(self):
        tsne_3d_instance = MethodeTSNE(self.df)

        X_tsne = tsne_3d_instance.tsne_reduction(nombre_de_dimension=self.axes)
        
        df_tsne = pd.DataFrame(X_tsne, columns=["t-SNE_1","t-SNE_2","t-SNE_3"])
        
        df_tsne["age"] = self.df["age"].values

        title = "Méthode de réduction de données avec t-SNE en 3D(Iteratif)."
        
        label = {"x": "t-SNE_1: Composant 1", "y": "t-SNE_2: Composant 2", "z": "t-SNE_3: Composant 3"}

        # Graphiques interactifs 3D
        fig = px.scatter_3d(df_tsne,
                x= X_tsne[:, 0],
                y= X_tsne[:, 1],
                z= X_tsne[:, 2],
                color= "age",
                title=title,
                labels=label
                )
        
        #fig.write_image("/home/adama/visualdata/Projet_stage/tests/resultats/img/3D/Reduction_t-SNE_3D.png", format="png")
        #fig.write_html("/home/adama/visualdata/Projet_stage/tests/resultats/html/3D/Reduction_t-SNE_3D.html")
        return fig.to_html()
    def visualisation_3D_umap(self):
        umap_3d_instance = MethodeUMAP(self.df)

        X_umap = umap_3d_instance.umap_reduction(nombre_de_dimension=self.axes)
        
        df_umap = pd.DataFrame(X_umap, columns=["UMAP_1","UMAP_2","UMAP_3"])
        
        df_umap["age"] = self.df["age"].values

        title = "Méthode de réduction de données avec UMAP en 3D(Iteratif)."
        
        label = {"x": "UMAP_1: Composant 1", "y": "UMAP_2: Composant 2", "z": "UMAP_3: Composant 3"}

        # Graphiques interactifs 3D
        fig = px.scatter_3d(df_umap,
                x= X_umap[:, 0],
                y= X_umap[:, 1],
                z= X_umap[:, 2],
                color= "age",
                title=title,
                labels=label
                )
        
        #fig.write_image("/home/adama/visualdata/Projet_stage/tests/resultats/img/3D/Reduction_UMAP_3D.png", format="png")
        #fig.write_html("/home/adama/visualdata/Projet_stage/tests/resultats/html/3D/Reduction_UMAP_3D.html")
        return fig.to_html()

    def visualisation_automatique(self):
        auto = AutoSelector(self.df, nombre_de_dimension=3)
        methode = auto.detecter_methode()
        match methode:
            case 'pca':
                return self.visualisation_3D_acp()
            case 'tsne':
                return self.visualisation_3D_tsne()
            case 'umap':
                return self.visualisation_3D_umap()