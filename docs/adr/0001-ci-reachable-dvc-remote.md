# ADR-001: CI-reachable DVC remote

- **Status:** Accepted
- **Date:** 2026-11-24

## Context

The committed DVC remote is local MinIO. GitHub-hosted runners cannot reach the maintainer's laptop, so a manually triggered DVC round-trip check needs an internet-reachable remote. The project already uses DVC's S3 remote locally; the CI remote should preserve the same DVC object-store behavior and be configured at runtime without committing provider-specific endpoints or credentials.

The maintainer's constraint is **free-tier first, with no bank card**. Provider pricing and limits below were checked on 2026-11-24. Free allowances and account requirements can change; recheck the linked provider documentation before creating an account or relying on a quota.

## Decision drivers

1. No bank card or billing method required to get started.
2. Free allowance sufficient for this project's small dataset and DVC round-trip verification.
3. S3 compatibility with DVC's `dvc-s3` remote, including a configurable endpoint and environment-based credentials.
4. Low or predictable egress and request costs if usage exceeds the free allowance.
5. Straightforward account, bucket, and credential setup for an individual student.
6. Keep the existing local MinIO remote and `.dvc/config` unchanged.

## Considered options

| Option | Free tier, egress, and account requirement (checked 2026-11-24) | DVC compatibility and credential model | Setup and fit |
| --- | --- | --- | --- |
| **Backblaze B2** | First 10 GB of storage is free; egress is free up to 3× average monthly stored data, then $0.01/GB. Backblaze says a billing method is not required to start exploring B2. [Pricing](https://www.backblaze.com/cloud-storage/pricing) · [B2 signup guide](https://help.backblaze.com/hc/en-us/articles/360010017893-Delivering-Private-Backblaze-B2-Content-Through-Cloudflare-CDN) | S3-compatible API uses S3 syntax and an endpoint of `https://s3.<region>.backblazeb2.com`; DVC supports S3-compatible endpoints and AWS environment credentials. Create a bucket-scoped application key for CI. [B2 S3 API](https://www.backblaze.com/docs/cloud-storage-s3-compatible-api) · [DVC S3-compatible remotes](https://doc.dvc.org/user-guide/data-management/remote-storage/amazon-s3) | Create an account, enable B2, create a bucket and application key. The provider's integration guide estimates about 15 minutes. Strong fit for the no-card constraint and the ticket's four S3 secrets. [Setup guide](https://www.backblaze.com/docs/en/cloud-storage-get-started-with-a-backblaze-integration) |
| **Cloudflare R2** | Free monthly usage includes 10 GB-month, 1 million Class A operations, 10 million Class B operations, and no egress charge. Enabling R2 uses a subscription checkout; Cloudflare requires a payment method to purchase products and services. [R2 pricing](https://developers.cloudflare.com/r2/pricing/) · [Create billing profile](https://developers.cloudflare.com/billing/get-started/create-billing-profile/) · [R2 setup](https://developers.cloudflare.com/r2/get-started/) | S3-compatible API and S3 credentials; DVC can set a custom endpoint. [R2 S3 API](https://developers.cloudflare.com/r2/api/s3/) · [DVC S3-compatible remotes](https://doc.dvc.org/user-guide/data-management/remote-storage/amazon-s3) | Easy technically, but it does not meet the maintainer's no-bank-card rule because the R2 subscription requires a payment method. |
| **Amazon S3** | The current Free plan gives new customers up to $200 in eligible-service credits for six months; this is introductory credit, not a lasting S3 free allowance. AWS says most new signups do not need a payment method, but it may request one for identity verification. S3 charges vary by storage, requests, retrieval, and data transfer. [AWS Free Tier FAQ](https://aws.amazon.com/free/free-tier-faqs/) · [S3 pricing](https://aws.amazon.com/s3/pricing/) | Native S3 support in DVC; use AWS credentials and a bucket-specific IAM policy. [DVC S3 remote](https://doc.dvc.org/user-guide/data-management/remote-storage/amazon-s3) | S3 is the most direct API match, but account verification may ask for a payment method and the free offer is time-limited. That uncertainty makes it a weaker fit for this constraint. |
| **Google Drive** | A standard Google Account includes up to 15 GB shared across Drive, Gmail, and Photos. That allowance needs no storage subscription; the account still has to be created. [Google storage allowance](https://support.google.com/drive/answer/9312312) | DVC has a native Google Drive remote, but it is not S3-compatible and does not use the ticket's S3 endpoint/secrets. DVC's default OAuth flow can work interactively; CI automation uses a service account or custom Google Cloud OAuth project, and default API quotas are shared. [DVC Google Drive remote](https://s.dvc.org/user-guide/data-management/remote-storage/google-drive) | Avoids an S3 bucket, but requires a different runtime configurator and secret model. It would change the ticket's specified S3 workflow rather than preserve its intended semantics. |
| **DagsHub Storage** | DagsHub's Individual plan is $0 and its current pricing page lists 20 GB of DagsHub Storage. Its DVC integration guide currently also says 100 GB, so the provider's public pages disagree; use 20 GB as the conservative figure and verify the account quota. The public material reviewed did not state whether signup requires a bank card. [Pricing](https://dagshub.com/pricing/) · [DVC storage guide](https://dagshub.com/docs/integration_guide/dvc/) | DagsHub provides a DVC remote and S3-compatible bucket. Credentials are a DagsHub token used as both access key and secret; the endpoint is repository/owner scoped. [DagsHub storage docs](https://dagshub.com/docs/feature_guide/dagshub_storage/) | Good DVC integration and free allowance, but the no-card condition is not verifiable from the public account/pricing documentation reviewed. Defer unless the maintainer confirms card-free signup. |

## Decision outcome

**Decision: Backblaze B2.** The maintainer selected B2 during follow-up setup, with the EU Central (Amsterdam) region. It is the best documented match for the hard no-bank-card rule, maintains the existing S3/DVC semantics, and offers a modest free storage allowance with bounded free egress. Backblaze's signup guide documents creating a free account and selecting its data region; the B2 S3-compatible API uses standard application keys.

Keep `.dvc/config` configured with only the local `minio` remote. The CI workflow will create a temporary `ci` remote from `DVC_S3_BUCKET` and `DVC_S3_ENDPOINT_URL`; credentials will be supplied only as GitHub Secrets/environment variables. The maintainer handles Backblaze account, bucket, and credential setup.

## Consequences

- **Next:** add the four GitHub Secrets listed in [the secrets guide](../engineering/secrets.md). The runtime remote configurator is implemented; the manual workflow will follow once those secrets exist.
- **Costs:** the documented B2 free storage and egress are likely adequate for this project, but they are not a hard spending cap. Review usage and provider pricing before storing larger artifacts.
- **Portability:** DVC continues to use its S3 remote type; only the endpoint, bucket, and credentials differ from local MinIO.
- **If B2 account setup asks for a bank card:** stop and revisit the decision. Do not switch providers silently; DagsHub is the next candidate only after confirming its card requirement and current storage quota.
- **Rotation:** rotate the B2 application key if it is exposed or when access should be revoked; update GitHub Secrets first, verify a round trip, then revoke the old key. Never put key values in the repository or issue comments.

## Links

- [DVC: Amazon S3 and compatible servers](https://doc.dvc.org/user-guide/data-management/remote-storage/amazon-s3)
- [Backblaze B2 pricing](https://www.backblaze.com/cloud-storage/pricing)
- [Backblaze B2 signup guide](https://help.backblaze.com/hc/en-us/articles/360010017893-Delivering-Private-Backblaze-B2-Content-Through-Cloudflare-CDN)
- [Cloudflare R2 pricing](https://developers.cloudflare.com/r2/pricing/)
- [AWS Free Tier FAQ](https://aws.amazon.com/free/free-tier-faqs/)
- [Google Drive remote in DVC](https://s.dvc.org/user-guide/data-management/remote-storage/google-drive)
- [DagsHub pricing](https://dagshub.com/pricing/)
