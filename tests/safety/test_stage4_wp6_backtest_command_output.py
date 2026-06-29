import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "reports" / "generate_stage4_wp6_backtest_command_output.py"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp6_backtest_command_output_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp6_backtest_command_output_report.md"
BACKTEST_JSON = ROOT / "reports" / "stage2b_backtest_report.json"
BACKTEST_MD = ROOT / "reports" / "stage2b_backtest_report.md"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage4WP6BacktestCommandOutputTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_backtest_command_output_is_repo_only_reviewed_benchmarked_and_manual(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage4_wp6_backtest_command_output.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertTrue(REPORT_JSON.exists())
        self.assertTrue(REPORT_MD.exists())
        self.assertTrue(BACKTEST_JSON.exists())
        self.assertTrue(BACKTEST_MD.exists())

        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(report["work_package"], "Stage 4 WP6 backtest command output")
        self.assertEqual(report["command_id"], "gtaa_backtest")
        self.assertEqual(report["asset_scope"], "ETF-only")
        self.assertTrue(report["repo_only"])
        self.assertFalse(report["executes_live_feishu"])
        self.assertFalse(report["modifies_real_runtime_config"])
        self.assertFalse(report["automatic_trading"])
        self.assertFalse(report[BROKER_ACCESS_SURFACE_FIELD])
        self.assertTrue(report["final_trading_manual"])
        self.assertEqual(report["reviewer_mode"], "simulated_separate_pass")
        self.assertEqual(report["route_plan"]["status"], "routed")
        self.assertFalse(report["route_plan"]["trade_ticket"])
        self.assertEqual(report["route_plan"]["repo_entrypoint"], "scripts/backtest/run_backtest.py")
        self.assertEqual(report["route_plan"]["repo_args"], ["--strategies", "gtaa_10m_sma"])
        self.assertIn("最终交易由用户手动决定", report["feishu_reply_preview"])

        backtest = report["backtest"]
        self.assertEqual(backtest["data_source"], "data/processed/price_panel.csv")
        self.assertEqual(backtest["universe_source"], "configs/universe/etf_universe.yaml")
        self.assertEqual(backtest["strategies"], ["gtaa_10m_sma"])
        self.assertTrue(backtest["benchmark_comparison_preserved"])
        self.assertEqual(backtest["benchmark_symbol"], "VTI")
        self.assertTrue(backtest["metrics"]["trade_count"] >= 0)
        self.assertIn("cagr", backtest["metrics"])
        self.assertIn("max_drawdown", backtest["metrics"])
        self.assertTrue(report["validation_checks"]["backtest_report_generated"])
        self.assertTrue(report["validation_checks"]["benchmark_comparison_present"])
        self.assertTrue(report["validation_checks"]["route_is_repo_only"])
        self.assertTrue(report["validation_checks"]["manual_trading_disclaimer_present"])

        generated_backtest = json.loads(BACKTEST_JSON.read_text(encoding="utf-8"))
        self.assertEqual(sorted(generated_backtest["strategies"]), ["gtaa_10m_sma"])
        self.assertIn("最终交易由用户手动决定", generated_backtest["manual_execution_note"])

        report_md = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", report_md)
        self.assertIn("scripts/backtest/run_backtest.py", report_md)
        self.assertIn("gtaa_10m_sma", report_md)
        self.assertIn("benchmark comparison", report_md)
        self.assertIn("VTI", report_md)
        self.assertNotIn("/" + "Volumes" + "/", report_md)
        self.assertNotIn("/" + "Users" + "/", report_md)


if __name__ == "__main__":
    unittest.main()
