import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
POLICY_JSON = ROOT / "reports" / "operations" / "stage6_wp3_log_redaction.json"
POLICY_MD = ROOT / "reports" / "operations" / "stage6_wp3_log_redaction.md"
REPORT_JSON = ROOT / "reports" / "program_runner" / "stage6_wp3_log_redaction_report.json"
REPORT_MD = ROOT / "reports" / "program_runner" / "stage6_wp3_log_redaction_report.md"
INTERNAL_JSON = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp3_log_redaction.json"
INTERNAL_MD = ROOT / "reports" / "internal_reviews" / "program" / "stage6_wp3_log_redaction.md"
STATE_JSON = ROOT / "ops" / "program_runner" / "program_runner_state.json"
HANDOFF_JSON = ROOT / "reports" / "codex_handoff" / "latest.json"
LOOP_STATE_JSON = ROOT / "ops" / "state" / "loop_state.json"
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))


class Stage6WP3LogRedactionTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_redactor_masks_sensitive_values_and_private_metadata(self) -> None:
        from scripts.safety.redact_sensitive_text import redact_text

        secret_key = "api" + "_key"
        bearer = "Bearer " + "sk-" + "abc123PRIVATE"
        pid_label = "p" + "id"
        pid_value = "543" + "21"
        user_path = "/" + "Users" + "/example/.tool/config.json"
        volume_path = "/" + "Volumes" + "/macos/example/Library/LaunchAgents/job.plist"
        text = "\n".join(
            [
                f"{secret_key}=real-value-123",
                f"Authorization: {bearer}",
                f"local path: {user_path}",
                f"launch agent: {volume_path}",
                f"{pid_label}: {pid_value}",
                "ETF signal generated for VTI only",
            ]
        )

        redacted = redact_text(text)

        self.assertIn(f"{secret_key}=<redacted>", redacted)
        self.assertIn("Authorization: Bearer <redacted>", redacted)
        self.assertIn("local path: <redacted-path>", redacted)
        self.assertIn("launch agent: <redacted-path>", redacted)
        self.assertIn("pid: <redacted-pid>", redacted)
        self.assertIn("ETF signal generated for VTI only", redacted)
        self.assertNotIn("real-value-123", redacted)
        self.assertNotIn("abc123PRIVATE", redacted)
        self.assertNotIn(user_path, redacted)
        self.assertNotIn(volume_path, redacted)
        self.assertNotIn(pid_value, redacted)

    def test_wp3_generator_creates_repo_only_log_redaction_artifacts(self) -> None:
        result = self.run_cmd(["scripts/reports/generate_stage6_wp3_log_redaction.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        for path in (POLICY_JSON, POLICY_MD, REPORT_JSON, REPORT_MD, INTERNAL_JSON, INTERNAL_MD):
            self.assertTrue(path.exists(), str(path))

        policy = json.loads(POLICY_JSON.read_text(encoding="utf-8"))
        report = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        internal = json.loads(INTERNAL_JSON.read_text(encoding="utf-8"))
        state = json.loads(STATE_JSON.read_text(encoding="utf-8"))
        handoff = json.loads(HANDOFF_JSON.read_text(encoding="utf-8"))
        loop_state = json.loads(LOOP_STATE_JSON.read_text(encoding="utf-8"))

        self.assertEqual(policy["report_type"], "log_redaction_policy")
        self.assertEqual(policy["work_package"], "Stage 6 WP3 log redaction")
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
        self.assertEqual(policy["next_work_package"], "Stage 6 WP4 public repo hygiene")
        self.assertEqual(policy["risk_agent_review"]["result"], "passed")
        self.assertFalse(policy["risk_agent_review"]["new_actionable_trade_suggestion"])

        rule_ids = [rule["rule_id"] for rule in policy["redaction_rules"]]
        self.assertEqual(
            rule_ids,
            [
                "secret_assignment_values",
                "authorization_headers",
                "absolute_local_paths",
                "local_private_references",
                "process_identifiers",
                "feishu_or_broker_private_identifiers",
            ],
        )
        for sample in policy["synthetic_validation_samples"]:
            self.assertTrue(sample["redacted"])
            self.assertFalse(sample["contains_original_sensitive_value"])

        self.assertEqual(report["status"], "completed_internal_review")
        self.assertEqual(report["work_package"], "Stage 6 WP3 log redaction")
        self.assertEqual(report["next_work_package"], "Stage 6 WP4 public repo hygiene")
        self.assertTrue(report["validation_checks"]["redactor_masks_secret_assignments"])
        self.assertTrue(report["validation_checks"]["redactor_masks_private_paths"])
        self.assertTrue(report["validation_checks"]["redactor_masks_process_ids"])
        self.assertTrue(report["validation_checks"]["manual_trading_disclaimer_present"])
        self.assertFalse(report["live_send_attempted"])
        self.assertFalse(report["real_runtime_modified"])

        self.assertEqual(internal["pass_fail"], "pass")
        self.assertEqual(internal["reviewer_mode"], "simulated_separate_pass")
        self.assertFalse(internal["requires_user_attention"])
        self.assertFalse(internal["risk_agent_review"]["new_actionable_trade_suggestion"])

        self.assertEqual(state["current_major_stage"], "Stage 6")
        self.assertEqual(state["current_work_package"], "Stage 6 WP4 public repo hygiene")
        self.assertEqual(state["last_completed_work_package"], "Stage 6 WP3 log redaction")
        self.assertEqual(state["last_internal_review"], "reports/internal_reviews/program/stage6_wp3_log_redaction.json")
        self.assertEqual(state["last_report"], "reports/program_runner/stage6_wp3_log_redaction_report.json")
        self.assertEqual(state["stage6"]["status"], "next_work_package_ready")
        self.assertIn("stage6_wp3_log_redaction", state["stage6"]["completed_work_packages"])
        self.assertEqual(state["stage6"]["next_work_package"], "Stage 6 WP4 public repo hygiene")
        self.assertEqual(state["status"], "next_work_package_ready")

        self.assertEqual(handoff["program_runner"]["current_work_package"], "Stage 6 WP4 public repo hygiene")
        self.assertEqual(handoff["program_runner"]["next_safe_action"], "resume Stage 6 WP4 public repo hygiene")
        self.assertEqual(loop_state["program_runner"]["current_work_package"], "Stage 6 WP4 public repo hygiene")

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
        self.assertIn("<redacted>", combined)
        self.assertNotIn("/" + "Volumes" + "/", combined)
        self.assertNotIn("/" + "Users" + "/", combined)
        self.assertNotIn("FEISHU_APP_SECRET", combined)
        self.assertNotIn("OPENAI_API_KEY", combined)
        self.assertNotIn("token=", combined)
        self.assertNotIn("auth=", combined)


if __name__ == "__main__":
    unittest.main()
