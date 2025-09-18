variable "project_id"  { type = string  default = "bq-small-corp" }
variable "region"      { type = string  default = "europe-west1" }
variable "location"    { type = string  default = "EU" }           # BigQuery location
variable "bucket_name" { type = string  default = "bq-small-corp-data" }
variable "dataset"     { type = string  default = "demo_dw" }
variable "repo_id"     { type = string  default = "apps" }         # Artifact Registry
variable "streamlit_image" {
  description = "Image Docker Streamlit à déployer"
  type        = string
  default     = "europe-west1-docker.pkg.dev/bq-small-corp/apps/gcp-pipeline:latest"
}
variable "loader_image" {
  description = "Image Docker du worker bq-loader"
  type        = string
  default     = "europe-west1-docker.pkg.dev/bq-small-corp/apps/bq-loader:latest"
}
