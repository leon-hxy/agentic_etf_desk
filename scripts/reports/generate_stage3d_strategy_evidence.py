#!/usr/bin/env python3
"""Generate Stage 3D strategy evidence from the Stage 3C validation report."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "strategy_evidence"
REPORT_JSON = REPORT_DIR / "stage3d_strategy_evidence_report.json"
REPORT_MD = REPORT_DIR / "stage3d_strategy_evidence_report.md"
STAGE3C_REPORT = ROOT / "reports" / "backtest_validation" / "stage3c_backtest_validation_report.json"
STAGE = "Stage 3D strategy evidence report"
FINAL_TRADING_NOTICE = "Final trading is manually decided by the user."
SAMPLE_LIMITATION = "Sample data only; not investment basis."

REQUIRED_STRATEGIES: dict[str, dict[str, str]] = {
    "benchmark_buy_hold": {
        "display_name": "Buy-and-Hold Benchmark",
        "role": "Baseline ETF benchmark evidence for comparison.",
    },
    "static_6040": {
        "display_name": "60/40 Static Allocation",
        "role": "Balanced ETF allocation evidence against the VTI benchmark.",
    },
    "gtaa_10m_sma": {
        "display_name": "GTAA 10-Month SMA",
        "role": "Global tactical asset allocation evidence using ETF trend filtering.",
    },
    "dual_momentum": {
        "display_name": "Dual Momentum",
        "role": "ETF rotation evidence using relative and absolute momentum signals.",
    },
}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def status_from_bool(value: bool) -> str:
    return "passed" if value else "failed"


def stable_generated_at(payload: dict[str, Any]) -> str:
    if not REPORT_JSON.exists():
        return datetime.now(timezone.utc).isoformat()
    try:
        previous = read_json(REPORT_JSON)
    except json.JSONDecodeError:
        return datetime.now(timezone.utc).isoformat()
    comparable = dict(payload)
    previous_comparable = dict(previous)
    comparable.pop("generated_at", None)
    previous_comparable.pop("generated_at", None)
    if comparable == previous_comparable and previous.get("generated_at"):
        return str(previous["generated_at"])
    return datetime.now(timezone.utc).isoformat()


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def build_risk_notes(strategy_id: str, validation: dict[str, Any]) -> list[str]:
    notes = [
        "Backtest evidence depends on a short sample panel and may not represent live market regimes.",
        "Benchmark comparison is against VTI only; broader benchmark selection should be reviewed before production use.",
    ]
    if float(validation.get("turnover", 0.0)) > 1.0:
        notes.append("Higher turnover increases sensitivity to transaction costs and implementation assumptions.")
    if strategy_id in {"gtaa_10m_sma", "dual_momentum"}:
        notes.append("Signal timing can lag rapid reversals and may underperform during choppy markets.")
    if strategy_id == "static_6040":
        notes.append("Static allocation may dilute equity upside and remains exposed to bond-equity correlation shifts.")
    if strategy_id == "benchmark_buy_hold":
        notes.append("Buy-and-Hold benchmark remains fully exposed to broad ETF market drawdowns.")
    return notes


def build_limitation_notes() -> list[str]:
    return [
        SAMPLE_LIMITATION,
        "Smoke evidence validates reporting and comparison plumbing, not investment merit.",
        "Formal use requires reviewed real data, source terms confirmation, and a separate major-stage review.",
    ]


def build_strategy_evidence(strategy_id: str, validation: dict[str, Any]) -> dict[str, Any]:
    metrics = {
        "strategy_cagr": float(validation.get("strategy_cagr", 0.0)),
        "benchmark_cagr": float(validation.get("benchmark_cagr", 0.0)),
        "excess_cagr_vs_benchmark": float(validation.get("excess_cagr_vs_benchmark", 0.0)),
        "strategy_max_drawdown": float(validation.get("strategy_max_drawdown", 0.0)),
        "benchmark_max_drawdown": float(validation.get("benchmark_max_drawdown", 0.0)),
        "max_drawdown_difference_vs_benchmark": float(
            validation.get("max_drawdown_difference_vs_benchmark", 0.0)
        ),
        "trade_count": int(validation.get("trade_count", 0)),
        "turnover": float(validation.get("turnover", 0.0)),
    }
    excess = metrics["excess_cagr_vs_benchmark"]
    drawdown_gap = metrics["max_drawdown_difference_vs_benchmark"]
    display_name = REQUIRED_STRATEGIES[strategy_id]["display_name"]
    return {
        "strategy_id": strategy_id,
        "display_name": display_name,
        "role": REQUIRED_STRATEGIES[strategy_id]["role"],
        "benchmark_symbol": str(validation.get("benchmark_symbol", "")),
        "has_required_metrics": bool(validation.get("has_required_metrics")),
        "has_benchmark_comparison": bool(validation.get("has_benchmark"))
        and "excess_cagr_vs_benchmark" in validation
        and "max_drawdown_difference_vs_benchmark" in validation,
        "metrics": metrics,
        "risk_notes": build_risk_notes(strategy_id, validation),
        "limitation_notes": build_limitation_notes(),
        "evidence_summary": (
            f"{display_name} produced {format_percent(metrics['strategy_cagr'])} sample CAGR versus "
            f"{format_percent(metrics['benchmark_cagr'])} for VTI, with "
            f"{format_percent(excess)} excess CAGR and {format_percent(drawdown_gap)} drawdown gap."
        ),
    }


def build_payload_from_stage3c(stage3c: dict[str, Any]) -> dict[str, Any]:
    validations = dict(stage3c.get("strategy_validations", {}))
    evidence = {
        strategy_id: build_strategy_evidence(strategy_id, validations[strategy_id])
        for strategy_id in REQUIRED_STRATEGIES
        if strategy_id in validations
    }
    data_boundary = dict(stage3c.get("data_boundary", {}))
    sample_data_only = bool(data_boundary.get("sample_data_only"))
    not_investment_basis = bool(data_boundary.get("not_investment_basis"))
    manual_note = str(stage3c.get("manual_execution_note", ""))

    required_present = list(evidence) == list(REQUIRED_STRATEGIES)
    benchmark_present = all(item["benchmark_symbol"] == "VTI" and item["has_benchmark_comparison"] for item in evidence.values())
    risk_limitations_documented = all(item["risk_notes"] and item["limitation_notes"] for item in evidence.values())
    manual_notice_present = FINAL_TRADING_NOTICE in manual_note or FINAL_TRADING_NOTICE in str(stage3c)
    stage3c_passed = stage3c.get("status") == "passed"
    sample_boundary_documented = sample_data_only and not_investment_basis and not bool(data_boundary.get("real_data_used"))
    status = "passed" if all(
        [
            stage3c_passed,
            required_present,
            benchmark_present,
            sample_boundary_documented,
            manual_notice_present,
            risk_limitations_documented,
        ]
    ) else "failed"

    payload: dict[str, Any] = {
        "stage": STAGE,
        "status": status,
        "report_json": rel(REPORT_JSON),
        "report_md": rel(REPORT_MD),
        "source_validation_report": rel(STAGE3C_REPORT),
        "strategies": list(REQUIRED_STRATEGIES),
        "strategy_evidence": evidence,
        "validation_checks": {
            "stage3c_validation_passed": status_from_bool(stage3c_passed),
            "required_strategies_present": status_from_bool(required_present),
            "benchmark_comparison_present": status_from_bool(benchmark_present),
            "sample_boundary_documented": status_from_bool(sample_boundary_documented),
            "manual_trading_notice_present": status_from_bool(manual_notice_present),
            "risk_and_limitations_documented": status_from_bool(risk_limitations_documented),
        },
        "data_boundary": {
            "source": str(data_boundary.get("source", "unknown")),
            "sample_data_only": sample_data_only,
            "real_data_used": bool(data_boundary.get("real_data_used")),
            "not_investment_basis": not_investment_basis,
            "price_panel_file": data_boundary.get("price_panel_file"),
            "panel_start_date": data_boundary.get("panel_start_date"),
            "panel_end_date": data_boundary.get("panel_end_date"),
            "symbols": data_boundary.get("symbols", []),
            "note": SAMPLE_LIMITATION,
        },
        "safety_flags": {
            "auto_trading_surface": False,
            "broker_surface": False,
            "broker_write_surface": False,
            "chatgpt_review_requested": False,
            "computer_use_executed": False,
            "dependencies_installed": False,
            "feishu_gateway_modified": False,
            "feishu_message_sent": False,
            "hermes_modified": False,
            "openclaw_modified": False,
            "real_config_modified": False,
            "secret_values_written": False,
            "secrets_touched": False,
            "sent_to_chatgpt": False,
            "services_restarted": False,
        },
        "manual_execution_note": FINAL_TRADING_NOTICE,
    }
    payload["generated_at"] = stable_generated_at(payload)
    return payload


def build_payload() -> dict[str, Any]:
    return build_payload_from_stage3c(read_json(STAGE3C_REPORT))


def write_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Stage 3D Strategy Evidence Report",
        "",
        f"- Stage: `{payload['stage']}`",
        f"- Status: `{payload['status']}`",
        f"- Source validation report: `{payload['source_validation_report']}`",
        "- Data boundary: Sample data only; not investment basis.",
        "",
        "## Validation Checks",
        "",
    ]
    for name, result in payload["validation_checks"].items():
        lines.append(f"- `{name}`: `{result}`")
    lines.extend(
        [
            "",
            "## Strategy Evidence",
            "",
            "| Strategy | Benchmark | Strategy CAGR | Benchmark CAGR | Excess CAGR | Drawdown Gap | Trades | Turnover |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in payload["strategy_evidence"].values():
        metrics = item["metrics"]
        lines.append(
            "| {name} | {benchmark} | {strategy_cagr} | {benchmark_cagr} | {excess} | "
            "{drawdown_gap} | {trades} | {turnover:.2f} |".format(
                name=item["display_name"],
                benchmark=item["benchmark_symbol"],
                strategy_cagr=format_percent(metrics["strategy_cagr"]),
                benchmark_cagr=format_percent(metrics["benchmark_cagr"]),
                excess=format_percent(metrics["excess_cagr_vs_benchmark"]),
                drawdown_gap=format_percent(metrics["max_drawdown_difference_vs_benchmark"]),
                trades=metrics["trade_count"],
                turnover=metrics["turnover"],
            )
        )
    lines.extend(["", "## Risk And Limitations", ""])
    for item in payload["strategy_evidence"].values():
        lines.append(f"### {item['display_name']}")
        lines.append("")
        lines.append(item["evidence_summary"])
        lines.append("")
        lines.append("Risk notes:")
        for note in item["risk_notes"]:
            lines.append(f"- {note}")
        lines.append("")
        lines.append("Limitation notes:")
        for note in item["limitation_notes"]:
            lines.append(f"- {note}")
        lines.append("")
    lines.extend(
        [
            "## Safety",
            "",
            "- No Computer Use.",
            "- No ChatGPT review requested.",
            "- No Feishu message sent.",
            "- No real Hermes, OpenClaw, or Feishu gateway modification.",
            "- No dependency installation.",
            "- No broker interface or automatic trading surface.",
            "",
            FINAL_TRADING_NOTICE,
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = build_payload()
    REPORT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(write_markdown(payload), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
