# Branching Policy

This project uses branch governance to keep major-stage review, construction,
and small-stage Codex self-review separate.

## Branch roles

`main` is the stable branch. It should only contain major-stage states that have
passed manual ChatGPT review, plus small repo-only governance and handoff fixes
that do not start a new business stage.

main is the stable branch and should only contain major-stage states that have
passed manual ChatGPT review.

main should only contain major-stage states that have passed manual ChatGPT review.

`stage/*` branches are major-stage construction branches. Stage 3 uses
`stage/stage3-data-backtest` for data-source, data-quality, backtest, and
strategy-evidence work.

stage/* branches are major-stage construction branches.

`task/*` branches are optional small-stage construction branches. Use them only
when a small-stage change needs extra isolation before it is merged back into
the active `stage/*` branch.

task/* branches are optional small-stage construction branches.

## Review rules

Small-stage review is Codex self-review. Codex must update repo handoff files,
run the relevant safety and smoke tests, and record the result before finishing
the round.

Major-stage review is manual ChatGPT review. Codex prepares public repo
materials, but the user decides whether and when to request ChatGPT review.

Codex does not request ChatGPT review for small stages.

Codex does not use Computer Use to send review requests to ChatGPT.

ChatGPT Computer Use automatic review route is deprecated.

## Stage 3 branch plan

Stage 3 construction starts from the latest `main` after Stage 2F.1 is pushed.
The construction branch is `stage/stage3-data-backtest`.

Stage 3A, 3B, 3C, and 3D are small stages and use Codex self-review. Stage 3E
packages the major-stage review materials and notifies the user through the
approved Feishu path that a manual ChatGPT review may be requested.

Stage 2F.1 must not start Stage 3 business code. It only creates the branch
policy, Stage 3 task plan, state updates, handoff artifacts, and safety tests.

Stage 3E is historical Stage 3 governance for the sample-data pipeline
validation package. After Stage 3.1 is merged into main, autonomous completion
work uses `stage/v1-autonomous-completion`.

Stage 3.2 through Stage 6 use final v1.0 program review only. Internal Program
Runner work packages use Codex internal review, and Codex does not request
ChatGPT review for internal Program Runner work packages.

Do not request ChatGPT review for internal Program Runner work packages.

## Safety boundaries

ETF-only remains mandatory. Final trading is manually decided by the user. The
system produces research, backtests, risk reviews, reports, and manual trade
recommendation tickets only.

Do not modify real `~/.hermes`, real `~/.openclaw`, or the real Feishu gateway
without explicit user approval for that exact live task.

Do not restart Hermes or OpenClaw, install dependencies, run Computer Use,
connect broker write interfaces, add automatic trading behavior, or publish
secrets, tokens, auth values, private runtime paths, Feishu credentials,
provider keys, or broker credentials.
