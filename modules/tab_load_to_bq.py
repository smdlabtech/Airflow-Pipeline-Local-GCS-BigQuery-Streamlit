# modules/tab_load_to_bq.py
import streamlit as st
from utils.gcp_bq import ensure_dataset, load_gcs_to_bq

def render():
    st.subheader("⬆️ Charger GCS → BigQuery (staging)")
    if not st.session_state.get("gcp_project_id") or not st.session_state.get("bq_dataset"):
        st.warning("Complète **GCP Setup**.")
        return
    ensure_dataset(st.session_state["gcp_project_id"], st.session_state["bq_dataset"], st.session_state.get("gcp_location","europe-west1"))
    gs_paths = st.session_state.get("gcs_files", [])
    if not gs_paths:
        st.info("Aucun fichier GCS détecté. Upload d'abord.")
        return
    table_name = st.text_input("Nom de table staging", value="staging_customers")
    autodetect = st.checkbox("Autodetect schema", value=True)
    write_disposition = st.selectbox("Write disposition", ["WRITE_TRUNCATE","WRITE_APPEND","WRITE_EMPTY"])
    if st.button("🚀 Charger dans BigQuery"):
        job = load_gcs_to_bq(
            project_id=st.session_state["gcp_project_id"],
            dataset=st.session_state["bq_dataset"],
            table=table_name,
            uris=gs_paths,
            autodetect=autodetect,
            write_disposition=write_disposition
        )
        st.success(f"✅ Job terminé: {job.job_id}")
        st.code(f"{st.session_state['gcp_project_id']}.{st.session_state['bq_dataset']}.{table_name}")
