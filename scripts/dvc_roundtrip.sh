#!/usr/bin/env bash
set -Eeuo pipefail

fail() {
    printf 'DVC round-trip failed: %s\n' "$1" >&2
    exit 1
}

project_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_root"

DVC_REMOTE=${DVC_REMOTE:-minio}
smoke_dir="$project_root/data/_smoke"
smoke_file="$smoke_dir/hello.txt"
temporary_cache=""
smoke_dir_created=false
cache_override_set=false
original_cache_set=false
original_cache_dir=""

[[ ! -e "$smoke_dir" ]] || fail "$smoke_dir already exists; move it aside before running the smoke check."
command -v uv >/dev/null 2>&1 || fail "uv is required to run the project DVC version."

local_config=$(uv run dvc config --local --list) || fail "could not read local DVC configuration."
while IFS='=' read -r key value; do
    if [[ "$key" == "cache.dir" ]]; then
        original_cache_set=true
        original_cache_dir=$value
    fi
done <<<"$local_config"

temporary_cache=$(mktemp -d "${TMPDIR:-/tmp}/drybean-dvc-cache.XXXXXX") \
    || fail "could not create a temporary DVC cache directory."

cleanup() {
    local exit_code=$?
    local restore_code=0
    trap - EXIT
    set +e

    if [[ "$smoke_dir_created" == true ]]; then
        rm -rf -- "$smoke_dir"
    fi
    if [[ -n "$temporary_cache" && -d "$temporary_cache" ]]; then
        rm -rf -- "$temporary_cache"
    fi

    if [[ "$cache_override_set" == true ]]; then
        if [[ "$original_cache_set" == true ]]; then
            uv run dvc config --local cache.dir "$original_cache_dir" >/dev/null
            restore_code=$?
        else
            uv run dvc config --local --unset cache.dir >/dev/null 2>&1
            restore_code=$?
        fi
        if [[ $restore_code -ne 0 && $exit_code -eq 0 ]]; then
            printf 'DVC round-trip failed: could not restore the previous local cache configuration.\n' >&2
            exit_code=1
        fi
    fi

    exit "$exit_code"
}
trap cleanup EXIT

if ! uv run dvc config --local cache.dir "$temporary_cache"; then
    fail "could not direct DVC to the temporary cache."
fi
cache_override_set=true

mkdir -p "$smoke_dir"
smoke_dir_created=true
printf 'DVC round-trip %s-%s-%s\n' "$(date +%s)" "$$" "$RANDOM" >"$smoke_file"

sha256_file() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{print $1}'
    else
        fail "sha256sum or shasum is required."
    fi
}

expected_sha=$(sha256_file "$smoke_file") || fail "could not checksum the test file."
uv run dvc add "$smoke_file" || fail "DVC could not add the temporary test file."
if ! uv run dvc push -r "$DVC_REMOTE"; then
    fail "push to remote '$DVC_REMOTE' failed; check that MinIO is running and AWS credentials are set."
fi

rm -f -- "$smoke_file"
rm -rf -- "$temporary_cache"
mkdir -p "$temporary_cache"
if ! uv run dvc pull -r "$DVC_REMOTE"; then
    fail "pull from remote '$DVC_REMOTE' failed; check that the remote is reachable and credentials are set."
fi

actual_sha=$(sha256_file "$smoke_file") || fail "DVC pull did not restore the test file."
[[ "$actual_sha" == "$expected_sha" ]] || fail "the restored file checksum does not match."

printf 'DVC ROUND-TRIP OK\n'
