# Contributing

## Workflow

Use one ticket, one branch, and one pull request. Create the branch from an up-to-date `main` branch.

Name branches `<type>/<issue>-<slug>`, using one of these types: `feat`, `fix`, `chore`, `docs`, `test`, `infra`, or `adr`.
For example: `chore/2-python-tooling`.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/), write the summary in the imperative mood,
and make each commit one logical change. Reference the issue number.

Examples:

- `chore(tooling): add ruff and mypy config (#2)`
- `feat(data): add dry bean dataset loader (#3)`
- `docs(readme): explain local setup (#1)`

## Pull requests

Open one pull request per ticket. Include `Closes #<issue-number>` in its description and explain how each
acceptance criterion was verified, including the commands run and their outcomes. Pull requests are squash-merged.

Checklist:

- [ ] Changes address the ticket and its acceptance criteria.
- [ ] Checks pass, or any limitation is explained.
- [ ] Documentation is updated where behavior or setup changed.
- [ ] No credentials, tokens, or real `.env` files are included.
- [ ] CI is green.

## Checks

The following commands become available after P1-02:

- `uv run ruff check .`
- `uv run ruff format --check .`
- `uv run mypy`
- `uv run pytest`

## Definition of Done

- [ ] All acceptance criteria checked, with evidence in the PR description
- [ ] Local checks pass (`uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, `uv run pytest`) once those exist
- [ ] Documentation updated where behaviour or setup changed
- [ ] No unrelated changes, no secrets, no generated artefacts committed
