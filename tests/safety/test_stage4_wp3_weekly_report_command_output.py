import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "reports" / "generate_stage4_wp3_weekly_report_command_output.py"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp3_weekly_report_command_output_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp3_weekly_report_command_output_report.md"
WEEKLY_REPORT_JSON = ROOT / "reports" / "stage2b_weekly_report.json"
WEEKLY_REPORT_MD = ROOT / "reports" / "stage2b_weekly_report.md"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage4WP3WeeklyReportCommandOutputTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_weekly_report_command_output_is_repo_only_and_benchmarked(self) -> None:
        setup = self.run_cmd(
            [
                "scripts/backtest/run_backtest.py",
                "--strategies",
                "benchmark_buy_hold,static_6040,gtaa_10m_sma,dual_momentum",
            ]
        )
        self.assertEqual(setup.returncode, 0, msg=setup.stdout + setup.stderr)

        result = self.run_cmd(["scripts/reports/generate_stage4_wp3_weekly_report_command_output.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertTrue(REPORT_JSON.exists())
        self.assertTrue(REPORT_MD.exists())
        self.assertTrue(WEEKLY_REPORT_JSON.exists())
        self.assertTrue(WEEKLY_REPORT_MD.exists())

        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(report["work_package"], "Stage 4 WP3 weekly report command output")
        self.assertEqual(report["command_id"], "weekly_report")
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
        self.assertEqual(report["route_plan"]["repo_entrypoint"], "scripts/reports/generate_weekly_report.py")
        self.assertIn("最终交易由用户手动决定", report["feishu_reply_preview"])

        weekly = json.loads(WEEKLY_REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(weekly["report_type"], "weekly_report")
        self.assertEqual(weekly["local_report_path"], "reports/stage2b_weekly_report.md")
        self.assertTrue(weekly["benchmark_comparison_preserved"])
        self.assertTrue(weekly["strategies_reviewed"])
        for strategy_id in weekly["strategies_reviewed"]:
            self.assertIn(strategy_id, report["weekly_report"]["strategies_reviewed"])

        report_md = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", report_md)
        self.assertIn("scripts/reports/generate_weekly_report.py", report_md)
        self.assertIn("benchmark comparison", report_md)
        self.assertNotIn("/" + "Volumes" + "/", report_md)
        self.assertNotIn("/" + "Users" + "/", report_md)


if __name__ == "__main__":
    unittest.main()
