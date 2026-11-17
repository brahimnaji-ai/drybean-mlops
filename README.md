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
- [Project structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Quick start

Coming with Phase 1: `uv sync`, `docker compose up`

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
