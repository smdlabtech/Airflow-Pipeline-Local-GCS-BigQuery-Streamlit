# modules/tab_gcp_setup.py
import streamlit as st

def render():
    st.subheader("🔧 Paramètres GCP")
    st.markdown("""
**Authentification (ADC)** :
```bash
gcloud auth application-default login
gcloud config set project <PROJECT_ID>
```
""")
    st.text_input("GCP Project ID", key="gcp_project_id", value=st.session_state.get("gcp_project_id","bq-small-corp"))
    st.text_input("GCS Bucket", key="gcs_bucket", value=st.session_state.get("gcs_bucket","bq-small-corp-data"))
    st.text_input("BigQuery Dataset", key="bq_dataset", value=st.session_state.get("bq_dataset","demo_dw"))
    st.text_input("Location (EU/US)", key="gcp_location", value=st.session_state.get("gcp_location","europe-west1"))
    st.info("⚠️ Le bucket et le dataset seront créés au besoin.")
