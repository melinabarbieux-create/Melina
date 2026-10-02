"""
Interface acheteur NidBuyer — Streamlit
"""
import os

import requests  # noqa: F401 (appels a l API, a implementer)
import streamlit as st

# URL de l'API : variable d'environnement (Cloud Run : --set-env-vars API_URL=https://...run.app)
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="NidBuyer", page_icon="🏠", layout="wide")
st.title("🏠 NidBuyer — Votre acheteur IA à Toulon")
# AI Act art. 50 : l'utilisateur doit savoir qu'il échange avec une IA
st.caption("NidBuyer est une intelligence artificielle. Ses analyses ne remplacent pas l'avis d'un professionnel.")

# --- Sidebar : profil acheteur ---
with st.sidebar:
    st.header("Mon profil")
    intention = st.selectbox(
        "Je cherche",
        ["rp", "rs", "investissement", "mixte"],
        format_func=lambda x: {
            "rp": "Résidence principale",
            "rs": "Résidence secondaire",
            "investissement": "Investissement locatif",
            "mixte": "Immeuble mixte",
        }[x],
    )
    budget = st.number_input("Budget max (€)", min_value=50_000, max_value=2_000_000, value=300_000, step=10_000)
    surface_min = st.number_input("Surface min (m²)", min_value=0, max_value=300, value=0)
    description = st.text_area("Décrivez votre bien idéal", placeholder="T3 calme, proche mer, lumineux...")

# --- Zone principale ---
tab_recherche, tab_chat, tab_marche = st.tabs(["Rechercher", "Chat", "Marché"])

with tab_recherche:
    if st.button("Trouver mes biens", type="primary"):
        # TODO : appeler POST /rechercher et afficher les résultats
        st.info("TODO : afficher les résultats de recherche ici")

with tab_chat:
    question = st.text_input("Posez une question sur le marché toulonnais")
    if st.button("Envoyer") and question:
        # TODO : appeler POST /chat et afficher la réponse
        st.info("TODO : afficher la réponse LLM ici")

with tab_marche:
    if st.button("Charger les médianes DVF par quartier"):
        # TODO : appeler GET /marche/quartiers et afficher un tableau / carte
        st.info("TODO : afficher les médianes DVF par quartier ici")
