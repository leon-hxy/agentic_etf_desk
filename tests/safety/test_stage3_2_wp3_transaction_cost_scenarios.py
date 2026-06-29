import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.2 WP3 transaction cost sensitivity scenarios"
NEXT_WORK_PACKAGE = "Stage 3.2 WP4 parameter sensitivity scenarios"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Stage32Wp3TransactionCostScenariosTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp3_generates_transaction_cost_sensitivity_report(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3_2_wp3_transaction_cost_scenarios.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["major_stage"], "Stage 3.2")
        self.assertEqual(payload["work_package"], STAGE)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(
            payload["source_backtest_report"],
            "reports/backtest_validation/stage3_1_wp3_backtest_validation_report.json",
        )
        self.assertEqual(payload["benchmark_symbol"], "VTI")
        self.assertEqual(payload["symbol_count"], 10)
        self.assertEqual(payload["unknown_symbols"], [])
        self.assertEqual(payload["transaction_cost_bps"], [0, 2, 5, 10, 25])
        self.assertTrue(payload["validation_checks"]["transaction_cost_scenarios"]["passed"])
        self.assertTrue(payload["validation_checks"]["benchmark_comparison_preserved"]["passed"])
        self.assertTrue(payload["validation_checks"]["universe_allowlist"]["passed"])
        self.assertTrue(payload["validation_checks"]["research_only_boundary"]["passed"])
        self.assertFalse(payload["safety_flags"]["computer_use_executed"])
        self.assertFalse(payload["safety_flags"]["broker_write_surface"])
        self.assertFalse(payload["safety_flags"]["order_placement_surface"])
        self.assertFalse(payload["safety_flags"]["real_config_modified"])

        scenario_results = payload["transaction_cost_scenarios"]
        self.assertEqual(sorted(scenario_results), ["0bps", "10bps", "25bps", "2bps", "5bps"])
        for scenario_id, scenario in scenario_results.items():
            self.assertEqual(set(scenario["strategy_results"]), set(payload["strategies"]))
            self.assertIn("cost_rate", scenario)
            self.assertIn("description", scenario)
            for strategy_id, result_payload in scenario["strategy_results"].items():
                self.assertIsInstance(strategy_id, str)
                self.assertEqual(result_payload["benchmark_symbol"], "VTI")
                self.assertGreaterEqual(result_payload["months"], 1)
                self.assertIn("scenario_cagr", result_payload)
                self.assertIn("benchmark_cagr", result_payload)
                self.assertIn("excess_cagr_vs_benchmark", result_payload)
                self.assertIn("max_drawdown", result_payload)
                self.assertIn("total_turnover", result_payload)
                self.assertIn("transaction_cost_drag", result_payload)
                self.assertGreaterEqual(result_payload["transaction_cost_drag"], 0.0)

        dual_momentum = scenario_results["2bps"]["strategy_results"]["dual_momentum"]
        higher_cost_dual_momentum = scenario_results["25bps"]["strategy_results"]["dual_momentum"]
        self.assertGreater(dual_momentum["scenario_cagr"], higher_cost_dual_momentum["scenario_cagr"])
        self.assertGreater(
            higher_cost_dual_momentum["transaction_cost_drag"],
            dual_momentum["transaction_cost_drag"],
        )
        self.assertIn("Final trading is manually decided by the user.", payload["final_trading_notice"])

        report = read_json("reports/research_robustness/stage3_2_wp3_transaction_cost_scenarios_report.json")
        self.assertEqual(report, payload)
        report_md = (
            ROOT / "reports/research_robustness/stage3_2_wp3_transaction_cost_scenarios_report.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user.", report_md)

    def test_wp3_internal_review_and_runner_state_advance_without_user_notification(self) -> None:
        review = read_json("reports/internal_reviews/program/stage3_2_wp3_transaction_cost_scenarios.json")
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
        self.assertTrue(review["domain_quant_reviewer"]["transaction_cost_scenarios_reviewed"])
        self.assertFalse(review["security_reviewer"]["secrets_touched"])
        self.assertFalse(review["integration_reviewer"]["real_runtime_modified"])
        self.assertFalse(review["requires_user_attention"])
        self.assertEqual(review["promote_to_next_work_package"], NEXT_WORK_PACKAGE)

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP7 long-term runbook")
        self.assertEqual(state["status"], "next_work_package_ready")
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(
            state["last_internal_review"],
            "reports/internal_reviews/program/stage6_wp6_openclaw_agent_boundary_checks.json",
        )
        self.assertEqual(
            state["last_report"],
            "reports/program_runner/stage6_wp6_openclaw_agent_boundary_checks_report.json",
        )
        self.assertIn("stage3_2_wp3_transaction_cost_scenarios", state["stage3_2"]["completed_work_packages"])
        self.assertEqual(state["stage4"]["current_work_package"], "Stage 4 WP7 OpenClaw agents draft or safe integration plan")
        self.assertFalse(state["stage3_2"]["user_notification_sent"])
        self.assertFalse(state["stage3_2"]["chatgpt_review_requested"])


if __name__ == "__main__":
    unittest.main()
