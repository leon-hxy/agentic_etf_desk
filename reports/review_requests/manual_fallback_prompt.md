# Manual ChatGPT Review Fallback Prompt

Computer Use relay is optional and draft-only. If relay is unavailable, copy the prompt below into ChatGPT.

This fallback不会自动下单，最终交易由用户手动决定。

```text
Request manual major-stage ChatGPT review for public GitHub repo https://github.com/leon-hxy/agentic_etf_desk.
Review `review_target_commit`: `2006d60f237a9b47f34236fd7dd299e9bbdb4f86`.
请只读取这些公开路径：`reports/review_requests/latest.md`, `reports/review_requests/latest.json`, `reports/codex_handoff/latest.md`, `reports/codex_handoff/latest.json`。
重点检查 ETF-only、安全边界、无自动下单/券商写接口、无敏感信息泄漏、测试是否足够。
请输出 pass/fail、高风险问题、必须修复项、下一步建议。
repo 是 public，不需要 GitHub connector。最终交易由用户手动决定，系统不会自动下单。
```
