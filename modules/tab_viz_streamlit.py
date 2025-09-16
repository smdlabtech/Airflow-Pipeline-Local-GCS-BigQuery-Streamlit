# modules/tab_viz_streamlit.py
import streamlit as st
from utils.gcp_bq import run_query_to_df

def render():
    st.subheader("📊 Visualisation depuis BigQuery")
    p = st.session_state.get("gcp_project_id"); d = st.session_state.get("bq_dataset")
    if not p or not d:
        st.warning("Complète **GCP Setup**.")
        return
    sql = f"""
SELECT country, SUM(order_amount) AS revenue
FROM `{p}.{d}.fact_orders` f
LEFT JOIN `{p}.{d}.dim_customer` d USING (customer_id)
GROUP BY country ORDER BY revenue DESC
"""
    st.code(sql, language="sql")
    if st.button("📈 Afficher"):
        df = run_query_to_df(sql, project=p)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
            st.bar_chart(df.set_index("country"))
        else:
            st.info("Pas de données.")
