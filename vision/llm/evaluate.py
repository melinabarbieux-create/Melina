"""
Piste LLM multimodal : analyse des photos par un modele qui lit les images.

Passez par backend.llm.generer(..., images=[...], schema=...) :
- en P2 : Gemini via Vertex AI (multimodal nativement) ;
- en P3 : un modele ouvert multimodal servi par Ollama (ex. gemma3, qwen2.5vl), sans changer ce code.

Conseil cout : 4 photos maximum par bien, redimensionnees (1024 px de large suffit).
Mesurez precision, latence et cout dans APPROACH.md.
"""
from typing import Literal

from pydantic import BaseModel, Field

from backend.llm import generer

PROMPT_VISION = """Analyse ces photos d'un bien immobilier a vendre.
Evalue l'etat general et les travaux visibles. Ne devine pas ce qui n'est pas visible."""


class EtatBien(BaseModel):
    etat_general: Literal["excellent", "bon", "correct", "a_renover"]
    travaux_detectes: list[str]
    estimation_travaux: Literal["0-5k", "5-20k", "20-50k", ">50k"]
    luminosite: int = Field(ge=1, le=5)
    score_presentation: int = Field(ge=1, le=10)


def evaluer_photos_llm(photos: list[bytes]) -> dict:
    """photos : contenu brut des images. Retourne le dict attendu par vision.model."""
    # TODO : preparer les images (nombre, taille), ajuster le prompt, mesurer
    etat = generer(PROMPT_VISION, schema=EtatBien, images=photos[:4], temperature=0)
    return etat.model_dump()
