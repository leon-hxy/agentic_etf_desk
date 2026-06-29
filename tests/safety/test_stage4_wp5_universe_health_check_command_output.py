import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "reports" / "generate_stage4_wp5_universe_health_check_command_output.py"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage4_wp5_universe_health_check_command_output_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage4_wp5_universe_health_check_command_output_report.md"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage4WP5UniverseHealthCheckCommandOutputTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_universe_health_check_command_output_is_repo_only_reviewed_and_manual(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage4_wp5_universe_health_check_command_output.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertTrue(REPORT_JSON.exists())
        self.assertTrue(REPORT_MD.exists())

        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(report["work_package"], "Stage 4 WP5 ETF universe health check command output")
        self.assertEqual(report["command_id"], "universe_health_check")
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
        self.assertEqual(report["route_plan"]["repo_entrypoint"], "scripts/data/validate_universe.py")
        self.assertIn("最终交易由用户手动决定", report["feishu_reply_preview"])

        health = report["universe_health_check"]
        self.assertEqual(health["status"], "pass")
        self.assertEqual(health["universe_file"], "configs/universe/etf_universe.yaml")
        self.assertGreater(health["allowed_count"], 0)
        self.assertEqual(health["disallowed_leveraged_or_inverse"], 0)
        self.assertEqual(health["errors"], [])
        self.assertTrue(report["validation_checks"]["universe_health_check_passed"])
        self.assertTrue(report["validation_checks"]["route_is_repo_only"])
        self.assertTrue(report["validation_checks"]["manual_trading_disclaimer_present"])

        report_md = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", report_md)
        self.assertIn("scripts/data/validate_universe.py", report_md)
        self.assertIn("configs/universe/etf_universe.yaml", report_md)
        self.assertIn("ETF-only", report_md)
        self.assertNotIn("/" + "Volumes" + "/", report_md)
        self.assertNotIn("/" + "Users" + "/", report_md)


if __name__ == "__main__":
    unittest.main()
