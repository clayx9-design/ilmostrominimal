import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime

# ------------------------------------------------------------
# Il Mostro 5.0 - Ultra UI (Web + Mobile Responsive)
# ------------------------------------------------------------

EXCEL_FILE_NAME = "Il Mostro 5.0.xlsx"
LEAGUE_AVG_MATCH_CARDS = 4.5
MAX_INDIVIDUAL_PROBABILITY = 42.0
STABILIZATION_K = 0.5

st.set_page_config(page_title="Il Mostro 5.0 - Ultra UI", page_icon="🤖⚽", layout="wide")

# --- CSS Responsive + Color Contrast Upgrade ---
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
    background: #f9fafc;
    color: #0b3d91;
    scroll-behavior: smooth;
}

/* Header */
.main-header {
    font-size: 2.6rem;
    font-weight: 900;
    color: #0b3d91;
    text-align: center;
    margin-bottom: 0.5rem;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
}
.sub-header {
    text-align: center;
    color: #475569;
    margin-bottom: 2rem;
}

/* Buttons */
.stButton>button {
    border-radius: 12px;
    font-weight: 700;
    padding: 0.75em 1.5em;
    color: white;
    background: linear-gradient(135deg, #0b3d91, #2563eb);
    border: none;
    transition: all 0.3s ease-in-out;
    box-shadow: 0 4px 15px rgba(37,99,235,0.4);
}
.stButton>button:hover {
    background: linear-gradient(135deg, #2563eb, #0b3d91);
    transform: translateY(-2px);
}

/* Card Style */
.card {
    background: white;
    border-radius: 18px;
    padding: 1.5rem;
    box-shadow: 0 10px 25px rgba(11,61,145,0.1);
    margin-bottom: 2rem;
}

/* Metrics */
.stMetric {
    background-color: #eef4ff !important;
    border-radius: 12px;
    padding: 12px !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* Player Card */
.player-card {
    background: white;
    border: 2px solid #e2e8f0;
    border-left: 5px solid #2563eb;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease-in-out;
}
.player-card:hover {
    transform: scale(1.01);
    box-shadow: 0 6px 18px rgba(37,99,235,0.15);
}

.player-name {
    font-weight: 700;
    color: #0b3d91;
}
.player-pos {
    color: #475569;
    font-size: 0.9rem;
}
.player-team {
    color: #1d4ed8;
    font-weight: 500;
}

/* Mobile Responsive Tweaks */
@media (max-width: 768px) {
    .main-header { font-size: 1.9rem; }
    .card { padding: 1rem; }
    .player-card { padding: 0.8rem; }
    .stButton>button { font-size: 0.9rem; }
}
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data(show_spinner=False)
def load_excel(source):
    try:
        if isinstance(source, str) and os.path.exists(source):
            xls = pd.ExcelFile(source)
        elif hasattr(source, 'read'):
            xls = pd.ExcelFile(io.BytesIO(source.read()))
        else:
            return {}, pd.DataFrame(), 0.3
        sheets = xls.sheet_names
        if not sheets:
            return {}, pd.DataFrame(), 0.3
        arbitri = pd.read_excel(xls, sheet_name=sheets[-1])
        arbitri.columns = [str(c).strip() for c in arbitri.columns]
        teams = {}
        for s in sheets[:-1]:
            df = pd.read_excel(xls, sheet_name=s)
            df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
            if all(c in df.columns for c in ['Player', 'Pos', 'Cartellini Gialli Totali', '90s Giocati Totali']):
                df = df.dropna(subset=['Player', 'Pos']).fillna(0)
                teams[s] = df
        total_g, total_90 = 0, 0
        for df in teams.values():
            total_g += df['Cartellini Gialli Totali'].sum()
            total_90 += df['90s Giocati Totali'].sum()
        global_avg = (total_g / total_90) if total_90 > 0 else 0.3
        return teams, arbitri, global_avg
    except Exception as e:
        st.error(f"Errore nel caricamento Excel: {e}")
        return {}, pd.DataFrame(), 0.3

# --- Calculation Functions ---
def calc_referee_index(ref_row, medie):
    if ref_row is None or ref_row.empty:
        return 1.0, 'Media'
    g = float(pd.to_numeric(ref_row.get('Gialli a partita', 4.0), errors='coerce') or 4.0)
    r = float(pd.to_numeric(ref_row.get('Rossi a partita', 0.2), errors='coerce') or 0.2)
    f = float(pd.to_numeric(ref_row.get('Falli a partita', 25.0), errors='coerce') or 25.0)
    sev = (g / medie['gialli']) * 0.7 + (r / medie['rossi']) * 0.15 + (f / medie['falli']) * 0.15
    cat = 'Alta' if sev > 1.25 else ('Bassa' if sev < 0.85 else 'Media')
    return round(sev, 2), cat

def calc_player_risk(row, global_avg, is_home=True, ref_index=1.0):
    try:
        pos = str(row.get('Pos', '')).upper()
        if 'GK' in pos: return 0
        g = float(row.get('Cartellini Gialli Totali', 0))
        n90 = float(row.get('90s Giocati Totali', 1))
        foul = float(row.get('Falli Fatti Totali', 0))
        base = g / n90 if n90 > 0 else global_avg
        risk = base * (1 + np.log1p(foul/n90) * 0.25)
        if any(x in pos for x in ['ATT','FW','ST']): risk *= 0.85
        elif any(x in pos for x in ['MF','CC','CM']): risk *= 0.95
        risk *= (1.06 if is_home else 0.94)
        risk *= (1 + (ref_index - 1.0) * 0.08)
        return float(max(0, risk))
    except: return 0

def risk_to_probability(risk, expected):
    if risk <= 0: return 0
    base = MAX_INDIVIDUAL_PROBABILITY / (1 + np.exp(-(risk - 6.5)))
    cap = MAX_INDIVIDUAL_PROBABILITY * (0.9 + 0.1 * min(1, expected / LEAGUE_AVG_MATCH_CARDS))
    norm = base / cap if cap>0 else 0
    return round(cap * (norm ** 0.92),1)

def estimate_total(ref_i, h_df, a_df):
    base = LEAGUE_AVG_MATCH_CARDS * (0.9 + 0.3*(ref_i-1))
    base = np.clip(base,3.0,8.0)
    def team_avg(df):
        if df.empty: return LEAGUE_AVG_MATCH_CARDS/2
        tot = df['Cartellini Gialli Totali'].sum()
        n = df['90s Giocati Totali'].sum()
        return tot / max(1.0, n/11)
    h,a = team_avg(h_df), team_avg(a_df)
    return float(np.clip(base*(0.85+0.35*((h+a)/(2*LEAGUE_AVG_MATCH_CARDS))),3.5,8.0))

# --- Main ---
def main():
    st.markdown('<div class="main-header">Il Mostro 5.0 ⚽</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pronostici Cartellini Serie A — Web & Mobile Optimized</div>', unsafe_allow_html=True)

    teams, arbitri, gavg = (None, None, 0.3)
    if os.path.exists(EXCEL_FILE_NAME):
        teams, arbitri, gavg = load_excel(EXCEL_FILE_NAME)
    else:
        up = st.file_uploader('Carica file Excel (Il Mostro 5.0.xlsx)', type=['xlsx'])
        if up is not None:
            teams, arbitri, gavg = load_excel(up)

    if not teams or arbitri is None or arbitri.empty:
        st.error('⚠️ Carica un file Excel valido con squadre e arbitri.')
        st.stop()

    tnames = sorted(teams.keys())
    ref_col = 'Nome' if 'Nome' in arbitri.columns else arbitri.columns[0]
    medie = {
        'gialli': arbitri.get('Gialli a partita', pd.Series()).mean() if 'Gialli a partita' in arbitri.columns else 4.0,
        'rossi': arbitri.get('Rossi a partita', pd.Series()).mean() if 'Rossi a partita' in arbitri.columns else 0.2,
        'falli': arbitri.get('Falli a partita', pd.Series()).mean() if 'Falli a partita' in arbitri.columns else 25.0
    }

    h,a = st.columns(2)
    with h:
        home = st.selectbox('🏠 Squadra Casa', tnames)
    with a:
        away = st.selectbox('🚗 Squadra Trasferta', [t for t in tnames if t!=home])
    ref = st.selectbox('👨‍⚖️ Arbitro', sorted(arbitri[ref_col].astype(str).unique().tolist()))

    if st.button('CALCOLA PRONOSTICO AI 🚀', use_container_width=True):
        hdf, adf = teams[home].copy(), teams[away].copy()
        ref_row = arbitri[arbitri[ref_col]==ref].iloc[0] if not arbitri[arbitri[ref_col]==ref].empty else None
        ref_i, ref_cat = calc_referee_index(ref_row, medie)
        total = estimate_total(ref_i, hdf, adf)
        hdf['Risk'] = hdf.apply(lambda r: calc_player_risk(r,gavg,True,ref_i), axis=1)
        adf['Risk'] = adf.apply(lambda r: calc_player_risk(r,gavg,False,ref_i), axis=1)
        hdf['Prob %'] = hdf['Risk'].apply(lambda x:risk_to_probability(x,total))
        adf['Prob %'] = adf['Risk'].apply(lambda x:risk_to_probability(x,total))

        comb = pd.concat([hdf.assign(Team=home), adf.assign(Team=away)])
        comb = comb[comb['Risk']>0].sort_values('Risk',ascending=False).reset_index(drop=True)
        top4 = comb.head(4)

        st.markdown(f'<div class="card"><h3 style="margin-bottom:0.3rem;">{home} vs {away}</h3><b>Arbitro:</b> {ref} ({ref_cat})<br><br>Stima Totale Gialli: <b>{total:.2f}</b></div>', unsafe_allow_html=True)

        st.subheader('🏆 Top 4 Consigliati')
        for _,row in top4.iterrows():
            st.markdown(f"""
            <div class='player-card'>
                <div class='player-team'>{row['Team']}</div>
                <div class='player-name'>{row['Player']} <span class='player-pos'>({row['Pos']})</span></div>
                <div>🎯 Probabilità: <b>{row['Prob %']}%</b> | 📊 Risk: {row['Risk']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        with st.expander('📋 Classifiche Complete'):
            c1,c2 = st.columns(2)
            with c1:
                st.markdown(f'**{home}**')
                st.dataframe(hdf[['Player','Pos','Risk','Prob %']], use_container_width=True)
            with c2:
                st.markdown(f'**{away}**')
                st.dataframe(adf[['Player','Pos','Risk','Prob %']], use_container_width=True)

        st.success('✅ Analisi completata — ottimizzata per mobile e desktop.')

if __name__=='__main__':
    main()
