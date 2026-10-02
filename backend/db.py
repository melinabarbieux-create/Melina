"""
Stockage des annonces dans Supabase (PostgreSQL), via son API REST.
FOURNI PAR L'ENSEIGNANT. Supabase est la source de verite ; ChromaDB n'est qu'un index.

Table a creer une fois dans Supabase (SQL Editor) :

    create table annonces (
      id text primary key,          -- ex. "bienici-123456"
      url_source text unique,
      source text, type text, quartier text, ville text default 'Toulon',
      surface real, prix real, nb_pieces int, dpe text,
      description text, photos jsonb default '[]',
      vu_le timestamptz default now()
    );

Variables : SUPABASE_URL, SUPABASE_KEY (cle service_role, jamais cote navigateur).
Sur Cloud Run, SUPABASE_KEY vient de Secret Manager (voir README).
"""
import os

import requests

COLONNES = ["id", "url_source", "source", "type", "quartier", "ville", "surface", "prix",
            "nb_pieces", "dpe", "description", "photos"]


def _config():
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
    if not url or not key or "placeholder" in url:
        return None
    return url.rstrip("/") + "/rest/v1/annonces", {
        "apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
    }


def disponible() -> bool:
    return _config() is not None


def charger_annonces(limite: int = 10_000) -> list[dict]:
    """Toutes les annonces (pour reconstruire l'index au demarrage)."""
    cfg = _config()
    if cfg is None:
        return []
    url, headers = cfg
    r = requests.get(url, headers=headers, params={"select": "*", "limit": limite}, timeout=30)
    r.raise_for_status()
    return r.json()


def enregistrer_annonces(annonces: list[dict]) -> int:
    """Insere ou met a jour (cle : id). Retourne le nombre de lignes envoyees."""
    cfg = _config()
    if cfg is None or not annonces:
        return 0
    url, headers = cfg
    lignes = [{k: a.get(k) for k in COLONNES} for a in annonces]
    r = requests.post(url, headers={**headers, "Prefer": "resolution=merge-duplicates"},
                      json=lignes, timeout=60)
    r.raise_for_status()
    return len(lignes)
