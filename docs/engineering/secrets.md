# CI secrets

Ticket 6 uses the accepted Backblaze B2 decision in [ADR-001](../adr/0001-ci-reachable-dvc-remote.md). Add these secrets after creating the bucket-scoped B2 application key; do not include values in the repository or issue comments.

Add the following names as GitHub Actions repository secrets. Store values in GitHub only; do not add them to `.env.example`, `.dvc/config`, workflow YAML, or issue comments.

| Secret name | Purpose | Rotation |
| --- | --- | --- |
| `DVC_S3_BUCKET` | Name of the provider bucket used by the CI DVC remote. | Update when the bucket is replaced or renamed; this is an identifier, not a credential. |
| `DVC_S3_ENDPOINT_URL` | HTTPS S3-compatible endpoint for the bucket's region/account. | Update when changing provider, account, or region. |
| `AWS_ACCESS_KEY_ID` | Access key for the CI-only object-store application key. | Create a replacement key, update this secret, verify the manual round trip, then revoke the old key. |
| `AWS_SECRET_ACCESS_KEY` | Secret half of the CI-only object-store application key. | Rotate together with `AWS_ACCESS_KEY_ID`; update both, verify, then revoke the old key. |

Use a dedicated key restricted to this bucket and only the object permissions DVC needs. Never reuse the MinIO root credentials or a personal cloud account's master key for CI. If a secret may have been exposed, revoke it at the provider immediately, replace the GitHub secret, and review recent access.
