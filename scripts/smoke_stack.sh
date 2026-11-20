#!/usr/bin/env bash
set -Eeuo pipefail

fail() {
    printf 'Smoke check failed: %s\n' "$1" >&2
    exit 1
}

command -v curl >/dev/null 2>&1 || fail "curl is required; install curl and retry."
command -v docker >/dev/null 2>&1 || fail "Docker is required; install Docker Desktop or Docker Engine."
docker compose version >/dev/null 2>&1 || fail "the Docker Compose plugin is required."

curl --fail --silent --show-error http://127.0.0.1:9000/minio/health/live >/dev/null \
    || fail "MinIO is not healthy at http://127.0.0.1:9000; start the stack with 'make up'."
curl --fail --silent --show-error http://127.0.0.1:5000/health >/dev/null \
    || fail "MLflow is not healthy at http://127.0.0.1:5000; start the stack with 'make up'."

compose=(docker compose)
"${compose[@]}" exec -T minio sh -ec '
    mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null
    mc ls local/mlflow >/dev/null
    mc ls local/dvc >/dev/null
' || fail "the required MinIO buckets 'mlflow' and 'dvc' are not available."

run_details=$("${compose[@]}" exec -T mlflow python -c 'import pathlib, uuid; from mlflow import MlflowClient; client = MlflowClient("http://localhost:5000"); experiment_id = client.create_experiment("stack-smoke-" + uuid.uuid4().hex); run = client.create_run(experiment_id); artifact = pathlib.Path("/tmp/drybean-stack-smoke.txt"); artifact.write_text("MLflow to MinIO smoke check\\n"); client.log_artifact(run.info.run_id, str(artifact)); print(experiment_id, run.info.run_id)') \
    || fail "MLflow could not create a run and log an artifact."
read -r experiment_id run_id <<<"$run_details"
[[ -n "${experiment_id:-}" && -n "${run_id:-}" ]] || fail "MLflow did not return the smoke run identifiers."

"${compose[@]}" exec -T minio sh -ec '
    mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null
    mc stat "local/mlflow/$1/$2/artifacts/drybean-stack-smoke.txt" >/dev/null
' sh "$experiment_id" "$run_id" \
    || fail "the MLflow artifact was not found in the MinIO 'mlflow' bucket."

printf 'Smoke check passed: MinIO and MLflow are healthy; buckets exist; artifact verified in MinIO.\n'
