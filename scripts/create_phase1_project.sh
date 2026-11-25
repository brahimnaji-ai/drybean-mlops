#!/usr/bin/env bash
set -euo pipefail

command -v gh >/dev/null 2>&1 || {
  printf 'GitHub CLI (gh) is required.\n' >&2
  exit 1
}
command -v jq >/dev/null 2>&1 || {
  printf 'jq is required.\n' >&2
  exit 1
}

OWNER="brahimnaji-ai"
REPOSITORY="${GH_REPO:-${OWNER}/drybean-mlops}"
TITLE="drybean-mlops"

projects="$(gh project list --owner "$OWNER" --format json)"
project_number="$(jq -r --arg title "$TITLE" \
  '.projects[] | select(.title == $title) | .number' <<<"$projects" | head -n 1)"

if [[ -z "$project_number" ]]; then
  project="$(gh project create --owner "$OWNER" --title "$TITLE" --format json)"
  project_number="$(jq -r '.number' <<<"$project")"
  printf 'Created project %s (#%s).\n' "$TITLE" "$project_number"
else
  printf 'Using existing project %s (#%s).\n' "$TITLE" "$project_number"
fi

linked_repositories="$(gh api graphql -F owner="$OWNER" -F number="$project_number" -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        repositories(first: 100) { nodes { nameWithOwner } }
      }
    }
  }
' --jq '.data.user.projectV2.repositories.nodes[].nameWithOwner')"

if ! grep -Fxq "$REPOSITORY" <<<"$linked_repositories"; then
  gh project link "$project_number" --owner "$OWNER" --repo "${REPOSITORY#*/}"
fi

project_fields="$(gh api graphql -F owner="$OWNER" -F number="$project_number" -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        id
        fields(first: 100) {
          nodes {
            ... on ProjectV2Field { id name }
            ... on ProjectV2SingleSelectField {
              id name
              options { id name color description }
            }
          }
        }
      }
    }
  }
')"
status_field="$(jq -c '.data.user.projectV2.fields.nodes[] | select(.name == "Status")' <<<"$project_fields")"
if [[ -z "$status_field" || "$status_field" == "null" ]]; then
  printf 'Project has no single-select Status field; set it manually to Backlog, Ready, In progress, In review, Done.\n' >&2
  exit 1
fi

status_mutation="$(jq -nr --arg field_id "$(jq -r '.id' <<<"$status_field")" \
  --argjson current "$status_field" '
  def options: [
    {name:"Backlog", color:"GRAY", description:"Not yet ready to start."},
    {name:"Ready", color:"BLUE", description:"Ready for work."},
    {name:"In progress", color:"YELLOW", description:"Work is underway."},
    {name:"In review", color:"PURPLE", description:"Awaiting review."},
    {name:"Done", color:"GREEN", description:"Completed."}
  ];
  def graphql_option($option):
    "{name: \($option.name|tojson), color: \($option.color), description: \($option.description|tojson)"
    + ([$current.options[]? | select((.name | ascii_downcase) == ($option.name | ascii_downcase)) | .id][0] as $id
       | if $id == null then "" else ", id: \($id|tojson)" end)
    + "}";
  "mutation { updateProjectV2Field(input: {fieldId: \($field_id|tojson), singleSelectOptions: ["
  + (options | map(graphql_option(.)) | join(", "))
  + "]}) { projectV2Field { ... on ProjectV2SingleSelectField { name options { name } } } } }"
')"
gh api graphql -f query="$status_mutation" >/dev/null
printf 'Configured Status options: Backlog, Ready, In progress, In review, Done.\n'

issue_urls="$(gh api graphql -F owner="$OWNER" -F number="$project_number" -f query='
  query($owner: String!, $number: Int!) {
    user(login: $owner) {
      projectV2(number: $number) {
        items(first: 100) {
          nodes {
            content {
              ... on Issue { url }
              ... on PullRequest { url }
            }
          }
        }
      }
    }
  }
' --jq '.data.user.projectV2.items.nodes[].content.url')"

for issue_number in {1..9}; do
  issue_url="https://github.com/${REPOSITORY}/issues/${issue_number}"
  if grep -Fxq "$issue_url" <<<"$issue_urls"; then
    printf 'Issue #%s is already on the project.\n' "$issue_number"
  else
    gh project item-add "$project_number" --owner "$OWNER" --url "$issue_url"
    issue_urls+=$'\n'"$issue_url"
  fi
done

printf 'Project board: https://github.com/users/%s/projects/%s\n' "$OWNER" "$project_number"
