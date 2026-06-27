import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BACKTEST_FILES = [
    "scripts/backtest/run_backtest.py",
    "scripts/backtest/metrics.py",
    "scripts/backtest/portfolio.py",
    "scripts/backtest/strategies.py",
    "scripts/backtest/report_writer.py",
]
DANGEROUS_TERMS = [
    "_".join(("place", "order")),
    "_".join(("submit", "order")),
    "_".join(("buy", "market")),
    "_".join(("sell", "market")),
    ".".join(("ib", "place" + "Order")),
    ".".join(("alpaca", "_".join(("submit", "order")))),
]


class BacktestSafetyTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_backtest_engine_files_exist_and_are_repo_only(self) -> None:
        for rel in BACKTEST_FILES:
            path = ROOT / rel
            self.assertTrue(path.exists(), rel)
            text = path.read_text(encoding="utf-8")
            self.assertIn("configs/universe/etf_universe.yaml", text, rel)
            self.assertIn("data/processed/price_panel.csv", text, rel)
            for term in DANGEROUS_TERMS:
                self.assertNotIn(term, text, rel)

    def test_backtest_rejects_symbols_outside_universe(self) -> None:
        result = self.run_cmd(
            [
                "scripts/backtest/run_backtest.py",
                "--strategies",
                "benchmark_buy_hold",
                "--symbols",
                "AAPL",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not allowed by universe", result.stderr)

    def test_backtest_report_contains_manual_disclaimer_and_metrics(self) -> None:
        result = self.run_cmd(
            [
                "scripts/backtest/run_backtest.py",
                "--strategies",
                "benchmark_buy_hold,static_6040",
            ]
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        report = json.loads((ROOT / "reports" / "stage2b_backtest_report.json").read_text())
        self.assertEqual(report["stage"], "Stage 2B")
        self.assertIn("最终交易由用户手动决定", report["manual_execution_note"])
        for strategy in ("benchmark_buy_hold", "static_6040"):
            metrics = report["strategies"][strategy]["metrics"]
            for key in (
                "cagr",
                "sharpe",
                "sortino",
                "max_drawdown",
                "calmar",
                "annualized_volatility",
                "win_rate",
                "turnover",
                "trade_count",
                "worst_month",
                "worst_year",
                "longest_drawdown_recovery_days",
            ):
                self.assertIn(key, metrics, key)


if __name__ == "__main__":
    unittest.main()
