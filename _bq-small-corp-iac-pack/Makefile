PROJECT=bq-small-corp
REGION=europe-west1
LOCATION=EU
REPO=apps

init:
\tpython -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

docker-up:
\tcd docker && docker compose up --build

build-streamlit:
\tdocker build -t "$(REGION)-docker.pkg.dev/$(PROJECT)/$(REPO)/gcp-pipeline:latest" -f docker/Dockerfile.streamlit .

build-worker:
\tdocker build -t "$(REGION)-docker.pkg.dev/$(PROJECT)/$(REPO)/bq-loader:latest" workers/loader

push-streamlit:
\tdocker push "$(REGION)-docker.pkg.dev/$(PROJECT)/$(REPO)/gcp-pipeline:latest"

push-worker:
\tdocker push "$(REGION)-docker.pkg.dev/$(PROJECT)/$(REPO)/bq-loader:latest"

tf-apply:
\tcd infra/terraform && terraform init && terraform apply -auto-approve \
\t\t-var="project_id=$(PROJECT)" -var="region=$(REGION)" -var="location=$(LOCATION)"
