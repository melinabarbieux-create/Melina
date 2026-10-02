"""
Interface commune R&D Vision.

Le Pole Produit appelle evaluer_etat_bien() sans savoir si c'est un CNN ou un LLM multimodal.
"""
from pathlib import Path

import requests


def charger_photos(photos: list[str]) -> list[bytes]:
    """Chemins locaux ou URLs -> contenu brut des images."""
    contenus = []
    for p in photos:
        if p.startswith("http"):
            contenus.append(requests.get(p, timeout=10).content)
        else:
            contenus.append(Path(p).read_bytes())
    return contenus


def evaluer_etat_bien(photos: list[str]) -> dict:
    """
    Analyse les photos d'un bien et estime son etat.

    Returns:
        {
            "etat_general":       "excellent" | "bon" | "correct" | "a_renover",
            "travaux_detectes":   ["peinture", "cuisine", "salle_de_bain", ...],
            "estimation_travaux": "0-5k" | "5-20k" | "20-50k" | ">50k",
            "luminosite":         1-5,
            "score_presentation": 1-10
        }

    Raises:
        ValueError si photos est vide.
    """
    if not photos:
        raise ValueError("Au moins une photo est requise.")
    # TODO : brancher votre approche, par exemple :
    # from vision.llm.evaluate import evaluer_photos_llm
    # return evaluer_photos_llm(charger_photos(photos))
    raise NotImplementedError("Choisissez votre approche dans vision/cnn/ ou vision/llm/")
