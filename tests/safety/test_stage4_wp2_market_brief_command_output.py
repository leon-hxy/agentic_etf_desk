import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "reports" / "generate_stage4_wp2_market_brief_command_output.py"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp2_market_brief_command_output_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp2_market_brief_command_output_report.md"
MARKET_BRIEF_JSON = ROOT / "reports" / "stage2b_market_brief.json"
MARKET_BRIEF_MD = ROOT / "reports" / "stage2b_market_brief.md"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage4WP2MarketBriefCommandOutputTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_market_brief_command_output_is_repo_only_and_benchmarked(self) -> None:
        setup = self.run_cmd(
            [
                "scripts/backtest/run_backtest.py",
                "--strategies",
                "benchmark_buy_hold,static_6040,gtaa_10m_sma,dual_momentum",
            ]
        )
        self.assertEqual(setup.returncode, 0, msg=setup.stdout + setup.stderr)

        result = self.run_cmd(["scripts/reports/generate_stage4_wp2_market_brief_command_output.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertTrue(REPORT_JSON.exists())
        self.assertTrue(REPORT_MD.exists())
        self.assertTrue(MARKET_BRIEF_JSON.exists())
        self.assertTrue(MARKET_BRIEF_MD.exists())

        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(report["work_package"], "Stage 4 WP2 market brief command output")
        self.assertEqual(report["command_id"], "market_brief")
        self.assertEqual(report["asset_scope"], "ETF-only")
        self.assertTrue(report["repo_only"])
        self.assertFalse(report["executes_live_feishu"])
        self.assertFalse(report["modifies_real_runtime_config"])
        self.assertFalse(report["automatic_trading"])
        self.assertFalse(report[BROKER_ACCESS_SURFACE_FIELD])
        self.assertTrue(report["final_trading_manual"])
        self.assertEqual(report["reviewer_mode"], "simulated_separate_pass")
        self.assertTrue(report["risk_agent_review"]["passed"])
        self.assertEqual(report["route_plan"]["status"], "routed")
        self.assertEqual(report["route_plan"]["repo_entrypoint"], "scripts/reports/generate_market_brief.py")
        self.assertIn("最终交易由用户手动决定", report["feishu_reply_preview"])

        brief = json.loads(MARKET_BRIEF_JSON.read_text(encoding="utf-8"))
        self.assertEqual(brief["report_type"], "market_brief")
        self.assertEqual(brief["local_report_path"], "reports/stage2b_market_brief.md")
        self.assertTrue(brief["benchmark_comparison_preserved"])
        self.assertTrue(brief["rows"])
        for row in brief["rows"]:
            self.assertIn("benchmark_symbol", row)
            self.assertIn("benchmark_cagr", row)
            self.assertIn("cagr_vs_benchmark", row)

        report_md = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", report_md)
        self.assertIn("scripts/reports/generate_market_brief.py", report_md)
        self.assertIn("benchmark comparison", report_md)
        self.assertNotIn("/" + "Volumes" + "/", report_md)
        self.assertNotIn("/" + "Users" + "/", report_md)


if __name__ == "__main__":
    unittest.main()
