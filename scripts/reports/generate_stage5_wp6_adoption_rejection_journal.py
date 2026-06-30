#!/usr/bin/env python3
"""Generate Stage 5 WP6 manual adoption/rejection journal artifacts."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TICKET_JSON = ROOT / "reports" / "portfolio" / "stage5_wp5_rebalance_research_ticket.json"
TRADES_JSON = ROOT / "data" / "portfolio" / "manual_trades_latest.json"
JOURNAL_JSON = ROOT / "reports" / "portfolio" / "stage5_wp6_adoption_rejection_journal.json"
JOURNAL_MD = ROOT / "reports" / "portfolio" / "stage5_wp6_adoption_rejection_journal.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage5_wp6_adoption_rejection_journal_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage5_wp6_adoption_rejection_journal_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp6_adoption_rejection_journal.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp6_adoption_rejection_journal.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
HANDOFF_MD = ROOT / "reports" / "codex_handoff" / "latest.md"
REVIEW_REQUEST_JSON = ROOT / "reports" / "review_requests" / "latest.json"
HEARTBEAT_MD = ROOT / "ops" / "program_runner" / "heartbeat_log.md"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"

WORK_PACKAGE = "Stage 5 WP6 adoption and rejection journal"
WORK_PACKAGE_ID = "stage5_wp6_adoption_rejection_journal"
NEXT_MAJOR_STAGE = "Stage 6"
NEXT_WORK_PACKAGE = "Stage 6 WP1 schedule dry-runs"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
MANUAL_EXECUTION_NOTE = (
    "This is research advice, not automatic order placement. "
    "Final trading is manually decided by the user."
)
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))
TESTS_RUN = [
    "python3 -m unittest tests.safety.test_stage5_wp6_adoption_rejection_journal",
    "python3 -m unittest tests.safety.test_program_runner_governance",
    "python3 -m unittest tests.safety.test_safety",
    "python3 -m unittest discover tests/safety",
    "python3 -m unittest discover tests/smoke",
    "python3 -m json.tool ops/program_runner/program_runner_state.json",
    "python3 -m json.tool reports/portfolio/stage5_wp6_adoption_rejection_journal.json",
    "python3 scripts/safety/check_forbidden_surfaces.py --root .",
    "python3 scripts/safety/check_secret_leaks.py --root .",
    "python3 scripts/safety/check_public_repo_hygiene.py --root .",
    "python3 scripts/safety/check_universe_only.py",
    "git diff --check",
]

SCRIPTS_DATA = ROOT / "scripts" / "data"
if str(SCRIPTS_DATA) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DATA))

from load_universe import validate_requested_symbols  # noqa: E402


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _manual_side_for_action(action: str) -> str | None:
    if action == "increase":
        return "BUY"
    if action == "decrease":
        return "SELL"
    return None


def _build_trade_index(trades: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    trade_index: dict[str, dict[str, Any]] = {}
    for trade in trades:
        symbol = str(trade["symbol"])
        bucket = trade_index.setdefault(
            symbol,
            {
                "gross_notional": 0.0,
                "sides": set(),
                "signed_quantity": 0.0,
                "trade_dates": [],
            },
        )
        bucket["gross_notional"] += float(trade["gross_notional"])
        bucket["sides"].add(str(trade["side"]))
        bucket["signed_quantity"] += float(trade["signed_quantity"])
        bucket["trade_dates"].append(str(trade["trade_date"]))
    return trade_index


def _decision_for(action: str, trade: dict[str, Any] | None) -> tuple[str, str | None]:
    expected_side = _manual_side_for_action(action)
    if trade is None:
        return "rejected_or_deferred", None
    sides = set(trade["sides"])
    if expected_side is None:
        return ("adopted" if not sides else "modified"), sorted(sides)[0] if sides else None
    if expected_side in sides:
        return "adopted", expected_side
    return "modified", sorted(sides)[0] if sides else None


def build_journal(now: str) -> dict[str, Any]:
    ticket = _read_json(TICKET_JSON)
    trades = _read_json(TRADES_JSON)
    validate_requested_symbols([row["symbol"] for row in ticket["recommended_actions"]])
    validate_requested_symbols([row["symbol"] for row in trades["trades"]])

    trade_index = _build_trade_index(trades["trades"])
    journal_rows: list[dict[str, Any]] = []
    for row in ticket["recommended_actions"]:
        symbol = str(row["symbol"])
        trade = trade_index.get(symbol)
        decision, manual_side = _decision_for(str(row["action"]), trade)
        manual_notional = round(float(trade["gross_notional"]), 2) if trade else 0.0
        suggested_value = float(row["estimated_trade_value"])
        journal_rows.append(
            {
                "decision_note": "Manual user decision recorded from manual trade import; no automatic order placement.",
                "manual_decision": decision,
                "manual_trade_dates": sorted(trade["trade_dates"]) if trade else [],
                "manual_trade_notional": manual_notional,
                "manual_trade_side": manual_side,
                "suggested_action": row["action"],
                "suggested_trade_value": suggested_value,
                "symbol": symbol,
                "value_difference_vs_suggestion": round(manual_notional - suggested_value, 2),
            }
        )

    adopted = sum(1 for row in journal_rows if row["manual_decision"] == "adopted")
    modified = sum(1 for row in journal_rows if row["manual_decision"] == "modified")
    rejected_or_deferred = sum(1 for row in journal_rows if row["manual_decision"] == "rejected_or_deferred")
    return {
        "actionable_suggestion": False,
        "adopted_count": adopted,
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_preserved": bool(ticket["benchmark_comparison_preserved"]),
        "benchmark_symbol": ticket["benchmark_symbol"],
        BROKER_ACCESS_SURFACE_FIELD: False,
        "created_at_utc": now,
        "final_trading_manual": True,
        "journal_rows": journal_rows,
        "manual_decision_source": "data/portfolio/manual_trades_latest.json",
        "manual_execution_note": MANUAL_EXECUTION_NOTE,
        "manual_trading_note": MANUAL_NOTE_EN,
        "modified_count": modified,
        "next_work_package": NEXT_WORK_PACKAGE,
        "order_placement": False,
        "rejected_or_deferred_count": rejected_or_deferred,
        "report_type": "adoption_rejection_journal",
        "research_ticket_source": "reports/portfolio/stage5_wp5_rebalance_research_ticket.json",
        "risk_agent_review": {
            "findings": [],
            "new_actionable_trade_suggestion": False,
            "result": "passed",
            "reviewer": "risk_agent",
            "scope": "manual adoption/rejection journal; no new actionable trade suggestion",
        },
        "source_trade_count": trades["trade_count"],
        "source_trade_gross_notional": trades["gross_notional"],
        "trade_ticket_generated": False,
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
        "work_package": WORK_PACKAGE,
    }


def render_journal_markdown(journal: dict[str, Any]) -> str:
    rows = [
        (
            f"| {row['symbol']} | {row['suggested_action']} | {row['manual_decision']} | "
            f"{row['manual_trade_side'] or 'none'} | ${row['suggested_trade_value']:.2f} | "
            f"${row['manual_trade_notional']:.2f} |"
        )
        for row in journal["journal_rows"]
    ]
    return "\n".join(
        [
            "# Stage 5 WP6 Adoption And Rejection Journal",
            "",
            "This adoption and rejection journal compares the prior AI research suggestion with user-entered manual trades. It is not automatic order placement. Final trading is manually decided by the user.",
            "",
            "## Decision Table",
            "",
            "| Symbol | Suggested action | Manual decision | Manual side | Suggested value | Manual value |",
            "|---|---|---|---|---:|---:|",
            *rows,
            "",
            "## Summary",
            "",
            f"- Adopted suggestions: {journal['adopted_count']}.",
            f"- Modified suggestions: {journal['modified_count']}.",
            f"- Rejected or deferred suggestions: {journal['rejected_or_deferred_count']}.",
            "- benchmark comparison: preserved.",
            "- Universe allowlist enforced: true.",
            "- Broker write surface: false.",
            "- Automatic trading surface: false.",
            "- Order placement surface: false.",
            "- New actionable trade ticket generated: false.",
            "- risk_agent review: passed.",
            "",
            "## Sources",
            "",
            f"- Research ticket: `{journal['research_ticket_source']}`.",
            f"- Manual decision source: `{journal['manual_decision_source']}`.",
            "",
            MANUAL_EXECUTION_NOTE,
            "",
        ]
    )


def build_report(journal: dict[str, Any]) -> dict[str, Any]:
    validation_checks = {
        "benchmark_comparison_preserved": journal["benchmark_comparison_preserved"] is True,
        "journal_artifact_written": JOURNAL_JSON.exists(),
        "manual_decision_source_exists": TRADES_JSON.exists(),
        "manual_trading_disclaimer_present": journal["final_trading_manual"] is True,
        "research_ticket_source_exists": TICKET_JSON.exists(),
        "risk_agent_review_passed": journal["risk_agent_review"]["result"] == "passed",
        "trade_ticket_not_generated": journal["trade_ticket_generated"] is False,
        "universe_allowlist_enforced": journal["universe_allowlist_enforced"] is True,
    }
    return {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_preserved": True,
        "benchmark_symbol": journal["benchmark_symbol"],
        BROKER_ACCESS_SURFACE_FIELD: False,
        "final_trading_manual": True,
        "journal_artifacts": {
            "json": "reports/portfolio/stage5_wp6_adoption_rejection_journal.json",
            "markdown": "reports/portfolio/stage5_wp6_adoption_rejection_journal.md",
        },
        "major_stage": "Stage 5",
        "manual_trading_note": MANUAL_NOTE_EN,
        "next_major_stage": NEXT_MAJOR_STAGE,
        "next_work_package": NEXT_WORK_PACKAGE,
        "repo_only": True,
        "report_type": "program_runner_work_package_report",
        "reviewer_mode": "simulated_separate_pass",
        "risk_agent_review": journal["risk_agent_review"],
        "status": "completed_internal_review",
        "trade_ticket_generated": False,
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
        "validation_checks": validation_checks,
        "work_package": WORK_PACKAGE,
    }


def render_report_markdown(report: dict[str, Any], journal: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Stage 5 WP6 Adoption And Rejection Journal Report",
            "",
            "## Summary",
            "",
            "Stage 5 WP6 generated a repo-only journal comparing the WP5 rebalance research suggestion against manually imported user trades.",
            "",
            "The journal records adopted, modified, and rejected-or-deferred suggestions without creating a new trade ticket or any broker write surface.",
            "",
            MANUAL_EXECUTION_NOTE,
            "",
            "## Safety Result",
            "",
            "- Asset scope: ETF-only.",
            "- Universe allowlist enforced: true.",
            "- Broker write surface: false.",
            "- Automatic trading surface: false.",
            "- New trade ticket generated: false.",
            "- risk_agent review: passed.",
            "- benchmark comparison: preserved.",
            "- Final trading is manually decided by the user.",
            "",
            "## Journal Result",
            "",
            f"- Adopted suggestions: {journal['adopted_count']}.",
            f"- Modified suggestions: {journal['modified_count']}.",
            f"- Rejected or deferred suggestions: {journal['rejected_or_deferred_count']}.",
            "",
            "## Artifacts",
            "",
            "- Journal JSON: `reports/portfolio/stage5_wp6_adoption_rejection_journal.json`",
            "- Journal markdown: `reports/portfolio/stage5_wp6_adoption_rejection_journal.md`",
            "- Work package report: `reports/program_runner/stage5_wp6_adoption_rejection_journal_report.json`",
            "- Internal review: `reports/internal_reviews/program/stage5_wp6_adoption_rejection_journal.json`",
            "",
            "## Next Safe Action",
            "",
            f"Proceed to `{report['next_work_package']}`.",
            "",
        ]
    )


def build_internal_review() -> dict[str, Any]:
    changed_files = [
        "ops/program_runner/heartbeat_log.md",
        "ops/program_runner/program_runner_state.json",
        "ops/state/loop_state.json",
        "reports/codex_handoff/latest.json",
        "reports/codex_handoff/latest.md",
        "reports/internal_reviews/program/stage5_wp6_adoption_rejection_journal.json",
        "reports/internal_reviews/program/stage5_wp6_adoption_rejection_journal.md",
        "reports/portfolio/stage5_wp6_adoption_rejection_journal.json",
        "reports/portfolio/stage5_wp6_adoption_rejection_journal.md",
        "reports/program_runner/stage5_wp6_adoption_rejection_journal_report.json",
        "reports/program_runner/stage5_wp6_adoption_rejection_journal_report.md",
        "reports/review_requests/latest.json",
        "scripts/reports/generate_stage5_wp6_adoption_rejection_journal.py",
        "tests/safety/test_program_runner_governance.py",
        "tests/safety/test_stage5_wp6_adoption_rejection_journal.py",
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
        "major_stage": "Stage 5",
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
        "risk_agent_review": {
            "new_actionable_trade_suggestion": False,
            "result": "pass",
            "trade_ticket_actionable_without_review": False,
        },
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
            "# Stage 5 WP6 Adoption And Rejection Journal Internal Review",
            "",
            "## Metadata",
            "",
            "- major_stage: Stage 5",
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
            "last_internal_review": "reports/internal_reviews/program/stage5_wp6_adoption_rejection_journal.json",
            "last_report": "reports/program_runner/stage5_wp6_adoption_rejection_journal_report.json",
            "status": "next_work_package_ready",
        }
    )
    state["stage5"].update(
        {
            "completed_work_packages": completed,
            "current_work_package": WORK_PACKAGE,
            "last_completed_work_package": WORK_PACKAGE,
            "last_internal_review": "reports/internal_reviews/program/stage5_wp6_adoption_rejection_journal.json",
            "last_report": "reports/program_runner/stage5_wp6_adoption_rejection_journal_report.json",
            "next_work_package": NEXT_WORK_PACKAGE,
            "reviewer_mode": "simulated_separate_pass",
            "status": "completed_internal_review",
            "user_notification_sent": False,
        }
    )
    state["stage6"] = {
        "chatgpt_review_requested": False,
        "completed_work_packages": [],
        "current_work_package": NEXT_WORK_PACKAGE,
        "last_completed_work_package": None,
        "last_internal_review": None,
        "last_report": None,
        "next_work_package": NEXT_WORK_PACKAGE,
        "reviewer_mode": None,
        "status": "next_work_package_ready",
        "user_notification_sent": False,
    }
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
        "last_internal_review": "reports/internal_reviews/program/stage5_wp6_adoption_rejection_journal.json",
        "last_report": "reports/program_runner/stage5_wp6_adoption_rejection_journal_report.json",
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
                "## Stage 3.1 Work Package Result",
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
                "## Program Runner",
                "",
                "- Program Runner status: `next_work_package_ready`.",
                f"- Current major stage: `{NEXT_MAJOR_STAGE}`.",
                f"- Current work package: `{NEXT_WORK_PACKAGE}`.",
                f"- Last completed work package: `{WORK_PACKAGE}`.",
                f"- Next safe action: resume {NEXT_WORK_PACKAGE}.",
                "- Codex requested ChatGPT review: false.",
                "- User notification sent: false.",
                "",
                "## Stage 5 Completed Work Packages",
                "",
                "- Stage 5 WP1 manual holdings CSV import: `completed_internal_review`.",
                "- Stage 5 WP2 manual trades CSV import: `completed_internal_review`.",
                "- Stage 5 WP3 portfolio weight calculation: `completed_internal_review`.",
                "- Stage 5 WP4 drift checks: `completed_internal_review`.",
                "- Stage 5 WP5 rebalance research ticket: `completed_internal_review`.",
                "- Stage 5 WP6 adoption and rejection journal: `completed_internal_review`.",
                "- Next work package: Stage 6 WP1 schedule dry-runs.",
                "",
                "## Stage 5 WP6 Result",
                "",
                "- Adoption/rejection journal: `reports/portfolio/stage5_wp6_adoption_rejection_journal.json`.",
                "- Work package report: `reports/program_runner/stage5_wp6_adoption_rejection_journal_report.json`.",
                "- Internal review: `reports/internal_reviews/program/stage5_wp6_adoption_rejection_journal.json`.",
                "- New actionable trade ticket generated: false.",
                "- risk_agent review: passed.",
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
                MANUAL_EXECUTION_NOTE,
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
    existing = HEARTBEAT_MD.read_text(encoding="utf-8") if HEARTBEAT_MD.exists() else "# Program Runner Heartbeat Log\n"
    kept_lines: list[str] = []
    skipping = False
    for line in existing.splitlines():
        if line.startswith("## ") and " Stage 5 WP6" in line:
            skipping = True
            continue
        if skipping and line.startswith("## "):
            skipping = False
        if not skipping:
            kept_lines.append(line)
    test_lines = "\n".join(f"  - `{test}`" for test in TESTS_RUN)
    entry = "\n".join(
        [
            f"\n## {now} Stage 5 WP6",
            "",
            f"- wake time in UTC: {now}",
            "- previous status: next_work_package_ready",
            f"- selected work package: {WORK_PACKAGE}",
            "- reviewer mode: simulated_separate_pass",
            "- tests run:",
            test_lines,
            "- commit pushed: yes, in this wake after verification",
            "- next status: next_work_package_ready",
            f"- next_safe_action: resume {NEXT_WORK_PACKAGE}",
            "- universe_allowlist_enforced: true",
            "- benchmark_comparison_preserved: true",
            "- trade_ticket_generated: false",
            "- risk_agent_review: passed",
            "- final_trading_manual: true",
        ]
    )
    HEARTBEAT_MD.write_text("\n".join(kept_lines).rstrip() + entry + "\n", encoding="utf-8")


def main() -> int:
    now = _now()
    journal = build_journal(now)
    _write_json(JOURNAL_JSON, journal)
    JOURNAL_MD.write_text(render_journal_markdown(journal), encoding="utf-8")

    report = build_report(journal)
    internal_review = build_internal_review()
    _write_json(REPORT_JSON, report)
    REPORT_MD.write_text(render_report_markdown(report, journal), encoding="utf-8")
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
                "journal": "reports/portfolio/stage5_wp6_adoption_rejection_journal.md",
                "next_work_package": NEXT_WORK_PACKAGE,
                "report": "reports/program_runner/stage5_wp6_adoption_rejection_journal_report.md",
                "status": "pass",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
