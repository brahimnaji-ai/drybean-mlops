# Architecture decision records

This directory records decisions that affect the project architecture. New records should follow the [MADR template](https://adr.github.io/madr/).

| ADR | Decision | Status | Related work |
|---|---|---|---|
| [ADR-001: CI-reachable DVC remote](0001-ci-reachable-dvc-remote.md) | Use an S3-compatible Backblaze B2 bucket for CI DVC access while keeping MinIO for local development. | Accepted | P1-06 |
| ADR-002: hosting target | Choose the production API hosting provider and deployment adapter. | Planned | Phase 3 |
