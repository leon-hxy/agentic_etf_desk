# Public Repo Policy

This project is a public repository. Public repo artifacts must be safe to read without exposing private local runtime details.

## Forbidden In Public Repo Files

Do not commit:

- Real secrets.
- Tokens.
- Auth values.
- `.env` values.
- Feishu App Secret values.
- Provider keys.
- Broker credentials.
- Private keys or certificates.
- User/channel allowlists when they expose private IDs.

## Private Local Metadata

Public files should also avoid exposing:

- Local usernames.
- Absolute local machine paths.
- Process identifiers.
- Exact live process state.
- Overly detailed local environment fingerprints.

Allowed public summaries include generalized statements such as:

- `macOS arm64`.
- `Hermes installed`.
- `OpenClaw installed`.
- `$HOME`, `$PROJECT_ROOT`, `$HERMES_HOME`, and `$OPENCLAW_HOME`.
- `~/.hermes` and `~/.openclaw` when used as generic home-relative paths.

## Public And Private Audit Split

All future audit work must produce two layers:

- Public sanitized summary for the repo.
- Local private detail under `local_private/`.

The `local_private/` directory is ignored by git except for `local_private/.gitkeep` and `local_private/README.md`.

Public handoff files must keep safe summaries only. They must not include local absolute paths, process identifiers, secret values, tokens, provider keys, broker credentials, or precise live machine state.

## Review Rule

Before every commit, run the public repo hygiene test and the normal safety/smoke tests. If a finding appears, sanitize the repo content rather than weakening the safety boundary.
