import streamlit as st
from utils.database import db
import pandas as pd

st.title(f"Commesse per: {st.session_state.get('cliente_nome', 'Cliente')}")

cliente_id = st.session_state.get("cliente_id")

if cliente_id:
    # Recupera i dati dalla tabella corretta 'commesse'
    try:
        response = db.table("commesse").select("*").eq("cliente_id", cliente_id).execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nessuna commessa trovata per questo cliente.")
    except Exception as e:
        st.error(f"Errore nel recupero commesse: {e}")
else:
    st.warning("Torna alla Home per selezionare un cliente.")

if st.button("← Torna alla lista"):
    st.switch_page("app.py")
