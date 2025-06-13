
import pandas as pd
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import time

class EconomicStressTracker:
    def __init__(self):
        self.pytrends = TrendReq(hl='it-IT', tz=60)
        self.stress_keywords = {
            'risparmio': ['come risparmiare', 'risparmiare soldi', 'spese inutili'],
            'lavoro_extra': ['secondo lavoro', 'lavoro part time', 'guadagnare extra'],
            'vendite_desperate': ['vendere auto', 'vendere oro', 'prestito veloce'],
            'assistenza': ['banco alimentare', 'aiuti economici', 'sussidi'],
            'debiti': ['come pagare debiti', 'ristrutturazione debiti', 'fallimento personale']
        }

    def get_trend_data(self, keywords, timeframe='today 12-m', geo='IT'):
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo)
            data = self.pytrends.interest_over_time()
            if not data.empty:
                data = data.drop(columns=['isPartial'], errors='ignore')
            time.sleep(2)
            return data
        except Exception as e:
            print(f"Errore nel raccogliere dati per {keywords}: {e}")
            return pd.DataFrame()

    def calculate_stress_score(self, data):
        if data.empty:
            return pd.Series()
        normalized_data = data.copy()
        for col in data.columns:
            if data[col].max() > 0:
                normalized_data[col] = (data[col] / data[col].max()) * 100
        weights = {
            'come risparmiare': 1.0,
            'secondo lavoro': 1.2,
            'vendere auto': 1.5,
            'banco alimentare': 2.0,
            'come pagare debiti': 1.8
        }
        stress_score = pd.Series(index=data.index, dtype=float)
        total_weight = 0
        for keyword in data.columns:
            weight = weights.get(keyword, 1.0)
            stress_score += normalized_data[keyword] * weight
            total_weight += weight
        return stress_score / total_weight if total_weight > 0 else stress_score

    def collect_all_data(self):
        all_data = {}
        for category, keywords in self.stress_keywords.items():
            category_data = pd.DataFrame()
            for keyword in keywords:
                trend_data = self.get_trend_data([keyword])
                if not trend_data.empty:
                    if category_data.empty:
                        category_data = trend_data.copy()
                    else:
                        category_data = category_data.join(trend_data, how='outer', rsuffix='_dup')
                        category_data = category_data.loc[:, ~category_data.columns.str.contains('_dup')]
            all_data[category] = category_data
        return all_data

    def create_composite_index(self, all_data):
        composite_series = []
        for category, data in all_data.items():
            if not data.empty:
                category_score = self.calculate_stress_score(data)
                category_score.name = category
                composite_series.append(category_score)
        if composite_series:
            composite_df = pd.concat(composite_series, axis=1)
            composite_df['Economic_Stress_Index'] = composite_df.mean(axis=1)
            return composite_df
        else:
            return pd.DataFrame()

    def analyze_trends(self, composite_df):
        if composite_df.empty:
            return {}
        latest_score = composite_df['Economic_Stress_Index'].iloc[-1]
        avg_score = composite_df['Economic_Stress_Index'].mean()
        trend_30d = composite_df['Economic_Stress_Index'].iloc[-4:].mean()
        trend_90d = composite_df['Economic_Stress_Index'].iloc[-12:].mean()
        if latest_score < 20:
            stress_level = "🟢 BASSO"
        elif latest_score < 40:
            stress_level = "🟡 MODERATO"
        elif latest_score < 60:
            stress_level = "🟠 ELEVATO"
        else:
            stress_level = "🔴 CRITICO"
        if trend_30d > trend_90d * 1.1:
            trend_direction = "📈 IN AUMENTO"
        elif trend_30d < trend_90d * 0.9:
            trend_direction = "📉 IN DIMINUZIONE"
        else:
            trend_direction = "➡️ STABILE"
        return {
            'latest_score': round(latest_score, 2),
            'stress_level': stress_level,
            'trend_direction': trend_direction,
            'avg_score': round(avg_score, 2),
            'trend_30d': round(trend_30d, 2),
            'trend_90d': round(trend_90d, 2)
        }

    def create_visualizations(self, composite_df, analysis):
        import matplotlib.pyplot as plt
        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(composite_df.index, composite_df['Economic_Stress_Index'], color='darkred', linewidth=2)
        ax.set_title("Trend dell'Indice di Stress Economico", fontsize=16)
        ax.set_ylabel("Punteggio")
        ax.set_xlabel("Data")
        ax.grid(True, alpha=0.3)
        return fig
