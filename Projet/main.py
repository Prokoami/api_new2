# main.py

# Importez les classes et fonctions du paquet packages
from packages.modules.loading import DataLoader
from packages.modules.netoyage import handle_missing_values, handle_duplicates
from packages.modules.analysis import Analyse
from packages.modules.visualisation_image import ImageVisualizer

import pandas as pd


def main():
    """
    Fonction principale interactive pour charger et nettoyer des données en local.
    """
    # 1. Demander à l'utilisateur de fournir le chemin absolu du fichier
    path = input("Veuillez entrer le chemin absolu du fichier à charger : ")

    print(f"\nVous avez saisi : {path}")

    try:
        # 2. Charger les données avec DataLoader
        dataloader = DataLoader()
        df = dataloader.load(path)

        if not isinstance(df, pd.DataFrame):
            print("Le fichier chargé n'est pas un DataFrame. Le script de nettoyage ne peut pas continuer.")
            return

        print("\n--- DataFrame Original ---")
        print(df.head())
        print(f"\nDimensions initiales : {df.shape}")
        print(f"Valeurs manquantes initiales : {df.isnull().sum().sum()}")
        print(f"Lignes dupliquées initiales : {df.duplicated().sum()}")

        df_nettoye = df.copy()

        # 3. Nettoyage interactif
        # 3.1 Gérer les valeurs manquantes
        supprimer_na = input("\nVoulez-vous supprimer les lignes contenant des valeurs manquantes ? (oui/non) : ").lower()
        if supprimer_na == 'oui':
            df_nettoye = handle_missing_values(df_nettoye, strategy='drop')

        # 3.2 Gérer les doublons
        supprimer_doublons = input("Voulez-vous supprimer les lignes dupliquées ? (oui/non) : ").lower()
        if supprimer_doublons == 'oui':
            df_nettoye = handle_duplicates(df_nettoye)

        print("\n--- DataFrame Nettoyé ---")
        print(df_nettoye.head())
        print(f"\nDimensions finales : {df_nettoye.shape}")

    except Exception as e:
        print(f"\nUne erreur est survenue : {e}")

if __name__ == "__main__":
    main()
