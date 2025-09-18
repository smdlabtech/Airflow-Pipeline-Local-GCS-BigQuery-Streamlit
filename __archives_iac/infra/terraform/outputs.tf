output "project_id"   { value = var.project_id }
output "region"       { value = var.region }
output "gcs_bucket"   { value = google_storage_bucket.data.name }
output "bq_dataset"   { value = google_bigquery_dataset.dw.dataset_id }
output "artifact_registry_repo" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repo_id}"
}
output "streamlit_url" {
  value = google_cloud_run_v2_service.streamlit.uri
}
output "streamlit_service_account" {
  value = google_service_account.streamlit.email
}
output "bq_loader_job_name" { value = google_cloud_run_v2_job.bq_loader.name }
