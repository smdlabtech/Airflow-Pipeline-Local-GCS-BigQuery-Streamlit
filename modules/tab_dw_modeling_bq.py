# modules/tab_dw_modeling_bq.py
import streamlit as st
from utils.gcp_bq import run_query

def render():
    st.subheader("🏗️ DW Modeling – BigQuery (Dim/Fact + DimDate + SCD2)")
    p = st.session_state.get("gcp_project_id"); d = st.session_state.get("bq_dataset")
    if not p or not d:
        st.warning("Complète **GCP Setup**.")
        return

    sql_dim = f"""
CREATE OR REPLACE TABLE `{p}.{d}.dim_customer` AS
SELECT customer_id, first_name, last_name, email, country
FROM `{p}.{d}.clean_customers`;
"""
    sql_fact = f"""
CREATE OR REPLACE TABLE `{p}.{d}.fact_orders` AS
SELECT
  CAST(order_id AS INT64) AS order_id,
  CAST(customer_id AS INT64) AS customer_id,
  DATE(order_date) AS order_date,
  CAST(order_amount AS NUMERIC) AS order_amount
FROM `{p}.{d}.staging_orders`;
"""
    if st.button("Créer DIM_CUSTOMER"):
        run_query(sql_dim, project=p); st.success("✅ dim_customer créé.")
    if st.button("Créer FACT_ORDERS"):
        run_query(sql_fact, project=p); st.success("✅ fact_orders créé.")

    with st.expander("📅 Créer DIM_DATE"):
        sql_dim_date = open("sql/01_dim_date.sql").read().replace("${PROJECT}", p).replace("${DATASET}", d)
        st.code(sql_dim_date, language="sql")
        if st.button("Créer DIM_DATE"):
            run_query(sql_dim_date, project=p); st.success("✅ dim_date créé.")

    with st.expander("🕓 SCD2 – dim_customer_history (MERGE)"):
        sql_scd2 = open("sql/02_scd2_dim_customer.sql").read().replace("${PROJECT}", p).replace("${DATASET}", d)
        st.code(sql_scd2, language="sql")
        if st.button("Appliquer SCD2"):
            run_query(sql_scd2, project=p); st.success("✅ SCD2 appliqué (dim_customer_history).")
