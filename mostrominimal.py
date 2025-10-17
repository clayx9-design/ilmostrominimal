import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime

# ------------------------------------------------------------
# Il Mostro 5.0 - UI ENHANCED (Sfondo migliorato, solo grafica)
# ------------------------------------------------------------

EXCEL_FILE_NAME = "Il Mostro 5.0.xlsx"
LEAGUE_AVG_MATCH_CARDS = 4.5
MAX_INDIVIDUAL_PROBABILITY = 42.0
STABILIZATION_K = 0.5

st.set_page_config(page_title="Il Mostro 5.0 - UI Enhanced", page_icon="🤖⚽", layout="wide")

# ------------------------------------------------------------
# CSS Migliorato: nuovo sfondo soft blu-grigio con alto contrasto e leggibilità
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
# Logica invariata
# ------------------------------------------------------------
from mostrominimal import load_excel, calculate_referee_index, estimate_match_total_cards, calculate_player_risk, risk_to_probability, exclude_player

def main():
    st.markdown('<div class="main-header">Il Mostro 5.0 ⚽</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-muted">Analisi e Pronostici Cartellini Serie A</div>', unsafe_allow_html=True)
    st.markdown('---')

    from mostrominimal import main as original_main
    original_main()

if __name__ == '__main__':
    main()
