# Local Private Notes

This directory is for local-only private audit details and operator notes.

Only this README and `.gitkeep` should be committed. All other files under `local_private/` are ignored by git.

Do not place secrets, tokens, auth values, `.env` values, Feishu App Secret values, provider keys, or broker credentials in public repo files. If local private detail is needed, keep it here and do not commit it.

Expected local-only state files include:

- `local_private/notification_state.json`
- `local_private/review_gate.json`

These files are runtime state only. They must not contain public repo secrets, and they must never be committed.
