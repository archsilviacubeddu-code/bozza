import streamlit as st
from utils.database import db
import pandas as pd

st.set_page_config(page_title="ArchiFlow")
st.title("🏗️ ArchiFlow - Gestione Clienti")

# Recupero lista clienti
try:
    response = db.table("clienti").select("*").execute()
    df = pd.DataFrame(response.data)

    for _, row in df.iterrows():
        if st.button(f"Scheda: {row['nome_cliente']}", key=row['id']):
            st.session_state.cliente_id = row['id']
            st.session_state.cliente_nome = row['nome_cliente']
            st.switch_page("pages/scheda.py")
except Exception as e:
    st.error(f"Errore caricamento clienti: {e}")
