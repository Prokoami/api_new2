
"""Import de bibliothèque `pandas`"""

import pandas as pd
import numpy as np

class CleanDataframeForJson:
    """Cette classe nettoie DataFrame
    """
    def clean_dataframe_for_json(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie un DataFrame pour le rendre compatible JSON :
        - remplace NaN, inf et -inf par None
        """
        if df.isnull().values.any():
            print("[INFO] NaN détectés dans les colonnes suivantes :")
            print(df.isnull().sum()[df.isnull().sum() > 0])
        df = df.replace([float('inf'), float('-inf')], None)
        df = df.replace({np.nan: None})
        df = df.where(pd.notnull(df), None)
        return df
