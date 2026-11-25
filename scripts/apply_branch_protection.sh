#!/usr/bin/env bash
set -euo pipefail

REPOSITORY="${GH_REPO:-brahimnaji-ai/drybean-mlops}"
RULESET_NAME="drybean-main-protection"

command -v gh >/dev/null 2>&1 || {
  printf 'GitHub CLI (gh) is required.\n' >&2
  exit 1
}
command -v jq >/dev/null 2>&1 || {
  printf 'jq is required.\n' >&2
  exit 1
}

ruleset_id="$(gh api "repos/${REPOSITORY}/rulesets" --paginate \
  --jq ".[] | select(.name == \"${RULESET_NAME}\") | .id" | head -n 1)"

payload="$(jq -n --arg name "$RULESET_NAME" '
  {
    name: $name,
    target: "branch",
    enforcement: "active",
    conditions: {
      ref_name: {
        include: ["refs/heads/main"],
        exclude: []
      }
    },
    rules: [
      {
        type: "pull_request",
        parameters: {
          required_approving_review_count: 0,
          dismiss_stale_reviews_on_push: false,
          require_code_owner_review: false,
          require_last_push_approval: false,
          required_review_thread_resolution: true
        }
      },
      {
        type: "required_status_checks",
        parameters: {
          strict_required_status_checks_policy: true,
          required_status_checks: [
            {context: "lint"},
            {context: "typecheck"},
            {context: "test"},
            {context: "docker-build"}
          ]
        }
      },
      {type: "required_linear_history"},
      {type: "non_fast_forward"},
      {type: "deletion"}
    ],
    bypass_actors: []
  }
')"

if [[ -n "$ruleset_id" ]]; then
  printf '%s' "$payload" | gh api "repos/${REPOSITORY}/rulesets/${ruleset_id}" \
    --method PUT --input - >/dev/null
  printf 'Updated ruleset %s (%s).\n' "$RULESET_NAME" "$ruleset_id"
else
  response="$(printf '%s' "$payload" | gh api "repos/${REPOSITORY}/rulesets" \
    --method POST --input -)"
  ruleset_id="$(jq -r '.id' <<<"$response")"
  printf 'Created ruleset %s (%s).\n' "$RULESET_NAME" "$ruleset_id"
fi

gh api "repos/${REPOSITORY}" --method PATCH \
  -F allow_squash_merge=true \
  -F allow_merge_commit=false \
  -F allow_rebase_merge=false \
  -F delete_branch_on_merge=true >/dev/null

gh api "repos/${REPOSITORY}" --jq \
  '"Merge settings: squash=\(.allow_squash_merge), merge_commit=\(.allow_merge_commit), rebase=\(.allow_rebase_merge), auto_delete=\(.delete_branch_on_merge)"'
