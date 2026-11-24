#!/usr/bin/env bash
set -Eeuo pipefail

fail() {
    printf 'DVC CI remote configuration failed: %s\n' "$1" >&2
    exit 1
}

[[ -n "${DVC_S3_BUCKET:-}" ]] || fail 'DVC_S3_BUCKET is required.'
[[ -n "${DVC_S3_ENDPOINT_URL:-}" ]] || fail 'DVC_S3_ENDPOINT_URL is required.'

if ! command -v uv >/dev/null 2>&1; then
    fail 'uv is required to run the project DVC version.'
fi

uv run dvc remote add -f ci "s3://${DVC_S3_BUCKET}" \
    || fail 'could not add the CI DVC remote.'
uv run dvc remote modify ci endpointurl "$DVC_S3_ENDPOINT_URL" \
    || fail 'could not set the CI DVC endpoint.'
