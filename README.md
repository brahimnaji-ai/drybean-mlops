# drybean-mlops

Automated MLOps pipeline (data versioning, training, safe deployment, drift monitoring) for UCI Dry Bean classification.

<!-- CI badge added in P1-07 -->

## Overview

This project builds an automated pipeline for classifying dry bean varieties from measured seed properties.
The UCI Dry Bean dataset contains seven classes and 16 numeric features.
The project focuses on the infrastructure and automation around the model, including data versioning,
training, safe deployment, and drift monitoring.

## Table of contents

- [Quick start](#quick-start)
- [Local stack](#local-stack)
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

Project plan, UML diagrams, and architecture decision records will be added in P1-09:

- [Project plan](docs/plan/)
- [UML diagrams](docs/uml/)
- [Architecture decision records](docs/adr/)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and repository conventions.

## License

This project is licensed under the [MIT License](LICENSE).
