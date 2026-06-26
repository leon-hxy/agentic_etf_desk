# Feishu Review Command Skill Draft

This is a repo-only Hermes skill draft. It must not be installed into real `~/.hermes` without explicit user approval.

## Purpose

Handle user replies in Feishu and create a local private review gate only when the user explicitly replies `确认审核`.

## Commands

### 确认审核

1. Read `reports/review_requests/latest.json`.
2. Verify the latest review request has a commit, stage, and passing test summary.
3. Write `local_private/review_gate.json`.
4. Set `approved` to true.
5. Set `approved_action` to `chatgpt_review_relay`.
6. Bind the gate to the latest commit.
7. Set `expires_at` to a short window such as 15 minutes after approval.
8. Generate a one-time nonce.
9. Reply in Feishu:
   `已确认，Codex 将尝试通过 Computer Use 向 ChatGPT 发送审核请求。不会自动下单，最终交易由用户手动决定。`

### 暂不审核

Do not write `local_private/review_gate.json`. Reply with a short acknowledgement.

### 只看状态

Return a concise handoff summary from `reports/codex_handoff/latest.json`.

### 开始下一阶段

Ask the user for explicit confirmation before entering any long-running Stage 2B work.

### 暂停 loop

Record only local private state if an approved local runtime integration exists. Do not modify this repo with private runtime details.

## Safety

- 不得修改真实 ~/.hermes unless the user later approves installation.
- 不得修改真实 ~/.openclaw.
- Do not modify real OpenClaw config.
- Do not restart services.
- Do not install dependencies.
- Do not write Feishu secrets, tokens, provider keys, or broker credentials.
- Do not create automatic trading capability.
