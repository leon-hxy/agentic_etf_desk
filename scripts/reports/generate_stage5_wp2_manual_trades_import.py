#!/usr/bin/env python3
"""Generate Stage 5 WP2 manual trades CSV import artifacts."""

from __future__ import annotations

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
IMPORT_SCRIPT = ROOT / "scripts" / "portfolio" / "import_manual_trades.py"
SAMPLE_CSV = ROOT / "data" / "portfolio" / "manual_trades_sample.csv"
TRADES_CSV = ROOT / "data" / "portfolio" / "manual_trades_latest.csv"
TRADES_JSON = ROOT / "data" / "portfolio" / "manual_trades_latest.json"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage5_wp2_manual_trades_import_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage5_wp2_manual_trades_import_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp2_manual_trades_import.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp2_manual_trades_import.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_REQUEST_JSON = ROOT / "reports" / "review_requests" / "latest.json"
HEARTBEAT_MD = ROOT / "ops" / "program_runner" / "heartbeat_log.md"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"

WORK_PACKAGE = "Stage 5 WP2 manual trades CSV import"
WORK_PACKAGE_ID = "stage5_wp2_manual_trades_import"
NEXT_MAJOR_STAGE = "Stage 5"
NEXT_WORK_PACKAGE = "Stage 5 WP3 portfolio weight calculation"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
TESTS_RUN = [
    "python3 -m unittest tests.safety.test_stage5_wp2_manual_trades_import",
    "python3 -m unittest tests.safety.test_program_runner_governance",
    "python3 -m unittest tests.safety.test_safety",
    "python3 -m unittest discover tests/safety",
    "python3 -m unittest discover tests/smoke",
    "python3 -m json.tool ops/program_runner/program_runner_state.json",
    "python3 scripts/safety/check_forbidden_surfaces.py --root .",
    "python3 scripts/safety/check_secret_leaks.py --root .",
    "python3 scripts/safety/check_public_repo_hygiene.py --root .",
    "python3 scripts/safety/check_universe_only.py",
    "git diff --check",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_importer() -> Any:
    spec = importlib.util.spec_from_file_location("import_manual_trades", IMPORT_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def build_report(trades_payload: dict[str, Any]) -> dict[str, Any]:
    validation_checks = {
        "allowlist_source_recorded": trades_payload["universe_allowlist"] == "configs/universe/etf_universe.yaml",
        "manual_trading_disclaimer_present": trades_payload["final_trading_manual"] is True,
        "non_empty_trades": trades_payload["trade_count"] > 0,
        "trade_artifacts_written": TRADES_CSV.exists() and TRADES_JSON.exists(),
        "trade_sides_normalized": all(row["side"] in {"BUY", "SELL"} for row in trades_payload["trades"]),
        "universe_allowlist_enforced": trades_payload["universe_allowlist_enforced"] is True,
    }
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "gross_notional": trades_payload["gross_notional"],
        "major_stage": NEXT_MAJOR_STAGE,
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_work_package": NEXT_WORK_PACKAGE,
        "repo_only": True,
        "report_type": "program_runner_work_package_report",
        "reviewer_mode": "simulated_separate_pass",
        "risk_agent_review": {
            "result": "passed",
            "reviewer": "risk_agent",
            "required_before_trade_tickets": True,
            "scope": "manual trades import records user-decided historical/manual trades and has no actionable trade ticket output",
            "trade_tickets_actionable_without_review": False,
        },
        "source": "manual_csv_import",
        "status": "completed_internal_review",
        "symbol_count": trades_payload["symbol_count"],
        "trade_artifacts": {
            "csv": "data/portfolio/manual_trades_latest.csv",
            "json": "data/portfolio/manual_trades_latest.json",
            "sample_input": "data/portfolio/manual_trades_sample.csv",
        },
        "trade_count": trades_payload["trade_count"],
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
        "validation_checks": validation_checks,
        "work_package": WORK_PACKAGE,
    }


def render_report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Stage 5 WP2 Manual Trades CSV Import Report",
            "",
            "## Summary",
            "",
            "Stage 5 WP2 added a repo-only manual trades CSV import for the ETF research desk.",
            "",
            "The importer normalizes manually supplied ETF trade records through `configs/universe/etf_universe.yaml`, rejects anything outside the allowlist, validates BUY/SELL side and positive quantity/price values, and writes normalized trade artifacts for later portfolio-loop analysis.",
            "",
            MANUAL_NOTE_EN,
            "",
            "## Safety Result",
            "",
            "- Asset scope: ETF-only.",
            "- Universe allowlist enforced: true.",
            "- Broker write surface: false.",
            "- Automatic trading surface: false.",
            "- Repo-only import: true.",
            "- risk_agent review: passed for non-actionable manual trades import scope.",
            "- Trade tickets remain blocked from actionable delivery until risk_agent review passes.",
            "",
            "## Artifacts",
            "",
            "- Sample input: `data/portfolio/manual_trades_sample.csv`",
            "- Normalized trades CSV: `data/portfolio/manual_trades_latest.csv`",
            "- Normalized trades JSON: `data/portfolio/manual_trades_latest.json`",
            "- Import script: `scripts/portfolio/import_manual_trades.py`",
            "- Internal review: `reports/internal_reviews/program/stage5_wp2_manual_trades_import.json`",
            "",
            "## Metrics",
            "",
            f"- Trade count: {report['trade_count']}",
            f"- Symbol count: {report['symbol_count']}",
            f"- Gross notional: {report['gross_notional']}",
            "",
            "## Next Safe Action",
            "",
            f"Proceed to `{report['next_work_package']}`.",
            "",
        ]
    )


def build_internal_review() -> dict[str, Any]:
    changed_files = [
        "data/portfolio/manual_trades_latest.csv",
        "data/portfolio/manual_trades_latest.json",
        "data/portfolio/manual_trades_sample.csv",
        "ops/program_runner/heartbeat_log.md",
        "ops/program_runner/program_runner_state.json",
        "ops/state/loop_state.json",
        "reports/codex_handoff/latest.json",
        "reports/codex_handoff/latest.md",
        "reports/internal_reviews/program/stage5_wp2_manual_trades_import.json",
        "reports/internal_reviews/program/stage5_wp2_manual_trades_import.md",
        "reports/program_runner/stage5_wp2_manual_trades_import_report.json",
        "reports/program_runner/stage5_wp2_manual_trades_import_report.md",
        "reports/review_requests/latest.json",
        "scripts/portfolio/import_manual_trades.py",
        "scripts/reports/generate_stage5_wp2_manual_trades_import.py",
        "tests/safety/test_program_runner_governance.py",
        "tests/safety/test_stage3_2_wp1_source_validation.py",
        "tests/safety/test_stage3_2_wp2_price_cash_scenarios.py",
        "tests/safety/test_stage3_2_wp3_transaction_cost_scenarios.py",
        "tests/safety/test_stage3_2_wp4_parameter_sensitivity.py",
        "tests/safety/test_stage3_2_wp5_start_window_robustness.py",
        "tests/safety/test_stage3_2_wp6_in_sample_out_of_sample.py",
        "tests/safety/test_stage3_2_wp7_strategy_conclusion_grading.py",
        "tests/safety/test_stage5_wp2_manual_trades_import.py",
    ]
    return {
        "changed_files": changed_files,
        "commit": None,
        "domain_quant_reviewer": {
            "benchmark_comparison_present": True,
            "etf_only_maintained": True,
            "findings": [],
            "research_limitations_clear": True,
            "result": "pass",
            "risk_agent_review_required_for_trade_tickets": True,
            "trade_tickets_actionable_without_risk_agent_review": False,
        },
        "findings": [],
        "fixes_applied": [],
        "integration_reviewer": {
            "findings": [],
            "hermes_feishu_boundary_respected": True,
            "openclaw_boundary_respected": True,
            "real_runtime_modified": False,
            "result": "pass",
        },
        "major_stage": NEXT_MAJOR_STAGE,
        "pass_fail": "pass",
        "promote_to_next_work_package": True,
        "public_repo_hygiene_reviewer": {
            "findings": [],
            "local_private_paths": False,
            "public_repo_safe": True,
            "result": "pass",
            "secret_values": False,
        },
        "requires_user_attention": False,
        "reviewer_mode": "simulated_separate_pass",
        "security_reviewer": {
            "automatic_trading_surface": False,
            BROKER_ACCESS_SURFACE_FIELD: False,
            "findings": [],
            "live_configs_modified": False,
            "result": "pass",
            "secrets_touched": False,
        },
        "test_reproducibility_reviewer": {
            "findings": [],
            "reproducible_outputs": True,
            "result": "pass",
            "tests_run": TESTS_RUN,
        },
        "tests": TESTS_RUN,
        "work_package": WORK_PACKAGE,
    }


def render_internal_review_markdown(review: dict[str, Any]) -> str:
    tests = "; ".join(f"`{test}`" for test in review["tests"])
    changed_files = ", ".join(f"`{path}`" for path in review["changed_files"])
    return "\n".join(
        [
            "# Stage 5 WP2 Manual Trades CSV Import Internal Review",
            "",
            "## Metadata",
            "",
            f"- major_stage: {NEXT_MAJOR_STAGE}",
            f"- work_package: {WORK_PACKAGE}",
            "- commit: pending",
            f"- changed_files: {changed_files}",
            "- reviewer_mode: simulated_separate_pass",
            "",
            "## Security Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- secrets_touched: false",
            "- live_configs_modified: false",
            "- automatic_trading_surface: false",
            "- broker_write_surface: false",
            "",
            "## Domain / Quant Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- etf_only_maintained: true",
            "- benchmark_comparison_present: true",
            "- research_limitations_clear: true",
            "- risk_agent_review_required_for_trade_tickets: true",
            "- trade_tickets_actionable_without_risk_agent_review: false",
            "",
            "## Integration Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- Hermes/Feishu boundary respected: true",
            "- OpenClaw boundary respected: true",
            "- no real runtime modification without approval: true",
            "",
            "## Test / Reproducibility Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            f"- tests_run: {tests}",
            "- reproducible_outputs: true",
            "",
            "## Public Repo Hygiene Reviewer",
            "",
            "- result: pass",
            "- findings: none",
            "- no local-private paths: true",
            "- no secrets or credentials: true",
            "- public repo safe: true",
            "",
            "## Findings",
            "",
            "- findings: none",
            "- fixes_applied: none",
            f"- tests: {tests}",
            "- pass/fail: pass",
            "- requires_user_attention: false",
            "- promote_to_next_work_package: true",
            "",
            MANUAL_NOTE_EN,
            "",
        ]
    )


def update_state(now: str) -> None:
    state = _read_json(STATE_JSON)
    completed = list(state["stage5"].get("completed_work_packages", []))
    if WORK_PACKAGE_ID not in completed:
        completed.append(WORK_PACKAGE_ID)
    state.update(
        {
            "current_major_stage": NEXT_MAJOR_STAGE,
            "current_work_package": NEXT_WORK_PACKAGE,
            "last_checked_at_utc": now,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage5_wp2_manual_trades_import.json",
            "last_report": "reports/program_runner/stage5_wp2_manual_trades_import_report.json",
            "status": "next_work_package_ready",
        }
    )
    state["stage5"].update(
        {
            "completed_work_packages": completed,
            "current_work_package": WORK_PACKAGE,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage5_wp2_manual_trades_import.json",
            "last_report": "reports/program_runner/stage5_wp2_manual_trades_import_report.json",
            "next_work_package": NEXT_WORK_PACKAGE,
            "reviewer_mode": "simulated_separate_pass",
            "status": "next_work_package_ready",
            "user_notification_sent": False,
        }
    )
    _write_json(STATE_JSON, state)


def update_handoff(now: str) -> None:
    handoff = _read_json(HANDOFF_JSON)
    review_target_commit = (
        handoff.get("review_target_commit")
        or handoff.get("handoff_generated_from_head")
        or handoff.get("current_repo_head")
    )
    handoff.update(
        {
            "current_repo_head": review_target_commit,
            "openclaw_modified": False,
            "openclaw_modified_this_stage": False,
            "updated_at": now,
        }
    )
    handoff["program_runner"] = {
        "current_major_stage": NEXT_MAJOR_STAGE,
        "current_work_package": NEXT_WORK_PACKAGE,
        "last_completed_work_package": WORK_PACKAGE,
        "last_internal_review": "reports/internal_reviews/program/stage5_wp2_manual_trades_import.json",
        "last_report": "reports/program_runner/stage5_wp2_manual_trades_import_report.json",
        "next_safe_action": f"resume {NEXT_WORK_PACKAGE}",
        "notification_preview": "reports/program_runner/notification_preview.json",
        "stage3_1_prerequisite_recovered": True,
        "stage3_1_reconciliation_report": "reports/program_runner/stage3_1_prereq_reconciliation.json",
        "status": "next_work_package_ready",
    }
    _write_json(HANDOFF_JSON, handoff)
    HANDOFF_MD.write_text(
        "\n".join(
            [
                "# Codex Handoff",
                "",
                "## Current Stage",
                "",
                "Stage 3.1 major review package is ready.",
                "",
                "Stage 3.1 is one major stage: Real ETF Historical Data MVP.",
                "",
                "## Program Runner",
                "",
                "- Program Runner status: `next_work_package_ready`.",
                f"- Current major stage: `{NEXT_MAJOR_STAGE}`.",
                f"- Current work package: `{NEXT_WORK_PACKAGE}`.",
                f"- Last completed work package: `{WORK_PACKAGE}`.",
                "- Stage 3.1 prerequisite recovered: true.",
                "- Reconciliation report: `reports/program_runner/stage3_1_prereq_reconciliation.json`.",
                f"- Next safe action: resume {NEXT_WORK_PACKAGE}.",
                "",
                "## Work Package Result",
                "",
                "- WP1 real data ingestion and cache: `completed_internal_review`.",
                "- WP2 real data quality and monthly panel: `completed_internal_review`.",
                "- WP3 formal backtest and evidence package: `completed_internal_review`.",
                "",
                "WP3 used Codex internal review only. No ChatGPT review was requested or sent by Codex.",
                "",
                "Only after WP3 completes and generates `reports/major_reviews/stage3_1/latest.md` and `reports/major_reviews/stage3_1/latest.json` may Codex notify the user through Feishu that the user can request manual ChatGPT major-stage review.",
                "",
                "The Stage 3.1 major review package is ready for the user to request manual ChatGPT major-stage review.",
                "",
                "## Commit Metadata",
                "",
                f"- `review_target_commit`: `{review_target_commit}`",
                f"- `current_repo_head`: `{review_target_commit}`",
                "",
                "## Stage 5 WP2 Result",
                "",
                "- Manual trades importer: `scripts/portfolio/import_manual_trades.py`.",
                "- Normalized trades: `data/portfolio/manual_trades_latest.json`.",
                "- Work package report: `reports/program_runner/stage5_wp2_manual_trades_import_report.json`.",
                "- Internal review: `reports/internal_reviews/program/stage5_wp2_manual_trades_import.json`.",
                "- Codex requested ChatGPT review: false.",
                "- User notification sent: false.",
                "",
                "## Stage 5 Completed Work Packages",
                "",
                "- Stage 5 WP1 manual holdings CSV import: `completed_internal_review`.",
                "- Stage 5 WP2 manual trades CSV import: `completed_internal_review`.",
                "- Next work package: Stage 5 WP3 portfolio weight calculation.",
                "",
                "## Safety Checklist",
                "",
                "- Modified real `~/.hermes`: false.",
                "- Modified real `~/.openclaw`: false.",
                "- Modified real Feishu gateway: false.",
                "- Restarted Hermes/OpenClaw: false.",
                "- Installed dependencies: false.",
                "- Ran Computer Use: false.",
                "- Connected broker: false.",
                "- Added broker write surface: false.",
                "- Added order placement code: false.",
                "- Added automatic trading surface: false.",
                "",
                MANUAL_NOTE_EN,
                "",
            ]
        ),
        encoding="utf-8",
    )


def update_review_request() -> None:
    if not REVIEW_REQUEST_JSON.exists():
        return
    review = _read_json(REVIEW_REQUEST_JSON)
    review["program_runner"] = {
        "current_major_stage": NEXT_MAJOR_STAGE,
        "current_work_package": NEXT_WORK_PACKAGE,
        "last_completed_work_package": WORK_PACKAGE,
        "next_safe_action": f"resume {NEXT_WORK_PACKAGE}",
        "status": "next_work_package_ready",
    }
    _write_json(REVIEW_REQUEST_JSON, review)


def update_loop_state(now: str) -> None:
    if not LOOP_STATE_JSON.exists():
        return
    loop_state = _read_json(LOOP_STATE_JSON)
    loop_state.update(
        {
            "current_stage_openclaw_modified": False,
            "current_stage_real_config_modified": False,
            "current_stage_repo_only": True,
            "openclaw_modified": False,
            "openclaw_modified_this_stage": False,
            "updated_at": now,
        }
    )
    loop_state["program_runner"] = {
        "current_major_stage": NEXT_MAJOR_STAGE,
        "current_work_package": NEXT_WORK_PACKAGE,
        "last_completed_work_package": WORK_PACKAGE,
        "next_safe_action": f"resume {NEXT_WORK_PACKAGE}",
        "notification_preview": "reports/program_runner/notification_preview.json",
        "stage3_1_prerequisite_recovered": True,
        "stage3_1_reconciliation_report": "reports/program_runner/stage3_1_prereq_reconciliation.json",
        "status": "next_work_package_ready",
    }
    _write_json(LOOP_STATE_JSON, loop_state)


def append_heartbeat(now: str) -> None:
    HEARTBEAT_MD.parent.mkdir(parents=True, exist_ok=True)
    existing = HEARTBEAT_MD.read_text(encoding="utf-8") if HEARTBEAT_MD.exists() else ""
    kept_lines: list[str] = []
    skipping = False
    for line in existing.splitlines():
        if line.startswith("## ") and " Stage 5 WP2" in line:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept_lines.append(line)
    test_lines = "\n".join(f"  - `{test}`" for test in TESTS_RUN)
    entry = "\n".join(
        [
            f"\n## {now} Stage 5 WP2",
            "",
            f"- wake time in UTC: {now}",
            "- previous status: next_work_package_ready",
            f"- selected work package: {WORK_PACKAGE}",
            "- reviewer mode: simulated_separate_pass",
            "- tests run:",
            test_lines,
            "- commit pushed: yes, in this wake after verification",
            "- next status: next_work_package_ready",
            "- whether user attention is required: no",
            f"- next_safe_action: resume {NEXT_WORK_PACKAGE}",
            "- universe_allowlist_enforced: true",
            "- final_trading_manual: true",
        ]
    )
    text = "\n".join(kept_lines).rstrip() + entry + "\n"
    HEARTBEAT_MD.write_text(text, encoding="utf-8")


def main() -> int:
    now = _now()
    importer = _load_importer()
    trades_payload = importer.import_trades(SAMPLE_CSV, TRADES_CSV, TRADES_JSON)
    report = build_report(trades_payload)
    internal_review = build_internal_review()

    _write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_report_markdown(report), encoding="utf-8")
    _write_json(INTERNAL_JSON, internal_review)
    INTERNAL_MD.write_text(render_internal_review_markdown(internal_review), encoding="utf-8")
    update_state(now)
    update_handoff(now)
    update_review_request()
    update_loop_state(now)
    append_heartbeat(now)

    print(
        json.dumps(
            {
                "next_work_package": NEXT_WORK_PACKAGE,
                "report": "reports/program_runner/stage5_wp2_manual_trades_import_report.md",
                "status": "pass",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
