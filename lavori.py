import streamlit as st
import pandas as pd
from utils.database import get_supabase_client

def mostra_lavori():
    st.markdown("<h2 style='text-align: left;'>🏗️ Gestione Lavori</h2>", unsafe_allow_html=True)
    supabase = get_supabase_client()
    lista_stati = ["Da iniziare", "In corso", "Sospeso", "Ultimato"]
    
    # Liste di classificazione centralizzate
    urbanistica = ["CIL", "CILA", "SCIA", "agibilità", "accertamento di conformità", "condono edilizio", "docfa", "voltura", "istanza catastale"]
    dir_lavori = ["rilievo", "progettazione", "direzione lavori", "computo metrico", "cantieri esterni", "cantieri interni"]
    
    def get_macro(tipo):
        # Conversione in minuscolo per confronto sicuro
        tipo_clean = tipo.lower().strip()
        if any(d.lower() == tipo_clean for d in dir_lavori): return "Direzione Lavori"
        if any(u.lower() == tipo_clean for u in urbanistica): return "Urbanistica e Catasto"
        return "Consulenza"

    if st.session_state.get('provenienza') == 'Lavori':
        st.session_state.stato_lavoro = "lista"
        del st.session_state.provenienza
    
    if 'stato_lavoro' not in st.session_state: st.session_state.stato_lavoro = "lista"

    # --- ZONA OPERATIVA ---
    if st.session_state.stato_lavoro != "lista":
        if st.button("⬅️ Torna alla lista"): 
            st.session_state.stato_lavoro = "lista"
            if 'temp_cliente_id' in st.session_state: del st.session_state.temp_cliente_id
            st.rerun()

        # FORM NUOVO
        if st.session_state.stato_lavoro == "nuovo":
            st.subheader("📝 Inserisci Nuovo Lavoro")
            if 'temp_cliente_id' not in st.session_state:
                nome_cerca = st.text_input("🔍 Cerca cliente")
                if nome_cerca:
                    clienti_res = supabase.table("clienti").select("id, nome, cognome").or_(f"nome.ilike.%{nome_cerca}%,cognome.ilike.%{nome_cerca}%").execute()
                    c_df = pd.DataFrame(clienti_res.data)
                    for _, row in c_df.iterrows():
                        if st.button(f"👤 {row['nome']} {row['cognome']}", key=f"sel_{row['id']}"):
                            st.session_state.temp_cliente_id = row['id']
                            st.session_state.temp_cliente_nome = f"{row['nome']} {row['cognome']}"
                            st.rerun()
            else:
                st.success(f"Cliente selezionato: {st.session_state.temp_cliente_nome}")
                if st.button("🔄 Cambia Cliente"): del st.session_state.temp_cliente_id; st.rerun()
                
                with st.form("form_nuovo_submit"):
                    tipi = [p['nome_pratica'] for p in supabase.table("tipologie_pratiche").select("nome_pratica").execute().data]
                    tipo = st.selectbox("Tipo Pratica", tipi)
                    ind = st.text_input("Indirizzo Lavoro")
                    inizio = st.date_input("Data Inizio", value=None)
                    fine = st.date_input("Data Conclusione", value=None)
                    stato = st.selectbox("Stato", lista_stati)
                    
                    if st.form_submit_button("💾 Salva Lavoro"):
                        supabase.table("commesse").insert({
                            "cliente_id": int(st.session_state.temp_cliente_id), 
                            "tipo_pratica": tipo, "macro_categoria": get_macro(tipo),
                            "indirizzo lavoro": ind, "inizio": str(inizio) if inizio else None, 
                            "conclusione": str(fine) if fine else None, "stato": stato
                        }).execute()
                        del st.session_state.temp_cliente_id; st.session_state.stato_lavoro = "lista"; st.rerun()

        # FORM MODIFICA
        elif st.session_state.stato_lavoro == "modifica":
            l = st.session_state.lavoro_selezionato
            c = l.get('clienti', {})
            st.subheader(f"📝 Modifica Lavoro #{l['id']}")
            tipi = [p['nome_pratica'] for p in supabase.table("tipologie_pratiche").select("nome_pratica").execute().data]
            
            with st.form("form_modifica"):
                c1, c2 = st.columns(2)
                with c1:
                    nome = st.text_input("Nome Cliente", value=c.get('nome', ''))
                    cognome = st.text_input("Cognome Cliente", value=c.get('cognome', ''))
                    ind = st.text_input("Indirizzo Lavoro", value=l.get('indirizzo lavoro', ''))
                    tipo = st.selectbox("Tipo Pratica", tipi, index=tipi.index(l.get('tipo_pratica')) if l.get('tipo_pratica') in tipi else 0)
                with c2:
                    inizio = st.date_input("Data Inizio", value=pd.to_datetime(l['inizio']).date() if l.get('inizio') and l['inizio'] != 'None' else None)
                    fine = st.date_input("Data Conclusione", value=pd.to_datetime(l['conclusione']).date() if l.get('conclusione') and l['conclusione'] != 'None' else None)
                    stato = st.selectbox("Stato", lista_stati, index=lista_stati.index(l.get('stato')) if l.get('stato') in lista_stati else 0)
                
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Salva Modifiche"):
                    supabase.table("commesse").update({
                        "indirizzo lavoro": ind, "tipo_pratica": tipo, "macro_categoria": get_macro(tipo),
                        "inizio": str(inizio), "conclusione": str(fine), "stato": stato
                    }).eq("id", l['id']).execute()
                    supabase.table("clienti").update({"nome": nome, "cognome": cognome}).eq("id", l['cliente_id']).execute()
                    st.session_state.stato_lavoro = "lista"; st.rerun()
                if b2.form_submit_button("🗑️ Elimina Lavoro"):
                    supabase.table("commesse").delete().eq("id", l['id']).execute()
                    st.session_state.stato_lavoro = "lista"; st.rerun()

    # --- ZONA LISTA ---
    else:
        st.subheader("📋 Elenco Lavori")
        if st.button("➕ Nuovo Lavoro", use_container_width=True): st.session_state.stato_lavoro = "nuovo"; st.rerun()
        
        st.markdown("---")
        if 'filtro_macro' not in st.session_state: st.session_state.filtro_macro = "Tutti"
        col_pad1, c1, c2, c3, col_pad2 = st.columns([1, 2, 2, 2, 1])
        
        def bottone_selezionabile(label, valore, colonna):
            testo = f"✅ {label}" if st.session_state.filtro_macro == valore else label
            if colonna.button(testo, use_container_width=True):
                st.session_state.filtro_macro = valore
                st.rerun()

        bottone_selezionabile("🏗️ Urbanistica e Catasto", "Urbanistica e Catasto", c1)
        bottone_selezionabile("💡 Consulenza", "Consulenza", c2)
        bottone_selezionabile("👷 Direzione Lavori", "Direzione Lavori", c3)
        
        st.markdown("---")
        if st.button("🔄 Reset Filtri"): st.session_state.filtro_macro = "Tutti"; st.rerun()

        query = st.text_input("🔍 Cerca per qualsiasi dato:")
        risposta = supabase.table("commesse").select("*, clienti(*)").order("id", desc=True).execute()
        df = pd.DataFrame(risposta.data)
        
        if not df.empty:
            if st.session_state.filtro_macro != "Tutti": df = df[df['macro_categoria'] == st.session_state.filtro_macro]
            if query:
                mask = (df['indirizzo lavoro'].str.contains(query, case=False, na=False) | 
                        df['tipo_pratica'].str.contains(query, case=False, na=False) |
                        df['clienti'].apply(lambda x: query.lower() in x['nome'].lower() or query.lower() in x['cognome'].lower() if isinstance(x, dict) else False))
                df = df[mask]
            
            for _, row in df.iterrows():
                with st.container(border=True):
                    c_r1, c_r2 = st.columns([3, 1])
                    with c_r1:
                        st.write(f"**{row.get('macro_categoria', 'N/D')}** | *{row.get('tipo_pratica', 'N/D')}*")
                        st.write(f"📍 {row.get('indirizzo lavoro', 'N/D')}")
                        c = row.get('clienti', {})
                        if st.button(f"👤 {c.get('nome', '')} {c.get('cognome', '')}", key=f"go_{row['id']}"):
                            st.session_state.cliente_selezionato = c; st.session_state.page = "Clienti"; st.session_state.stato = "modifica"; st.session_state.provenienza = 'Lavori'; st.rerun()
                    with c_r2:
                        st.write(f"**Stato:** {row.get('stato', 'N/D')}")
                        if st.button(f"✏️ Modifica #{row['id']}", key=f"edit_{row['id']}", use_container_width=True):
                            st.session_state.lavoro_selezionato = row.to_dict(); st.session_state.stato_lavoro = "modifica"; st.rerun()
