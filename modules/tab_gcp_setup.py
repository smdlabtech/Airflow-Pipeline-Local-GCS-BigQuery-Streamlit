# modules/tab_gcp_setup.py
import streamlit as st

# def render():
#     st.subheader("🔧 Paramètres GCP")
#     st.markdown("""
# **Authentification (ADC)** :
# ```bash
# gcloud auth application-default login
# gcloud config set project <PROJECT_ID>
# ```
# """)
#     st.text_input("GCP Project ID", key="gcp_project_id", value=st.session_state.get("gcp_project_id","bq-small-corp"))
#     st.text_input("GCS Bucket", key="gcs_bucket", value=st.session_state.get("gcs_bucket","bq-small-corp-data"))
#     st.text_input("BigQuery Dataset", key="bq_dataset", value=st.session_state.get("bq_dataset","demo_dw"))
#     st.text_input("Location (EU/US)", key="gcp_location", value=st.session_state.get("gcp_location","europe-west1"))
#     st.info("⚠️ Le bucket et le dataset seront créés au besoin.")


##########################################################################
# modules/tab_gcp_setup.py
import streamlit as st
from modules.status_manager import update_status, display_status, Status

def render():
    st.subheader("🔧 Paramètres GCP")
    display_status('gcp_setup', 'Statut Configuration')
    
    st.markdown("""
    **Authentification (ADC)** :
    ```bash
    gcloud auth application-default login
    gcloud config set project <PROJECT_ID>
    ```
    """)
    
    project_id = st.text_input("GCP Project ID", key="gcp_project_id", value=st.session_state.get("gcp_project_id","bq-small-corp"))
    bucket = st.text_input("GCS Bucket", key="gcs_bucket", value=st.session_state.get("gcs_bucket","bq-small-corp-data"))
    dataset = st.text_input("BigQuery Dataset", key="bq_dataset", value=st.session_state.get("bq_dataset","demo_dw"))
    location = st.text_input("Location (EU/US)", key="gcp_location", value=st.session_state.get("gcp_location","europe-west1"))
    
    if st.button("✅ Valider la Configuration GCP"):
        try:
            # Simulation de validation
            if project_id and bucket and dataset:
                update_status('gcp_setup', Status.SUCCESS)
                st.success("Configuration GCP validée avec succès!")
            else:
                update_status('gcp_setup', Status.FAILED)
                st.error("Veuillez remplir tous les champs")
        except Exception as e:
            update_status('gcp_setup', Status.FAILED)
            st.error(f"Erreur de configuration: {str(e)}")