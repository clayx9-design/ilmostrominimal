import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime
import time # Aggiunto per simulare il caricamento

# ------------------------------------------------------------
# Il Mostro 5.0 - UI ENHANCED (Sfondo migliorato, solo grafica)
# ------------------------------------------------------------

EXCEL_FILE_NAME = "Il Mostro 5.0.xlsx"
LEAGUE_AVG_MATCH_CARDS = 4.5
MAX_INDIVIDUAL_PROBABILITY = 42.0
STABILIZATION_K = 0.5

st.set_page_config(page_title="Il Mostro 5.0 - UI Enhanced", page_icon="🤖⚽", layout="wide")

# ------------------------------------------------------------
# CSS Migliorato
# ------------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(180deg, #e0e7ff 0%, #f8fafc 60%, #e2e8f0 100%);
    color: #0b3d91;
    scroll-behavior: smooth;
}

/* HEADER */
.main-header {
    font-size: 2.8rem;
    color: #0b3d91;
    font-weight: 900;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 5px;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.15);
}
.small-muted {
    color: #334155;
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 30px;
}

/* BUTTONS */
.stButton>button {
    border-radius: 10px;
    font-weight: 700;
    background: linear-gradient(135deg, #1d4ed8, #0b3d91);
    color: white;
    padding: 0.9rem 1.7rem;
    transition: all 0.3s ease-in-out;
    border: none;
    box-shadow: 0 6px 14px rgba(37,99,235,0.4);
}
.stButton>button:hover {
    background: linear-gradient(135deg, #0b3d91, #1d4ed8);
    transform: translateY(-2px);
}

/* CARDS */
.card {
    background: rgba(255,255,255,0.85);
    border-radius: 20px;
    padding: 1.8rem;
    box-shadow: 0 12px 30px rgba(11,61,145,0.12);
    margin-bottom: 2rem;
    border-left: 6px solid #2563eb;
    backdrop-filter: blur(8px);
}

/* METRIC BOXES */
.stMetric {
    background: linear-gradient(135deg, #e0f2fe, #ffffff);
    border-radius: 12px !important;
    padding: 14px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    text-align: center !important;
}

/* PLAYER ROWS */
.player-row-container {
    background: rgba(255,255,255,0.9);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 3px 10px rgba(11,61,145,0.1);
    transition: all 0.25s ease-in-out;
    border-left: 5px solid #3b82f6;
}
.player-row-container:hover {
    transform: scale(1.02);
    box-shadow: 0 8px 20px rgba(37,99,235,0.2);
}
.player-team-text {
    font-weight: 600;
    color: #1e3a8a;
}
.player-info-text {
    font-size: 1.05rem;
    font-weight: 500;
    color: #0f172a;
}

/* MOBILE OPTIMIZATION */
@media (max-width: 768px) {
    .main-header { font-size: 2.1rem; }
    .stButton>button { font-size: 0.9rem; padding: 0.6rem 1rem; }
    .player-info-text { font-size: 0.95rem; }
    .card { padding: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# LOGICA (Mock-up per l'esecuzione)
# ------------------------------------------------------------

# Mock-up dei dati di esempio
MOCK_DATA = pd.DataFrame({
    'Giocatore': ['Rossi M.', 'Verdi A.', 'Bianchi S.'],
    'Squadra': ['JUV', 'INT', 'MIL'],
    'Partite Giocate': [10, 12, 9],
    'Cartellini Gialli': [3, 4, 2],
    'Cartellini Rossi': [0, 1, 0],
    'Rischio Calcolato': [0.25, 0.35, 0.15]
})

@st.cache_data
def load_excel(file_content):
    """Simula il caricamento e la preparazione dei dati da Excel."""
    time.sleep(1) # Simula un ritardo di caricamento
    return MOCK_DATA.copy()

def calculate_referee_index(data):
    """Simula il calcolo dell'indice dell'arbitro."""
    return 1.12 # Esempio

def estimate_match_total_cards(referee_index, team1, team2):
    """Simula la stima dei cartellini totali in una partita."""
    return 5.1 # Esempio

def calculate_player_risk(player_data):
    """Simula il calcolo del rischio individuale del giocatore."""
    return player_data['Rischio Calcolato'] # Ritorna il rischio mock

def risk_to_probability(risk, match_cards_avg):
    """Simula la conversione del rischio in probabilità in %."""
    prob = risk * (100 / LEAGUE_AVG_MATCH_CARDS) * match_cards_avg
    return np.clip(prob, 0, MAX_INDIVIDUAL_PROBABILITY)

def exclude_player(player_name):
    """Simula l'esclusione di un giocatore (es. per infortunio/squalifica)."""
    return False # Esempio

# ------------------------------------------------------------
# LOGICA PRINCIPALE (Precedentemente 'original_main' non definito)
# ------------------------------------------------------------

def run_analysis():
    """Logica per la visualizzazione dei risultati (mock)."""
    
    st.subheader("Risultati dell'Analisi")

    # 1. Caricamento/Selezione File
    uploaded_file = st.file_uploader("Carica il file Excel di analisi (Il Mostro 5.0.xlsx)", type=["xlsx"])

    if uploaded_file is not None:
        try:
            # Mostra la data di caricamento
            st.info(f"File caricato con successo: {uploaded_file.name} - ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

            # Carica i dati
            data = load_excel(uploaded_file.read())
            
            # Parametri di input per la UI (Mock-up)
            col1, col2 = st.columns(2)
            arbitro_scelto = col1.selectbox("Seleziona l'Arbitro", ['Maresca', 'Orsato', 'La Penna'])
            partita_scelta = col2.selectbox("Seleziona la Partita", ['JUV vs INT', 'MIL vs ROM', 'NAP vs LAZ'])

            # 2. Calcoli (Mock)
            ref_index = calculate_referee_index(data)
            match_cards = estimate_match_total_cards(ref_index, 'TeamA', 'TeamB')

            st.markdown('<div class="card">', unsafe_allow_html=True)
            colA, colB, colC = st.columns(3)
            with colA:
                st.metric("Indice Arbitro", f"{ref_index:.2f}", delta_color="normal")
            with colB:
                st.metric("Cartellini Stimati (Media)", f"{match_cards:.2f}", delta_color="normal")
            with colC:
                st.metric("Probabilità Max Indiv.", f"{MAX_INDIVIDUAL_PROBABILITY:.1f}%", delta_color="off")
            st.markdown('</div>', unsafe_allow_html=True)


            # 3. Calcolo e Visualizzazione del Rischio Giocatori
            data['Rischio'] = calculate_player_risk(data)
            data['Probabilità (%)'] = risk_to_probability(data['Rischio'], match_cards)
            
            st.subheader(f"Pronostici Cartellini per la Partita: {partita_scelta}")

            # Ordina per probabilità (i più rischiosi in alto)
            data_sorted = data.sort_values(by='Probabilità (%)', ascending=False).head(5)

            for index, row in data_sorted.iterrows():
                player = row['Giocatore']
                team = row['Squadra']
                prob = f"{row['Probabilità (%)']:.1f}%"
                
                # Visualizzazione personalizzata (come nel CSS)
                st.markdown(f"""
                <div class="player-row-container">
                    <div>
                        <span class="player-info-text">{player}</span>
                        <br>
                        <span class="player-team-text">{team}</span>
                    </div>
                    <div>
                        <span class="player-info-text" style="color: {'#ef4444' if row['Probabilità (%)'] > 20 else '#f97316'}; font-weight: 700;">{prob}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Errore durante l'elaborazione del file: {e}")
            st.stop()
    else:
        st.info("Per iniziare, carica il file Excel 'Il Mostro 5.0.xlsx' contenente i dati storici.")
    

# ------------------------------------------------------------
# FUNZIONE MAIN - La UI
# ------------------------------------------------------------

def main():
    st.markdown('<div class="main-header">Il Mostro 5.0 ⚽</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-muted">Analisi e Pronostici Cartellini Serie A</div>', unsafe_allow_html=True)
    st.markdown('---')
    
    # Chiama la funzione di analisi corretta
    run_analysis() 

if __name__ == '__main__':
    main()
