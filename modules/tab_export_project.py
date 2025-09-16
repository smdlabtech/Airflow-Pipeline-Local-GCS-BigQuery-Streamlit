# modules/tab_export_project.py
import streamlit as st, os, io, zipfile

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            fp = os.path.join(root, file)
            # skip streamlit cache dirs
            if "/.streamlit/" in fp or "/__pycache__/" in fp: 
                continue
            arc = os.path.relpath(fp, start=path)
            ziph.write(fp, arc)

def render():
    st.subheader("📦 Export complet du projet")
    folder = st.text_input("Dossier racine à zipper", value=".")
    if st.button("Créer ZIP"):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            zipdir(folder, z)
        st.success("✅ Archive prête.")
        st.download_button("⬇️ Télécharger gcp_pipeline_v2.zip", data=buf.getvalue(), file_name="gcp_pipeline_v2.zip", mime="application/zip")
