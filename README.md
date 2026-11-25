# drybean-mlops

Automated MLOps pipeline (data versioning, training, safe deployment, drift monitoring) for UCI Dry Bean classification.

[![CI](https://github.com/brahimnaji-ai/drybean-mlops/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/brahimnaji-ai/drybean-mlops/actions/workflows/ci.yml)

## Overview

This project builds an automated pipeline for classifying dry bean varieties from measured seed properties.
The UCI Dry Bean dataset contains seven classes and 16 numeric features.
The project focuses on the infrastructure and automation around the model, including data versioning,
training, safe deployment, and drift monitoring.

## Table of contents

- [Quick start](#quick-start)
- [Local stack](#local-stack)
- [Data versioning (DVC)](#data-versioning-dvc)
- [Project structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Quick start

Install the Python environment with `uv sync`. To run the local tracking and object storage services, see [Local stack](#local-stack).

## Local stack

The local stack provides an MLflow tracking server backed by MinIO object storage. MinIO and its `mc` client are built from pinned official source releases because the upstream project no longer publishes the referenced container images.

Prerequisites: Docker with the Compose plugin, `uv`, `make`, Bash, and `curl` (for the smoke check).

1. Copy `.env.example` to `.env`. The included MinIO credentials are local development placeholders; keep `.env` private and replace them if needed.
2. Start the services with `make up` (or `docker compose up -d --build --wait`). The first start builds MinIO and MLflow images and can take several minutes.
3. Open the MLflow UI at <http://localhost:5000> or MinIO Console at <http://localhost:9001>. Sign in to MinIO with the `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` values from `.env`. MinIO's S3-compatible endpoint is <http://localhost:9000>.
4. Run `make smoke` to check service health, required buckets, and an artifact written through MLflow to MinIO.
5. Stop services and keep stored data with `make down`. Reset all local data, including MLflow metadata and MinIO objects, with `make down-v`.

Compose publishes ports only on `127.0.0.1`. It creates the `mlflow` and `dvc` buckets on startup; initialization is safe to repeat. Named volumes retain data across `make down` and are removed by `make down-v`.

Troubleshooting: ensure Docker is running and `.env` defines both `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD`. If a port is already in use, stop the conflicting local service before starting this stack. Use `docker compose logs minio mlflow` to inspect service startup.

## Data versioning (DVC)

DVC stores data and model contents in the MinIO `dvc` bucket; Git stores the small `.dvc` pointer files and pipeline metadata. Start MinIO first with `make up`. The committed DVC remote points to `s3://dvc` at `http://localhost:9000` and contains no credentials.

Provide the MinIO credentials to DVC through the AWS environment variables. In Bash or Git Bash, load the ignored `.env` and map the MinIO values:

```bash
set -a
. ./.env
set +a
export AWS_ACCESS_KEY_ID="$MINIO_ROOT_USER"
export AWS_SECRET_ACCESS_KEY="$MINIO_ROOT_PASSWORD"
```

Alternatively, store them in the ignored `.dvc/config.local` file:

```bash
uv run dvc config --local remote.minio.access_key_id "$MINIO_ROOT_USER"
uv run dvc config --local remote.minio.secret_access_key "$MINIO_ROOT_PASSWORD"
```

Track a dataset or model with `uv run dvc add <path>`, then commit its generated `.dvc` pointer. Share the contents with `uv run dvc push`; retrieve them with `uv run dvc pull`. Never `git add` dataset or model contents under `data/` or `models/`; stage only `.dvc` pointer files and `dvc.lock` there. DVC cache, temporary files, and local credentials are ignored by Git.

Run `bash scripts/dvc_roundtrip.sh` to verify a push/pull round trip using temporary data and a temporary DVC cache. Set `DVC_REMOTE` to use another configured remote; it defaults to `minio`.

## Project structure

```text
.
├── src/drybean/
├── tests/
├── configs/
├── data/
├── models/
├── reports/
├── scripts/
├── docs/
└── .github/
```

## Documentation

Project design documents:

- [Project plan](docs/plan/drybean-mlops-project-plan.pdf)
- [UML diagrams and regeneration guide](docs/uml/README.md)
- [Architecture decision records](docs/adr/README.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and repository conventions.

## License

This project is licensed under the [MIT License](LICENSE).
