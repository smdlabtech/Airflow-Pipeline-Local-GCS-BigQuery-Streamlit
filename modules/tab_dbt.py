# modules/tab_dbt.py
import streamlit as st

def render():
    st.subheader("📦 dbt – Squelette BigQuery")
    st.markdown("""
Le dossier `dbt/` contient :
- `dbt_project.yml`
- `models/` (staging, warehouse, marts)
- `profiles.example.yml` (à copier vers `~/.dbt/profiles.yml`)

Commandes utiles :
```bash
pip install dbt-bigquery
dbt debug
dbt deps
dbt run
dbt test
dbt docs generate && dbt docs serve
```
""")
    with st.expander("📄 dbt_project.yml"):
        st.code(open("dbt/dbt_project.yml").read(), language="yaml")
    with st.expander("📄 profiles.example.yml"):
        st.code(open("dbt/profiles.example.yml").read(), language="yaml")
    with st.expander("📄 Exemple modèle (staging_customers.sql)"):
        st.code(open("dbt/models/staging/staging_customers.sql").read(), language="sql")
