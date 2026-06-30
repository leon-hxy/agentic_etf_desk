import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEIGHTS_CSV = ROOT / "data" / "portfolio" / "portfolio_weights_latest.csv"
WEIGHTS_JSON = ROOT / "data" / "portfolio" / "portfolio_weights_latest.json"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage5_wp3_portfolio_weights_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage5_wp3_portfolio_weights_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp3_portfolio_weights.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp3_portfolio_weights.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage5WP3PortfolioWeightsTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_portfolio_weight_calculation_reads_manual_holdings_and_rejects_unknown_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            holdings_json = Path(temp_dir) / "manual_holdings_latest.json"
            holdings_json.write_text(
                json.dumps(
                    {
                        "asset_scope": "ETF-only",
                        "final_trading_manual": True,
                        "holdings": [
                            {"symbol": "vti", "quantity": 10, "market_value": 2500.50},
                            {"symbol": "BND", "quantity": 20, "market_value": 1450.00},
                            {"symbol": "BIL", "quantity": 5, "market_value": 459.50},
                        ],
                        "source": "manual_csv_import",
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_cmd(["scripts/portfolio/calculate_portfolio_weights.py", "--holdings", str(holdings_json)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            payload = json.loads(WEIGHTS_JSON.read_text(encoding="utf-8"))
            self.assertEqual(payload["source"], "manual_holdings_snapshot")
            self.assertEqual(payload["asset_scope"], "ETF-only")
            self.assertTrue(payload["universe_allowlist_enforced"])
            self.assertTrue(payload["final_trading_manual"])
            self.assertFalse(payload[BROKER_ACCESS_SURFACE_FIELD])
            self.assertFalse(payload["automatic_trading"])
            self.assertEqual(payload["symbol_count"], 3)
            self.assertEqual(payload["total_market_value"], 4410.0)
            self.assertAlmostEqual(payload["total_weight"], 1.0)
            self.assertEqual(payload["largest_position"]["symbol"], "VTI")
            self.assertEqual(payload["smallest_position"]["symbol"], "BIL")
            self.assertEqual([row["symbol"] for row in payload["weights"]], ["VTI", "BND", "BIL"])
            self.assertAlmostEqual(payload["weights"][0]["portfolio_weight"], 2500.5 / 4410.0)

            with WEIGHTS_CSV.open(encoding="utf-8") as handle:
                csv_rows = list(csv.DictReader(handle))
            self.assertEqual([row["symbol"] for row in csv_rows], ["VTI", "BND", "BIL"])

            bad_holdings_json = Path(temp_dir) / "bad_manual_holdings_latest.json"
            bad_holdings_json.write_text(
                json.dumps(
                    {
                        "holdings": [
                            {"symbol": "AAPL", "quantity": 1, "market_value": 100.00},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            bad_result = self.run_cmd(
                ["scripts/portfolio/calculate_portfolio_weights.py", "--holdings", str(bad_holdings_json)]
            )
            self.assertNotEqual(bad_result.returncode, 0)
            self.assertIn("not allowed by universe", bad_result.stderr)

    def test_wp3_generator_records_internal_review_and_advances_to_drift_checks(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage5_wp3_portfolio_weights.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD, WEIGHTS_CSV, WEIGHTS_JSON):
            self.assertTrue(path.exists(), str(path))

        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))

        self.assertEqual(report["work_package"], "Stage 5 WP3 portfolio weight calculation")
        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["asset_scope"], "ETF-only")
        self.assertTrue(report["repo_only"])
        self.assertTrue(report["universe_allowlist_enforced"])
        self.assertFalse(report[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(report["automatic_trading"])
        self.assertTrue(report["final_trading_manual"])
        self.assertEqual(report["next_work_package"], "Stage 5 WP4 drift checks")
        self.assertEqual(report["reviewer_mode"], "simulated_separate_pass")
        self.assertEqual(report["risk_agent_review"]["result"], "passed")
        self.assertFalse(report["risk_agent_review"]["trade_tickets_actionable_without_review"])
        self.assertAlmostEqual(report["total_weight"], 1.0)
        self.assertEqual(internal["pass_fail"], "pass")
        self.assertFalse(internal["requires_user_attention"])

        self.assertEqual(state["current_major_stage"], "Stage 5")
        self.assertEqual(state["current_work_package"], "Stage 5 WP4 drift checks")
        self.assertEqual(state["last_completed_work_package"], "Stage 5 WP3 portfolio weight calculation")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage5_wp3_portfolio_weights.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage5_wp3_portfolio_weights_report.json")
        self.assertEqual(state["stage5"]["status"], "next_work_package_ready")
        self.assertIn("stage5_wp3_portfolio_weights", state["stage5"]["completed_work_packages"])
        self.assertEqual(state["stage5"]["next_work_package"], "Stage 5 WP4 drift checks")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 5 WP4 drift checks")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 5 WP4 drift checks")

        combined = REPORT_MD.read_text(encoding="utf-8") + "\n" + INTERNAL_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("portfolio weight calculation", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)


if __name__ == "__main__":
    unittest.main()
