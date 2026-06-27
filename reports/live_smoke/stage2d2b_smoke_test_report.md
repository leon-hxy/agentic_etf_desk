# Stage 2D.2B Live Notification Smoke Report

- Stage: `Stage 2D.2B live notification smoke completed; review gate pending`
- Generated at: `2026-06-27T15:13:26Z`
- Mode: `approved_live_notification_smoke`
- Approved live smoke: `true`
- Hermes skill load checked: `true`
- Hermes skills enabled: `true`
- Installed skill ids: `feishu-loop-notifier`, `feishu-review-command`
- Skill check method: `hermes skills list` reported both local skills as enabled; no Hermes restart was performed.
- Gateway status checked: `true`
- Gateway status public summary: status command returned successfully; raw status output was not published.
- Feishu message sent: `true`
- Feishu message count: `1`
- Feishu message target public: configured Feishu default target.
- Feishu message sensitive content: `false`
- Feishu confirmation observed: `false`
- Review gate written: `false`
- Review gate status: `pending_feishu_confirmation`
- OpenClaw modified: `false`
- Feishu gateway modified: `false`
- Services restarted: `false`
- Dependencies installed: `false`
- Computer Use executed: `false`
- Secret values printed: `false`
- Secret values committed: `false`
- Auto trading surface: `false`
- Broker surface: `false`

The smoke notification contained only a Stage 2D.2B status, the confirmation phrase request, and the manual-trading safety notice. Raw gateway status, raw logs, Feishu target identifiers, user identifiers, and secret-bearing configuration were not published.

Final trading is manually decided by the user. This system does not automatically place orders.
