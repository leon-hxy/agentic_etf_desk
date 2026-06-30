import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_JSON = ROOT / "reports" / "operations" / "stage6_wp5_notification_stability.json"
POLICY_MD = ROOT / "reports" / "operations" / "stage6_wp5_notification_stability.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp5_notification_stability_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp5_notification_stability_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp5_notification_stability.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp5_notification_stability.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage6WP5NotificationStabilityTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_wp5_generator_creates_repo_only_notification_stability_artifacts(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage6_wp5_notification_stability.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (POLICY_JSON, POLICY_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        policy = json.loads(POLICY_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))
        loop_state = json.loads(LOOP_STATE_JSON.read_text(encoding="utf-8"))

        self.assertEqual(policy["report_type"], "notification_stability_policy")
        self.assertEqual(policy["work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertEqual(policy["asset_scope"], "ETF-only")
        self.assertTrue(policy["repo_only"])
        self.assertTrue(policy["final_trading_manual"])
        self.assertFalse(policy["automatic_trading"])
        self.assertFalse(policy[BROKER_ACCESS_SURFACE_FIELD])
        self.assertFalse(policy["order_placement"])
        self.assertFalse(policy["live_send_attempted"])
        self.assertFalse(policy["real_runtime_modified"])
        self.assertFalse(policy["services_restarted"])
        self.assertFalse(policy["trade_ticket_generated"])
        self.assertEqual(policy["next_work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(policy["risk_agent_review"]["result"], "passed")
        self.assertFalse(policy["risk_agent_review"]["new_actionable_trade_suggestion"])

        check_ids = [check["check_id"] for check in policy["stability_checks"]]
        self.assertEqual(
            check_ids,
            [
                "idempotent_notification_preview",
                "allowed_status_only",
                "blocked_or_approval_next_safe_action",
                "secret_free_message_body",
                "repo_only_live_send_fallback",
                "delivery_status_audit_fields",
            ],
        )
        self.assertEqual(policy["notification_contract"]["send_gate_statuses"], ["blocked", "approval_required", "final_review_ready"])
        self.assertFalse(policy["notification_contract"]["send_on_work_package_completed"])
        self.assertFalse(policy["notification_contract"]["send_on_internal_review_completed"])
        self.assertTrue(policy["notification_contract"]["preview_required_when_live_send_not_allowed"])
        self.assertEqual(policy["validation_summary"]["status"], "pass")
        self.assertEqual(policy["validation_summary"]["findings_count"], 0)

        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertEqual(report["next_work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertTrue(report["validation_checks"]["idempotency_key_defined"])
        self.assertTrue(report["validation_checks"]["allowed_status_gate_defined"])
        self.assertTrue(report["validation_checks"]["next_safe_action_required"])
        self.assertTrue(report["validation_checks"]["notification_preview_fallback_defined"])
        self.assertTrue(report["validation_checks"]["manual_trading_disclaimer_present"])
        self.assertFalse(report["live_send_attempted"])
        self.assertFalse(report["real_runtime_modified"])

        self.assertEqual(internal["pass_fail"], "pass")
        self.assertEqual(internal["reviewer_mode"], "simulated_separate_pass")
        self.assertFalse(internal["requires_user_attention"])
        self.assertFalse(internal["risk_agent_review"]["new_actionable_trade_suggestion"])

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP5 Hermes/Feishu notification stability")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage6_wp5_notification_stability.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage6_wp5_notification_stability_report.json")
        self.assertEqual(state["stage6"]["status"], "next_work_package_ready")
        self.assertIn("stage6_wp5_notification_stability", state["stage6"]["completed_work_packages"])
        self.assertEqual(state["stage6"]["next_work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 6 WP6 OpenClaw agent boundary checks")
        self.assertEqual(loop_state["program_runner"]["current_work_package"], "Stage 6 WP6 OpenClaw agent boundary checks")

        combined = "\n".join(
            [
                POLICY_MD.read_text(encoding="utf-8"),
                REPORT_MD.read_text(encoding="utf-8"),
                INTERNAL_MD.read_text(encoding="utf-8"),
                json.dumps(policy, sort_keys=True),
            ]
        )
        self.assertIn("Final trading is manually decided by the user", combined)
        self.assertIn("repo-only", combined)
        self.assertIn("live send attempted: false", combined)
        self.assertIn("next_safe_action", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)
        self.assertNotIn("FEISHU_APP_SECRET", combined)
        self.assertNotIn("OPENAI_API_KEY", combined)
        self.assertNotIn("token=", combined)
        self.assertNotIn("auth=", combined)


if __name__ == "__main__":
    unittest.main()
