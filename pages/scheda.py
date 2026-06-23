import streamlit as st
from utils.db import db
import pandas as pd

# Configurazione della pagina
st.set_page_config(page_title="Scheda Lavoro", layout="wide")

# Controllo sicurezza: se non c'è un cliente selezionato, torna alla home
if "cliente_id" not in st.session_state:
    st.warning("Nessun cliente selezionato. Torna alla lista.")
    if st.button("Vai alla lista clienti"):
        st.switch_page("app.py")
    st.stop()

# Titolo dinamico
st.title(f"Scheda Lavoro: {st.session_state.get('cliente_nome', 'Cliente')}")

# Recupero dati dei lavori filtrati per cliente_id
# Assicurati che nella tua tabella 'lavori' esista la colonna 'cliente_id'
cliente_id = st.session_state.cliente_id
try:
    response = db.table("lavori").select("*").eq("cliente_id", cliente_id).execute()
    df_lavori = pd.DataFrame(response.data)

    if not df_lavori.empty:
        st.dataframe(df_lavori, use_container_width=True)
    else:
        st.info("Nessun lavoro trovato per questo cliente.")
except Exception as e:
    st.error(f"Errore nel recupero dati: {e}")

# Pulsante di navigazione
if st.button("← Torna alla lista clienti"):
    st.switch_page("app.py")
