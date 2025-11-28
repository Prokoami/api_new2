# === Étape 1: Définir l'image de base ===
# Utilisation d'une image Python officielle et légère.
# Spécifier une version (ex: 3.9) garantit la reproductibilité.
FROM python:3.9-slim

# === Étape 2: Définir l'environnement ===
# Définir le répertoire de travail dans le conteneur.
# Toutes les commandes suivantes s'exécuteront à partir de ce chemin.
WORKDIR /app

# Empêche Python d'écrire des fichiers .pyc sur le disque.
ENV PYTHONDONTWRITEBYTECODE 1
# Assure que la sortie de Python est affichée immédiatement dans les logs du conteneur.
ENV PYTHONUNBUFFERED 1

# === Étape 3: Installer les dépendances ===
# Copier uniquement le fichier des dépendances pour profiter du cache de Docker.
# Cette couche ne sera reconstruite que si requirements.txt change.
COPY requirements.txt .

# Installer les dépendances Python.
# --no-cache-dir réduit la taille de l'image.
# --upgrade pip s'assure que nous avons la dernière version de pip.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# === Étape 4: Copier le code de l'application ===
# Copier le reste des fichiers de l'application dans le répertoire de travail.
COPY . .

# === Étape 5: Exécuter l'application ===
# Exposer le port 8000 pour que le conteneur puisse recevoir du trafic.
EXPOSE 8000

# Commande pour démarrer le serveur de production Gunicorn.
# Il gère les workers Uvicorn pour exécuter l'application FastAPI.
# L'option -b 0.0.0.0:8000 est cruciale pour rendre le serveur accessible depuis l'extérieur du conteneur.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "api:app"]