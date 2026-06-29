import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DRIFT_JSON = ROOT / "data" / "portfolio" / "portfolio_drift_latest.json"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage5_wp4_drift_checks_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage5_wp4_drift_checks_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp4_drift_checks.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp4_drift_checks.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage5WP4DriftChecksTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_drift_checker_compares_latest_weights_to_static_6040_targets(self) -> None:
        result = self.run_cmd(["scripts/portfolio/check_portfolio_drift.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertTrue(DRIFT_JSON.exists())

        payload = json.loads(DRIFT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["asset_scope"], "ETF-only")
        self.assertEqual(payload["source"], "portfolio_weights_latest")
        self.assertEqual(payload["target_strategy_id"], "static_6040")
        self.assertEqual(payload["benchmark_symbol"], "VTI")
        self.assertTrue(payload["benchmark_comparison_preserved"])
        self.assertTrue(payload["universe_allowlist_enforced"])
        self.assertTrue(payload["final_trading_manual"])
        self.assertFalse(payload[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(payload["automatic_trading"])
        self.assertFalse(payload["trade_ticket_generated"])
        self.assertEqual(payload["status"], "within_threshold")
        self.assertEqual(payload["drift_threshold"], 0.05)
        self.assertEqual(payload["max_drift_symbol"], "VTI")
        self.assertAlmostEqual(payload["max_absolute_drift"], abs(0.5670068027210884 - 0.6))

        rows = {row["symbol"]: row for row in payload["drift_rows"]}
        self.assertEqual(set(rows), {"VTI", "BND", "BIL"})
        self.assertAlmostEqual(rows["VTI"]["current_weight"], 0.5670068027210884)
        self.assertAlmostEqual(rows["VTI"]["target_weight"], 0.6)
        self.assertEqual(rows["VTI"]["direction"], "below_target")
        self.assertFalse(rows["VTI"]["breaches_threshold"])
        self.assertEqual(rows["BND"]["direction"], "above_target")
        self.assertEqual(rows["BIL"]["direction"], "above_target")

    def test_drift_checker_flags_threshold_breaches_without_generating_trade_ticket(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            weights_json = Path(temp_dir) / "weights.json"
            output_json = Path(temp_dir) / "drift.json"
            weights_json.write_text(
                json.dumps(
                    {
                        "asset_scope": "ETF-only",
                        "final_trading_manual": True,
                        "weights": [
                            {"symbol": "VTI", "portfolio_weight": 0.8, "market_value": 800.0, "quantity": 8},
                            {"symbol": "BND", "portfolio_weight": 0.1, "market_value": 100.0, "quantity": 1},
                            {"symbol": "BIL", "portfolio_weight": 0.1, "market_value": 100.0, "quantity": 1},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_cmd(
                [
                    "scripts/portfolio/check_portfolio_drift.py",
                    "--weights",
                    str(weights_json),
                    "--output",
                    str(output_json),
                    "--threshold",
                    "0.05",
                ]
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "drift_review_needed")
            self.assertEqual(payload["max_drift_symbol"], "VTI")
            self.assertFalse(payload["trade_ticket_generated"])
            self.assertEqual(payload["next_research_step"], "Stage 5 WP5 rebalance research ticket")

    def test_wp4_generator_records_internal_review_and_advances_to_rebalance_research_ticket(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage5_wp4_drift_checks.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD, DRIFT_JSON):
            self.assertTrue(path.exists(), str(path))

        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))

        self.assertEqual(report["work_package"], "Stage 5 WP4 drift checks")
        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["asset_scope"], "ETF-only")
        self.assertTrue(report["repo_only"])
        self.assertTrue(report["universe_allowlist_enforced"])
        self.assertFalse(report[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(report["automatic_trading"])
        self.assertFalse(report["trade_ticket_generated"])
        self.assertTrue(report["final_trading_manual"])
        self.assertTrue(report["benchmark_comparison_preserved"])
        self.assertEqual(report["benchmark_symbol"], "VTI")
        self.assertEqual(report["target_strategy_id"], "static_6040")
        self.assertEqual(report["next_work_package"], "Stage 5 WP5 rebalance research ticket")
        self.assertEqual(report["reviewer_mode"], "simulated_separate_pass")
        self.assertEqual(report["risk_agent_review"]["result"], "passed")
        self.assertFalse(report["risk_agent_review"]["trade_tickets_actionable_without_review"])
        self.assertEqual(internal["pass_fail"], "pass")
        self.assertFalse(internal["requires_user_attention"])

        self.assertEqual(state["current_major_stage"], "Stage 5")
        self.assertEqual(state["current_work_package"], "Stage 5 WP5 rebalance research ticket")
        self.assertEqual(state["last_completed_work_package"], "Stage 5 WP4 drift checks")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage5_wp4_drift_checks.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage5_wp4_drift_checks_report.json")
        self.assertEqual(state["stage5"]["status"], "next_work_package_ready")
        self.assertIn("stage5_wp4_drift_checks", state["stage5"]["completed_work_packages"])
        self.assertEqual(state["stage5"]["next_work_package"], "Stage 5 WP5 rebalance research ticket")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 5 WP5 rebalance research ticket")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 5 WP5 rebalance research ticket")

        combined = REPORT_MD.read_text(encoding="utf-8") + "\n" + INTERNAL_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("drift checks", combined)
        self.assertIn("benchmark comparison", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)


if __name__ == "__main__":
    unittest.main()
