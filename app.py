# app.py
import streamlit as st
# Modifier les imports comme ceci :
from modules.tab_gcp_setup import render as tab_gcp_setup
from modules.tab_upload_to_gcs import render as tab_upload_to_gcs
from modules.tab_load_to_bq import render as tab_load_to_bq
from modules.tab_sql_transforms import render as tab_sql_transforms
from modules.tab_dw_modeling_bq import render as tab_dw_modeling_bq
from modules.tab_viz_streamlit import render as tab_viz_streamlit
from modules.tab_exports import render as tab_exports
from modules.tab_orchestration import render as tab_orchestration
from modules.tab_dbt import render as tab_dbt
from modules.tab_export_project import render as tab_export_project
from modules.status_manager import init_statuses, display_all_statuses

# Initialiser les statuts
init_statuses()

st.set_page_config(page_title="GCP Pipeline : Local Data → GCS → BigQuery", page_icon="☁️", layout="wide")

st.title("☁️ GCP Pipeline : Local Data → GCS → BigQuery → Streamlit")
st.caption("Project: bq-small-corp | Region (GCS): europe-west1 | BQ Location: EU. Local → GCS → BigQuery → Viz (SCD2, DimDate, dbt, Docker, Airflow).")

# Afficher la sidebar avec les statuts
display_all_statuses()

tabs = st.tabs([
    "🔧 GCP Setup",
    "📤 Upload → GCS", 
    "⬆️ Load GCS → BigQuery",
    "🧮 SQL Transforms (BQ)",
    "🏗️ DW Modeling (BQ)",
    "📊 Visualisation (from BQ)",
    "📤 Exports (BQ ⇄ GCS & CSV)",
    "🛠️ Orchestration (Airflow)",
    "📦 dbt (squelette)",
    "📦 Export Projet (ZIP)"
])

with tabs[0]: tab_gcp_setup()
with tabs[1]: tab_upload_to_gcs()
with tabs[2]: tab_load_to_bq()
with tabs[3]: tab_sql_transforms()
with tabs[4]: tab_dw_modeling_bq()
with tabs[5]: tab_viz_streamlit()
with tabs[6]: tab_exports()
with tabs[7]: tab_orchestration()
with tabs[8]: tab_dbt()
with tabs[9]: tab_export_project()