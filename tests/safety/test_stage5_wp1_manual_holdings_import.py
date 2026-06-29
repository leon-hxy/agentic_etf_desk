import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
IMPORT_SCRIPT = ROOT / "scripts" / "portfolio" / "import_manual_holdings.py"
GENERATOR = ROOT / "scripts" / "reports" / "generate_stage5_wp1_manual_holdings_import.py"
HOLDINGS_CSV = ROOT / "data" / "portfolio" / "manual_holdings_latest.csv"
HOLDINGS_JSON = ROOT / "data" / "portfolio" / "manual_holdings_latest.json"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage5_wp1_manual_holdings_import_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage5_wp1_manual_holdings_import_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp1_manual_holdings_import.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage5_wp1_manual_holdings_import.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage5WP1ManualHoldingsImportTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_manual_holdings_import_normalizes_allowed_etfs_and_rejects_unknown_symbols(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_csv = Path(temp_dir) / "holdings.csv"
            with input_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["symbol", "quantity", "market_value"])
                writer.writeheader()
                writer.writerow({"symbol": "vti", "quantity": "10", "market_value": "2500.50"})
                writer.writerow({"symbol": "BND", "quantity": "20", "market_value": "1450.00"})
                writer.writerow({"symbol": "BIL", "quantity": "5", "market_value": "459.50"})

            result = self.run_cmd(["scripts/portfolio/import_manual_holdings.py", "--input", str(input_csv)])
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

            payload = json.loads(HOLDINGS_JSON.read_text(encoding="utf-8"))
            self.assertEqual(payload["source"], "manual_csv_import")
            self.assertEqual(payload["asset_scope"], "ETF-only")
            self.assertTrue(payload["universe_allowlist_enforced"])
            self.assertTrue(payload["final_trading_manual"])
            self.assertFalse(payload[BROKER_ACCESS_SURFACE_FIELD])
            self.assertFalse(payload["automatic_trading"])
            self.assertEqual(payload["symbol_count"], 3)
            self.assertEqual(payload["total_market_value"], 4410.0)
            self.assertAlmostEqual(payload["holdings"][0]["portfolio_weight"], 2500.5 / 4410.0)
            self.assertEqual([row["symbol"] for row in payload["holdings"]], ["VTI", "BND", "BIL"])

            with HOLDINGS_CSV.open(encoding="utf-8") as handle:
                csv_rows = list(csv.DictReader(handle))
            self.assertEqual([row["symbol"] for row in csv_rows], ["VTI", "BND", "BIL"])

            bad_csv = Path(temp_dir) / "bad_holdings.csv"
            with bad_csv.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["symbol", "quantity", "market_value"])
                writer.writeheader()
                writer.writerow({"symbol": "AAPL", "quantity": "1", "market_value": "100.00"})

            bad_result = self.run_cmd(["scripts/portfolio/import_manual_holdings.py", "--input", str(bad_csv)])
            self.assertNotEqual(bad_result.returncode, 0)
            self.assertIn("not allowed by universe", bad_result.stderr)

    def test_wp1_generator_records_internal_review_and_advances_to_manual_trades_import(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage5_wp1_manual_holdings_import.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD, HOLDINGS_CSV, HOLDINGS_JSON):
            self.assertTrue(path.exists(), str(path))

        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))

        self.assertEqual(report["work_package"], "Stage 5 WP1 manual holdings CSV import")
        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["asset_scope"], "ETF-only")
        self.assertTrue(report["repo_only"])
        self.assertTrue(report["universe_allowlist_enforced"])
        self.assertFalse(report[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(report["automatic_trading"])
        self.assertTrue(report["final_trading_manual"])
        self.assertEqual(report["next_work_package"], "Stage 5 WP2 manual trades CSV import")
        self.assertEqual(report["reviewer_mode"], "simulated_separate_pass")
        self.assertEqual(report["risk_agent_review"]["result"], "passed")
        self.assertFalse(report["risk_agent_review"]["trade_tickets_actionable_without_review"])
        self.assertEqual(internal["pass_fail"], "pass")
        self.assertFalse(internal["requires_user_attention"])

        self.assertEqual(state["current_major_stage"], "Stage 5")
        self.assertEqual(state["current_work_package"], "Stage 5 WP2 manual trades CSV import")
        self.assertEqual(state["last_completed_work_package"], "Stage 5 WP1 manual holdings CSV import")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage5_wp1_manual_holdings_import.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage5_wp1_manual_holdings_import_report.json")
        self.assertEqual(state["stage5"]["status"], "next_work_package_ready")
        self.assertIn("stage5_wp1_manual_holdings_import", state["stage5"]["completed_work_packages"])
        self.assertEqual(state["stage5"]["next_work_package"], "Stage 5 WP2 manual trades CSV import")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 5 WP2 manual trades CSV import")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 5 WP2 manual trades CSV import")

        combined = REPORT_MD.read_text(encoding="utf-8") + "\n" + INTERNAL_MD.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("manual holdings CSV import", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)


if __name__ == "__main__":
    unittest.main()
