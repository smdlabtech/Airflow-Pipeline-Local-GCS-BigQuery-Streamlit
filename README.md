# ☁️ GCP Pipeline : Local Data → GCS → BigQuery → DBT → Streamlit

🎉**Nouveautés** : DimDate, SCD2, onglet Exports (BQ→GCS & CSV), squelette **dbt**, **Dockerfile** & **docker-compose**, export **ZIP** depuis l'app.

## 🚀 Démarrage local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 🔑 Authentification GCP (Option A – Application Default Credentials)
L’application utilise les **Application Default Credentials (ADC)** de GCP.  
Configure-les une fois avec le SDK Google Cloud :

```bash
# Connecter ton compte Google et créer les credentials ADC
gcloud auth application-default login

# Définir ton projet par défaut
gcloud config set project bq-small-corp

# (Optionnel) Vérifier que tout est bien configuré
gcloud auth application-default print-access-token
gcloud config get-value project
```

Ces credentials sont stockés automatiquement (Windows : `%APPDATA%\gcloud\application_default_credentials.json`)  
et seront utilisés par la librairie `google-cloud-bigquery` et `google-cloud-storage`.

---


### ⚙️ Commandes optionnelles de dépannage

#### 🟢 Solution 2 : Vérifier le projet GCP
```bash
# Vérifiez le projet configuré
gcloud config get-value project

# Si nécessaire, changez le projet
gcloud config set project VOTRE_PROJECT_ID
```

#### 🟢 Solution 3 : Vérifier les permissions
Assurez-vous que :
- Le projet GCP existe  
- Vous avez les droits **BigQuery Admin** et **Storage Admin**  
- Votre compte a les permissions nécessaires  

#### 🟢 Solution 4 : Utiliser un service account (production)
Pour la production, utilisez un fichier de service account :

```python
from google.oauth2 import service_account
from google.cloud import bigquery

credentials = service_account.Credentials.from_service_account_file(
    'chemin/vers/votre/service-account-key.json',
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
client = bigquery.Client(credentials=credentials, project=project_id)
```

📋 **Étapes de résolution recommandées**
```bash
# 1) Authentification locale
gcloud auth application-default login

# 2) Vérifier l’authentification
gcloud auth list

# 3) Configurer le projet par défaut
gcloud config set project bq-small-corp

# 4) Relancer l'application
streamlit run app.py
```

🔧 **Pour le déploiement Docker**
Si vous utilisez Docker, montez vos credentials :
```yaml
# docker-compose.yml
volumes:
  - ~/.config/gcloud:/root/.config/gcloud  # Pour les credentials ADC
  # ou
  - ./service-account-key.json:/app/service-account-key.json  # Pour un service account
```

💡 **Bonnes pratiques**
- Développement local : utilisez `gcloud auth application-default login`  
- Environnements conteneurisés : utilisez des service accounts  
- Production : privilégiez **Workload Identity Federation** ou des secrets managés  

ℹ️ Cette erreur est normale lors de la première configuration d'une application GCP.  
Une fois l'authentification configurée, elle disparaît. ✅

---

### ▶️ Lancer l'application
```bash
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

### Defaults utilisés pour ce template
- PROJECT_ID: `bq-small-corp`
- REGION (GCS): `europe-west1`
- BigQuery LOCATION: `EU`
- GCS BUCKET par défaut: `bq-small-corp-data`
- BigQuery DATASET par défaut: `demo_dw`
