# 1) APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "artifactregistry.googleapis.com",
    "bigquery.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "workflows.googleapis.com",
    "cloudscheduler.googleapis.com",
    "eventarc.googleapis.com",
    "pubsub.googleapis.com",
  ])
  project  = var.project_id
  service  = each.key
  disable_on_destroy = false
}

# 2) GCS
resource "google_storage_bucket" "data" {
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 90 }
  }
  depends_on = [google_project_service.apis]
}

# 3) BigQuery
resource "google_bigquery_dataset" "dw" {
  dataset_id                 = var.dataset
  location                   = var.location
  delete_contents_on_destroy = true
  depends_on = [google_project_service.apis]
}

# 4) Service accounts + IAM
resource "google_service_account" "streamlit" {
  account_id   = "streamlit-sa"
  display_name = "Streamlit Service Account"
}
resource "google_service_account" "worker" {
  account_id   = "worker-sa"
  display_name = "BQ Loader Worker SA"
}
resource "google_service_account" "cicd" {
  account_id   = "ci-cd-sa"
  display_name = "CI/CD Service Account"
}

# IAM Streamlit
resource "google_project_iam_member" "streamlit_bq_job" {
  role   = "roles/bigquery.jobUser"
  member = "serviceAccount:${google_service_account.streamlit.email}"
}
resource "google_project_iam_member" "streamlit_bq_viewer" {
  role   = "roles/bigquery.dataViewer"
  member = "serviceAccount:${google_service_account.streamlit.email}"
}
resource "google_storage_bucket_iam_member" "streamlit_bucket" {
  bucket = google_storage_bucket.data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.streamlit.email}"
}

# IAM Worker
resource "google_project_iam_member" "worker_bq_job" {
  role   = "roles/bigquery.jobUser"
  member = "serviceAccount:${google_service_account.worker.email}"
}
resource "google_project_iam_member" "worker_bq_editor" {
  role   = "roles/bigquery.dataEditor"
  member = "serviceAccount:${google_service_account.worker.email}"
}
resource "google_storage_bucket_iam_member" "worker_bucket" {
  bucket = google_storage_bucket.data.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.worker.email}"
}

# IAM CI/CD
resource "google_project_iam_member" "cicd_artifact_writer" {
  role   = "roles/artifactregistry.writer"
  member = "serviceAccount:${google_service_account.cicd.email}"
}
resource "google_project_iam_member" "cicd_run_admin" {
  role   = "roles/run.admin"
  member = "serviceAccount:${google_service_account.cicd.email}"
}
resource "google_project_iam_member" "cicd_sa_user" {
  role   = "roles/iam.serviceAccountUser"
  member = "serviceAccount:${google_service_account.cicd.email}"
}

# 5) Artifact Registry
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = var.repo_id
  description   = "App images"
  format        = "DOCKER"
  depends_on    = [google_project_service.apis]
}

# 6) Cloud Run - Streamlit
resource "google_cloud_run_v2_service" "streamlit" {
  name     = "gcp-pipeline-streamlit"
  location = var.region

  template {
    service_account = google_service_account.streamlit.email
    containers {
      image = var.streamlit_image
      ports { container_port = 8501 }
      env { name = "PROJECT_ID"   value = var.project_id }
      env { name = "BQ_LOCATION"  value = var.location }
      env { name = "GCS_BUCKET"   value = var.bucket_name }
      env { name = "BQ_DATASET"   value = var.dataset }
    }
  }
  traffic { type = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST" percent = 100 }
  ingress = "INGRESS_TRAFFIC_ALL"
  depends_on = [google_artifact_registry_repository.docker_repo]
}

resource "google_cloud_run_v2_service_iam_member" "streamlit_public" {
  name     = google_cloud_run_v2_service.streamlit.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 7) Cloud Run Job - Worker ETL
resource "google_cloud_run_v2_job" "bq_loader" {
  name     = "bq-loader"
  location = var.region
  template {
    template {
      service_account = google_service_account.worker.email
      containers {
        image = var.loader_image
        env { name = "PROJECT_ID"  value = var.project_id }
        env { name = "BQ_DATASET"  value = var.dataset }
        env { name = "BQ_LOCATION" value = var.location }
        env { name = "GCS_BUCKET"  value = var.bucket_name }
      }
    }
  }
  depends_on = [google_artifact_registry_repository.docker_repo]
}

# 8) Workflows + Scheduler to run the job nightly
resource "google_service_account" "scheduler" {
  account_id   = "scheduler-sa"
  display_name = "Scheduler Invoker"
}
resource "google_project_iam_member" "workflows_invoker" {
  role   = "roles/workflows.invoker"
  member = "serviceAccount:${google_service_account.scheduler.email}"
}

resource "google_workflows_workflow" "run_bq_loader" {
  name   = "run-bq-loader"
  region = var.region
  source_contents = <<-YAML
    main:
      steps:
      - run:
          call: http.request
          args:
            url: "https://run.googleapis.com/v2/projects/${var.project_id}/locations/${var.region}/jobs/${google_cloud_run_v2_job.bq_loader.name}:run"
            method: "POST"
            auth: { type: OAuth2 }
          result: r
      - done:
          return: ${r}
  YAML
}

resource "google_cloud_scheduler_job" "cron_bq_loader" {
  name      = "cron-bq-loader"
  region    = var.region
  schedule  = "0 2 * * *"
  time_zone = "Europe/Paris"
  http_target {
    http_method = "POST"
    uri         = "https://workflowexecutions.googleapis.com/v1/projects/${var.project_id}/locations/${var.region}/workflows/${google_workflows_workflow.run_bq_loader.name}/executions"
    oauth_token { service_account_email = google_service_account.scheduler.email }
    headers = { "Content-Type" = "application/json" }
    body    = jsonencode({})
  }
}
