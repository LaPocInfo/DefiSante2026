def calculer_points(points_base: float, duree_minutes: int, intensite: str) -> float:
   
    multiplicateur_intensite = {
        "faible": 0.75,
        "moyenne": 1.0,
        "intense": 1.25,
    }

    mult = multiplicateur_intensite.get(intensite, 1.0)
   
    points = points_base * (duree_minutes / 30) * mult
    return round(points, 2)
