import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime

# ------------------------------------------------------------
# Il Mostro 5.0 - v6 NO EXPORT (Tema Giallo/Rosso)
# ------------------------------------------------------------

# CONFIG
EXCEL_FILE_NAME = "Il Mostro 5.0.xlsx"
LEAGUE_AVG_MATCH_CARDS = 4.5
MAX_INDIVIDUAL_PROBABILITY = 42.0
STABILIZATION_K = 0.5

st.set_page_config(page_title="Il Mostro 5.0 - Solo UI", page_icon="🤖⚽", layout="wide")

# -------------------------
# CSS (TEMA GIALLLO/ROSSO)
# -------------------------
st.markdown("""
<style>
/* Base Theme */
/* Sfondo dell'app: Grigio chiaro per un contrasto migliore */
body { background-color: #e9ecef; } 

/* Intestazione: Giallo brillante */
.main-header { 
    font-size: 2.8rem; 
    color: #ffc107; /* Giallo brillante */
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1); 
    font-weight: 900; 
    text-align: center; 
    padding-bottom: 5px; 
    border-bottom: 3px solid #ffc107;
    margin-bottom: 20px;
}
h2, h3, h4 { color: #dc3545; } /* Titoli secondari in rosso */

/* Pulsanti: Giallo/Blu scuro per leggibilità */
.stButton>button { 
    border-radius: 8px; 
    font-weight: bold;
    border: 1px solid #ffc107; /* Bordo Giallo */
    color: #0b3d91; /* Testo Blu Scuro */
    background-color: #fff8e1; /* Sfondo Giallo chiarissimo */
    transition: all 0.3s;
}
.stButton>button:hover {
    background-color: #ffc107; /* Hover Giallo scuro */
    color: white;
}

/* Summary Card Styling: Sfondo giallo pallido (richiamo cartellino) */
.card { 
    background: #fff8e1; /* Giallo molto chiaro */
    border-radius: 15px; 
    padding: 20px; 
    box-shadow: 0 10px 30px rgba(255,193,7,0.2); /* Ombra Gialla */
    margin-bottom: 30px; 
}

/* Metriche: Bianco con bordo Rosso (richiamo cartellino) */
.stMetric {
    background-color: #ffffff; /* Bianco puro per contrasto elevato */
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 3px 10px rgba(220,53,69,0.15); /* Ombra Rossa */
    margin-bottom: 10px; 
    border-left: 5px solid #dc3545; /* Bordo Rosso forte */
}

/* Player row styling for exclusion */
.player-row-container {
    background-color: white;
    padding: 10px 15px;
    border-radius: 8px;
    margin-bottom: 8px;
    border: 1px solid #e5e7eb;
}
.player-info-text {
    font-size: 1.1rem;
    font-weight: 500;
}
.player-team-text {
    font-weight: bold;
    color: #4b5563;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Utility & Data Loading (Invariate)
# -------------------------
@st.cache_data(show_spinner=False)
def load_excel(source):
    """Carica file excel. Restituisce dizionario fogli squadra e DataFrame arbitri."""
    try:
        if isinstance(source, str) and os.path.exists(source):
            xls = pd.ExcelFile(source)
        elif hasattr(source, 'read'):
            xls = pd.ExcelFile(io.BytesIO(source.read()))
        else:
            return {}, pd.DataFrame(), 0.3

        sheets = xls.sheet_names
        if len(sheets) == 0:
            return {}, pd.DataFrame(), 0.3

        arb_df = pd.read_excel(xls, sheet_name=sheets[-1])
        arb_df.columns = [str(c).strip() for c in arb_df.columns]
        
        teams = {}
        for s in sheets[:-1]:
            df = pd.read_excel(xls, sheet_name=s)
            df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
            required = ['Player', 'Pos', 'Cartellini Gialli Totali', '90s Giocati Totali']
            if all(c in df.columns for c in required):
                df = df.dropna(subset=['Player', 'Pos']).fillna(0)
                teams[s] = df
        
        total_g, total_90 = 0, 0
        for tdf in teams.values():
            total_g += tdf['Cartellini Gialli Totali'].sum()
            total_90 += tdf['90s Giocati Totali'].sum()
        global_avg = (total_g / total_90) if total_90 > 0 else 0.3
        return teams, arb_df, global_avg
    except Exception as e:
        st.error(f"Errore caricamento Excel: Assicurati che il file 'Il Mostro 5.0.xlsx' sia presente e che 'openpyxl' sia installato (controlla requirements.txt). Dettaglio: {e}")
        return {}, pd.DataFrame(), 0.3

def calculate_referee_index(ref_row, arb_medie):
    try:
        if ref_row is None or ref_row.empty: return 1.0, 'Media'
        gialli = pd.to_numeric(ref_row.get('Gialli a partita', ref_row.get('Gialli', np.nan)), errors='coerce')
        gialli = float(gialli) if not pd.isna(gialli) else arb_medie.get('gialli', 4.0)
        rossi = pd.to_numeric(ref_row.get('Rossi a partita', ref_row.get('Rossi', np.nan)), errors='coerce')
        rossi = float(rossi) if not pd.isna(rossi) else arb_medie.get('rossi', 0.2)
        falli = pd.to_numeric(ref_row.get('Falli a partita', ref_row.get('Falli', np.nan)), errors='coerce')
        falli = float(falli) if not pd.isna(falli) else arb_medie.get('falli', 25.0)

        norm = (gialli / (arb_medie['gialli'] if arb_medie['gialli']>0 else LEAGUE_AVG_MATCH_CARDS)) * 0.7
        norm += (rossi / (arb_medie['rossi'] if arb_medie['rossi']>0 else 0.2)) * 0.15
        norm += (falli / (arb_medie['falli'] if arb_medie['falli']>0 else 25.0)) * 0.15

        severity = max(0.6, norm)
        if severity > 1.25: cat = 'Alta'
        elif severity < 0.85: cat = 'Bassa'
        else: cat = 'Media'
        return round(severity, 3), cat
    except Exception:
        return 1.0, 'Media'

def estimate_match_total_cards(ref_index, home_df, away_df):
    baseline = LEAGUE_AVG_MATCH_CARDS * (0.9 + 0.3 * (ref_index - 1.0))
    baseline = np.clip(baseline, 3.0, 8.0)
    
    def team_avg(df):
        if df is None or df.empty: return LEAGUE_AVG_MATCH_CARDS/2
        total_g = df['Cartellini Gialli Totali'].sum()
        total_90 = df['90s Giocati Totali'].sum()
        games = max(1.0, total_90/11.0)
        return total_g / games

    h_avg = team_avg(home_df)
    a_avg = team_avg(away_df)
    team_factor = (h_avg + a_avg) / (2 * LEAGUE_AVG_MATCH_CARDS)
    est = baseline * (0.85 + 0.35 * team_factor)
    return float(np.clip(est, 3.5, 8.0))

def calculate_player_risk(row, global_avg, is_home=True, ref_index=1.0):
    try:
        pos = str(row.get('Pos', '')).upper()
        if 'GK' in pos: return 0.0

        g_tot = float(pd.to_numeric(row.get('Cartellini Gialli Totali', 0), errors='coerce') or 0)
        n90 = float(pd.to_numeric(row.get('90s Giocati Totali', 0), errors='coerce') or 0)
        g_curr = float(pd.to_numeric(row.get('Cartellini Gialli 25/26', 0), errors='coerce') or 0)
        n90_curr = float(pd.to_numeric(row.get('90s Giocati 25/26', 0), errors='coerce') or 0)
        falli = float(pd.to_numeric(row.get('Falli Fatti Totali', 0), errors='coerce') or 0)

        n90_stab = n90 + (STABILIZATION_K if n90 < 5 else 0)
        n90c_stab = n90_curr + (STABILIZATION_K if n90_curr < 5 else 0)
        base_rate = (g_tot / n90_stab) if n90_stab>0 else global_avg
        trend_rate = (g_curr / n90c_stab) if n90c_stab>0 else base_rate

        w_base = 0.7
        risk = base_rate * w_base + trend_rate * (1 - w_base)

        if n90 > 0:
            foul_intensity = (falli / n90)
            risk *= (1 + np.log1p(foul_intensity) * 0.25)

        if any(x in pos for x in ['ATT', 'FW', 'ST']): pos_mod = 0.85
        elif any(x in pos for x in ['MF', 'CC', 'CM']): pos_mod = 0.98
        else: pos_mod = 1.0
        risk *= pos_mod
        risk *= (1.06 if is_home else 0.94)
        risk *= (1 + (ref_index - 1.0) * 0.08)

        return float(max(0, risk))
    except Exception:
        return 0.0

def risk_to_probability(risk, expected_total):
    if risk <= 0: return 0.0
    center = 6.5
    scale = 1.0
    raw = MAX_INDIVIDUAL_PROBABILITY * (1 / (1 + np.exp(-scale * (risk - center))))

    stress = min(1.0, expected_total / LEAGUE_AVG_MATCH_CARDS)
    cap = MAX_INDIVIDUAL_PROBABILITY * (0.88 + 0.12 * stress)
    cap = min(cap, MAX_INDIVIDUAL_PROBABILITY)

    normalized = raw / cap if cap>0 else 0
    final = cap * (normalized ** 0.92)
    return float(np.clip(final, 0.0, MAX_INDIVIDUAL_PROBABILITY))

def exclude_player(player_name):
    """Rimuove un giocatore dai risultati combinati e aggiorna lo stato."""
    if not st.session_state['combined_results'].empty:
        st.session_state['combined_results'] = st.session_state['combined_results'][
            st.session_state['combined_results']['Player'] != player_name
        ].reset_index(drop=True)
        st.toast(f"❌ Giocatore {player_name} escluso!", icon='🚫')
        st.rerun()

# -------------------------
# Main Application Logic
# -------------------------

def main():
    # Intestazione minimal
    st.markdown('<div class="main-header">Il Mostro 5.0 ⚽</div>', unsafe_allow_html=True)
    st.markdown('***') 

    # Inizializzazione stato
    state_defaults = {
        'combined_results': pd.DataFrame(), 'home_team': '', 'away_team': '', 
        'est_total': 0.0, 'ref_cat': '', 'ref_name': ''
    }
    for k, v in state_defaults.items():
        if k not in st.session_state: st.session_state[k] = v

    # Caricamento Dati
    teams, arbitri, global_avg = None, None, 0.3
    with st.sidebar:
        st.header("Caricamento Dati 📂")
        if os.path.exists(EXCEL_FILE_NAME):
            teams, arbitri, global_avg = load_excel(EXCEL_FILE_NAME)
            if teams and not arbitri.empty:
                st.success(f"Dati caricati da {EXCEL_FILE_NAME}")
        
        if not teams or arbitri is None or arbitri.empty:
             uploaded = st.file_uploader('Carica file Excel (Il Mostro 5.0.xlsx)', type=['xlsx'])
             if uploaded is not None:
                teams, arbitri, global_avg = load_excel(uploaded)
                if teams and not arbitri.empty:
                    st.success('File caricato con successo.')


    if not teams or arbitri is None or arbitri.empty:
        st.error('⚠️ Carica un file Excel valido per procedere.')
        st.stop()

    team_names = sorted(teams.keys())
    ref_name_col = 'Nome' if 'Nome' in arbitri.columns else arbitri.columns[0]
    arb_medie = {'gialli': arbitri.get('Gialli a partita', pd.Series()).mean() if 'Gialli a partita' in arbitri.columns else 4.0,
                 'rossi': arbitri.get('Rossi a partita', pd.Series()).mean() if 'Rossi a partita' in arbitri.columns else 0.2,
                 'falli': arbitri.get('Falli a partita', pd.Series()).mean() if 'Falli a partita' in arbitri.columns else 25.0}

    # 1. Configurazione Partita
    st.subheader('1. Configura Partita 🏟️')
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            home = st.selectbox('Squadra Casa', team_names, index=team_names.index(st.session_state['home_team']) if st.session_state['home_team'] in team_names else 0, key='home_sel')
        with c2:
            away_options = [t for t in team_names if t!=home]
            away_index = away_options.index(st.session_state['away_team']) if st.session_state['away_team'] in away_options else 0
            away = st.selectbox('Squadra Trasferta', away_options, index=away_index, key='away_sel')
        with c3:
            ref_name = st.selectbox('Arbitro', sorted(arbitri[ref_name_col].astype(str).unique().tolist()), key='ref_sel')
            st.caption(f"**Data:** {datetime.now().strftime('%Y-%m-%d')}")

    st.markdown('***')
    st.subheader('2. Esegui Pronostico 🧠')

    if st.button('CALCOLA PRONOSTICO AI 🚀', use_container_width=True):
        st.session_state['home_team'] = home
        st.session_state['away_team'] = away
        
        with st.spinner(f'Analizzando {home} vs {away} con arbitro {ref_name}...'):
            home_df = teams.get(home).copy()
            away_df = teams.get(away).copy()
            ref_row = arbitri[arbitri[ref_name_col] == ref_name].iloc[0] if not arbitri[arbitri[ref_name_col] == ref_name].empty else None
            ref_index, ref_cat = calculate_referee_index(ref_row, arb_medie)
            est_total = estimate_match_total_cards(ref_index, home_df, away_df)

            home_df['Risk'] = home_df.apply(lambda r: calculate_player_risk(r, global_avg, True, ref_index), axis=1)
            away_df['Risk'] = away_df.apply(lambda r: calculate_player_risk(r, global_avg, False, ref_index), axis=1)
            home_r = home_df[home_df['Risk']>0].sort_values('Risk', ascending=False).reset_index(drop=True)
            away_r = away_df[away_df['Risk']>0].sort_values('Risk', ascending=False).reset_index(drop=True)

            home_r['Prob %'] = home_r['Risk'].apply(lambda x: round(risk_to_probability(x, est_total),1))
            away_r['Prob %'] = away_r['Risk'].apply(lambda x: round(risk_to_probability(x, est_total),1))

            combined = pd.concat([
                home_r[['Player', 'Pos', 'Risk', 'Prob %']].assign(Team=home), 
                away_r[['Player', 'Pos', 'Risk', 'Prob %']].assign(Team=away)
            ])
            combined['Risk'] = combined['Risk'].round(3)
            combined = combined.sort_values('Risk', ascending=False).reset_index(drop=True)
            
            st.session_state['combined_results'] = combined.copy()
            st.session_state['est_total'] = est_total
            st.session_state['ref_cat'] = ref_cat
            st.session_state['ref_name'] = ref_name
            
        st.rerun()

    if not st.session_state['combined_results'].empty:
        est_total = st.session_state['est_total']
        ref_cat = st.session_state['ref_cat']
        ref_name = st.session_state['ref_name']
        current_combined = st.session_state['combined_results'].copy()
        
        total_risk_current = current_combined['Risk'].sum()
        home_share = (current_combined[current_combined['Team']==st.session_state['home_team']]['Risk'].sum() / total_risk_current * 100) if total_risk_current > 0 else 50.0
        away_share = 100 - home_share

        # 3. Visualizzazione Risultati
        st.subheader('3. Risultati e Top 4 Consigliati ✨')
        
        # Summary Card (Mobile-Friendly)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"**{st.session_state['home_team']} vs {st.session_state['away_team']}** — Arbitro: **{ref_name}** ({ref_cat})", unsafe_allow_html=True)
        
        # Le metriche sono visualizzate in pila per la leggibilità su mobile (no st.columns)
        st.metric('Stima Totale Gialli', f"{est_total:.2f}")
        st.metric(f'Quota Rischio {st.session_state['home_team']}', f"{home_share:.1f}%")
        st.metric(f'Quota Rischio {st.session_state['away_team']}', f"{away_share:.1f}%")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('***')
        
        # Top 4 Consigliati (Filtro) - FISSO A 4 GIOCATORI
        top4_df = current_combined.head(4).copy()
        st.markdown('#### 🏆 Top 4 Giocatori con Rischio Più Alto')
        st.caption('Usa il pulsante **❌ Escludi** per rimuovere un giocatore non titolare o non disponibile.')

        # Mostra la classifica e i pulsanti di esclusione
        st.markdown('<div style="margin-top: 15px;"></div>', unsafe_allow_html=True)
        if not top4_df.empty:
            for index, row in top4_df.iterrows():
                player = row['Player']
                team = row['Team']
                pos = row['Pos']
                
                # Player Row layout
                with st.container():
                    st.markdown('<div class="player-row-container">', unsafe_allow_html=True)
                    # Colonne ottimizzate per la riga del giocatore
                    col_t, col_p, col_btn = st.columns([1, 2.5, 0.5])
                    
                    with col_t:
                        st.markdown(f'<span class="player-team-text">{team}</span>', unsafe_allow_html=True)
                    with col_p:
                        st.markdown(f'<span class="player-info-text">{player} ({pos})</span>', unsafe_allow_html=True)
                    with col_btn:
                        # Pulsante di esclusione
                        st.button('❌ Escludi', key=f'exclude_{player}_{index}', on_click=exclude_player, args=(player,), help='Rimuovi giocatore non titolare/disponibile', use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info('Nessun giocatore con rischio rilevante trovato (o tutti sono stati esclusi).')

        st.markdown('***')
        
        st.success('Analisi completata.')

    else:
        st.info('Premi "CALCOLA PRONOSTICO AI 🚀" per iniziare l\'analisi.')


if __name__ == '__main__':
    main()
