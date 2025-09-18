# # modules/tab_sql_transforms.py
# import streamlit as st
# from utils.gcp_bq import run_query

# def render():
#     st.subheader("🧮 SQL Transforms – BigQuery (staging → clean)")
#     p = st.session_state.get("gcp_project_id"); d = st.session_state.get("bq_dataset")
#     if not p or not d:
#         st.warning("Complète **GCP Setup**.")
#         return

#     default_sql = f"""
# -- Clean customers (exemple)
# CREATE OR REPLACE TABLE `{p}.{d}.clean_customers` AS
# SELECT DISTINCT
#   CAST(customer_id AS INT64) AS customer_id,
#   TRIM(first_name) AS first_name,
#   TRIM(last_name)  AS last_name,
#   LOWER(email)     AS email,
#   country
# FROM `{p}.{d}.staging_customers`
# WHERE customer_id IS NOT NULL;
# """
#     sql = st.text_area("SQL BigQuery", value=default_sql, height=220)
#     if st.button("▶️ Exécuter SQL"):
#         rows = run_query(sql, project=p)
#         st.success("✅ Requête exécutée.")
#         if rows is not None: st.dataframe(rows, use_container_width=True)

#     with st.expander("📌 Bonus SQL inclus (DimDate / SCD2)"):
#         st.code(open("sql/01_dim_date.sql").read(), language="sql")
#         st.code(open("sql/02_scd2_dim_customer.sql").read(), language="sql")




# modules/tab_sql_transforms.py
import streamlit as st
from utils.gcp_bq import run_query
from modules.status_manager import update_status, display_status, Status

def render():
    st.subheader("🧮 SQL Transforms – BigQuery (staging → clean)")
    display_status('sql_transform', 'Statut Transformations')
    
    p = st.session_state.get("gcp_project_id"); d = st.session_state.get("bq_dataset")
    if not p or not d:
        st.warning("Complète **GCP Setup**.")
        update_status('sql_transform', Status.FAILED)
        return

    default_sql = f"""
CREATE OR REPLACE TABLE `{p}.{d}.clean_customers` AS
SELECT DISTINCT
  CAST(customer_id AS INT64) AS customer_id,
  TRIM(first_name) AS first_name,
  TRIM(last_name)  AS last_name,
  LOWER(email)     AS email,
  country
FROM `{p}.{d}.staging_customers`
WHERE customer_id IS NOT NULL;
"""
    sql = st.text_area("SQL BigQuery", value=default_sql, height=220)
    
    if st.button("▶️ Exécuter SQL"):
        try:
            update_status('sql_transform', Status.PENDING)
            rows = run_query(sql, project=p)
            if rows is not None:
                update_status('sql_transform', Status.SUCCESS)
                st.success("✅ Requête exécutée.")
                st.dataframe(rows, use_container_width=True)
            else:
                update_status('sql_transform', Status.SUCCESS)
                st.success("✅ Requête exécutée (pas de résultat à afficher).")
        except Exception as e:
            update_status('sql_transform', Status.FAILED)
            st.error(f"❌ Erreur SQL: {str(e)}")