"""
API NidBuyer (FastAPI), deployee sur Cloud Run.

Pas de planificateur interne : sur Cloud Run, le service s'eteint sans trafic.
L'ingestion quotidienne est declenchee par Cloud Scheduler, qui appelle POST /admin/sync
avec l'en-tete X-Admin-Token (voir README).
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from pydantic import BaseModel

from . import db, llm
from .ingestion import sync

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # L'index ChromaDB local a disparu au redemarrage : on le reconstruit depuis Supabase.
    try:
        from .rag import get_collection, indexer_annonces
        if db.disponible() and get_collection().count() == 0:
            n = indexer_annonces(db.charger_annonces())
            logger.info("Index reconstruit depuis Supabase : %s annonces", n)
    except NotImplementedError:
        logger.warning("indexer_annonces() pas encore implemente : index vide")
    except Exception as e:  # l'API doit demarrer meme si Supabase est indisponible
        logger.error("Reconstruction de l'index impossible : %s", e)
    yield


app = FastAPI(title="NidBuyer API", version="0.2.0", lifespan=lifespan)


# --- Modeles ---

class ProfilAcheteur(BaseModel):
    intention: str          # "rp" | "rs" | "investissement" | "mixte"
    budget_max: float
    surface_min: float | None = None
    quartiers: list[str] = []
    nb_pieces_min: int | None = None
    description_libre: str = ""


class AlerteProfil(BaseModel):
    email: str
    profil: ProfilAcheteur


class Question(BaseModel):
    question: str
    profil: ProfilAcheteur | None = None


# --- Endpoints produit ---
# AI Act, art. 50 (applicable depuis le 2 aout 2026) : l'utilisateur doit savoir qu'il
# echange avec une IA. Toute reponse produite par le LLM inclut le champ "mention_ia"
# (utiliser llm.MENTION_IA), et le frontend l'affiche.

@app.get("/health")
def health():
    """Reponse immediate, sans dependance externe : utilisee par le check de deploiement."""
    return {"status": "ok", "llm": llm.provider(), "modele": llm.modele()}


@app.get("/biens")
def liste_biens(budget_max: float | None = None, surface_min: float | None = None,
                quartier: str | None = None):
    """Liste filtree des biens disponibles."""
    # TODO
    raise HTTPException(status_code=501, detail="Non implemente")


@app.get("/biens/{bien_id}")
def detail_bien(bien_id: str):
    """Detail d'un bien + fiche decision LLM."""
    # TODO
    raise HTTPException(status_code=501, detail="Non implemente")


@app.post("/rechercher")
def rechercher(profil: ProfilAcheteur):
    """
    Profil acheteur -> les 5 meilleurs biens.

    Contrat de reponse :
    {
      "resultats": [ {"id": str, "prix": float, "surface": float, "quartier": str,
                      "score": float, "label": str, "analyse": str}, ... ],   # 5 maximum
      "mention_ia": str
    }
    Aucun bien au-dessus de profil.budget_max. Index vide -> "resultats": [] (pas d'erreur 500).
    """
    from .rag import search_similar
    from .scoring import score_opportunite, fiche_decision
    from .marche import mediane_quartier
    cands = [b for b in search_similar(profil.description_libre or "appartement", n_results=30) if b.get("prix", 0) <= profil.budget_max]
    out = []
    for b in cands:
        med = mediane_quartier(b.get("quartier"))
        sc = score_opportunite(b, med, profil.intention)
        out.append({"id": b["id"], "prix": b["prix"], "surface": b["surface"], "quartier": b["quartier"], **sc})
    out = sorted(out, key=lambda x: -x["score"])[:5]
    for b in out:
        med = mediane_quartier(b.get("quartier"))
        fiche = fiche_decision(b, {"mediane_prix_m2": med}) if med else "Mediane du quartier inconnue."
        b["analyse"] = llm.generer(
            f"Faits calcules : {fiche}\nBien : {b['surface']} m2, {b['quartier']}, {b['prix']} EUR.\n"
            f"Profil acheteur : {profil.intention}. Redige 3 phrases : opportunite, point d'attention, conseil. "
            "Reprends les chiffres tels quels.")
    return {"resultats": out, "mention_ia": llm.MENTION_IA}


@app.post("/chat")
def chat(q: Question):
    """
    Question libre -> reponse argumentee, appuyee sur les annonces (RAG).
    Contrat : {"reponse": str, "sources": [id, ...], "mention_ia": str}
    """
    # TODO
    raise HTTPException(status_code=501, detail="Non implemente")


@app.post("/alerte")
def creer_alerte(alerte: AlerteProfil):
    """Enregistrer un profil pour recevoir des alertes sur les nouveaux biens."""
    # TODO : persister dans Supabase (table alertes), pas dans un fichier local
    raise HTTPException(status_code=501, detail="Non implemente")


@app.get("/marche/quartiers")
def marche_quartiers():
    """Medianes DVF par quartier (voir backend/marche.py)."""
    from .marche import medianes
    return medianes()


# --- Admin ---

def _verifier_token(token: str | None) -> None:
    attendu = os.environ.get("ADMIN_TOKEN")
    if not attendu or token != attendu:
        raise HTTPException(status_code=401, detail="Jeton admin manquant ou invalide")


@app.post("/admin/sync")
def admin_sync(background_tasks: BackgroundTasks, dry_run: bool = False,
               x_admin_token: str | None = Header(default=None)):
    """
    Lance une synchronisation des annonces en arriere-plan.
    Protege par l'en-tete X-Admin-Token (= variable ADMIN_TOKEN). Appele par Cloud Scheduler.
    """
    _verifier_token(x_admin_token)
    background_tasks.add_task(sync, dry_run=dry_run)
    return {"status": "sync lancee en arriere-plan", "dry_run": dry_run}


@app.get("/admin/status")
def admin_status():
    """Etat de la base : annonces indexees, derniere synchro, derniers appels LLM."""
    from .ingestion import derniere_sync
    from .rag import get_collection
    try:
        n = get_collection().count()
    except Exception:
        n = 0
    appels = llm.JOURNAL[-50:]
    return {
        "annonces_indexees": n,
        "derniere_sync": derniere_sync(),
        "llm": {"provider": llm.provider(), "modele": llm.modele(), "derniers_appels": len(appels),
                "latence_moyenne_s": round(sum(a["latence_s"] for a in appels) / len(appels), 2) if appels else None},
    }
