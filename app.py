# app.py

import streamlit as st
from ui.page_accueil import MainWindow

# Configuration de la page
st.set_page_config(
    page_title="CalculLAB",
    page_icon="🧮",
    layout="wide"
)

# Sidebar - Navigation
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio(
    "Aller vers",
    (
        "🏠 Accueil",
        "💡 Numérisation & Dématérialisation"
    )
)

# Affichage des pages selon le choix
if page == "🏠 Accueil":
    MainWindow()

elif page == "💡 Numérisation & Dématérialisation":
    NumerationOptionsWindow()

# Pied de page ou informations supplémentaires
st.sidebar.markdown("---")
st.sidebar.info("👨‍💻 Développé par Adama Gueye - UADB")


