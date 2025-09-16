# modules/tab_upload_to_gcs.py
import streamlit as st
from utils.gcp_io import ensure_bucket, upload_fileobj

def render():
    st.subheader("📤 Upload local → Google Cloud Storage")
    if not st.session_state.get("gcp_project_id") or not st.session_state.get("gcs_bucket"):
        st.warning("Complète d'abord **GCP Setup**.")
        return
    uploaded = st.file_uploader("Uploader un/des CSV", type=["csv"], accept_multiple_files=True)
    if uploaded:
        ensure_bucket(st.session_state["gcs_bucket"], st.session_state.get("gcp_location","europe-west1"))
        paths = []
        for f in uploaded:
            blob_path = f"landing/{f.name}"
            upload_fileobj(st.session_state["gcs_bucket"], blob_path, f)
            paths.append(f"gs://{st.session_state['gcs_bucket']}/{blob_path}")
        st.success("✅ Envoyé vers GCS :")
        for p in paths: st.write(p)
        st.session_state["gcs_files"] = paths
    else:
        st.info("Sélectionne des fichiers CSV.")
