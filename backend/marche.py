"""
Medianes DVF par quartier de Toulon.

Difficulte a anticiper : le fichier DVF ne contient PAS de colonne « quartier ».
Il contient la commune, la section cadastrale et les coordonnees (latitude, longitude).
Il faut donc rattacher chaque vente a un quartier, par exemple :
- via les IRIS de l'INSEE (decoupage infra-communal, contours publics sur data.gouv.fr),
  en testant dans quel contour tombe chaque point (lat, lon) ;
- ou via une table de correspondance section cadastrale -> quartier, faite a la main
  pour les quartiers cibles (Mourillon, Cap Brun, Saint-Jean-du-Var, Centre, ...).
Documentez le choix dans le README : c'est une question classique du jury.

Le resultat attendu est un petit fichier agrege, versionne (donnees publiques agregees) :
    data/medianes_quartiers.csv   colonnes : quartier, mediane_prix_m2, nb_ventes
"""
import csv
from pathlib import Path

FICHIER = Path(__file__).resolve().parent.parent / "data" / "medianes_quartiers.csv"


def medianes() -> dict[str, dict]:
    """{quartier: {"mediane_prix_m2": float, "nb_ventes": int}} ; {} si le fichier n'existe pas."""
    if not FICHIER.exists():
        return {}
    with FICHIER.open(encoding="utf-8") as f:
        return {
            ligne["quartier"]: {
                "mediane_prix_m2": float(ligne["mediane_prix_m2"]),
                "nb_ventes": int(ligne["nb_ventes"]),
            }
            for ligne in csv.DictReader(f)
        }


def mediane_quartier(quartier: str | None) -> float | None:
    """Mediane DVF du quartier en EUR/m2, None si quartier inconnu.
    TODO : gerer les variantes d'ecriture ("Le Mourillon" / "mourillon" / "MOURILLON")."""
    if not quartier:
        return None
    m = medianes().get(quartier)
    return m["mediane_prix_m2"] if m else None
