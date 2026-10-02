"""
Calcul du score d'opportunite d'un bien : prix au m2 compare a la mediane DVF du quartier.
"""

PROFILS = ("rp", "rs", "investissement", "mixte")

MALUS_TRAVAUX = {
    "investissement": 0.0,   # travaux = marge de negociation
    "rp":             0.3,   # travaux = contrainte pour une famille
    "rs":             0.15,
    "mixte":          0.1,
}


def score_opportunite(bien: dict, mediane_quartier: float | None, profil: str,
                      vision_result: dict | None = None) -> dict:
    """
    Score d'opportunite d'un bien pour un profil d'acheteur.

    Args:
        bien: dict avec au moins 'prix' et 'surface'
        mediane_quartier: mediane DVF du quartier en EUR/m2 (None si inconnue)
        profil: "rp" | "rs" | "investissement" | "mixte"
        vision_result: sortie optionnelle de vision.model.evaluer_etat_bien(),
                       ou {"travaux_score": 0..1} (0 = aucun travaux, 1 = travaux lourds)

    Returns:
        {
          "score":     float,       positif = bonne affaire, negatif = trop cher
          "ecart_pct": float | None, (prix_m2 - mediane) / mediane * 100
          "label":     "opportunite" | "prix_marche" | "surevalue" | "inconnu"
        }

    Contrat :
    - profil inconnu -> ValueError ;
    - prix, surface ou mediane absents ou <= 0 -> {"score": 0.0, "ecart_pct": None, "label": "inconnu"}, sans exception ;
    - le malus travaux reduit le score d'autant plus que MALUS_TRAVAUX[profil] est grand.
    Les seuils entre opportunite / prix_marche / surevalue sont a choisir et justifier.
    """
    if profil not in PROFILS:
        raise ValueError(profil)
    prix, surface = bien.get("prix") or 0, bien.get("surface") or 0
    if prix <= 0 or surface <= 0 or not mediane_quartier or mediane_quartier <= 0:
        return {"score": 0.0, "ecart_pct": None, "label": "inconnu"}
    ecart = (prix / surface - mediane_quartier) / mediane_quartier * 100
    score = -ecart / 100
    if vision_result:
        score -= MALUS_TRAVAUX[profil] * vision_result.get("travaux_score", 0)
    label = "opportunite" if ecart < -5 else ("surevalue" if ecart > 5 else "prix_marche")
    return {"score": round(score, 4), "ecart_pct": round(ecart, 2), "label": label}


def fiche_decision(bien: dict, dvf_quartier: dict) -> str:
    """
    Fiche factuelle transmise au LLM, qui redige ensuite l'analyse.

    dvf_quartier : {"mediane_prix_m2": float, ...}

    Contrat : la fiche contient le prix au m2 du bien, la mediane du quartier (valeurs
    arrondies a l'euro) et l'ecart en %. Ce sont des faits calcules en Python :
    le LLM ne doit jamais faire ces calculs lui-meme.
    """
    pm2 = bien["prix"] / bien["surface"]
    med = dvf_quartier["mediane_prix_m2"]
    return f"Prix/m2 : {pm2:,.0f} EUR ; mediane quartier : {med:,.0f} EUR ; ecart : {(pm2-med)/med*100:+.1f} %".replace(",", " ")


def rendement_locatif(bien: dict, loyer_estime: float) -> dict:
    """
    Rendement locatif estime (bonus profil investisseur).

    Returns:
        {"rendement_brut_pct": float, "rendement_net_pct": float}

    Convention du cours :
    - brut = loyer mensuel x 12 / prix x 100
    - net  = brut x 0,75  (approximation : charges, taxe fonciere, vacance, gestion)
    """
    brut = loyer_estime * 12 / bien["prix"] * 100
    return {"rendement_brut_pct": round(brut, 2), "rendement_net_pct": round(brut * 0.75, 2)}
