import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SMOKE_STRATEGIES = [
    "benchmark_buy_hold",
    "static_6040",
    "gtaa_10m_sma",
    "dual_momentum",
]


class BacktestSmokeTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_stage2b_smoke_backtests_generate_reports(self) -> None:
        result = self.run_cmd(
            [
                "scripts/backtest/run_backtest.py",
                "--strategies",
                ",".join(SMOKE_STRATEGIES),
                "--frequency",
                "daily",
                "--price-field",
                "adjusted_close",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for rel in (
            "reports/stage2b_backtest_report.md",
            "reports/stage2b_backtest_report.json",
            "reports/stage2b_backtest_report.html",
        ):
            self.assertTrue((ROOT / rel).exists(), rel)

        payload = json.loads((ROOT / "reports" / "stage2b_backtest_report.json").read_text())
        self.assertEqual(set(payload["strategies"]), set(SMOKE_STRATEGIES))
        self.assertEqual(payload["data_source"], "data/processed/price_panel.csv")
        self.assertIn("最终交易由用户手动决定", payload["manual_execution_note"])

        for strategy_id in SMOKE_STRATEGIES:
            result_path = ROOT / "backtests" / "stage2b_smoke" / strategy_id / "results.json"
            curve_path = ROOT / "backtests" / "stage2b_smoke" / strategy_id / "equity_curve.csv"
            risk_path = ROOT / "backtests" / "stage2b_smoke" / strategy_id / "risk_summary.json"
            self.assertTrue(result_path.exists(), strategy_id)
            self.assertTrue(curve_path.exists(), strategy_id)
            self.assertTrue(risk_path.exists(), strategy_id)


if __name__ == "__main__":
    unittest.main()
