# Stage 6 WP4 Public Repo Hygiene

This repo-only policy hardens the public repository checks that keep runtime-private detail, credential-shaped values, and local machine metadata out of committed artifacts.

Final trading is manually decided by the user.

## Hygiene Controls

| Control | Description | Verification |
|---|---|---|
| no_secret_or_token_values | Public files must not contain secrets, tokens, auth values, provider keys, Feishu app secrets, broker credentials, private keys, or sensitive assignment values. | scripts/safety/check_secret_leaks.py and scripts/safety/check_public_repo_hygiene.py |
| no_absolute_local_paths | Public files must avoid absolute local user or volume paths and exact live runtime fingerprints. | scripts/safety/check_public_repo_hygiene.py |
| no_credentialed_urls | Public files must not include URLs with embedded user credential material. | credentialed URL detection in scripts/safety/check_public_repo_hygiene.py |
| no_committed_local_private_details | Only local_private placeholders may be committed; private detail artifacts stay untracked. | local_private detail detection in scripts/safety/check_public_repo_hygiene.py |
| public_private_audit_split | Audit outputs keep public sanitized summaries in reports and private detail under local_private. | docs/public_repo_policy.md plus public repo hygiene scan |
| pre_commit_hygiene_verification | Run public repo hygiene, secret, forbidden-surface, ETF-universe, safety, smoke, and diff checks before pushing. | Program Runner required test list |

## Scan Summary

- status: pass.
- findings_count: 0.
- credentialed URL detection: enabled.
- local_private detail detection: enabled.

## Safety Result

- repo-only: true.
- live send attempted: false.
- real runtime modified: false.
- services restarted: false.
- broker write surface: false.
- automatic trading surface: false.
- order placement surface: false.
- trade ticket generated: false.
- risk_agent review: passed; no actionable trade suggestion generated.

## Next Safe Action

Proceed to `Stage 6 WP5 Hermes/Feishu notification stability`.
