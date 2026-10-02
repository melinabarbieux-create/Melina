"""
Indexation et recherche semantique sur les annonces immobilieres (ChromaDB).

Sur Cloud Run, le disque du conteneur est efface a chaque redemarrage : l'index
ChromaDB local est donc un CACHE, reconstruit au demarrage depuis Supabase
(voir main.py, lifespan). Supabase est la source de verite.
"""
import os

import chromadb
from chromadb.utils import embedding_functions

# Modele d'embedding : a justifier dans le README (langue, vitesse, taille, cout).
# Le defaut est multilingue : les annonces sont en francais.
# all-MiniLM-L6-v2 (anglais) est plus rapide mais moins bon en francais : mesurez-le.
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
COLLECTION = "annonces_toulon"

_client = None
_ef = None


def get_collection():
    """Collection ChromaDB, creee au premier appel dans CHROMA_PATH (defaut ./chroma_db)."""
    global _client, _ef
    if _client is None:
        _client = chromadb.PersistentClient(path=os.environ.get("CHROMA_PATH", "./chroma_db"))
        _ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    return _client.get_or_create_collection(name=COLLECTION, embedding_function=_ef)


def texte_a_encoder(annonce: dict) -> str:
    """
    Texte qui represente l'annonce dans l'espace vectoriel.
    Ce choix a plus d'impact sur la qualite du RAG que le choix du modele : testez.
    """
    # TODO : a ameliorer (quels champs ? dans quel ordre ? la description entiere ?)
    return f"{annonce.get('type', '')} {annonce.get('surface', '')} m2 {annonce.get('quartier', '')} — {annonce.get('description', '')}"


def indexer_annonces(annonces: list[dict]) -> int:
    """
    Indexe (ou met a jour) des annonces dans ChromaDB.

    Contrat :
    - chaque annonce a au minimum : id, type, surface, quartier, prix, description ;
    - reindexer une annonce deja presente (meme id) la met a jour, sans doublon ;
    - les metadonnees stockees contiennent au moins id, prix, surface, quartier ;
    - retourne le nombre d'annonces indexees.

    Attention : ChromaDB n'accepte dans les metadonnees que str, int, float, bool (pas None, pas de liste).
    """
    if not annonces:
        return 0
    meta = [{k: v for k, v in a.items() if isinstance(v, (str, int, float, bool))} for a in annonces]
    get_collection().upsert(ids=[str(a["id"]) for a in annonces],
                            documents=[texte_a_encoder(a) for a in annonces], metadatas=meta)
    return len(annonces)


def search_similar(query: str, n_results: int = 5, filtre_meta: dict | None = None) -> list[dict]:
    """
    Recherche semantique.

    Contrat :
    - retourne au plus n_results dicts (moins si l'index contient moins d'annonces), du plus proche au moins proche ;
    - chaque dict contient les metadonnees du bien, dont "id" ;
    - filtre_meta (ex. {"quartier": "Mourillon"}) restreint les resultats aux biens correspondants ;
    - index vide : retourne [] sans lever d'erreur.
    """
    c = get_collection()
    n = min(n_results, c.count())
    if n == 0:
        return []
    return c.query(query_texts=[query], n_results=n, where=filtre_meta or None)["metadatas"][0]
