import streamlit as st
from utils.database import db
import pandas as pd

st.set_page_config(page_title="Scheda Lavoro")

st.title(f"Lavori per: {st.session_state.get('cliente_nome', 'Cliente')}")

cliente_id = st.session_state.get("cliente_id")

if cliente_id:
    # Recupera i lavori filtrati per quel cliente
    response = db.table("lavori").select("*").eq("cliente_id", cliente_id).execute()
    df = pd.DataFrame(response.data)
    
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("Nessun lavoro trovato per questo cliente.")
else:
    st.warning("Per favore, torna alla home e seleziona un cliente.")

if st.button("← Torna alla lista"):
    st.switch_page("app.py")
