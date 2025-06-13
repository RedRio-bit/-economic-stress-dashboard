
import streamlit as st
from stress_tracker import EconomicStressTracker
from datetime import datetime

st.set_page_config(page_title="Indice di Stress Economico", layout="wide")
st.title("📉 Economic Stress Index - Italia")
st.markdown("Analisi del livello di stress economico basata sulle ricerche Google Trends.")

tracker = EconomicStressTracker()

if st.button("🔄 Aggiorna dati"):
    with st.spinner("Raccolta dati in corso..."):
        all_data = tracker.collect_all_data()
        composite_df = tracker.create_composite_index(all_data)
        if not composite_df.empty:
            analysis = tracker.analyze_trends(composite_df)
            st.success("✅ Dati aggiornati!")

            st.subheader("📊 Risultati principali")
            st.metric("🎯 Score Attuale", analysis['latest_score'])
            st.write(f"**Livello Stress**: {analysis['stress_level']}")
            st.write(f"**Trend**: {analysis['trend_direction']}")
            st.write(f"**Media 30gg**: {analysis['trend_30d']}")
            st.write(f"**Media 90gg**: {analysis['trend_90d']}")

            fig = tracker.create_visualizations(composite_df, analysis)
            st.pyplot(fig)

            st.download_button(
                label="💾 Scarica CSV",
                data=composite_df.to_csv().encode('utf-8'),
                file_name=f"economic_stress_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv'
            )
        else:
            st.error("❌ Nessun dato disponibile.")
else:
    st.info("Premi il bottone sopra per iniziare l’analisi.")
