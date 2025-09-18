# app.py
import streamlit as st

from modules import (
    tab_gcp_setup,
    tab_upload_to_gcs,
    tab_load_to_bq,
    tab_sql_transforms,
    tab_dw_modeling_bq,
    tab_viz_streamlit,
    tab_exports,
    tab_orchestration,
    tab_dbt,
    tab_export_project
)

st.set_page_config(page_title="GCP Pipeline – Local → GCS → BigQuery", page_icon="☁️", layout="wide")

st.title("☁️ GCP Pipeline – Local → GCS → BigQuery → Streamlit")
st.caption("Project: bq-small-corp | Region (GCS): europe-west1 | BQ Location: EU. Local → GCS → BigQuery → Viz (SCD2, DimDate, dbt, Docker, Airflow).")

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

with tabs[0]: tab_gcp_setup.render()
with tabs[1]: tab_upload_to_gcs.render()
with tabs[2]: tab_load_to_bq.render()
with tabs[3]: tab_sql_transforms.render()
with tabs[4]: tab_dw_modeling_bq.render()
with tabs[5]: tab_viz_streamlit.render()
with tabs[6]: tab_exports.render()
with tabs[7]: tab_orchestration.render()
with tabs[8]: tab_dbt.render()
with tabs[9]: tab_export_project.render()
