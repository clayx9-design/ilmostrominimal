import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
warnings.filterwarnings('ignore')

# Configurazione pagina
st.set_page_config(
    page_title="⚽ Il Mostro 5.0 - Predittore Cartellini Pro Enhanced",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato migliorato
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.8rem;
        border-radius: 18px;
        color: white;
        text-align: center;
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        margin-bottom: 1.2rem;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .prediction-high {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
        border-left: 5px solid #ff4757;
    }
    
    .prediction-medium {
        background: linear-gradient(135deg, #feca57, #ff9ff3);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(254, 202, 87, 0.4);
        border-left: 5px solid #ffa502;
    }
    
    .prediction-low {
        background: linear-gradient(135deg, #48dbfb, #0abde3);
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.8rem 0;
        box-shadow: 0 6px 20px rgba(72, 219, 251, 0.4);
        border-left: 5px solid #00a8ff;
    }
    
    .formula-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 6px solid #667eea;
        color: #2c3e50;
        font-family: 'Courier New', monospace;
    }
    
    .auto-load-info {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    .team-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border-left: 6px solid #4ECDC4;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-top: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

class EnhancedMostroPredictor:
    def __init__(self):
        self.teams_data = {}
        self.referees_data = pd.DataFrame()
        self.QUOTA_MEDIA = 28.5
        self.QUOTA_MASSIMA = 41.0
        self.QUOTA_MINIMA = 15.0
        
        # Parametri della formula avanzata
        self.MEDIA_ASSOLUTA_PARTITE_PER_GIALLO = 5.2  # Media campionato
        self.MEDIA_ASSOLUTA_FALLI_PER_GIALLO = 6.8    # Media campionato
    
    def _process_data_frame(self, df_raw):
        """Esegue la pulizia e la conversione dei tipi per il DataFrame."""
        df = df_raw.copy()
        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
        
        df = df.fillna(0)
        
        numeric_cols = [
            'Cartellini Gialli Totali', '90s Giocati Totali', 
            'Cartellini Gialli 25/26', '90s Giocati 25/26', 
            'Falli Fatti Totali', 'Falli Fatti 25/26',
            'Media 90s per Cartellino Totale', 'Media 90s per Cartellino 25/26',
            'Media Falli per Cartellino Totale', 'Media Falli per Cartellino 25/26',
            'Ritardo Cartellino (Partite)', # COLONNA CRITICA PER IL RITARDO
            # Colonne arbitri (per la conversione)
            'Gialli a partita', 'Rossi a partita', 'Falli a partita'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df, None

    def auto_load_excel_data(self):
        """Carica automaticamente il file Excel se presente nella directory, leggendo TUTTI i fogli."""
        excel_files = [
            "Il Mostro 5.0.xlsx",
            "il mostro 5.0.xlsx", 
            "IL MOSTRO 5.0.xlsx",
            "Il_Mostro_5.0.xlsx"
        ]
        
        for filename in excel_files:
            if os.path.exists(filename):
                try:
                    sheets_dict = pd.read_excel(filename, sheet_name=None)
                    
                    teams_loaded_count = 0
                    referee_loaded = False
                    
                    for sheet_name, df_raw in sheets_dict.items():
                        
                        df, error_msg = self._process_data_frame(df_raw)
                        
                        if df is None or len(df) == 0:
                            continue
                            
                        # LOGICA CARICAMENTO ARBITRI 
                        ref_sheet_keywords = ['arbitri', 'referee', 'ref']
                        is_referee_sheet_name = any(kw in sheet_name.lower() for kw in ref_sheet_keywords)
                        referee_stats_cols = ['Gialli a partita', 'Rossi a partita']
                        has_referee_stats = any(col in df.columns for col in referee_stats_cols)
                        ref_col_name = next((col for col in df.columns if 'nome' in col.lower() or 'arbitro' in col.lower()), None)

                        if (is_referee_sheet_name or has_referee_stats) and ref_col_name:
                            self.referees_data = df.copy()
                            referee_loaded = True
                            continue

                        # LOGICA CARICAMENTO SQUADRE 
                        required_cols_team = ['Player', 'Pos']
                        if all(col in df.columns for col in required_cols_team):
                            df_team = df.dropna(subset=['Player', 'Pos']).copy()
                            if len(df_team) > 0:
                                self.teams_data[sheet_name] = df_team
                                teams_loaded_count += 1
                                
                    
                    if teams_loaded_count > 0:
                        ref_status = "Arbitri caricati" if referee_loaded else "Arbitri NON caricati"
                        return True, f"✅ File '{filename}' caricato. Caricate **{teams_loaded_count}** squadre (da {len(sheets_dict)} fogli). {ref_status}."
                    
                except Exception as e:
                    continue
        
        return False, "❌ Nessun file 'Il Mostro 5.0.xlsx' trovato nella directory o i dati non sono validi."
        
    def load_csv_data(self, uploaded_files):
        """Carica i dati dai file CSV/XLSX caricati dall'utente (squadre e arbitri)"""
        if not uploaded_files:
            return False, "Nessun file caricato."

        self.teams_data = {}
        self.referees_data = pd.DataFrame()
        teams_loaded = 0
        referee_loaded = False

        for file in uploaded_files:
            try:
                if file.name.endswith('.csv'):
                    df_raw = pd.read_csv(file)
                else:
                    df_raw = pd.read_excel(file, sheet_name=0) 

                base_name = file.name.split(' - ')[-1].replace('.csv', '').replace('.xlsx', '').strip()
                
                df, error_msg = self._process_data_frame(df_raw)
                
                if error_msg or df is None:
                    st.warning(f"Errore nel processare {file.name}: {error_msg}")
                    continue

                if 'Arbitri' in base_name or 'arbitri' in base_name:
                    self.referees_data = df
                    referee_loaded = True
                else:
                    self.teams_data[base_name] = df
                    teams_loaded += 1
                        
            except Exception as e:
                st.warning(f"Errore nel caricamento del file {file.name}: {str(e)}")
                continue
        
        if teams_loaded == 0 and not referee_loaded:
            return False, "Nessuna squadra o arbitro caricato correttamente."
        
        referee_status = "Arbitri caricati" if referee_loaded else "Arbitri NON caricati"
        return True, f"Caricati dati per **{len(self.teams_data)}** squadre e {referee_status}"

    def calculate_referee_factor(self, referee_name):
        """Calcola il fattore di severità dell'arbitro."""
        if self.referees_data.empty:
            return 1.0, "Media", {}

        # CERCA LA COLONNA NOME ARBITRO
        ref_col = next((col for col in self.referees_data.columns if 'nome' in col.lower() or 'arbitro' in col.lower()), None)
        
        if ref_col is None:
            # Se la colonna non è stata trovata, usa un default
            return 1.0, "Media", {}

        referee_row = self.referees_data[self.referees_data[ref_col] == referee_name]
        
        if referee_row.empty:
            return 1.0, "Media", {}
        
        referee_row = referee_row.iloc[0]

        yellow_per_match = pd.to_numeric(referee_row.get('Gialli a partita', 4.5), errors='coerce')
        red_per_match = pd.to_numeric(referee_row.get('Rossi a partita', 0.2), errors='coerce')
        fouls_per_match = pd.to_numeric(referee_row.get('Falli a partita', 25.0), errors='coerce')

        if pd.isna(yellow_per_match): yellow_per_match = 4.5
        if pd.isna(red_per_match): red_per_match = 0.2
        if pd.isna(fouls_per_match): fouls_per_match = 25.0

        severity_index = (
            (yellow_per_match / 4.5) * 0.65 + 
            (red_per_match / 0.2) * 0.20 + 
            (fouls_per_match / 25.0) * 0.15
        )

        if severity_index > 1.3:
            category = "Molto Alta"
        elif severity_index > 1.15:
            category = "Alta"
        elif severity_index < 0.8:
            category = "Bassa"
        elif severity_index < 0.9:
            category = "Media-Bassa"
        else:
            category = "Media"

        return max(0.6, min(1.8, severity_index)), category, {}


    def calculate_enhanced_prediction(self, df_players, team_type, referee_factor, min_quota_perc):
        """
        Calcola la probabilità avanzata di cartellino giallo per ogni giocatore.
        """
        if df_players.empty:
            return pd.DataFrame()

        # 1. Calcolo Indici di Rischio (inverso dei rapporti)
        df_players['Indice Rischio 90s'] = (1 / df_players['Media 90s per Cartellino Totale']).replace(np.inf, 0)
        df_players['Indice Rischio Falli'] = (1 / df_players['Media Falli per Cartellino Totale']).replace(np.inf, 0)

        # 2. Fattore Ritardo (Delay Factor)
        delay_ratio = (df_players['Ritardo Cartellino (Partite)'] / self.MEDIA_ASSOLUTA_PARTITE_PER_GIALLO).clip(lower=0)
        delay_factor = (1 + delay_ratio).clip(upper=2.0) 

        # 3. Calcolo dell'Indice di Rischio Integrato
        df_players['Rischio Integrato'] = (
            (df_players['Indice Rischio 90s'] * 0.40) +
            (df_players['Indice Rischio Falli'] * 0.40)
        )
        
        # 4. Applico il Fattore Ritardo
        df_players['Rischio Cartellino (Avanzato)'] = df_players['Rischio Integrato'] * delay_factor

        # 5. Applicazione Fattore Arbitro
        df_players['Rischio Finale'] = df_players['Rischio Cartellino (Avanzato)'] * referee_factor

        # 6. Conversione in Quota (%)
        max_risk = df_players['Rischio Finale'].max()
        if max_risk > 0:
            df_players['Rischio Scalato'] = (df_players['Rischio Finale'] / max_risk) * 100
        else:
             df_players['Rischio Scalato'] = 0

        range_quota = self.QUOTA_MASSIMA - self.QUOTA_MINIMA
        df_players['Quota (%)'] = self.QUOTA_MASSIMA - (df_players['Rischio Scalato'] / 100) * range_quota
        df_players['Quota (%)'] = df_players['Quota (%)'].clip(lower=self.QUOTA_MINIMA, upper=self.QUOTA_MASSIMA)

        df_players = df_players.sort_values(by='Rischio Finale', ascending=False)
        
        # Rinomina colonne per visualizzazione
        df_players = df_players.rename(columns={
            'Cartellini Gialli Totali': 'Gialli Tot.',
            'Media 90s per Cartellino Totale': 'Media 90s/Giallo',
            'Media Falli per Cartellino Totale': 'Media Falli/Giallo',
            'Ritardo Cartellino (Partite)': 'Ritardo (Partite)' # Nome rinominato per l'output
        })
        
        return df_players

# --- FUNZIONE HELPER PER IL BILANCIAMENTO ---
def get_balanced_top_4(df_ranked, home_team, away_team):
    """
    Seleziona i Top 4 giocatori garantendo un massimo di 3-1 di ripartizione tra le due squadre.
    Seleziona sempre il giocatore con il rischio più alto tra quelli che non violano la regola.
    """
    df_top_4_list = []
    home_count = 0
    away_count = 0
    
    # Itera sulla classifica completa (già ordinata per Rischio Finale)
    for index, row in df_ranked.iterrows():
        if len(df_top_4_list) == 4:
            break
            
        player_team = row['Squadra']
        
        # Logica di bilanciamento (Max 3 per squadra nel Top 4)
        if player_team == home_team:
            if home_count < 3:
                df_top_4_list.append(row)
                home_count += 1
            # Se home_count è 3, ignora questo giocatore e cerca il prossimo che non viola la regola.
        elif player_team == away_team:
            if away_count < 3:
                df_top_4_list.append(row)
                away_count += 1
            # Se away_count è 3, ignora questo giocatore e cerca il prossimo che non viola la regola.
                
    # Ritorna il DataFrame Top 4, riordinato per Rischio Finale
    if not df_top_4_list:
        return pd.DataFrame()
        
    return pd.DataFrame(df_top_4_list).sort_values(by='Rischio Finale', ascending=False)
    
# --- LOGICA APP STREAMLIT ---

# La funzione exclude_player_callback non è più necessaria e il suo codice è stato integrato in run_app
def run_app():
    predictor = EnhancedMostroPredictor()
    
    # Inizializzazione Session State per persistenza dei dati e dello stato
    if 'excluded_players' not in st.session_state:
        st.session_state.excluded_players = []
    if 'prediction_ran' not in st.session_state:
        st.session_state.prediction_ran = False
    if 'df_prediction' not in st.session_state:
        st.session_state.df_prediction = pd.DataFrame()
    if 'prediction_error' not in st.session_state: # Nuovo stato per gli errori
        st.session_state.prediction_error = None
    if 'last_home_team' not in st.session_state:
        st.session_state.last_home_team = 'Seleziona Squadra'
        st.session_state.last_away_team = 'Seleziona Squadra'
        st.session_state.last_referee = 'Arbitro Non Caricato'

    st.markdown('<div class="main-header">⚽ Il Mostro 5.0 - Predittore Cartellini Pro Enhanced</div>', unsafe_allow_html=True)

    # --- Caricamento Dati ---
    st.sidebar.header("📂 Caricamento Dati")
    uploaded_files = st.sidebar.file_uploader(
        "Carica file CSV/XLSX per Squadre e Arbitri (es. SQUADRA_A.csv, SQUADRA_B.csv, ARBITRI.csv)",
        type=['csv', 'xlsx'],
        accept_multiple_files=True
    )
    
    # Tenta caricamento manuale
    if uploaded_files:
        success, message = predictor.load_csv_data(uploaded_files) 
        st.sidebar.info(message)
    
    # Tenta caricamento automatico
    if not predictor.teams_data:
        success_auto, message_auto = predictor.auto_load_excel_data()
        st.sidebar.info(message_auto)
        
    team_names = sorted(list(predictor.teams_data.keys()))
    
    referee_names = ['Arbitro Non Caricato']
    referee_col = next((col for col in predictor.referees_data.columns if 'nome' in col.lower() or 'arbitro' in col.lower()), None)
    
    # Controlla ref_col prima di usarlo per filtrare i nomi
    if not predictor.referees_data.empty and referee_col:
        # Se la colonna esiste, usala per popolare il selectbox
        referee_names = sorted(predictor.referees_data[referee_col].unique().tolist())
    elif not predictor.referees_data.empty:
        # Fallback se i dati arbitri sono caricati ma la colonna nome è incerta
        if len(predictor.referees_data.columns) > 0:
            referee_names = sorted(predictor.referees_data.iloc[:, 0].unique().tolist())
        
    # --- IMPOSTAZIONI PARTITA (HOME/AWAY/ARBITRO) ---
    st.header("⚙️ Impostazioni Partita")
    
    col_home, col_away, col_ref = st.columns(3)
    
    with col_home:
        selected_home = st.selectbox("Squadra di Casa 🏠", options=["Seleziona Squadra"] + team_names, key='home_team')
    
    with col_away:
        options_away = [t for t in team_names if t != selected_home]
        selected_away = st.selectbox("Squadra in Trasferta 🚌", options=["Seleziona Squadra"] + options_away, key='away_team')
        
    with col_ref:
        selected_referee = st.selectbox("Arbitro 👨‍⚖️", options=referee_names, key='referee')

    # --- LOGICA DI RESET E TASTO DI AVVIO ---
    
    # Logica di reset: se le selezioni principali sono cambiate, resetta lo stato
    if selected_home != st.session_state.last_home_team or \
       selected_away != st.session_state.last_away_team or \
       selected_referee != st.session_state.last_referee:
        
        if selected_home != 'Seleziona Squadra' and selected_away != 'Seleziona Squadra':
            st.session_state.prediction_ran = False
            st.session_state.df_prediction = pd.DataFrame()
            st.session_state.prediction_error = None
            st.session_state.excluded_players = []
            
        st.session_state.last_home_team = selected_home
        st.session_state.last_away_team = selected_away
        st.session_state.last_referee = selected_referee


    is_ready_to_run = selected_home != "Seleziona Squadra" and selected_away != "Seleziona Squadra" and selected_referee != "Arbitro Non Caricato" and selected_home != selected_away
    
    if is_ready_to_run:
        st.markdown("---")
        
        # Pulsante che attiva il calcolo e aggiorna lo stato
        if st.button("▶️ **Avvia Predizione e Calcolo Ritardo**", type="primary"):
            
            # 1. Preparazione e Calcolo
            min_quota_perc = predictor.QUOTA_MINIMA 
            ref_factor, ref_category, ref_stats = predictor.calculate_referee_factor(selected_referee)
            
            df_home = predictor.teams_data.get(selected_home, pd.DataFrame()).copy()
            df_away = predictor.teams_data.get(selected_away, pd.DataFrame()).copy()
            
            df_home['Squadra'] = selected_home
            df_away['Squadra'] = selected_away
            df_all_players = pd.concat([df_home, df_away], ignore_index=True)
            
            # --- CHECK CRITICO DATI RITARDO ---
            RITARDO_COL_NAME = 'Ritardo Cartellino (Partite)'
            
            # Assicurati che la colonna esista nel DF combinato PRIMA di calcolare
            if RITARDO_COL_NAME not in df_all_players.columns:
                st.session_state.prediction_ran = True 
                st.session_state.df_prediction = pd.DataFrame() 
                st.session_state.prediction_error = f"❌ **ERRORE DATI CRITICI RITARDO:** La colonna '{RITARDO_COL_NAME}' è **mancante** in almeno uno dei fogli squadra. Assicurati che il nome sia corretto (case-sensitive)."
                st.rerun()
                return
                
            # Assicurati che il dato non sia composto solo da zeri/NaN
            ritardo_data = pd.to_numeric(df_all_players[RITARDO_COL_NAME], errors='coerce').fillna(0)
            if ritardo_data.sum() == 0 and ritardo_data.count() > 0:
                 st.session_state.prediction_ran = True 
                 st.session_state.df_prediction = pd.DataFrame() 
                 st.session_state.prediction_error = f"⚠️ **AVVISO DATI RITARDO:** La colonna '{RITARDO_COL_NAME}' è presente ma contiene solo valori zero. Il calcolo del Ritardo non sarà efficace."
                 # Continua il calcolo ma avvisa

            # 2. Esecuzione Calcolo Predizione
            df_prediction_result = predictor.calculate_enhanced_prediction(df_all_players, 'Home', ref_factor, min_quota_perc)
            
            # Salva il risultato nel Session State
            st.session_state.df_prediction = df_prediction_result
            st.session_state.prediction_ran = True
            st.session_state.ref_factor = ref_factor
            st.session_state.ref_category = ref_category
            
            st.rerun()
            
        # Logica di visualizzazione dei risultati (attiva solo se la predizione è stata eseguita)
        elif st.session_state.prediction_ran: 
            
            # Mostra l'errore o l'avviso se presente
            if st.session_state.prediction_error:
                st.error(st.session_state.prediction_error)
                # Resetta l'errore dopo averlo mostrato per non bloccare l'app se è solo un AVVISO
                if "AVVISO DATI RITARDO" in st.session_state.prediction_error:
                    pass 
                else:
                    return # Blocchiamo se è un errore critico

            # 0. Info Arbitro
            st.header(f"🔮 Risultati Predizione: {st.session_state.last_home_team} vs {st.session_state.last_away_team}")
            st.info(f"Fattore Severità Arbitro **{st.session_state.last_referee}**: **{st.session_state.ref_category}** (Fattore: {st.session_state.ref_factor:.2f})")
            
            # Recupera il df dal session state
            df_prediction = st.session_state.df_prediction.copy()
            
            # 4. Applicazione Logica di Esclusione
            if st.session_state.excluded_players:
                df_prediction_filtered = df_prediction[~df_prediction['Player'].isin(st.session_state.excluded_players)]
                exclusion_list = [f"**{p}**" for p in st.session_state.excluded_players]
                st.warning(f"❌ Giocatori attualmente esclusi: {', '.join(exclusion_list)}.")
            else:
                df_prediction_filtered = df_prediction.copy()

            # --- SEZIONE 1: TOP 4 PREDIZIONE RISCHIO CON BILANCIAMENTO ---
            if not df_prediction_filtered.empty:
                
                # CHIAMATA ALLA FUNZIONE DI BILANCIAMENTO 
                df_top_4 = get_balanced_top_4(
                    df_prediction_filtered, 
                    st.session_state.last_home_team, 
                    st.session_state.last_away_team
                )
                
                st.subheader("🚨 Top 4 Probabili Ammoniti per Partita (Max 3-1 Bilanciato)")
                
                # Calcola il bilanciamento finale
                home_count_final = sum(1 for p in df_top_4['Squadra'] if p == st.session_state.last_home_team)
                away_count_final = len(df_top_4) - home_count_final
                st.caption(f"Bilanciamento Top 4: **{home_count_final}** per {st.session_state.last_home_team} vs **{away_count_final}** per {st.session_state.last_away_team}")
                
                cols = st.columns([0.5, 2.5, 1, 1.5, 1])
                cols[0].markdown("**#**", unsafe_allow_html=True)
                cols[1].markdown("**Giocatore (Squadra)**", unsafe_allow_html=True)
                cols[2].markdown("**Pos**", unsafe_allow_html=True)
                cols[3].markdown("**Quota (%)**", unsafe_allow_html=True)
                cols[4].markdown("**Azione**", unsafe_allow_html=True)
                st.markdown("---")
                
                for i, (index, row) in enumerate(df_top_4.iterrows()):
                    player_name = row['Player']
                    
                    col_i = st.columns([0.5, 2.5, 1, 1.5, 1])
                    
                    col_i[0].write(i + 1)
                    col_i[1].markdown(f"**{player_name}** ({row['Squadra']})")
                    col_i[2].write(row['Pos'])
                    
                    quota_text = f"**{row['Quota (%)']:.2f}**"
                    if row['Quota (%)'] < 20:
                        col_i[3].markdown(f'<div style="color: #c0392b; font-weight: bold;">{quota_text}</div>', unsafe_allow_html=True)
                    elif row['Quota (%)'] < 25:
                        col_i[3].markdown(f'<div style="color: #f39c12; font-weight: bold;">{quota_text}</div>', unsafe_allow_html=True)
                    else:
                        col_i[3].markdown(quota_text, unsafe_allow_html=True)
                        
                    with col_i[4]:
                        if st.button(
                            "❌ Escludi", 
                            key=f'exclude_{player_name}_{i}'
                        ):
                            if player_name in st.session_state.excluded_players:
                                st.session_state.excluded_players.remove(player_name)
                            else:
                                st.session_state.excluded_players.append(player_name)
                            
                            st.rerun()
                    
                st.markdown("---")

                # --- SEZIONE 2: CLASSIFICA RITARDO CARTELLINO ---
                st.subheader("⏰ Classifica Ritardo Cartellino (Giocatori 'in debito')")
                
                # Filtra e mostra i top 10 con ritardo positivo (utilizzando il DF salvato)
                df_delay = df_prediction[df_prediction['Ritardo (Partite)'] > 0].copy()
                df_delay = df_delay.sort_values(by='Ritardo (Partite)', ascending=False).head(10)
                
                if not df_delay.empty:
                    st.dataframe(
                        df_delay[['Player', 'Squadra', 'Pos', 'Ritardo (Partite)', 'Gialli Tot.']].style.format({
                            'Ritardo (Partite)': "{:.2f}"
                        }), 
                        use_container_width=True,
                        hide_index=True
                    )
                    st.caption("Il **Ritardo** indica di quante partite il giocatore è 'in debito' rispetto alla media campionato. Maggiore è il valore, maggiore è la probabilità statistica di prendere un cartellino.")
                else:
                    st.info("Nessun giocatore ha un ritardo positivo di cartellino in questa partita.")
                
                st.markdown("---")
                
                # --- SEZIONE 3: CLASSIFICA COMPLETA ---
                st.subheader("Classifica Completa Rischio Cartellini (Tutti i Giocatori)")
                
                display_cols = ['Player', 'Squadra', 'Pos', 'Quota (%)', 'Rischio Finale', 'Media 90s/Giallo', 'Media Falli/Giallo', 'Ritardo (Partite)', 'Gialli Tot.']
                
                display_df = df_prediction[display_cols].copy().rename(columns={
                    'Rischio Finale': 'Rischio'
                })
                
                display_df.insert(0, 'Escluso', display_df['Player'].apply(lambda x: '❌' if x in st.session_state.excluded_players else ''))

                st.dataframe(
                    display_df.style.format({
                        'Quota (%)': "{:.2f}", 
                        'Rischio': "{:.3f}", 
                        'Media 90s/Giallo': "{:.2f}",
                        'Media Falli/Giallo': "{:.2f}",
                        'Ritardo (Partite)': "{:.2f}"
                    }), 
                    use_container_width=True,
                    hide_index=True
                )
            
            else:
                st.warning("Nessun giocatore rientra nei criteri di Quota Minima o la classifica è vuota.")
            
    else:
        st.info("Seleziona la squadra di casa, quella in trasferta e l'arbitro (e assicurati che le squadre siano diverse) e premi il tasto Avvia Predizione.")


if __name__ == '__main__':
    run_app()
