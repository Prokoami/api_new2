import pandas as pd
import csv
from io import StringIO

def read_uploaded_file(file):
    """Lit un fichier CSV ou Excel uploadé via FastAPI et retourne un DataFrame."""
    try:
        content = file.file.read()

        if file.filename.endswith('.csv'):
            # Gestion des encodages
            try:
                decoded_content = content.decode('utf-8')
            except UnicodeDecodeError:
                decoded_content = content.decode('latin-1')

            # Détection du séparateur
            sample = decoded_content[:1000]
            try:
                sep = csv.Sniffer().sniff(sample).delimiter
            except Exception:
                sep = ','

            return pd.read_csv(StringIO(decoded_content), sep=sep)

        elif file.filename.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file.file)

        else:
            raise ValueError("Format de fichier non supporté (seulement CSV ou Excel).")

    except Exception as e:
        raise Exception(f"Erreur de lecture du fichier: {e}")
