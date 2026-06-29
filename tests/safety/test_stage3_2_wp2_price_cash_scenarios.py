import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.2 WP2 price discrepancy and cash assumption scenarios"
NEXT_WORK_PACKAGE = "Stage 3.2 WP3 transaction cost sensitivity scenarios"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Stage32Wp2PriceCashScenariosTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp2_generates_price_discrepancy_and_cash_scenario_report(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_2_wp2_price_cash_scenarios.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["major_stage"], "Stage 3.2")
        self.assertEqual(payload["work_package"], STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["monthly_panel_file"], "data/processed/stage3_1_monthly_panel.csv")
        self.assertEqual(payload["raw_price_file"], "data/raw/prices_yahoo_chart.csv")
        self.assertEqual(
            payload["source_backtest_report"],
            "reports/backtest_validation/stage3_1_wp3_backtest_validation_report.json",
        )
        self.assertEqual(payload["benchmark_symbol"], "VTI")
        self.assertEqual(payload["cash_proxy_symbol"], "BIL")
        self.assertEqual(payload["short_treasury_proxy_symbol"], "IEF")
        self.assertEqual(payload["symbol_count"], 10)
        self.assertEqual(payload["price_discrepancies"], [])
        self.assertEqual(
            [scenario["tolerance_bps"] for scenario in payload["price_tolerance_scenarios"]],
            [1, 5, 10],
        )
        self.assertTrue(all(scenario["passed"] for scenario in payload["price_tolerance_scenarios"]))
        self.assertTrue(payload["validation_checks"]["price_discrepancy_tolerances"]["passed"])
        self.assertTrue(payload["validation_checks"]["cash_assumption_scenarios"]["passed"])
        self.assertTrue(payload["validation_checks"]["benchmark_comparison_preserved"]["passed"])
        self.assertTrue(payload["validation_checks"]["universe_allowlist"]["passed"])
        self.assertFalse(payload["safety_flags"]["computer_use_executed"])
        self.assertFalse(payload["safety_flags"]["broker_write_surface"])
        self.assertFalse(payload["safety_flags"]["order_placement_surface"])

        cash_scenarios = payload["cash_assumption_scenarios"]
        self.assertEqual(
            sorted(cash_scenarios),
            ["base_bil_cash_proxy", "short_treasury_ief_proxy", "zero_return_cash"],
        )
        for scenario_id, scenario in cash_scenarios.items():
            self.assertIn(scenario_id, scenario["description_key"])
            self.assertEqual(set(scenario["strategy_results"]), set(payload["strategies"]))
            for strategy_id, result_payload in scenario["strategy_results"].items():
                self.assertEqual(result_payload["benchmark_symbol"], "VTI")
                self.assertIn("scenario_cagr", result_payload)
                self.assertIn("benchmark_cagr", result_payload)
                self.assertIn("excess_cagr_vs_benchmark", result_payload)
                self.assertIn("max_drawdown", result_payload)
                self.assertGreaterEqual(result_payload["months"], 1)
                self.assertIn("cash_proxy_weight_months", result_payload)
                self.assertIsInstance(strategy_id, str)
        self.assertNotEqual(
            cash_scenarios["base_bil_cash_proxy"]["strategy_results"]["static_6040"]["scenario_cagr"],
            cash_scenarios["zero_return_cash"]["strategy_results"]["static_6040"]["scenario_cagr"],
        )
        self.assertIn("Final trading is manually decided by the user.", payload["final_trading_notice"])

        report = read_json("reports/research_robustness/stage3_2_wp2_price_cash_scenarios_report.json")
        self.assertEqual(report, payload)
        report_md = (ROOT / "reports/research_robustness/stage3_2_wp2_price_cash_scenarios_report.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Final trading is manually decided by the user.", report_md)

    def test_wp2_internal_review_and_runner_state_advance_without_user_notification(self) -> None:
        review = read_json("reports/internal_reviews/program/stage3_2_wp2_price_cash_scenarios.json")
        state = read_json("ops/program_runner/program_runner_state.json")

        self.assertEqual(review["major_stage"], "Stage 3.2")
        self.assertEqual(review["work_package"], STAGE)
        self.assertEqual(review["reviewer_mode"], "simulated_separate_pass")
        self.assertEqual(review["pass_fail"], "passed")
        self.assertEqual(review["security_reviewer"]["result"], "passed")
        self.assertEqual(review["domain_quant_reviewer"]["result"], "passed")
        self.assertEqual(review["risk_agent_review"]["result"], "passed")
        self.assertTrue(review["risk_agent_review"]["no_actionable_trade_tickets_generated"])
        self.assertEqual(review["integration_reviewer"]["result"], "passed")
        self.assertEqual(review["test_reproducibility_reviewer"]["result"], "passed")
        self.assertEqual(review["public_repo_hygiene_reviewer"]["result"], "passed")
        self.assertTrue(review["domain_quant_reviewer"]["etf_only_maintained"])
        self.assertTrue(review["domain_quant_reviewer"]["benchmark_comparison_present"])
        self.assertFalse(review["security_reviewer"]["secrets_touched"])
        self.assertFalse(review["integration_reviewer"]["real_runtime_modified"])
        self.assertFalse(review["requires_user_attention"])
        self.assertEqual(review["promote_to_next_work_package"], NEXT_WORK_PACKAGE)

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP3 log redaction")
        self.assertEqual(state["status"], "next_work_package_ready")
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP2 error recovery")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage6_wp2_error_recovery.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage6_wp2_error_recovery_report.json")
        self.assertFalse(state["stage3_2"]["user_notification_sent"])
        self.assertFalse(state["stage3_2"]["chatgpt_review_requested"])
        self.assertIn("stage3_2_wp2_price_cash_scenarios", state["stage3_2"]["completed_work_packages"])
        self.assertEqual(state["stage4"]["current_work_package"], "Stage 4 WP7 OpenClaw agents draft or safe integration plan")


if __name__ == "__main__":
    unittest.main()
