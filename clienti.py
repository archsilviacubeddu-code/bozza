import streamlit as st
import pandas as pd
from utils.database import get_supabase_client

def mostra_clienti():
    st.markdown("<h2 style='text-align: left;'>👤 Gestione Anagrafica Clienti</h2>", unsafe_allow_html=True)
    supabase = get_supabase_client()
    
    try:
        pratiche_res = supabase.table("tipologie_pratiche").select("nome_pratica").order("nome_pratica").execute()
        lista_pratiche = [p['nome_pratica'] for p in pratiche_res.data]
    except: lista_pratiche = ["Altro"]

    if 'stato' not in st.session_state: st.session_state.stato = "lista"
    try:
        risposta = supabase.table("clienti").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(risposta.data)
    except: df = pd.DataFrame()

    # --- ZONA OPERATIVA ---
    if st.session_state.stato != "lista":
        if st.button("⬅️ Torna alla lista"): st.session_state.stato = "lista"; st.rerun()
            
        if st.session_state.stato == "nuovo":
            st.subheader("📝 Inserisci Nuovo Cliente")
            with st.form("form_nuovo", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    nome = st.text_input("Nome"); cognome = st.text_input("Cognome")
                    cf = st.text_input("CF / P.IVA"); email = st.text_input("Email")
                    tel = st.text_input("Telefono")
                with c2:
                    ind = st.text_input("Indirizzo"); cap = st.text_input("CAP")
                    citta = st.text_input("Città")
                    tipo = st.selectbox("Tipo di pratica", lista_pratiche)
                    ind_p = st.text_input("Indirizzo pratica")
                if st.form_submit_button("💾 Salva"):
                    supabase.table("clienti").insert({"nome": nome, "cognome": cognome, "cf_piva": cf, "email": email, "telefono": tel, "indirizzo": ind, "cap": cap, "citta": citta, "tipo di pratica": tipo, "indirizzo pratica": ind_p}).execute()
                    st.session_state.stato = "lista"; st.rerun()

        elif st.session_state.stato == "modifica":
            c = st.session_state.cliente_selezionato
            st.subheader("📝 Modifica Cliente")
            with st.form("form_modifica"):
                c1, c2 = st.columns(2)
                with c1:
                    n = st.text_input("Nome", value=c.get('nome')); cog = st.text_input("Cognome", value=c.get('cognome'))
                    cf = st.text_input("CF / P.IVA", value=c.get('cf_piva')); em = st.text_input("Email", value=c.get('email'))
                    tel = st.text_input("Telefono", value=c.get('telefono'))
                with c2:
                    ind = st.text_input("Indirizzo", value=c.get('indirizzo')); cap = st.text_input("CAP", value=c.get('cap'))
                    cit = st.text_input("Città", value=c.get('citta'))
                    idx = lista_pratiche.index(c.get('tipo di pratica')) if c.get('tipo di pratica') in lista_pratiche else 0
                    tip = st.selectbox("Tipo di pratica", lista_pratiche, index=idx); indp = st.text_input("Indirizzo pratica", value=c.get('indirizzo pratica'))
                
                c1_btn, c2_btn = st.columns(2)
                if c1_btn.form_submit_button("💾 Salva Modifiche"):
                    supabase.table("clienti").update({"nome": n, "cognome": cog, "cf_piva": cf, "email": em, "telefono": tel, "indirizzo": ind, "cap": cap, "citta": cit, "tipo di pratica": tip, "indirizzo pratica": indp}).eq("id", c['id']).execute()
                    st.session_state.stato = "lista"; st.rerun()
                if c2_btn.form_submit_button("🗑️ Cancella"):
                    supabase.table("clienti").delete().eq("id", c['id']).execute()
                    st.session_state.stato = "lista"; st.rerun()

    # --- ZONA LISTA (Layout coerente col Nuovo Cliente) ---
    st.subheader("📋 Elenco Clienti")
    query = st.text_input("🔍 Cerca cliente:")
    if st.button("➕ Nuovo Cliente", use_container_width=True): st.session_state.stato = "nuovo"; st.rerun()
            
    if not df.empty:
        if query: df = df[df['nome'].str.contains(query, case=False, na=False) | df['cognome'].str.contains(query, case=False, na=False)]
        
        # Iterazione per mostrare ogni cliente con lo stesso layout a 2 colonne
        for _, row in df.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Nome:** {row.get('nome', '')}")
                    st.write(f"**Cognome:** {row.get('cognome', '')}")
                    st.write(f"**CF/PIVA:** {row.get('cf_piva', '')}")
                with c2:
                    st.write(f"**Pratica:** {row.get('tipo di pratica', '')}")
                    st.write(f"**Città:** {row.get('citta', '')}")
                    if st.button(f"✏️ Modifica #{row['id']}", key=f"btn_{row['id']}", use_container_width=True):
                        st.session_state.cliente_selezionato = row.to_dict()
                        st.session_state.stato = "modifica"; st.rerun()
    
    # Padding per stabilità
    for _ in range(5): st.write("")

