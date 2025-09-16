# modules/tab_exports.py
import streamlit as st
from utils.gcp_bq import run_query_to_df, extract_table_to_gcs
import pandas as pd
import io

def render():
    st.subheader("📤 Exports")
    p = st.session_state.get("gcp_project_id"); d = st.session_state.get("bq_dataset")
    if not p or not d:
        st.warning("Complète **GCP Setup**.")
        return

    st.markdown("**1) Télécharger en CSV depuis une requête BigQuery**")
    sql = st.text_area("SQL pour export CSV", value=f"SELECT * FROM `{p}.{d}.dim_customer` LIMIT 1000", height=160)
    if st.button("⬇️ Exécuter & Télécharger CSV"):
        df = run_query_to_df(sql, project=p)
        if df is not None:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Télécharger result.csv", data=csv, file_name="result.csv", mime="text/csv")
        else:
            st.info("Aucun résultat.")

    st.markdown("---")
    st.markdown("**2) Exporter une table BigQuery vers GCS (CSV/Parquet)**")
    table = st.text_input("Table complète (project.dataset.table)", value=f"{p}.{d}.fact_orders")
    fmt = st.selectbox("Format", ["CSV","PARQUET"])
    gcs_uri = st.text_input("URI GCS cible (ex: gs://my-bucket/exports/fact_orders-*.parquet)", value=f"gs://{st.session_state.get('gcs_bucket','bucket')}/exports/fact_orders-*.parquet")
    if st.button("🚀 Lancer extract job → GCS"):
        job = extract_table_to_gcs(table=table, destination_uri=gcs_uri, fmt=fmt)
        st.success(f"✅ Export lancé / terminé: {job.job_id}")
        st.write("Destination:", gcs_uri)
