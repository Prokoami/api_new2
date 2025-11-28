
class StringUtils:
    """Classe utilitaire pour les opérations sur les chaînes de caractères."""

    @staticmethod
    def sans_espace(chaine: str) -> str:
        """
        Remplace les espaces par des underscores dans une chaîne de caractères.

        Args:
            chaine (str): Chaîne de caractères pouvant contenir des espaces.

        Returns:
            str: Chaîne de caractères avec les espaces remplacés par des underscores.
        
        Example:
        >>> chaine = "colonne avec espace"
        >>> chaine_modifier = sans_espace(chaine)
        >>> print(chaine_modifier)
        'colonne_avec_espace'
        """
        return chaine.replace(" ", "_")
