#!/usr/bin/env bash
set -euo pipefail

REPOSITORY="${GH_REPO:-brahimnaji-ai/drybean-mlops}"

gh api "repos/${REPOSITORY}" --method PATCH \
  -F 'description=Automated MLOps pipeline for UCI Dry Bean classification' >/dev/null

gh api "repos/${REPOSITORY}/topics" --method PUT \
  -F 'names[]=mlops' \
  -F 'names[]=dvc' \
  -F 'names[]=mlflow' \
  -F 'names[]=fastapi' \
  -F 'names[]=docker' \
  -F 'names[]=github-actions' \
  -F 'names[]=evidently' \
  -F 'names[]=python' >/dev/null

gh api "repos/${REPOSITORY}/vulnerability-alerts" --method PUT >/dev/null
gh api "repos/${REPOSITORY}/automated-security-fixes" --method PUT >/dev/null

payload='{"security_and_analysis":{"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"}}}'
printf '%s' "$payload" | gh api "repos/${REPOSITORY}" --method PATCH --input - >/dev/null

printf 'Dependabot alerts and updates, secret scanning, push protection, and metadata configured for %s.\n' "$REPOSITORY"
