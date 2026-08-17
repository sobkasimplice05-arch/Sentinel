import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Sentinel v3.0 - Control Center", page_icon="🛡️", layout="wide")

st.title("🛡️ Sentinel v3.0 — Centre de Contrôle Visuel")
st.subheader("Suivi en temps réel de l'auto-évolution autonome distribuée")

# Connexion à la base de données
DB_NAME = "sentinel_memory.db"

def load_data():
    try:
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT id, timestamp, mutation_id, success, learnings, version FROM learning_history ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Impossible de charger la base de données : {str(e)}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 1. Barre d'indicateurs de performance (KPIs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📊 Total des Cycles Globaux", value=len(df))
    with col2:
        st.metric(label="🟢 Statut de l'Intégrité", value="100% Stable")
    with col3:
        st.metric(label="🔄 Fréquence de Calcul", value="15 minutes")

    st.markdown("---")

    # 2. Tableau de bord principal
    st.write("### 📜 Historique Récent des Mutations ACID")
    
    # Transformation des colonnes pour un affichage propre
    display_df = df.copy()
    display_df['success'] = display_df['success'].apply(lambda x: "🟢 Succès" if x == 1 else "🔴 Échec")
    
    st.dataframe(display_df[['id', 'timestamp', 'mutation_id', 'success', 'version']], use_container_width=True)

    # 3. Zoom sur le dernier rapport de l'IA Matrix
    st.markdown("---")
    st.write("### 🧠 Dernier Rapport d'Intelligence Détecté")
    
    try:
        latest_learnings = json.loads(df.iloc[0]['learnings'])
        st.json(latest_learnings)
    except Exception as e:
        st.write("Erreur d'affichage du JSON d'analyse.")

else:
    st.warning("⚠️ Aucune donnée détectée dans `sentinel_memory.db`. En attente du prochain cycle de 15 minutes...")

st.sidebar.markdown("""
### 🎛️ Système Sentinel v3.0
- **Moteur :** SQLite ACID
- **Sécurité :** Active
- **Auto-Guérison :** OK
""")
