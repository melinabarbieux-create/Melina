# TP 1 — Premier agent NidBuyer

**Durée : 1h30** · binômes · une copie du template `nidbuyer-base`

## Installation (15 min)

Créez votre copie : sur https://github.com/Teaching-AI/nidbuyer-base, **Use this template → Create a new repository**.

```bash
git clone <votre copie de nidbuyer-base>
cd nidbuyer-base
cp .env.example .env                   # Windows : copy .env.example .env
```

Ouvrez `.env` dans votre éditeur et remplacez `collez-votre-cle-ici` par votre clé AI Studio.
Si l'enseignant donne un autre modèle, changez aussi `LLM_MODEL`. Puis :

```bash
uv run python -m exercices.m1_agent "Avec 250 000 euros empruntés sur 25 ans à 3,4 %, je paie combien par mois ?"
```

Le premier lancement installe Python et les dépendances (une minute), les suivants sont immédiats.
Attendu : un appel à `simuler_pret`, une réponse avec 1 238,19 €, et le nombre de tokens.

Pas de uv ? Installez-le (Mac/Linux : `curl -LsSf https://astral.sh/uv/install.sh | sh` ;
Windows : `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`),
puis ouvrez un nouveau terminal. En dernier recours : `python -m venv .venv`, activez-le,
`pip install -r exercices/requirements-tp.txt`, et lancez sans `uv run` (Python 3.10 ou plus).

Sans clé ou sans réseau : mettez `LLM_PROVIDER=fake` dans `.env`. L'agent appelle alors chaque outil une
fois avec des arguments bidons : utile pour voir la mécanique, pas pour juger la qualité.

> Votre clé d'API est un secret. Elle va dans `.env` (ignoré par git), jamais dans le code, un commit ou une capture d'écran.

## Étape 1 — Lire avant de lancer (15 min)

Ouvrez `backend/outils.py` et `exercices/m1_agent.py`. Répondez en binôme :
1. Quels outils l'agent a-t-il ? Qu'est-ce que le modèle voit de chacun ?
2. Pourquoi `ecart_au_marche` prend-il un `bien_id` et pas un prix et une surface ?
3. Que se passe-t-il quand un outil lève une `ValueError` ? (cherchez dans `backend/llm.py`, fonction `_executer_outil`)

## Étape 2 — Lancer (20 min)

```bash
uv run python -m exercices.m1_agent "Je cherche un T3 au Mourillon sous 250 000 euros. C'est une bonne affaire ?"
```

Lisez la trace : quels outils, dans quel ordre, avec quels arguments ? Puis essayez :

| Question | Outils appelés | Réponse juste ? |
|---|---|---|
| « Qu'y a-t-il sous 100 000 € ? » | | |
| « Le bien a06 est-il au prix du marché ? » | | |
| « Avec 250 000 € empruntés sur 25 ans à 3,4 %, je paie combien par mois ? » | | |
| « Une maison avec jardin près des écoles, 450 k€ max, et la mensualité si j'emprunte tout sur 25 ans à 3,4 % » | | |

Pour la dernière, comptez les tours. Lancez-la trois fois : l'agent fait-il toujours pareil ?

## Étape 3 — Ajouter un outil (30 min)

Un acheteur dans l'ancien paie des **frais de notaire** d'environ 7,5 % du prix (règle simple
pour le TP ; dans le neuf, environ 2,5 %). Ajoutez dans `backend/outils.py` :

```python
def frais_de_notaire(prix: float, neuf: bool = False) -> dict:
    """..."""   # à vous : c'est le seul mode d'emploi du modèle
```

Ajoutez-le à `OUTILS` dans `m1_agent.py`, puis demandez :
« J'ai 50 000 € d'apport. Pour le T3 a06, combien dois-je emprunter et quelle mensualité sur 20 ans à 3,4 % ? »

L'agent doit enchaîner : frais de notaire → montant à emprunter → simulation de prêt.
S'il fait le calcul « prix + frais − apport » de tête, est-ce un problème ? Comment l'éviter ?

## Étape 4 — La docstring compte (10 min)

Remplacez la docstring de `simuler_pret` par `"""Calcul."""`. Relancez la question de l'étape 3.
Que se passe-t-il ? Remettez la bonne docstring.

## À retenir

- L'agent ne voit que le nom, la docstring et les paramètres des outils.
- Les calculs sont dans les outils ; le modèle orchestre et rédige.
- Lire la trace des appels est le premier réflexe de débogage.
