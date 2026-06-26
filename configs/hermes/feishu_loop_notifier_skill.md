# Feishu Loop Notifier Skill Draft

This is a repo-only Hermes skill draft. It must not be installed into real `~/.hermes` without explicit user approval.

## Purpose

Notify the user in Feishu when Codex has produced a new review request.

## Inputs

- `reports/review_requests/latest.json`
- `reports/codex_handoff/latest.json`
- local-only state file `local_private/notification_state.json`

## Behavior

1. Read `reports/review_requests/latest.json`.
2. Read `reports/codex_handoff/latest.json`.
3. Compare the latest commit and stage with `local_private/notification_state.json`.
4. If the same commit/stage was already notified, do nothing.
5. If the review request is new, notify the user in Feishu:
   `Codex 已完成任务，测试结果为 X，是否审核？`
6. Offer reply options:
   - `确认审核`
   - `暂不审核`
   - `只看状态`
   - `开始下一阶段`
   - `暂停 loop`
7. Record local notification state in `local_private/notification_state.json`.

## Safety

- 不得修改真实 ~/.hermes unless the user later approves installation.
- 不得修改真实 ~/.openclaw.
- Do not write Feishu secrets into this repo.
- Do not store private user IDs or chat IDs in public files.
- Do not send secrets, local paths, Feishu credentials, provider keys, or broker credentials.
- The notification must say this loop 不会自动下单 and 最终交易由用户手动决定.
