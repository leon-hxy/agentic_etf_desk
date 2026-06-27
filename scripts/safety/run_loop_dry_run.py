#!/usr/bin/env python3
"""Generate or validate the Stage 2C repo-only loop dry-run report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPORT_JSON = Path("reports/loop_dry_run/stage2c_loop_dry_run.json")
REPORT_MD = Path("reports/loop_dry_run/stage2c_loop_dry_run.md")
LOOP_STATE = Path("ops/state/loop_state.json")
TASK = Path("ops/tasks/stage2c_loop_automation_dry_run.md")


def load_json(root: Path, path: Path) -> dict[str, Any]:
    return json.loads((root / path).read_text(encoding="utf-8"))


def safety_flags() -> dict[str, bool]:
    return {
        "real_config_modified": False,
        "hermes_modified": False,
        "openclaw_modified": False,
        "feishu_gateway_modified": False,
        "services_restarted": False,
        "dependencies_installed": False,
        "secrets_touched": False,
        "auto_trading_surface": False,
        "computer_use_executed": False,
    }


def build_payload(root: Path) -> dict[str, Any]:
    loop_state = load_json(root, LOOP_STATE)
    repo_only_writes = [
        str(REPORT_JSON),
        str(REPORT_MD),
        "reports/review_requests/notification_preview.json",
        "reports/review_requests/notification_preview.md",
        str(LOOP_STATE),
        str(TASK),
    ]
    return {
        "stage": "Stage 2C completed",
        "mode": "repo_only_dry_run",
        "dry_run_only": True,
        "source_task": str(TASK),
        "inputs": [
            "reports/codex_handoff/latest.json",
            "reports/review_requests/latest.json",
            str(LOOP_STATE),
            str(TASK),
        ],
        "repo_only_writes": repo_only_writes,
        "state_transition": {
            "from": "Stage 2B completed",
            "to": loop_state["current_stage"],
            "next_task": loop_state["next_task"],
            "next_task_status": loop_state["next_task_status"],
        },
        "dry_run_steps": [
            "Read latest handoff and review request artifacts.",
            "Read loop state and Stage 2C task file.",
            "Render repo-only loop dry-run report.",
            "Render repo-only notification preview.",
            "Wait for user direction before any live integration work.",
        ],
        "blocked_live_actions": [
            "Modify real ~/.hermes",
            "Modify real ~/.openclaw",
            "Modify a real Feishu gateway",
            "Restart Hermes or OpenClaw",
            "Install dependencies",
            "Run real Computer Use",
            "Write secrets, tokens, auth values, .env values, provider keys, Feishu App Secret, or broker credentials",
            "Connect broker write interfaces",
        ],
        "safety_flags": safety_flags(),
        "manual_trading_notice": (
            "This is a repo-only dry run. It will not send orders, will not create "
            "automatic trading capability, and final trading is manually decided by the user."
        ),
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 2C Loop Automation Dry Run",
        "",
        f"- Stage: `{payload['stage']}`",
        f"- Mode: `{payload['mode']}`",
        f"- Dry run only: `{str(payload['dry_run_only']).lower()}`",
        f"- State transition: `{payload['state_transition']['from']}` -> `{payload['state_transition']['to']}`",
        f"- Next task: `{payload['state_transition']['next_task']}`",
        f"- Next task status: `{payload['state_transition']['next_task_status']}`",
        "",
        "## Repo-Only Writes",
        "",
    ]
    lines.extend(f"- `{path}`" for path in payload["repo_only_writes"])
    lines.extend(
        [
            "",
            "## Blocked Live Actions",
            "",
        ]
    )
    lines.extend(f"- {action}" for action in payload["blocked_live_actions"])
    lines.extend(
        [
            "",
            "## Safety Flags",
            "",
        ]
    )
    lines.extend(f"- `{key}`: `{str(value).lower()}`" for key, value in payload["safety_flags"].items())
    lines.extend(
        [
            "",
            "This dry run does not modify real Hermes/OpenClaw configuration, does not modify a real Feishu gateway, does not restart services, does not install dependencies, does not run Computer Use, and does not touch secrets.",
            "",
            "This system will not automatically send orders. Final trading is manually decided by the user.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(root: Path) -> dict[str, Any]:
    payload = build_payload(root)
    json_path = root / REPORT_JSON
    md_path = root / REPORT_MD
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def add(findings: list[dict[str, str]], file: str, reason: str) -> None:
    findings.append({"file": file, "reason": reason})


def check(root: Path) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    if not (root / REPORT_JSON).exists():
        add(findings, str(REPORT_JSON), "missing dry-run JSON report")
        return {"status": "fail", "findings": findings}
    if not (root / REPORT_MD).exists():
        add(findings, str(REPORT_MD), "missing dry-run Markdown report")

    expected = build_payload(root)
    actual = load_json(root, REPORT_JSON)
    if actual != expected:
        add(findings, str(REPORT_JSON), "dry-run JSON report is stale")

    for path in actual.get("repo_only_writes", []):
        if path.startswith("/") or path.startswith("~"):
            add(findings, str(REPORT_JSON), "repo-only write path is not relative")
        if "local_private" in path:
            add(findings, str(REPORT_JSON), "repo-only write path points to local_private")

    for field, value in actual.get("safety_flags", {}).items():
        if value is not False:
            add(findings, str(REPORT_JSON), f"{field} must be false")

    text = (root / REPORT_MD).read_text(encoding="utf-8") if (root / REPORT_MD).exists() else ""
    if "Final trading is manually decided by the user" not in text:
        add(findings, str(REPORT_MD), "missing manual trading notice")
    if "does not run Computer Use" not in text:
        add(findings, str(REPORT_MD), "missing Computer Use dry-run notice")

    return {"status": "pass" if not findings else "fail", "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    payload = check(root) if args.check else {"status": "generated", "report": str(REPORT_JSON), "payload": write_outputs(root)}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"pass", "generated"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
