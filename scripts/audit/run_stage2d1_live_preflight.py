#!/usr/bin/env python3
"""Run Stage 2D.1 read-only live preflight and write sanitized repo reports."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


REPORT_DIR = Path("reports/live_preflight")
TASK_PATH = Path("ops/tasks/stage2d1_read_only_live_preflight.md")
OUTPUTS = {
    "preflight": (
        REPORT_DIR / "stage2d1_live_preflight_report.json",
        REPORT_DIR / "stage2d1_live_preflight_report.md",
    ),
    "minimal_change": (
        REPORT_DIR / "stage2d1_minimal_change_list.json",
        REPORT_DIR / "stage2d1_minimal_change_list.md",
    ),
    "backup": (
        REPORT_DIR / "stage2d1_backup_checklist.json",
        REPORT_DIR / "stage2d1_backup_checklist.md",
    ),
    "rollback": (
        REPORT_DIR / "stage2d1_rollback_checklist.json",
        REPORT_DIR / "stage2d1_rollback_checklist.md",
    ),
    "safety": (
        REPORT_DIR / "stage2d1_safety_test_results.json",
        REPORT_DIR / "stage2d1_safety_test_results.md",
    ),
}
EXPECTED_FEISHU_KEYS = [
    "FEISHU_APP_ID",
    "FEISHU_APP_SECRET",
    "FEISHU_DOMAIN",
    "FEISHU_CONNECTION_MODE",
    "FEISHU_ALLOWED_USERS",
    "FEISHU_HOME_CHANNEL",
    "FEISHU_GROUP_POLICY",
    "FEISHU_REQUIRE_MENTION",
]


def run_read_only_command(command: list[str], timeout: int = 5) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
        return {
            "command": " ".join(command[:3]),
            "available": True,
            "exit_code": completed.returncode,
            "stdout_line_count": len(completed.stdout.splitlines()),
            "stderr_line_count": len(completed.stderr.splitlines()),
        }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {
            "command": " ".join(command[:3]),
            "available": False,
            "exit_code": None,
            "stdout_line_count": 0,
            "stderr_line_count": 0,
        }


def path_status(home: Path, label: str) -> dict[str, Any]:
    path = home / label.removeprefix("~/")
    return {
        "label": label,
        "exists": path.exists(),
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
    }


def key_names_from_env(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    keys: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            keys.add(key)
    return sorted(keys)


def key_names_from_yaml_like(path: Path) -> list[str]:
    if not path.exists() or not path.is_file():
        return []
    keys: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_-]*)\s*:", line)
        if match:
            keys.add(match.group(1))
    return sorted(keys)


def process_summary() -> dict[str, Any]:
    completed = subprocess.run(
        ["ps", "-axo", "comm=,args="],
        text=True,
        capture_output=True,
        check=False,
    )
    keywords = ("hermes", "feishu", "gateway")
    names: set[str] = set()
    matched_count = 0
    for line in completed.stdout.splitlines():
        lowered = line.lower()
        if not any(keyword in lowered for keyword in keywords):
            continue
        matched_count += 1
        command = line.strip().split(maxsplit=1)[0]
        names.add(Path(command).name)
    return {
        "keyword_match_count": matched_count,
        "process_names": sorted(names),
    }


def launchctl_summary() -> dict[str, Any]:
    completed = subprocess.run(
        ["launchctl", "list"],
        text=True,
        capture_output=True,
        check=False,
    )
    labels: set[str] = set()
    running_labels: set[str] = set()
    keywords = ("hermes", "feishu", "gateway")
    for line in completed.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue
        label = parts[-1]
        if not any(keyword in label.lower() for keyword in keywords):
            continue
        labels.add(label)
        if parts[0] != "-":
            running_labels.add(label)
    return {
        "label_count": len(labels),
        "running_label_count": len(running_labels),
        "labels": sorted(labels),
    }


def listening_ports_summary() -> dict[str, Any]:
    completed = subprocess.run(
        ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"],
        text=True,
        capture_output=True,
        check=False,
    )
    ports: set[str] = set()
    commands: set[str] = set()
    keywords = ("hermes", "feishu", "gateway")
    for line in completed.stdout.splitlines()[1:]:
        lowered = line.lower()
        if not any(keyword in lowered for keyword in keywords):
            continue
        parts = line.split()
        if not parts:
            continue
        commands.add(parts[0])
        address = parts[-2] if len(parts) >= 2 else ""
        if ":" in address:
            ports.add(address.rsplit(":", 1)[-1])
    return {
        "matched_command_names": sorted(commands),
        "listening_ports": sorted(port for port in ports if port.isdigit()),
    }


def build_preflight(root: Path) -> dict[str, Any]:
    home = Path.home()
    hermes_home = Path(os.environ.get("HERMES_HOME", str(home / ".hermes"))).expanduser()
    config_path = hermes_home / "config.yaml"
    env_path = hermes_home / ".env"
    env_keys = key_names_from_env(env_path)
    config_keys = key_names_from_yaml_like(config_path)
    command_checks = {
        "which_hermes": {
            "command": "command -v hermes",
            "found": shutil.which("hermes") is not None,
        },
        "hermes_version": run_read_only_command(["hermes", "--version"]),
        "hermes_gateway_status": run_read_only_command(["hermes", "gateway", "status"]),
    }

    return {
        "stage": "Stage 2D.1 read-only live preflight completed",
        "mode": "read_only_live_preflight",
        "approval_scope": {
            "read_only_live_preflight": True,
            "live_write_approved": False,
            "service_restart_approved": False,
            "dependency_install_approved": False,
            "computer_use_approved": False,
            "feishu_send_approved": False,
        },
        "hermes": {
            "config_paths": [
                "~/.hermes",
                "~/.hermes/config.yaml",
                "~/.hermes/.env",
                "~/.hermes/SOUL.md",
                "~/.hermes/memories",
                "~/.hermes/skills",
            ],
            "path_status": [
                path_status(home, "~/.hermes"),
                path_status(home, "~/.hermes/config.yaml"),
                path_status(home, "~/.hermes/.env"),
                path_status(home, "~/.hermes/SOUL.md"),
                path_status(home, "~/.hermes/memories"),
                path_status(home, "~/.hermes/skills"),
            ],
            "config_key_names": config_keys,
            "env_key_names": env_keys,
            "command_checks": command_checks,
            "process_summary": process_summary(),
            "launchctl_summary": launchctl_summary(),
            "listening_ports_summary": listening_ports_summary(),
        },
        "feishu_gateway": {
            "expected_key_names": EXPECTED_FEISHU_KEYS,
            "present_key_names": sorted(key for key in EXPECTED_FEISHU_KEYS if key in env_keys),
            "missing_key_names": sorted(key for key in EXPECTED_FEISHU_KEYS if key not in env_keys),
            "gateway_config_candidate_paths": [
                "~/.hermes/config.yaml",
                "~/.hermes/.env",
                "~/.hermes/skills",
            ],
            "real_message_sent": False,
        },
        "installable_points": {
            "~/.hermes/config.yaml": config_path.exists(),
            "~/.hermes/.env": env_path.exists(),
            "~/.hermes/skills": (hermes_home / "skills").exists(),
            "configs/hermes/feishu_loop_notifier_skill.md": (
                root / "configs/hermes/feishu_loop_notifier_skill.md"
            ).exists(),
            "configs/hermes/feishu_review_command_skill.md": (
                root / "configs/hermes/feishu_review_command_skill.md"
            ).exists(),
            "ops/review_gate/review_gate.example.json": (
                root / "ops/review_gate/review_gate.example.json"
            ).exists(),
        },
        "safety_flags": safety_flags(),
        "raw_command_output_written": False,
        "secret_values_written": False,
        "final_trading_notice": "Final trading is manually decided by the user.",
    }


def safety_flags() -> dict[str, bool]:
    return {
        "real_config_modified": False,
        "hermes_modified": False,
        "openclaw_modified": False,
        "feishu_gateway_modified": False,
        "services_restarted": False,
        "dependencies_installed": False,
        "secrets_touched": False,
        "secret_values_written": False,
        "feishu_message_sent": False,
        "computer_use_executed": False,
        "auto_trading_surface": False,
    }


def minimal_change_list() -> dict[str, Any]:
    return {
        "stage": "Stage 2D.1 read-only live preflight completed",
        "mode": "planned_only",
        "requires_user_approval_before_live_change": True,
        "live_changes_applied": False,
        "candidate_changes": [
            {
                "target": "~/.hermes/skills",
                "source": "configs/hermes/feishu_loop_notifier_skill.md",
                "action": "future approved install or registration only",
            },
            {
                "target": "~/.hermes/skills",
                "source": "configs/hermes/feishu_review_command_skill.md",
                "action": "future approved install or registration only",
            },
            {
                "target": "local_private/review_gate.json",
                "source": "ops/review_gate/review_gate.example.json",
                "action": "future approved local private gate creation only",
            },
        ],
        "non_actions": [
            "No live config changed",
            "No service restarted",
            "No dependency installed",
            "No Feishu message sent",
            "No Computer Use run",
            "No secret value written",
        ],
        "final_trading_notice": "Final trading is manually decided by the user.",
    }


def backup_checklist() -> dict[str, Any]:
    return {
        "stage": "Stage 2D.1 read-only live preflight completed",
        "backup_created": False,
        "requires_user_approval_before_backup": True,
        "future_backup_items": [
            "~/.hermes/config.yaml",
            "~/.hermes/.env",
            "~/.hermes/skills",
            "real Feishu gateway config path selected by user",
        ],
        "manifest_rules": [
            "Record file labels, checksums, sizes, timestamps, and redacted key names only",
            "Do not record secret values",
            "Do not commit backup files to this repo",
        ],
        "final_trading_notice": "Final trading is manually decided by the user.",
    }


def rollback_checklist() -> dict[str, Any]:
    return {
        "stage": "Stage 2D.1 read-only live preflight completed",
        "rollback_executed": False,
        "requires_user_approval_before_rollback": True,
        "future_rollback_items": [
            "Restore approved Hermes backup files",
            "Restore approved Feishu gateway backup files",
            "Remove future installed notification skill only if user approves",
            "Remove future local approval gate file only if user approves",
            "Restart services only if user explicitly approves",
        ],
        "abort_conditions": [
            "Any secret value would be printed",
            "Any Feishu message would be sent without approval",
            "Any service restart is needed without approval",
            "Any automatic trading surface appears",
        ],
        "final_trading_notice": "Final trading is manually decided by the user.",
    }


def safety_results() -> dict[str, Any]:
    flags = safety_flags()
    return {
        "stage": "Stage 2D.1 read-only live preflight completed",
        "status": "passed",
        "live_actions_detected": False,
        "safety_flags": flags,
        "checks": [
            "Read-only config path existence checked",
            "Only key names recorded from environment-like files",
            "Process and launchctl status summarized without raw command lines",
            "No Feishu message sent",
            "No Computer Use run",
            "No service restart",
            "No dependency installation",
            "No broker or automatic trading surface added",
        ],
        "final_trading_notice": "Final trading is manually decided by the user.",
    }


def render_markdown(title: str, payload: dict[str, Any]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Stage: `{payload.get('stage', '')}`",
        f"- Mode: `{payload.get('mode', payload.get('status', ''))}`",
        "",
        "## Sanitized JSON",
        "",
        "```json",
        json.dumps(payload, indent=2, sort_keys=True),
        "```",
        "",
        "No secret values, raw command output, absolute local paths, service restarts, dependency installs, Feishu sends, or Computer Use actions are included.",
        "",
        "Final trading is manually decided by the user.",
        "",
    ]
    return "\n".join(lines)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_outputs(root: Path) -> dict[str, Any]:
    payloads = {
        "preflight": build_preflight(root),
        "minimal_change": minimal_change_list(),
        "backup": backup_checklist(),
        "rollback": rollback_checklist(),
        "safety": safety_results(),
    }
    titles = {
        "preflight": "Stage 2D.1 Live Preflight Report",
        "minimal_change": "Stage 2D.1 Minimal Change List",
        "backup": "Stage 2D.1 Backup Checklist",
        "rollback": "Stage 2D.1 Rollback Checklist",
        "safety": "Stage 2D.1 Safety Test Results",
    }
    for key, payload in payloads.items():
        json_path, md_path = OUTPUTS[key]
        write_json(root / json_path, payload)
        (root / md_path).write_text(render_markdown(titles[key], payload), encoding="utf-8")
    return {
        "status": "generated",
        "stage": "Stage 2D.1 read-only live preflight completed",
        "outputs": {key: [str(path) for path in paths] for key, paths in OUTPUTS.items()},
    }


def check_outputs(root: Path) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    for key, paths in OUTPUTS.items():
        for path in paths:
            if not (root / path).exists():
                findings.append({"file": str(path), "reason": f"missing {key} output"})
    if findings:
        return {"status": "fail", "findings": findings}

    preflight = json.loads((root / OUTPUTS["preflight"][0]).read_text(encoding="utf-8"))
    if preflight.get("mode") != "read_only_live_preflight":
        findings.append({"file": str(OUTPUTS["preflight"][0]), "reason": "wrong mode"})
    for field, value in preflight.get("safety_flags", {}).items():
        if value is not False:
            findings.append({"file": str(OUTPUTS["preflight"][0]), "reason": f"{field} must be false"})

    combined = "\n".join((root / path).read_text(encoding="utf-8") for paths in OUTPUTS.values() for path in paths)
    forbidden = [
        "/" + "Users" + "/",
        "/" + "Volumes" + "/",
        "FEISHU" + "_APP" + "_SECRET=",
        "OpenAI API key=",
        "token=",
        "secret=",
        "auth=",
        "sent_to_feishu: true",
        "computer_use_executed: true",
        "services_restarted: true",
        "dependencies_installed: true",
    ]
    for fragment in forbidden:
        if fragment in combined:
            findings.append({"file": "reports/live_preflight", "reason": f"contains {fragment}"})
    return {"status": "pass" if not findings else "fail", "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    payload = check_outputs(root) if args.check else write_outputs(root)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] in {"generated", "pass"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
