import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
from nltk.corpus import stopwords
import nltk


def create_word_cloud(
    df: pd.DataFrame, 
    colonne_texte: str, 
    background_color: str, 
    max_words: int, 
    width: int, 
    height: int, 
    stopwords_lang: str = None
) -> plt.Figure:
    """
    Génère une figure Matplotlib contenant le nuage de mots.
    """
    
    # 1. Préparation du Texte
    if colonne_texte not in df.columns:
        # Devrait déjà être géré par l'API, mais bonne pratique
        raise KeyError(f"La colonne '{colonne_texte}' est introuvable dans les données.")

    # Concaténer tout le texte en une seule chaîne, en gérant les valeurs manquantes
    text_data = ' '.join(df[colonne_texte].astype(str).dropna().tolist())
    
    # 2. Définition des Stop Words (Mots Vides)
    custom_stopwords = set()
    if stopwords_lang and stopwords_lang in nltk.corpus.stopwords.fileids():
        custom_stopwords = set(stopwords.words(stopwords_lang))
    
    # 3. Génération du Nuage de Mots
    wc = WordCloud(
        background_color=background_color,
        max_words=max_words,
        width=width,
        height=height,
        stopwords=custom_stopwords,
        contour_color='steelblue',
        collocations=False  # Pour des nuages plus propres
    )
    
    # Créer le nuage à partir du texte
    wc.generate(text_data)

    # 4. Création et Configuration de la Figure Matplotlib
    fig, ax = plt.subplots(figsize=(width / 100, height / 100)) # Ajuster la taille en pouces
    ax.imshow(wc, interpolation='bilinear')
    ax.axis("off") # Cacher les axes

    # Retourner la figure Matplotlib pour l'encodage en Base64
    return fig