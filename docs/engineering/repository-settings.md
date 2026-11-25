# Repository settings

This repository uses the following GitHub settings for Phase 1. The scripts are safe to re-run.

## Main branch and merge policy

The `drybean-main-protection` repository ruleset targets `refs/heads/main` and is active. It requires:

- A pull request before merging, with zero required approvals for this solo project
- Resolution of all review conversations
- Passing `lint`, `typecheck`, `test`, and `docker-build` checks from the latest base revision
- Linear history, with force pushes and branch deletion blocked

The repository permits squash merging only and deletes merged branches automatically. To apply or update these settings, use an authenticated GitHub CLI session with repository administration rights and `jq` installed:

```bash
bash scripts/apply_branch_protection.sh
```

## Dependency updates

`.github/dependabot.yml` schedules weekly Monday updates for `uv`, GitHub Actions, the MLflow Docker image, and Docker Compose. Minor and patch updates are grouped, labeled `type:chore`, and use the `chore(deps)` commit prefix.

## Security and repository metadata

The script sets the repository description to “Automated MLOps pipeline for UCI Dry Bean classification” and topics to `mlops`, `dvc`, `mlflow`, `fastapi`, `docker`, `github-actions`, `evidently`, and `python`. It enables Dependabot alerts and Dependabot security updates through their dedicated repository endpoints, then enables secret scanning and push protection:

```bash
bash scripts/apply_repository_security.sh
```

Run it with a GitHub CLI session that has repository administration rights. GitHub may require a supported repository visibility or plan for some security features; the command returns the API error if a feature is unavailable.

## Phase 1 project board

Create and link the `drybean-mlops` project board and add issues 1–9 with:

```bash
bash scripts/create_phase1_project.sh
```

The GitHub CLI session needs the `project` scope in addition to repository access; `gh` and `jq` must be installed. The script sets the built-in `Status` options to `Backlog`, `Ready`, `In progress`, `In review`, and `Done` through the Projects GraphQL API, preserving option IDs when names match. If the token cannot update the field, open the project, use the `Status` field menu to edit its options, replace the list with those five values, and report that permission limitation on the issue. Re-running the script reuses the existing project and tolerates issues that are already on the board.

## Verify settings

Inspect the main-branch ruleset in **Settings → Rules → Rulesets**, merge settings with:

```bash
gh api repos/brahimnaji-ai/drybean-mlops --jq '[.allow_squash_merge,.allow_merge_commit,.allow_rebase_merge,.delete_branch_on_merge]'
```

The expected values are `[true,false,false,true]`. Confirm security features on **Settings → Code security and analysis**, Dependabot update jobs on **Insights → Dependency graph → Dependabot**, and the linked board under the repository's **Projects** tab.
