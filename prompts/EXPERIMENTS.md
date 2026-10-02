# Journal des expérimentations — Prompt Engineering

Comparez **3 versions** du prompt de fiche décision :
1. sur le **jeu de test du module 2** (20 annonces annotées) → tableau chiffré ci-dessous ;
2. sur **un bien de référence** → réponses complètes, pour illustrer.

## Mesures sur le jeu de test

| | V1 | V2 | V3 |
|---|---|---|---|
| Sorties valides (schéma) | /20 | /20 | /20 |
| Chiffres recopiés sans erreur (prix/m², médiane, écart) | /20 | /20 | /20 |
| Hallucinations (info absente de l'annonce) | | | |
| Latence médiane (s) | | | |
| Tokens moyens (entrée / sortie) | | | |

Méthode de comptage (qui a vérifié, comment) :

---

## Bien de référence (à choisir une fois, garder pour toutes les versions)

> **Exemple** : T3, 68m², Mourillon, 215 000€ — description : "Bel appartement lumineux, cuisine rénovée, balcon vue mer partielle, proximité plage du Mourillon."
> DVF quartier Mourillon : médiane 3 400 €/m² → bien à 3 162 €/m², soit **-7%**

---

## V1 — Prompt basique

```
[Coller ici le texte exact de votre V1]
```

**Réponse obtenue sur le bien de référence :**

> [Coller ici la réponse du LLM]

**Analyse :**
- Ce qui fonctionne :
- Ce qui manque :

---

## V2 — Format de sortie structuré

```
[Coller ici le texte exact de votre V2]
```

**Réponse obtenue sur le bien de référence :**

> [Coller ici la réponse du LLM]

**Analyse :**
- Ce qui s'est amélioré :
- Ce qui reste perfectible :

---

## V3 — Chain-of-thought

```
[Coller ici le texte exact de votre V3]
```

**Réponse obtenue sur le bien de référence :**

> [Coller ici la réponse du LLM]

**Analyse :**
- Pourquoi V3 > V1 ?
- Trade-off (longueur, coût tokens, latence) :

---

## Conclusion

Version retenue en production : **V?**

Raison principale :
