# GitHub Public Repo Security

This repository is public. Treat every committed file as globally readable.

## Recommended GitHub Settings

- Confirm GitHub Secret scanning is enabled.
- Enable Push protection where available.
- Keep branch protection or review rules aligned with the repository's risk profile.

## What Not To Upload

Do not upload:

- Real local private audit details.
- Real secrets, tokens, auth values, provider keys, Feishu App Secret values, or broker credentials.
- Local machine absolute paths or local usernames.
- Private process identifiers or exact live service state details.
- Broker account files or write credentials.

## If A Secret Was Ever Uploaded

If a real secret was ever committed, immediately rotate the secret. Editing git history is not enough because public clones, caches, or logs may already contain it.

## If Private Metadata Was Uploaded

If non-secret personal or device metadata was uploaded, the user can choose:

1. Soft sanitize: sanitize only current `HEAD`.
2. Strict sanitize: rewrite git history with a reviewed tool such as `git filter-repo`.
3. Recreate the public repository from a clean export.
4. Keep history as-is and accept that old non-secret metadata remains visible.

## Stage 2A.5 Boundary

This stage must not rewrite git history automatically. It only sanitizes current `HEAD` and documents the choices for any stricter future cleanup.
