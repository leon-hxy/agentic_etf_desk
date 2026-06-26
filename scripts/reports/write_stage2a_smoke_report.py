#!/usr/bin/env python3
"""Write the Stage 2A smoke report from repo-only artifacts."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"
PANEL_METADATA = ROOT / "data" / "processed" / "price_panel_metadata.json"
UNIVERSE_FILE = ROOT / "configs" / "universe" / "etf_universe.yaml"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_report() -> dict[str, object]:
    if not UNIVERSE_FILE.exists():
        raise FileNotFoundError("Missing configs/universe/etf_universe.yaml")
    if not PANEL_METADATA.exists():
        raise FileNotFoundError("Missing data/processed/price_panel_metadata.json")

    universe = load_json(UNIVERSE_FILE)
    metadata = load_json(PANEL_METADATA)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    payload = {
        "stage": "2A",
        "scope": "repo-only",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "universe_file": "configs/universe/etf_universe.yaml",
        "allowed_count": len([entry for entry in universe["universe"] if entry["is_allowed"]]),
        "price_panel_file": metadata["price_panel_file"],
        "symbols": metadata["symbols"],
        "manual_trading_disclaimer": "Final trading is manually decided by the user.",
    }

    md = "\n".join(
        [
            "# Stage 2A Smoke Report",
            "",
            "Scope: repo-only ETF universe and sample data pipeline.",
            "",
            f"Allowed ETF count: {payload['allowed_count']}",
            f"Price panel: `{payload['price_panel_file']}`",
            f"Symbols: {', '.join(payload['symbols'])}",
            "",
            "This is research advice only, not automatic order placement.",
            "Final trading is manually decided by the user.",
            "",
        ]
    )

    md_path = REPORTS_DIR / "stage2a_smoke_report.md"
    json_path = REPORTS_DIR / "stage2a_smoke_report.json"
    md_path.write_text(md, encoding="utf-8")
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    payload = write_report()
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

