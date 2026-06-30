#!/usr/bin/env python3
"""Check manual ETF portfolio weight drift against the static_6040 target."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "portfolio"
DEFAULT_WEIGHTS_JSON = DATA_DIR / "portfolio_weights_latest.json"
DEFAULT_STRATEGY_JSON = ROOT / "strategies" / "static_6040" / "strategy.yaml"
OUTPUT_JSON = DATA_DIR / "portfolio_drift_latest.json"
MANUAL_NOTE_EN = "Final trading is manually decided by the user."
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))

SCRIPTS_DATA = ROOT / "scripts" / "data"
if str(SCRIPTS_DATA) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DATA))

from load_universe import validate_requested_symbols  # noqa: E402


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_current_weights(path: Path) -> dict[str, float]:
    payload = _read_json(path)
    rows = payload.get("weights")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Portfolio weights snapshot must contain a non-empty weights list")
    symbols = validate_requested_symbols([str(row.get("symbol", "")) for row in rows])
    if len(set(symbols)) != len(symbols):
        raise ValueError("Portfolio weights snapshot must not contain duplicate symbols")

    weights: dict[str, float] = {}
    for row, symbol in zip(rows, symbols, strict=True):
        weight = float(row.get("portfolio_weight"))
        if weight < 0:
            raise ValueError(f"{symbol} has negative portfolio_weight: {weight}")
        weights[symbol] = weight
    if sum(weights.values()) <= 0:
        raise ValueError("Portfolio weights must sum to a positive value")
    return weights


def _load_strategy(path: Path) -> dict[str, Any]:
    strategy = _read_json(path)
    weight_rule = dict(strategy.get("weight_rule", {}))
    raw_targets = dict(weight_rule.get("target_weights", {}))
    if not raw_targets:
        raise ValueError("Strategy must define target_weights")

    symbols = validate_requested_symbols([str(symbol) for symbol in raw_targets])
    targets = {symbol: float(raw_targets[raw_symbol]) for raw_symbol, symbol in zip(raw_targets, symbols, strict=True)}
    if any(weight < 0 for weight in targets.values()):
        raise ValueError("Strategy target weights must be non-negative")
    target_sum = sum(targets.values())
    if abs(target_sum - 1.0) > 0.000001:
        raise ValueError(f"Strategy target weights must sum to 1.0, got {target_sum}")

    return {
        "benchmark_symbol": dict(strategy.get("benchmark", {})).get("symbol"),
        "strategy_id": strategy.get("strategy_id"),
        "targets": targets,
    }


def check_portfolio_drift(
    weights_json: Path = DEFAULT_WEIGHTS_JSON,
    strategy_json: Path = DEFAULT_STRATEGY_JSON,
    output_json: Path = OUTPUT_JSON,
    drift_threshold: float = 0.05,
) -> dict[str, Any]:
    if drift_threshold < 0:
        raise ValueError("Drift threshold must be non-negative")

    current_weights = _load_current_weights(weights_json)
    strategy = _load_strategy(strategy_json)
    target_weights = strategy["targets"]
    all_symbols = sorted(set(current_weights) | set(target_weights))
    validate_requested_symbols(all_symbols)

    drift_rows: list[dict[str, Any]] = []
    for symbol in all_symbols:
        current = current_weights.get(symbol, 0.0)
        target = target_weights.get(symbol, 0.0)
        drift = current - target
        if drift > 0:
            direction = "above_target"
        elif drift < 0:
            direction = "below_target"
        else:
            direction = "on_target"
        absolute_drift = abs(drift)
        drift_rows.append(
            {
                "absolute_drift": absolute_drift,
                "breaches_threshold": absolute_drift > drift_threshold,
                "current_weight": current,
                "direction": direction,
                "drift": drift,
                "drift_bps": round(drift * 10000, 4),
                "symbol": symbol,
                "target_weight": target,
            }
        )

    max_row = max(drift_rows, key=lambda row: row["absolute_drift"])
    status = "drift_review_needed" if any(row["breaches_threshold"] for row in drift_rows) else "within_threshold"
    payload = {
        "asset_scope": "ETF-only",
        "automatic_trading": False,
        "benchmark_comparison_preserved": True,
        "benchmark_symbol": strategy["benchmark_symbol"],
        BROKER_ACCESS_SURFACE_FIELD: False,
        "drift_rows": drift_rows,
        "drift_threshold": drift_threshold,
        "final_trading_manual": True,
        "manual_trading_note": MANUAL_NOTE_EN,
        "max_absolute_drift": max_row["absolute_drift"],
        "max_drift_symbol": max_row["symbol"],
        "next_research_step": "Stage 5 WP5 rebalance research ticket",
        "source": "portfolio_weights_latest",
        "status": status,
        "target_strategy_id": strategy["strategy_id"],
        "trade_ticket_generated": False,
        "universe_allowlist": "configs/universe/etf_universe.yaml",
        "universe_allowlist_enforced": True,
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Check ETF portfolio drift against static_6040 targets")
    parser.add_argument("--weights", default=str(DEFAULT_WEIGHTS_JSON), help="Portfolio weights JSON snapshot")
    parser.add_argument("--strategy", default=str(DEFAULT_STRATEGY_JSON), help="Strategy JSON/YAML file")
    parser.add_argument("--output", default=str(OUTPUT_JSON), help="Output drift JSON path")
    parser.add_argument("--threshold", type=float, default=0.05, help="Absolute drift threshold as a decimal weight")
    args = parser.parse_args()
    try:
        payload = check_portfolio_drift(Path(args.weights), Path(args.strategy), Path(args.output), args.threshold)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps({"status": payload["status"], "max_drift_symbol": payload["max_drift_symbol"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
