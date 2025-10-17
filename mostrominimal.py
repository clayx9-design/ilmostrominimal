import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime

# ------------------------------------------------------------
# Il Mostro 5.0 - UI ENHANCED (Miglioramento solo grafico web/mobile)
# ------------------------------------------------------------

EXCEL_FILE_NAME = "Il Mostro 5.0.xlsx"
LEAGUE_AVG_MATCH_CARDS = 4.5
MAX_INDIVIDUAL_PROBABILITY = 42.0
STABILIZATION_K = 0.5

st.set_page_config(page_title="Il Mostro 5.0 - UI Enhanced", page_icon="🤖⚽", layout="wide")

# ------------------------------------------------------------
# CSS Migliorato: Design fluido, contrasto elevato, mobile responsive
# ------------------------------------------------------------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(180deg, #f9fafc 0%, #eef2ff 100%);
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
    text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
}
.small-muted {
    color: #475569;
    font-size: 1.1rem;
    text-align: center;
    margin-bottom: 30px;
}

/* BUTTONS */
.stButton>button {
    border-radius: 10px;
    font-weight: 700;
    background: linear-gradient(135deg, #2563eb, #0b3d91);
    color: white;
    padding: 0.8rem 1.6rem;
    transition: all 0.3s ease-in-out;
    border: none;
    box-shadow: 0 4px 12px rgba(37,99,235,0.3);
}
.stButton>button:hover {
    background: linear-gradient(135deg, #0b3d91, #2563eb);
    transform: scale(1.03);
}

/* CARDS */
.card {
    background: white;
    border-radius: 18px;
    padding: 1.6rem;
    box-shadow: 0 10px 25px rgba(11,61,145,0.1);
    margin-bottom: 1.8rem;
    border-left: 6px solid #2563eb;
}

/* METRIC BOXES */
.stMetric {
    background: linear-gradient(135deg, #eef4ff, #ffffff);
    border-radius: 12px !important;
    padding: 12px !important;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    text-align: center !important;
}

/* PLAYER ROWS */
.player-row-container {
    background: #ffffff;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.7rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 8px rgba(11,61,145,0.08);
    transition: all 0.2s ease-in-out;
}
.player-row-container:hover {
    transform: scale(1.01);
    box-shadow: 0 6px 15px rgba(37,99,235,0.18);
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
# Tutte le funzioni e logiche rimangono invariate rispetto al file originale
# ------------------------------------------------------------

from mostrominimal import load_excel, calculate_referee_index, estimate_match_total_cards, calculate_player_risk, risk_to_probability, exclude_player

def main():
    st.markdown('<div class="main-header">Il Mostro 5.0 ⚽</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-muted">Analisi e Pronostici Cartellini Serie A</div>', unsafe_allow_html=True)
    st.markdown('---')

    # Riutilizzo della logica invariata dal file di origine
    from mostrominimal import main as original_main
    original_main()

if __name__ == '__main__':
    main()
