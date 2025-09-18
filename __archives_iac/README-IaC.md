# IaC + Worker Pack — bq-small-corp

Ce pack ajoute à ton repo :
- **Terraform** (GCS, BigQuery, SAs, Artifact Registry, Cloud Run service + Job, Workflows + Scheduler)
- **Worker Cloud Run Job** (`bq-loader`) qui charge `staging_*`, exécute clean + DimDate + SCD2 + Fact
- **GitHub Actions**: build/push images, terraform apply
- **Makefile**: commandes rapides

## Déploiement rapide
```bash
# 1) Build & push images (ou via GitHub Actions)
make build-streamlit build-worker
gcloud auth configure-docker europe-west1-docker.pkg.dev
make push-streamlit push-worker

# 2) Provision infra
make tf-apply

# 3) Lancer le job manuellement (exemples)
gcloud run jobs execute bq-loader --region europe-west1   --args="--uris","gs://bq-small-corp-data/landing/customers.csv","--table","staging_customers"

gcloud run jobs execute bq-loader --region europe-west1   --args="--uris","gs://bq-small-corp-data/landing/orders.csv","--table","staging_orders"
```
