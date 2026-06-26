# Feishu Message Templates

Repo-only message templates for a future Hermes notification layer.

## New Review Request

Codex 已完成任务，测试结果为 `{test_result}`，是否审核？

可回复：

- 确认审核
- 暂不审核
- 只看状态
- 开始下一阶段
- 暂停 loop

提醒：这个系统不会自动下单，最终交易由用户手动决定。

## Review Confirmed

已确认，Codex 将尝试通过 Computer Use 向 ChatGPT 发送审核请求。不会自动下单，最终交易由用户手动决定。

## Review Declined

已记录：暂不审核。不会写入 review gate。

## Status Only

当前阶段：`{stage}`

最新提交：`{commit}`

测试结果：`{tests}`

提醒：最终交易由用户手动决定。

## Relay Failed Fallback

Computer Use relay 未完成。请手动复制：

`请读取 leon-hxy/agentic_etf_desk 的 reports/review_requests/latest.md 和 reports/codex_handoff/latest.json，审核最新阶段是否通过。`
