import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "reports" / "backtest_validation" / "stage3c_backtest_validation_report.json"
REPORT_MD = ROOT / "reports" / "backtest_validation" / "stage3c_backtest_validation_report.md"
INTERNAL_REVIEW_JSON = ROOT / "reports" / "internal_reviews" / "stage3" / "stage3c_backtest_validation.json"
sys.path.insert(0, str(ROOT / "scripts" / "backtest"))
import validate_stage3c_backtest as stage3c_validator  # noqa: E402


STRATEGY_IDS = [
    "benchmark_buy_hold",
    "static_6040",
    "equal_weight_etf",
    "gtaa_10m_sma",
    "dual_momentum",
    "time_series_momentum_vol_target",
    "inverse_volatility_allocation",
    "etf_mean_reversion_sandbox",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Stage3CBacktestValidationTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_stage3c_validation_script_generates_formal_report(self) -> None:
        result = self.run_cmd(["scripts/backtest/validate_stage3c_backtest.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["stage"], "Stage 3C backtest validation")
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["report_json"], "reports/backtest_validation/stage3c_backtest_validation_report.json")
        self.assertEqual(payload["report_md"], "reports/backtest_validation/stage3c_backtest_validation_report.md")

        report = read_json(REPORT_JSON)
        self.assertEqual(report, payload)
        self.assertEqual(report["input_backtest_report"], "reports/stage2b_backtest_report.json")
        self.assertEqual(report["stage3b_quality_report"], "reports/data_quality/stage3b_data_quality_report.json")
        self.assertTrue(report["data_boundary"]["sample_data_only"])
        self.assertFalse(report["data_boundary"]["real_data_used"])
        self.assertTrue(report["data_boundary"]["not_investment_basis"])
        self.assertIn("sample", report["data_boundary"]["source"])
        self.assertEqual(report["validation_checks"]["stage3b_quality_passed"], "passed")
        self.assertEqual(report["validation_checks"]["all_strategies_have_benchmarks"], "passed")
        self.assertEqual(report["validation_checks"]["all_strategies_have_required_metrics"], "passed")
        self.assertEqual(report["validation_checks"]["manual_trading_notice_present"], "passed")

        self.assertEqual(set(report["strategies"]), set(STRATEGY_IDS))
        for strategy_id in STRATEGY_IDS:
            self.assertIn(strategy_id, report["strategy_validations"])
            validation = report["strategy_validations"][strategy_id]
            self.assertEqual(validation["benchmark_symbol"], "VTI")
            self.assertTrue(validation["has_benchmark"])
            self.assertTrue(validation["has_required_metrics"])
            self.assertIn("excess_cagr_vs_benchmark", validation)
            self.assertIn("max_drawdown_difference_vs_benchmark", validation)

        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Stage 3C Backtest Validation Report", text)
        self.assertIn("Sample data only", text)
        self.assertIn("Final trading is manually decided by the user", text)

    def test_stage3c_validation_helpers_detect_invalid_inputs(self) -> None:
        invalid_strategy = stage3c_validator.validate_strategy(
            "invalid",
            {
                "metrics": {"cagr": 0.1},
                "benchmark": {"symbol": "", "metrics": {}},
            },
        )
        self.assertFalse(invalid_strategy["has_benchmark"])
        self.assertFalse(invalid_strategy["has_required_metrics"])
        self.assertFalse(invalid_strategy["benchmark_has_required_metrics"])

        payload = stage3c_validator.build_payload_from_inputs(
            quality={"status": "failed"},
            metadata={"source": "real", "price_panel_file": "data/processed/price_panel.csv"},
            reference_backtest={"strategies": {}},
            formal_backtest={"manual_execution_note": "", "strategies": {}},
        )
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["validation_checks"]["stage3b_quality_passed"], "failed")
        self.assertEqual(payload["validation_checks"]["reference_smoke_report_loaded"], "failed")
        self.assertEqual(payload["validation_checks"]["manual_trading_notice_present"], "failed")
        self.assertEqual(payload["validation_checks"]["sample_data_boundary_documented"], "failed")
        self.assertFalse(payload["data_boundary"]["sample_data_only"])
        self.assertTrue(payload["data_boundary"]["real_data_used"])

    def test_stage3c_updates_governance_state_after_internal_review(self) -> None:
        task = read("ops/tasks/stage3c_backtest_validation.md")
        runner = read_json(ROOT / "ops" / "runners" / "stage3_runner_state.json")
        loop_state = read_json(ROOT / "ops" / "state" / "loop_state.json")
        handoff = read_json(ROOT / "reports" / "codex_handoff" / "latest.json")
        review = read_json(INTERNAL_REVIEW_JSON)

        self.assertIn("status: completed_internal_review", task)
        self.assertEqual(runner["status"], "major_stage_ready")
        self.assertEqual(runner["current_minor_stage"], "Stage 3E")
        self.assertEqual(runner["current_task"], "ops/tasks/stage3_major_review_package.md")
        self.assertEqual(runner["completed_minor_stages"], ["Stage 3A", "Stage 3B", "Stage 3C", "Stage 3D", "Stage 3E"])
        self.assertEqual(runner["remaining_minor_stages"], [])
        self.assertFalse(runner["computer_use_executed"])
        self.assertFalse(runner["feishu_notification_sent"])
        self.assertFalse(runner["chatgpt_review_for_minor_stages_allowed"])

        self.assertEqual(loop_state["current_stage"], "Stage 3E major_review_package_ready")
        self.assertEqual(loop_state["stage3c_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3d_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3e_task_status"], "completed_internal_review")
        self.assertIsNone(loop_state["next_minor_task"])
        self.assertEqual(loop_state["next_minor_task_status"], "major_review_ready")
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertFalse(loop_state["current_stage_feishu_message_sent"])

        self.assertEqual(handoff["stage"], "Stage 3E major_review_package_ready")
        self.assertEqual(handoff["stage3c_task_status"], "completed_internal_review")
        self.assertEqual(handoff["stage3d_task_status"], "completed_internal_review")
        self.assertEqual(handoff["stage3e_task_status"], "completed_internal_review")
        self.assertEqual(handoff["stage3_runner_current_minor_stage"], "Stage 3E")
        self.assertFalse(handoff["chatgpt_review_requested"])
        self.assertFalse(handoff["computer_use_executed"])
        self.assertFalse(handoff["feishu_message_sent"])

        self.assertEqual(review["minor_stage"], "Stage 3C")
        self.assertEqual(review["status"], "completed_internal_review")
        self.assertEqual(review["task_file"], "ops/tasks/stage3c_backtest_validation.md")
        for section in ("security_reviewer", "domain_reviewer", "integration_reviewer", "test_reviewer"):
            self.assertEqual(review[section]["result"], "pass")
            self.assertIn(review[section]["reviewer_mode"], {"subagent_read_only", "simulated_separate_pass"})
        self.assertFalse(review["requires_user_attention"])
        self.assertFalse(review["chatgpt_review_requested"])
        self.assertFalse(review["computer_use_executed"])
        self.assertFalse(review["feishu_message_sent"])


if __name__ == "__main__":
    unittest.main()
