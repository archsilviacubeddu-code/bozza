import streamlit as st
import pandas as pd
import clienti
import lavori
from utils.database import get_supabase_client

# Configurazione pagina
st.set_page_config(page_title="Archiflow - Gestionale", layout="wide")

# CSS: Uniformità pulsanti sidebar
st.markdown("""
    <style>
    [data-testid="stSidebar"] button { width: 100% !important; height: 60px !important; display: flex !important; align-items: center !important; justify-content: flex-start !important; padding-left: 20px !important; font-size: 18px !important; font-weight: 900 !important; border: 2px solid #333 !important; border-radius: 10px !important; background-color: #ffffff !important; color: #000000 !important; margin-bottom: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# Inizializzazione stato
if 'page' not in st.session_state: st.session_state.page = "Home"

# SIDEBAR
with st.sidebar:
    st.markdown("### 🏗️ ArchiFlow Menu")
    if st.button("🏠 Home"): st.session_state.page = "Home"; st.rerun()
    if st.button("👤 Clienti"): st.session_state.page = "Clienti"; st.rerun()
    if st.button("🏗️ Lavori"): st.session_state.page = "Lavori"; st.rerun()
    if st.button("📅 Scadenze"): st.session_state.page = "Scadenzario"; st.rerun()

# AREA PRINCIPALE
supabase = get_supabase_client()

if st.session_state.page == "Home":
    st.title("Archiflow - Gestionale")
    st.header("Home")
    
    c1, c2, c3 = st.columns(3)
    
    # Colonna Clienti (Tabellare con Cerca Live)
    with c1:
        st.subheader("👤 Clienti")
        q_c = st.text_input("🔍 Cerca cliente (iniziale)", key="q_c")
        try:
            res_c = supabase.table("clienti").select("id, nome, cognome, \"tipo di pratica\"").execute()
            df_c = pd.DataFrame(res_c.data)
            if q_c and not df_c.empty:
                df_c = df_c[df_c['nome'].str.contains(q_c, case=False, na=False) | df_c['cognome'].str.contains(q_c, case=False, na=False)]
            st.dataframe(df_c.head(10), use_container_width=True, hide_index=True)
        except Exception as e: st.error("Errore database Clienti")

    # Colonna Lavori (Tabellare con Cerca Live)
    with c2:
        st.subheader("🏗️ Lavori")
        q_l = st.text_input("🔍 Cerca lavoro (iniziale)", key="q_l")
        try:
            res_l = supabase.table("commesse").select("id, \"indirizzo lavoro\", tipo_pratica").execute()
            df_l = pd.DataFrame(res_l.data)
            if q_l and not df_l.empty:
                df_l = df_l[df_l['indirizzo lavoro'].str.contains(q_l, case=False, na=False) | df_l['tipo_pratica'].str.contains(q_l, case=False, na=False)]
            st.dataframe(df_l.head(10), use_container_width=True, hide_index=True)
        except Exception as e: st.error("Errore database Lavori")

    # Colonna Scadenze
    with c3:
        st.subheader("📅 Scadenze")
        st.text_input("🔍 Cerca scadenza", key="q_s")
        st.info("Sistema scadenze in configurazione.")

elif st.session_state.page == "Clienti":
    clienti.mostra_clienti()

elif st.session_state.page == "Lavori":
    lavori.mostra_lavori()

elif st.session_state.page == "Scadenzario":
    st.title("📅 Scadenze")
