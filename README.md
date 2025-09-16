# ☁️ GCP Pipeline v2 – Local → GCS → BigQuery → Streamlit

**Nouveautés** : DimDate, SCD2, onglet Exports (BQ→GCS & CSV), squelette **dbt**, **Dockerfile** & **docker-compose**, export **ZIP** depuis l'app.

## 🚀 Démarrage local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

gcloud auth application-default login
gcloud config set project <PROJECT_ID>

streamlit run app.py
```

## 🧱 Onglets
1. **GCP Setup** – Project/Bucket/Dataset/Location
2. **Upload → GCS** – envoie `landing/*.csv` dans GCS
3. **Load → BQ** – crée des tables `staging_*`
4. **SQL Transforms** – crée `clean_*` (+ code DimDate/SCD2 fourni)
5. **DW Modeling** – boutons : `dim_customer`, `fact_orders`, `dim_date`, `SCD2`
6. **Visualisation** – chart depuis BQ
7. **Exports** – CSV download (requête) & extract job BQ→GCS (CSV/Parquet)
8. **Orchestration** – DAG Airflow exemple
9. **dbt** – squelette (staging/warehouse/marts)
10. **Export Projet** – création d’un ZIP complet du repo

## 🐳 Docker
```bash
cd docker
docker compose up --build
```
Montez vos creds GCP dans `.gcp/sa.json` si vous utilisez un **service account**.

## 🧪 dbt (optionnel)
```bash
pip install dbt-bigquery
cp dbt/profiles.example.yml ~/.dbt/profiles.yml
dbt debug && dbt run && dbt test
```

## ⚠️ Droits requis
- GCS: Storage Object Admin (à restreindre finement en prod)
- BQ: BigQuery Data Editor / Job User, etc.


---
### Defaults utilisés pour ce template
- PROJECT_ID: `bq-small-corp`
- REGION (GCS): `europe-west1`
- BigQuery LOCATION: `EU`
- GCS BUCKET par défaut: `bq-small-corp-data`
- BigQuery DATASET par défaut: `demo_dw`
