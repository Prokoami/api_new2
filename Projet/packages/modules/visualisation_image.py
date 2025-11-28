import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import cv2
import os

class ImageVisualizer:
    """
    Affiche l'/les image(s) chargé depuis un dossier en local.
    
    Attribut:
        image_path (str) : Chemin de l'image à affiché.
    """
    
    def __init__(self, image_path: str):
        """
        Récupère le chemin d'une image.
        
        Une image récupérer par cette classe est chargée en mémoire(buffer).
        
        Args:
            image_path(str) : Le chemin d'une image.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Le fichier {image_path} est introuvable")
        self.image_path = image_path
        self.image = Image.open(image_path).convert("RGB")
        self.image_array = np.array(self.image)

    def show_image(self, title="Image originale"):
        """
        Affichage simple de l'image
        
        Args:
            title(str) : Le titre de l'image charger.
        """
        plt.imshow(self.image)
        plt.axis("off")
        plt.title(title)
        plt.show()

    # def show_multiple_image(self, images, titles=None):
    #     """Affichage de plusieurs images côte à côte"""
    #     n = len(images)
    #     plt.figure(figsize=(15, 5))
    #     for i, img in enumerate(images):
    #         plt.subplot(1, n, i+1)
    #         plt.imshow(img)
    #         plt.axis("off")
    #         if titles:
    #             plt.title(titles[i])
    #     plt.show()

    def histogram_intensity(self):
        """Histogramme des intensités par canal"""
        colors = ("r", "g", "b")
        plt.figure(figsize=(8, 5))
        for i, col in enumerate(colors):
            hist = cv2.calcHist([self.image_array], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)
        plt.title("Histogramme des intensités (R, G, B)")
        plt.xlabel("Valeurs de pixels")
        plt.ylabel("Fréquence")
        plt.show()

    def heatmap_gray(self):
        """Visualisation en heatmap de l'image en niveaux de gris"""
        gray = cv2.cvtColor(self.image_array, cv2.COLOR_RGB2GRAY)
        plt.imshow(gray, cmap="hot")
        plt.colorbar()
        plt.title("Heatmap (niveaux de gris)")
        plt.show()

    def edges(self):
        """Détection des contours avec Canny"""
        gray = cv2.cvtColor(self.image_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        plt.imshow(edges, cmap="gray")
        plt.title("Contours (Canny)")
        plt.axis("off")
        plt.show()

    def pixel_scatter(self, n_points=5000):
        """Nuage de pixels dans l’espace RGB"""
        pixels = self.image_array.reshape(-1, 3)
        idx = np.random.choice(len(pixels), size=min(n_points, len(pixels)), replace=False)
        sample = pixels[idx]

        fig = plt.figure(figsize=(8, 6))
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(sample[:, 0], sample[:, 1], sample[:, 2],
                   c=sample / 255.0, marker=".")
        ax.set_xlabel("Rouge")
        ax.set_ylabel("Vert")
        ax.set_zlabel("Bleu")
        plt.title("Nuage de pixels (espace RGB)")
        plt.show()