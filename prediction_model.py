import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class CardPredictionModel:
    def __init__(self):
        self.yellow_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.red_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def _calculate_base_features(self, df):
        """Calcola features base per la predizione"""
        features = df.copy()
        
        # Normalizzazione per minuti giocati
        features['Falli_per_90min'] = (features['Falli_Commessi'] / features['Minuti_Giocati']) * 90
        features['Gialli_per_90min'] = (features['Cartellini_Gialli'] / features['Minuti_Giocati']) * 90
        features['Rossi_per_90min'] = (features['Cartellini_Rossi'] / features['Minuti_Giocati']) * 90
        
        # Sostituire infiniti e NaN con 0
        features = features.replace([np.inf, -np.inf], 0).fillna(0)
        
        # Fattore età (giocatori giovani e vecchi più inclini ai cartellini)
        features['Fattore_Eta'] = np.where(
            (features['Età'] < 23) | (features['Età'] > 32), 1.2, 1.0
        )
        
        # Fattore posizione (difensori e centrocampisti più a rischio)
        position_risk = {
            'Difensore': 1.3,
            'Centrocampista': 1.2,
            'Attaccante': 1.0,
            'Portiere': 0.5
        }
        features['Fattore_Posizione'] = features['Posizione'].map(position_risk).fillna(1.0)
        
        # Indice aggressività
        features['Indice_Aggressivita'] = (
            features['Falli_per_90min'] * 0.4 +
            features['Gialli_per_90min'] * 0.4 +
            features['Rossi_per_90min'] * 0.2
        )
        
        # Trend recente (simulato con variazione casuale)
        np.random.seed(42)
        features['Trend_Recente'] = np.random.normal(1.0, 0.2, len(features))
        features['Trend_Recente'] = np.clip(features['Trend_Recente'], 0.5, 1.5)
        
        return features
    
    def _get_position_weights(self, position):
        """Restituisce pesi specifici per posizione"""
        weights = {
            'Portiere': {'yellow': 0.3, 'red': 0.2},
            'Difensore': {'yellow': 1.4, 'red': 1.3},
            'Centrocampista': {'yellow': 1.2, 'red': 1.1},
            'Attaccante': {'yellow': 1.0, 'red': 0.9}
        }
        return weights.get(position, {'yellow': 1.0, 'red': 1.0})
    
    def predict_cards(self, df):
        """Predice la probabilità di cartellini per ogni giocatore"""
        features_df = self._calculate_base_features(df)
        
        yellow_risks = []
        red_risks = []
        
        for idx, row in features_df.iterrows():
            # Calcolo rischio cartellino giallo
            yellow_base = (
                row['Falli_per_90min'] * 8 +
                row['Gialli_per_90min'] * 25 +
                row['Indice_Aggressivita'] * 15
            )
            
            # Applicazione fattori correttivi
            position_weights = self._get_position_weights(row['Posizione'])
            yellow_risk = (
                yellow_base * 
                row['Fattore_Eta'] * 
                position_weights['yellow'] * 
                row['Trend_Recente']
            )
            
            # Calcolo rischio cartellino rosso
            red_base = (
                row['Rossi_per_90min'] * 50 +
                row['Falli_per_90min'] * 2 +
                row['Indice_Aggressivita'] * 5
            )
            
            red_risk = (
                red_base * 
                row['Fattore_Eta'] * 
                position_weights['red'] * 
                row['Trend_Recente']
            )
            
            # Normalizzazione e clipping
            yellow_risk = np.clip(yellow_risk, 0, 100)
            red_risk = np.clip(red_risk, 0, 50)  # I rossi sono più rari
            
            yellow_risks.append(yellow_risk)
            red_risks.append(red_risk)
        
        return pd.DataFrame({
            'Rischio_Giallo': yellow_risks,
            'Rischio_Rosso': red_risks
        })
    
    def get_risk_explanation(self, player_data):
        """Fornisce spiegazione del rischio per un giocatore"""
        explanations = []
        
        # Analisi falli
        if player_data['Falli_Commessi'] > 50:
            explanations.append("🔴 Alto numero di falli commessi")
        elif player_data['Falli_Commessi'] > 30:
            explanations.append("🟡 Numero moderato di falli")
        else:
            explanations.append("🟢 Basso numero di falli")
        
        # Analisi storico cartellini
        if player_data['Cartellini_Gialli'] > 8:
            explanations.append("🔴 Storico elevato di cartellini gialli")
        elif player_data['Cartellini_Gialli'] > 4:
            explanations.append("🟡 Storico moderato di cartellini")
        
        # Analisi posizione
        if player_data['Posizione'] in ['Difensore', 'Centrocampista']:
            explanations.append("⚠️ Posizione ad alto rischio cartellini")
        
        # Analisi età
        if player_data['Età'] < 23:
            explanations.append("⚠️ Età giovane, maggiore impulsività")
        elif player_data['Età'] > 32:
            explanations.append("⚠️ Età avanzata, possibili reazioni eccessive")
        
        return explanations
    
    def calculate_team_risk_profile(self, df):
        """Calcola il profilo di rischio per squadra"""
        team_profiles = {}
        
        for team in df['Squadra'].unique():
            team_data = df[df['Squadra'] == team]
            predictions = self.predict_cards(team_data)
            
            profile = {
                'avg_yellow_risk': predictions['Rischio_Giallo'].mean(),
                'avg_red_risk': predictions['Rischio_Rosso'].mean(),
                'high_risk_players': len(predictions[predictions['Rischio_Giallo'] > 70]),
                'total_players': len(team_data)
            }
            
            team_profiles[team] = profile
        
        return team_profiles