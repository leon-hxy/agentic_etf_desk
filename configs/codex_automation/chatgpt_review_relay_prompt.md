# ChatGPT Review Relay Prompt Draft

This is a Codex App automation prompt draft. It is not installed and must not run live Computer Use without future user approval.

## Draft Behavior

Periodically check `local_private/review_gate.json`.

If no valid gate exists, do not perform any ChatGPT UI operation.

If a valid gate exists:

1. Build the ChatGPT review prompt with `scripts/review_relay/build_chatgpt_review_prompt.py`.
2. Use Computer Use or Chrome to open ChatGPT.
3. Create or open the intended ChatGPT conversation.
4. Paste the generated public prompt.
5. Before sending, verify the prompt contains no secrets, local paths, tokens, auth values, Feishu credentials, provider keys, broker credentials, or private runtime config.
6. Send the prompt.
7. Update `reports/review_requests/relay_status.md` and `relay_status.json`.
8. Mark the gate used with `scripts/review_relay/mark_review_gate_used.py`.

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

Stage 2A.6 only creates this draft. It does not create automation, open ChatGPT, or use Computer Use.
