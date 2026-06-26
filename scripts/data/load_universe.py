#!/usr/bin/env python3
"""Load the repo-only ETF universe allowlist."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
UNIVERSE_PATH = ROOT / "configs" / "universe" / "etf_universe.yaml"
REQUIRED_FIELDS = {
    "symbol",
    "name",
    "asset_class",
    "region",
    "currency",
    "exchange",
    "category",
    "is_leveraged",
    "is_inverse",
    "is_allowed",
    "defensive_asset",
    "notes",
}


def load_universe(path: Path = UNIVERSE_PATH) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Universe file is not JSON-compatible YAML and PyYAML is not installed"
            ) from exc
        payload = yaml.safe_load(text)

    if not isinstance(payload, dict):
        raise ValueError("Universe payload must be a mapping")
    entries = payload.get("universe")
    if not isinstance(entries, list):
        raise ValueError("Universe payload must contain a universe list")
    return payload


def universe_entries(path: Path = UNIVERSE_PATH) -> list[dict[str, Any]]:
    return list(load_universe(path)["universe"])


def allowed_entries(path: Path = UNIVERSE_PATH) -> list[dict[str, Any]]:
    return [entry for entry in universe_entries(path) if bool(entry.get("is_allowed"))]


def allowed_symbols(path: Path = UNIVERSE_PATH) -> list[str]:
    return [str(entry["symbol"]).upper() for entry in allowed_entries(path)]


def validate_requested_symbols(requested: list[str], path: Path = UNIVERSE_PATH) -> list[str]:
    allowed = set(allowed_symbols(path))
    normalized = [symbol.strip().upper() for symbol in requested if symbol.strip()]
    unknown = [symbol for symbol in normalized if symbol not in allowed]
    if unknown:
        raise ValueError(f"Symbol(s) not allowed by universe: {', '.join(unknown)}")
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Print ETF universe summary")
    parser.add_argument("--path", default=str(UNIVERSE_PATH))
    args = parser.parse_args()
    path = Path(args.path)
    entries = universe_entries(path)
    payload = {
        "universe_file": str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
        "total_count": len(entries),
        "allowed_count": len([entry for entry in entries if entry.get("is_allowed")]),
        "allowed_symbols": allowed_symbols(path),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)

