def calculer_points(points_base: float, duree_minutes: int, intensite: str) -> float:
    """
    Calcule les points Défi Santé selon la durée et l'intensité.
    Points de base = points par tranche de 30 minutes à intensité moyenne.
    """
    multiplicateur_intensite = {
        "faible": 0.75,
        "moyenne": 1.0,
        "intense": 1.25,
    }

    mult = multiplicateur_intensite.get(intensite, 1.0)
    # Points proportionnels à la durée (base = 30 min)
    points = points_base * (duree_minutes / 30) * mult
    return round(points, 2)
