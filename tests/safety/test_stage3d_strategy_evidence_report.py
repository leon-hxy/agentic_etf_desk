import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "reports" / "strategy_evidence" / "stage3d_strategy_evidence_report.json"
REPORT_MD = ROOT / "reports" / "strategy_evidence" / "stage3d_strategy_evidence_report.md"
INTERNAL_REVIEW_JSON = ROOT / "reports" / "internal_reviews" / "stage3" / "stage3d_strategy_evidence_report.json"
REQUIRED_STRATEGIES = [
    "benchmark_buy_hold",
    "static_6040",
    "gtaa_10m_sma",
    "dual_momentum",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Stage3DStrategyEvidenceReportTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_stage3d_strategy_evidence_script_generates_formal_report(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage3d_strategy_evidence.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["stage"], "Stage 3D strategy evidence report")
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["report_json"], "reports/strategy_evidence/stage3d_strategy_evidence_report.json")
        self.assertEqual(payload["report_md"], "reports/strategy_evidence/stage3d_strategy_evidence_report.md")
        self.assertEqual(
            payload["source_validation_report"],
            "reports/backtest_validation/stage3c_backtest_validation_report.json",
        )
        self.assertEqual(payload["manual_execution_note"], "Final trading is manually decided by the user.")
        self.assertEqual(payload["strategies"], REQUIRED_STRATEGIES)

        self.assertTrue(payload["data_boundary"]["sample_data_only"])
        self.assertFalse(payload["data_boundary"]["real_data_used"])
        self.assertTrue(payload["data_boundary"]["not_investment_basis"])
        self.assertIn("sample", payload["data_boundary"]["note"].lower())
        self.assertIn("not investment", payload["data_boundary"]["note"].lower())

        for check in (
            "stage3c_validation_passed",
            "required_strategies_present",
            "benchmark_comparison_present",
            "sample_boundary_documented",
            "manual_trading_notice_present",
            "risk_and_limitations_documented",
        ):
            self.assertEqual(payload["validation_checks"][check], "passed")

        evidence = payload["strategy_evidence"]
        self.assertEqual(set(evidence), set(REQUIRED_STRATEGIES))
        self.assertIn("Buy-and-Hold", evidence["benchmark_buy_hold"]["display_name"])
        self.assertIn("60/40", evidence["static_6040"]["display_name"])
        self.assertIn("GTAA", evidence["gtaa_10m_sma"]["display_name"])
        self.assertIn("Dual Momentum", evidence["dual_momentum"]["display_name"])
        for strategy_id in REQUIRED_STRATEGIES:
            item = evidence[strategy_id]
            self.assertEqual(item["benchmark_symbol"], "VTI")
            self.assertTrue(item["has_required_metrics"])
            self.assertTrue(item["has_benchmark_comparison"])
            self.assertIn("excess_cagr_vs_benchmark", item["metrics"])
            self.assertIn("max_drawdown_difference_vs_benchmark", item["metrics"])
            self.assertGreaterEqual(len(item["risk_notes"]), 2)
            self.assertGreaterEqual(len(item["limitation_notes"]), 2)
            self.assertTrue(item["evidence_summary"])
            self.assertTrue(any("sample" in note.lower() for note in item["limitation_notes"]))
            self.assertTrue(any("not investment" in note.lower() for note in item["limitation_notes"]))

        for flag in (
            "auto_trading_surface",
            "broker_surface",
            "broker_write_surface",
            "chatgpt_review_requested",
            "computer_use_executed",
            "feishu_message_sent",
            "real_config_modified",
            "secret_values_written",
            "secrets_touched",
        ):
            self.assertFalse(payload["safety_flags"][flag], flag)

        self.assertEqual(read_json(REPORT_JSON), payload)
        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Stage 3D Strategy Evidence Report", text)
        self.assertIn("Buy-and-Hold", text)
        self.assertIn("60/40", text)
        self.assertIn("GTAA", text)
        self.assertIn("Dual Momentum", text)
        self.assertIn("Sample data only", text)
        self.assertIn("not investment basis", text)
        self.assertIn("Final trading is manually decided by the user", text)

    def test_stage3d_updates_governance_state_after_internal_review(self) -> None:
        task = read("ops/tasks/stage3d_strategy_evidence_report.md")
        runner = read_json(ROOT / "ops" / "runners" / "stage3_runner_state.json")
        loop_state = read_json(ROOT / "ops" / "state" / "loop_state.json")
        handoff = read_json(ROOT / "reports" / "codex_handoff" / "latest.json")
        review = read_json(INTERNAL_REVIEW_JSON)

        self.assertIn("status: completed_internal_review", task)
        self.assertIn("reports/strategy_evidence/stage3d_strategy_evidence_report.md", task)
        self.assertEqual(runner["status"], "major_stage_ready")
        self.assertEqual(runner["current_minor_stage"], "Stage 3F")
        self.assertEqual(runner["current_task"], "ops/tasks/stage3f_major_gate_feishu_notification_fix.md")
        self.assertEqual(runner["completed_minor_stages"], ["Stage 3A", "Stage 3B", "Stage 3C", "Stage 3D", "Stage 3E", "Stage 3F"])
        self.assertEqual(runner["remaining_minor_stages"], [])
        self.assertTrue(runner["major_review_required"])
        self.assertFalse(runner["computer_use_executed"])
        self.assertTrue(runner["feishu_notification_sent"])
        self.assertFalse(runner["chatgpt_review_for_minor_stages_allowed"])
        self.assertFalse(runner["requires_user_attention"])

        self.assertEqual(loop_state["current_stage"], "Stage 3F major_gate_feishu_notification_sent")
        self.assertEqual(loop_state["stage3d_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3e_task_status"], "completed_internal_review")
        self.assertEqual(loop_state["stage3_runner_current_minor_stage"], "Stage 3F")
        self.assertEqual(loop_state["stage3_runner_current_task"], "ops/tasks/stage3f_major_gate_feishu_notification_fix.md")
        self.assertIsNone(loop_state["next_minor_task"])
        self.assertEqual(loop_state["next_minor_task_status"], "manual_major_review_ready")
        self.assertFalse(loop_state["current_stage_chatgpt_review_requested"])
        self.assertFalse(loop_state["current_stage_computer_use_executed"])
        self.assertTrue(loop_state["current_stage_feishu_message_sent"])

        self.assertEqual(handoff["stage"], "Stage 3F major_gate_feishu_notification_sent")
        self.assertEqual(handoff["stage3d_task_status"], "completed_internal_review")
        self.assertEqual(handoff["stage3e_task_status"], "completed_internal_review")
        self.assertEqual(handoff["stage3_runner_current_minor_stage"], "Stage 3F")
        self.assertEqual(handoff["stage3_runner_current_task"], "ops/tasks/stage3f_major_gate_feishu_notification_fix.md")
        self.assertFalse(handoff["chatgpt_review_requested"])
        self.assertFalse(handoff["computer_use_executed"])
        self.assertTrue(handoff["feishu_message_sent"])

        self.assertEqual(review["minor_stage"], "Stage 3D")
        self.assertEqual(review["status"], "completed_internal_review")
        self.assertEqual(review["task_file"], "ops/tasks/stage3d_strategy_evidence_report.md")
        self.assertEqual(review["evidence_report"], "reports/strategy_evidence/stage3d_strategy_evidence_report.json")
        for section in ("security_reviewer", "domain_reviewer", "integration_reviewer", "test_reviewer"):
            self.assertEqual(review[section]["result"], "pass")
            self.assertIn(review[section]["reviewer_mode"], {"subagent_read_only", "simulated_separate_pass"})
        self.assertFalse(review["requires_user_attention"])
        self.assertFalse(review["chatgpt_review_requested"])
        self.assertFalse(review["computer_use_executed"])
        self.assertFalse(review["feishu_message_sent"])


if __name__ == "__main__":
    unittest.main()
