#!/usr/bin/env python3
"""
Rapport de score a partir des resultats JUnit de tests/test_auto_eval.py.
Les points de chaque test sont lus dans sa docstring : "[N pt]" ou "[N pts]".
Le rapport apparait dans l'onglet Actions > Summary.
"""
import ast
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests" / "test_auto_eval.py"
XML = ROOT / "eval_results.xml"
RESTE = [("Tests caches (enseignant, avant soutenance)", 10), ("Code - enseignant", 25),
         ("Soutenance - groupe", 30), ("Individuel (question + contribution git)", 20)]


def bareme():
    """[(classe, test, points, description)] dans l'ordre du fichier."""
    lignes = []
    for classe in ast.parse(TESTS.read_text(encoding="utf-8")).body:
        if not isinstance(classe, ast.ClassDef):
            continue
        for f in classe.body:
            if isinstance(f, ast.FunctionDef) and f.name.startswith("test_"):
                doc = ast.get_docstring(f) or ""
                m = re.search(r"\[(\d+) pts?\]\s*(.*)", doc)
                lignes.append((classe.name, f.name, int(m.group(1)) if m else 0, m.group(2) if m else f.name))
    return lignes


def resultats():
    if not XML.exists():
        return {}
    res = {}
    for tc in ET.parse(XML).getroot().iter("testcase"):
        ko = tc.find("failure") is not None or tc.find("error") is not None
        res[(tc.get("classname", "").split(".")[-1], tc.get("name"))] = "skip" if tc.find("skipped") is not None else ("fail" if ko else "pass")
    return res


def main():
    res, total, maxi, lignes = resultats(), 0, 0, ["# Rapport d'évaluation automatique", ""]
    classe_courante = None
    for classe, test, pts, desc in bareme():
        if classe != classe_courante:
            lignes += ["", f"### {classe.removeprefix('Test')}", "", "| Critère | Points | Résultat |", "|---|---|---|"]
            classe_courante = classe
        etat = res.get((classe, test), "non lancé")
        gagne = pts if etat == "pass" else 0
        total, maxi = total + gagne, maxi + pts
        icone = {"pass": "✅", "fail": "❌", "skip": "⏭️"}.get(etat, "⚪")
        lignes.append(f"| {desc} | {gagne}/{pts} | {icone} |")
    lignes += ["", "---", "", f"## Tests publics : **{total} / {maxi}**", "",
               "Reste de la note, évalué par l'enseignant :", "", "| Volet | Points |", "|---|---|"]
    lignes += [f"| {label} | ? / {pts} |" for label, pts in RESTE]
    rapport = "\n".join(lignes) + "\n"
    (ROOT / "evaluation_report.md").write_text(rapport, encoding="utf-8")
    print(rapport)


if __name__ == "__main__":
    main()
