# ChatGPT Review Relay Prompt Draft

This is a Codex App automation prompt draft. It is not installed and must not run live Computer Use without future user approval.

## Draft Behavior

Periodically check `local_private/review_gate.json`.

If no valid gate exists, do not perform any ChatGPT UI operation.

If a valid gate exists:

1. Build the ChatGPT review prompt with `scripts/review_relay/build_chatgpt_review_prompt.py`.
2. Default to `dedicated_review_thread`.
3. Use `existing_conversation_url` only when `local_private/chatgpt_review_target.json` exists and explicitly selects that mode.
4. Never write an existing ChatGPT conversation URL to public repo files.
5. Use Computer Use or Chrome to open ChatGPT only after explicit user approval for the live relay.
6. Verify the selected ChatGPT conversation matches the target mode before entering text.
7. Paste or clipboard-insert the generated short public prompt; do not type a long prompt character by character.
8. Before sending, verify the prompt contains no secrets, local paths, tokens, auth values, Feishu credentials, provider keys, broker credentials, or private runtime config.
9. Send only if the input box contains exactly the short prompt and no residual draft.
10. After sending, confirm the complete prompt appears as one sent message.
11. If the target conversation mismatches, residual draft is present, the prompt is split, or the sent message cannot be confirmed, mark failed and stop.
12. Update `reports/review_requests/relay_status.md` and `relay_status.json`.
13. Mark the gate used with `scripts/review_relay/mark_review_gate_used.py` only after a confirmed send.

## Restrictions

- Do not access pages other than `chatgpt.com`, `github.com`, and `raw.githubusercontent.com`.
- Do not read local secrets.
- Do not modify real `~/.hermes`.
- Do not modify real `~/.openclaw`.
- Do not restart services.
- Do not install dependencies.
- Do not access broker systems.
- Do not create automatic trading capability.
- Do not place orders.

Stage 2E.1 only hardens this draft and public prompt generation. It does not open ChatGPT, send a message, or use Computer Use.
