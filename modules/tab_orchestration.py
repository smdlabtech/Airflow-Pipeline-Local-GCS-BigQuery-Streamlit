# modules/tab_orchestration.py
import streamlit as st
def render():
    st.subheader("🛠️ Orchestration – Airflow")
    st.caption("DAG Airflow avec GCSToBigQuery + BigQueryInsertJobOperator + SCD2/DimDate.")
    st.code(open("airflow/dags/gcp_pipeline_dag.py","r").read(), language="python")
