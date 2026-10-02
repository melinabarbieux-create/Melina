# NidBuyer — version de référence (MBA2 2026-2027)

NidBuyer est l'acheteur IA de l'agence NidDouillet, à Toulon. Cette version **fonctionne** :
c'est le point de départ commun de tous les groupes du MBA2, anciens du MBA1 comme nouveaux arrivants.

Cette année, on en fait un **agent** : un assistant qui choisit lui-même ses outils
(chercher des biens, comparer au marché, simuler un prêt) pour répondre à un acheteur.

> Les données de `data/` (12 annonces, médianes par quartier) sont des **exemples fictifs**
> pour démarrer. Les vraies données arrivent en P1.

---

## Démarrage rapide (module 1, 2 octobre)

```bash
git clone <votre copie de ce repo>
cd nidbuyer-base
cp .env.example .env            # Windows : copy .env.example .env
# ouvrir .env et coller votre clé AI Studio (gratuite : https://aistudio.google.com)
uv run python -m exercices.m1_agent "Je cherche un T3 au Mourillon sous 250 000 euros, c'est une bonne affaire ?"
```

`uv run` installe Python et les dépendances au premier lancement (voir `pyproject.toml`).
Installer uv : https://docs.astral.sh/uv/ (Mac/Linux : `curl -LsSf https://astral.sh/uv/install.sh | sh`).
Sans uv : `python -m venv .venv`, l'activer, `pip install -r exercices/requirements-tp.txt` (Python 3.10+).

Sans clé ni réseau : `LLM_PROVIDER=fake` dans `.env` pour voir la mécanique (réponses factices).

> **Votre clé d'API est un secret.** Jamais dans le code, jamais dans un commit, jamais sur
> une capture d'écran. Le fichier `.env` est ignoré par git : c'est là qu'elle va.

Énoncés des TP : dossier [`enonces/M1/`](enonces/M1/) ([TP 1 « Premier agent »](enonces/M1/TP1-premier-agent.md), [TP 2 « Casser l'agent »](enonces/M1/TP2-casser-l-agent.md)).

---

## Ce qu'il y a dedans

```
backend/
├── llm.py         # Accès unique aux LLM (gemini · vertex · ollama · fake) + boucle d'agent
├── outils.py      # Les outils de l'agent : chercher_biens, ecart_au_marche, simuler_pret
├── scoring.py     # Score d'opportunité d'un bien vs médiane du quartier
├── rag.py         # Recherche sémantique (ChromaDB)
├── marche.py      # Médianes des ventes par quartier
├── main.py        # API FastAPI (/rechercher, /admin/status...)
├── db.py          # Stockage des annonces (Supabase)
├── ingestion.py   # Collecte quotidienne des annonces
└── sources/       # Sources d'annonces
exercices/         # TP des modules (m1_agent.py...)
frontend/          # Interface Streamlit
vision/            # Estimation de l'état d'un bien à partir des photos
data/              # Données d'exemple (fictives)
tests/             # Tests
```

**Trois règles qui valent pour toute l'année :**
1. Tous les appels à un LLM passent par `backend/llm.py`. Changer de modèle = changer une variable d'environnement, pas le code.
2. Les calculs (prix au m², écart au marché, mensualité) sont faits en Python, dans les outils. Le modèle orchestre et rédige ; il ne calcule jamais.
3. Aucun secret dans le code.

---

## Lancer l'API complète (optionnel au M1)

L'API complète a besoin du modèle d'embedding (plus lourd à installer) :

```bash
uv pip install -r requirements.txt
cp .env.example .env        # puis remplir
uvicorn backend.main:app --reload     # → http://localhost:8000/docs
streamlit run frontend/app.py         # → http://localhost:8501
```

---

## La suite

| Quand | Ce que devient ce repo |
|---|---|
| M1 (2 oct.) | Premier agent, pannes d'un agent |
| M2 (9 oct.) | Jeu d'évaluation automatique de l'agent |
| P1 (30 oct. → 27 nov.) | NidBuyer agent sur vraies données, évalué |
| P2 (15 janv. → 11 fév.) | Déployé sur Google Cloud et en version interne, comparés |
| P3 (19 fév. → 19 mars) | Audité par un autre groupe, mis en conformité |
