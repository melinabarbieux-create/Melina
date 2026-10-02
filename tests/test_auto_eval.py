"""
Evaluation automatique — Projet 2 NidBuyer. NE PAS MODIFIER.
Lance par GitHub Actions a chaque push sur main (.github/workflows/eval.yml).

Tests publics : 15 points. 10 points de tests caches (memes contrats, autres cas)
sont lances par l'enseignant avant la soutenance. Les contrats sont dans les docstrings
de backend/scoring.py, backend/rag.py et backend/main.py : respectez-les.

Le LLM est remplace par LLM_PROVIDER=fake : aucun appel reseau, aucun cout.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["LLM_PROVIDER"] = "fake"

BIEN = {"id": "t-001", "type": "T3", "surface": 68, "quartier": "Mourillon", "prix": 215_000,
        "description": "Bel appartement lumineux, balcon vue mer partielle."}
MEDIANE = 3_400

ANNONCES = [
    {"id": "001", "type": "T3", "surface": 68, "quartier": "Mourillon", "prix": 215_000,
     "description": "Bel appartement lumineux, balcon vue mer partielle, cuisine rénovée."},
    {"id": "002", "type": "T2", "surface": 45, "quartier": "Cap Brun", "prix": 180_000,
     "description": "Petit appartement proche plage, idéal investissement locatif, déjà loué."},
    {"id": "003", "type": "T4", "surface": 95, "quartier": "Mourillon", "prix": 350_000,
     "description": "Grand appartement familial, 3 chambres, proche écoles, parking sous-sol."},
]


def _readme() -> str:
    return (ROOT / "README.md").read_text(encoding="utf-8")


def _url_deployee() -> str | None:
    m = re.search(r"https://[\w.\-]+\.run\.app", _readme())
    return m.group(0) if m else None


# ── Livrables ecrits (3 pts) ─────────────────────────────────────────────────

class TestLivrables:
    def test_readme_complet(self):
        """[1 pt] README : URL Cloud Run, nombre d'annonces, 4 membres nommes."""
        r = _readme()
        assert _url_deployee(), "URL https://...run.app absente du README"
        assert "XXX" not in r, "Remplacer XXX par le nombre d'annonces indexees"
        assert "Prénom NOM" not in r, "Remplir le tableau de l'equipe"

    def test_experiments(self):
        """[1 pt] prompts/EXPERIMENTS.md : 3 versions documentees avec resultats."""
        c = (ROOT / "prompts" / "EXPERIMENTS.md").read_text(encoding="utf-8")
        assert len(re.findall(r"^## V\d", c, re.M)) >= 3, "3 sections '## V1', '## V2', '## V3' attendues"
        assert "[Coller ici" not in c, "Des blocs du modele n'ont pas ete remplis"
        assert len(c) > 1500, "EXPERIMENTS.md trop court pour 3 versions argumentees"

    def test_approach(self):
        """[1 pt] vision/APPROACH.md : approche, mesure chiffree, limites."""
        c = (ROOT / "vision" / "APPROACH.md").read_text(encoding="utf-8")
        assert len(c) > 800, "APPROACH.md trop court"
        assert re.search(r"\d+ ?%", c), "Aucune mesure chiffree (%) dans APPROACH.md"


# ── Scoring (4 pts) ──────────────────────────────────────────────────────────

class TestScoring:
    @pytest.fixture
    def scoring(self):
        import backend.scoring as m
        return m

    def test_sous_evalue(self, scoring):
        """[1 pt] Bien sous la mediane : ecart negatif, score positif."""
        r = scoring.score_opportunite(BIEN, MEDIANE, "rp")
        assert r["ecart_pct"] < 0 and r["score"] > 0

    def test_sur_evalue(self, scoring):
        """[1 pt] Bien au-dessus de la mediane : ecart positif, score negatif."""
        r = scoring.score_opportunite({**BIEN, "prix": 280_000}, MEDIANE, "rp")
        assert r["ecart_pct"] > 0 and r["score"] < 0

    def test_malus_travaux(self, scoring):
        """[1 pt] Travaux lourds : l'investisseur est moins penalise que la famille."""
        v = {"travaux_score": 1.0}
        assert (scoring.score_opportunite(BIEN, MEDIANE, "investissement", v)["score"]
                > scoring.score_opportunite(BIEN, MEDIANE, "rp", v)["score"])

    def test_fiche_decision(self, scoring):
        """[1 pt] La fiche contient la mediane et l'ecart en %."""
        fiche = scoring.fiche_decision(BIEN, {"mediane_prix_m2": MEDIANE})
        assert re.search(r"3[\s  ]?400", fiche), "Mediane (3 400) absente de la fiche"
        assert "%" in fiche


# ── RAG (3 pts) ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="class")
def index(tmp_path_factory):
    os.environ["CHROMA_PATH"] = str(tmp_path_factory.mktemp("chroma"))
    import backend.rag as rag
    rag._client = None
    rag.indexer_annonces(ANNONCES)
    return rag


@pytest.mark.usefixtures("index")
class TestRAG:
    def test_nombre_resultats(self, index):
        """[1 pt] search_similar renvoie n_results biens avec leur id."""
        r = index.search_similar("appartement vue mer", n_results=2)
        assert len(r) == 2 and all("id" in b for b in r)

    def test_pertinence_famille(self, index):
        """[1 pt] Recherche famille -> le T4 familial en premier."""
        assert index.search_similar("grand appartement pour une famille", n_results=1)[0]["id"] == "003"

    def test_pertinence_investissement(self, index):
        """[1 pt] Recherche investissement -> le T2 loue en premier."""
        assert index.search_similar("investissement locatif rentable", n_results=1)[0]["id"] == "002"


# ── API (2 pts) ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def api(tmp_path_factory):
    env = {**os.environ, "LLM_PROVIDER": "fake", "ADMIN_TOKEN": "test-token",
           "CHROMA_PATH": str(tmp_path_factory.mktemp("chroma_api")),
           "SUPABASE_URL": "https://placeholder.supabase.co", "SUPABASE_KEY": "placeholder"}
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "18765",
                             "--log-level", "warning"], cwd=ROOT, env=env)
    for _ in range(60):
        try:
            urllib.request.urlopen("http://127.0.0.1:18765/health", timeout=1)
            break
        except Exception:
            time.sleep(1)
    yield "http://127.0.0.1:18765"
    proc.terminate()
    proc.wait()


def _get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.status, json.loads(r.read() or b"null")


class TestAPI:
    def test_health_et_docs(self, api):
        """[1 pt] L'API demarre : /health et /docs repondent."""
        assert _get(f"{api}/health")[0] == 200
        assert urllib.request.urlopen(f"{api}/docs", timeout=10).status == 200

    def test_admin_status(self, api):
        """[1 pt] /admin/status renvoie annonces_indexees et derniere_sync."""
        status, data = _get(f"{api}/admin/status")
        assert status == 200 and {"annonces_indexees", "derniere_sync"} <= data.keys()


# ── Deploiement et equipe (3 pts) ────────────────────────────────────────────

class TestDeploiement:
    def test_cloud_run_repond(self):
        """[2 pts] L'URL Cloud Run du README repond sur /health."""
        url = _url_deployee()
        assert url, "URL https://...run.app absente du README"
        try:
            status, _ = _get(f"{url}/health")
        except Exception as e:
            pytest.fail(f"{url}/health ne repond pas : {e}")
        assert status == 200

    def test_pr_par_membre(self):
        """[1 pt] Au moins 4 auteurs differents de PR mergees."""
        repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_TOKEN")
        if not repo or not token:
            pytest.skip("Verifie uniquement dans GitHub Actions")
        req = urllib.request.Request(
            f"https://api.github.com/repos/{repo}/pulls?state=closed&per_page=100",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
        prs = json.loads(urllib.request.urlopen(req, timeout=15).read())
        auteurs = {p["user"]["login"] for p in prs if p.get("merged_at")}
        assert len(auteurs) >= 4, f"PR mergees par {len(auteurs)} membre(s) : {sorted(auteurs)}"
