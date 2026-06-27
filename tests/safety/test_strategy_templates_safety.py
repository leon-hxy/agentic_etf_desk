import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STRATEGY_IDS = [
    "benchmark_buy_hold",
    "static_6040",
    "equal_weight_etf",
    "gtaa_10m_sma",
    "dual_momentum",
    "time_series_momentum_vol_target",
    "inverse_volatility_allocation",
    "etf_mean_reversion_sandbox",
]
REQUIRED_FIELDS = {
    "strategy_id",
    "description",
    "universe_source",
    "rebalance_frequency",
    "signal_frequency",
    "weight_rule",
    "risk_limits",
    "benchmark",
    "transaction_cost_assumption",
    "data_requirements",
    "manual_execution_note",
}
FORBIDDEN_ASSETS = [
    "individual stock",
    "option",
    "future",
    "crypto",
    "leveraged etf",
    "inverse etf",
]


def allowed_symbols() -> set[str]:
    payload = json.loads((ROOT / "configs" / "universe" / "etf_universe.yaml").read_text())
    return {entry["symbol"] for entry in payload["universe"] if entry["is_allowed"]}


class StrategyTemplatesSafetyTest(unittest.TestCase):
    def test_all_required_strategy_templates_exist(self) -> None:
        for strategy_id in STRATEGY_IDS:
            strategy_dir = ROOT / "strategies" / strategy_id
            self.assertTrue((strategy_dir / "README.md").exists(), strategy_id)
            self.assertTrue((strategy_dir / "strategy.yaml").exists(), strategy_id)

    def test_strategy_yaml_files_are_complete_and_universe_bound(self) -> None:
        allowed = allowed_symbols()
        for strategy_id in STRATEGY_IDS:
            payload = json.loads(
                (ROOT / "strategies" / strategy_id / "strategy.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(payload["strategy_id"], strategy_id)
            self.assertTrue(REQUIRED_FIELDS.issubset(payload), strategy_id)
            self.assertEqual(payload["universe_source"], "configs/universe/etf_universe.yaml")
            self.assertIn("benchmark", payload)
            self.assertIn("Final trading", payload["manual_execution_note"])

            configured_symbols = set(payload.get("allowed_symbols", []))
            self.assertTrue(configured_symbols, strategy_id)
            self.assertTrue(configured_symbols.issubset(allowed), strategy_id)

    def test_strategy_text_keeps_manual_trading_and_sandbox_notes(self) -> None:
        for strategy_id in STRATEGY_IDS:
            combined = "\n".join(
                [
                    (ROOT / "strategies" / strategy_id / "README.md").read_text(encoding="utf-8"),
                    (ROOT / "strategies" / strategy_id / "strategy.yaml").read_text(encoding="utf-8"),
                ]
            )
            self.assertIn("最终交易由用户手动决定", combined, strategy_id)
            self.assertIn("not automatic order placement", combined, strategy_id)
            for term in FORBIDDEN_ASSETS:
                self.assertNotIn(term, combined.lower(), strategy_id)

        sandbox = (ROOT / "strategies" / "etf_mean_reversion_sandbox" / "README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("sandbox", sandbox.lower())
        self.assertIn("不建议实盘", sandbox)


if __name__ == "__main__":
    unittest.main()
