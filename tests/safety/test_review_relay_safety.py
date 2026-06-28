import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ReviewRelaySafetyTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_review_gate_example_is_safe_and_bound(self) -> None:
        path = ROOT / "ops" / "review_gate" / "review_gate.example.json"
        self.assertTrue(path.exists())
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(payload["approved"])
        self.assertEqual(payload["approved_action"], "chatgpt_review_relay")
        self.assertEqual(payload["repo"], "leon-hxy/agentic_etf_desk")
        self.assertEqual(payload["commit"], "PLACEHOLDER_COMMIT_SHA")
        self.assertEqual(payload["one_time_nonce"], "PLACEHOLDER_NONCE")
        self.assertFalse(payload["used"])
        self.assertIn("expires_at", payload)

    def test_real_review_gate_and_notification_state_are_not_committed(self) -> None:
        for rel in ("local_private/review_gate.json", "local_private/notification_state.json"):
            path = ROOT / rel
            tracked = subprocess.run(
                ["git", "ls-files", "--error-unmatch", rel],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(tracked.returncode, 0, rel)
            if path.exists():
                ignored = subprocess.run(
                    ["git", "check-ignore", "-q", rel],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(ignored.returncode, 0, rel)

    def test_relay_status_keeps_manual_controls_with_or_without_live_relay(self) -> None:
        status = json.loads((ROOT / "reports" / "review_requests" / "relay_status.json").read_text())
        self.assertTrue(status["chatgpt_prompt_generated"])
        self.assertTrue(status["manual_fallback_available"])

        if status["relay_stage"] in {
            "stage2f_review_governance_manual_only",
            "stage2f1_branch_governance_manual_only",
            "stage3a_codex_self_review_no_chatgpt",
            "stage3b_codex_self_review_no_chatgpt",
            "stage3ab_internal_review_no_chatgpt",
            "stage3c_internal_review_no_chatgpt",
            "stage3d_internal_review_no_chatgpt",
            "stage3e_major_review_ready_manual_only",
            "stage3f_major_gate_feishu_notified_manual_review_ready",
            "stage3f1_review_target_commit_consistent_manual_review_ready",
            "stage3_major_gate_finalized_manual_review_ready",
        }:
            self.assertFalse(status["review_gate_required"])
            self.assertTrue(status["chatgpt_computer_use_auto_review_deprecated"])
            self.assertTrue(status["chatgpt_review_is_manual"])
            if status["relay_stage"] in {
                "stage3e_major_review_ready_manual_only",
                "stage3f_major_gate_feishu_notified_manual_review_ready",
                "stage3f1_review_target_commit_consistent_manual_review_ready",
                "stage3_major_gate_finalized_manual_review_ready",
            }:
                self.assertEqual(status["review_route"], "manual_chatgpt_review_for_major_stage")
                self.assertTrue(status["manual_chatgpt_review_ready"])
                if status["relay_stage"] == "stage3f_major_gate_feishu_notified_manual_review_ready":
                    self.assertTrue(status["feishu_message_sent"])
                if status["relay_stage"] == "stage3f1_review_target_commit_consistent_manual_review_ready":
                    self.assertEqual(status["review_target_consistency_status"], "passed")
                if status["relay_stage"] == "stage3_major_gate_finalized_manual_review_ready":
                    self.assertEqual(status["finalization_status"], "completed")
                    self.assertEqual(status["review_target_consistency_status"], "passed")
                    self.assertFalse(status["request_chatgpt_review_for_finalization_fixes"])
            else:
                self.assertEqual(status["review_route"], "codex_self_review_for_small_stage")
            self.assertEqual(status["major_review_route"], "manual_chatgpt_review_for_major_stage")
            self.assertFalse(status["automatic_chatgpt_prompt_send_allowed"])
            self.assertFalse(status["computer_use_executed"])
            self.assertFalse(status["sent_to_chatgpt"])
            self.assertIn(
                status["status_reason"],
                {
                    "chatgpt_computer_use_auto_review_deprecated",
                    "stage3a_passed_codex_self_review_no_chatgpt_request",
                    "stage3b_passed_codex_self_review_no_chatgpt_request",
                    "stage3ab_completed_internal_review_no_chatgpt_request",
                    "stage3c_completed_internal_review_no_chatgpt_request",
                    "stage3d_completed_internal_review_no_chatgpt_request",
                    "stage3e_major_review_package_ready_manual_chatgpt_review",
                    "stage3f_major_gate_feishu_notification_sent",
                    "stage3f1_review_target_commit_consistency_fixed",
                    "stage3_major_gate_finalization_completed",
                },
            )
            self.assertIn(
                status["input_delivery_contract"]["prompt_entry_method"],
                {"user_manual_copy_only", "not_applicable_small_stage_self_review"},
            )
        elif status["relay_stage"] == "stage2e1_relay_hardening_repo_only":
            self.assertTrue(status["review_gate_required"])
            self.assertFalse(status["computer_use_executed"])
            self.assertFalse(status["sent_to_chatgpt"])
            self.assertEqual(status["status_reason"], "repo_only_relay_hardening_ready_no_live_send")
            self.assertEqual(status["target_conversation_mode"], "dedicated_review_thread")
            self.assertEqual(status["recommended_target_mode"], "dedicated_review_thread")
            self.assertIn("existing_conversation_url", status["supported_target_modes"])
            self.assertEqual(
                status["existing_conversation_url_source"],
                "local_private/chatgpt_review_target.json",
            )
            self.assertIsNone(status["existing_conversation_url_public_value"])
            self.assertEqual(
                status["input_delivery_contract"]["prompt_entry_method"],
                "paste_or_clipboard_insert",
            )
            self.assertTrue(status["input_delivery_contract"]["long_prompt_typing_forbidden"])
            self.assertEqual(
                status["input_delivery_contract"]["pre_send_safety_check_status"],
                "pass",
            )
            self.assertEqual(status["failure_policy"], "mark_failed_and_stop")
            self.assertFalse(status["auto_trading_surface"] if "auto_trading_surface" in status else False)
        elif status["relay_stage"] == "stage2e0_chatgpt_relay_smoke":
            self.assertTrue(status["review_gate_required"])
            self.assertTrue(status["computer_use_executed"])
            self.assertTrue(status["sent_to_chatgpt"])
            self.assertEqual(status["status_reason"], "sent_with_degraded_split_prompt")
            self.assertFalse(status["auto_trading_surface"])
            self.assertFalse(status["broker_or_trading_site_accessed"])
        else:
            self.assertTrue(status["review_gate_required"])
            self.assertEqual(status["relay_stage"], "draft_only")
            self.assertFalse(status["computer_use_executed"])
            if (ROOT / "local_private" / "review_gate.json").exists():
                self.assertTrue(status["review_gate_seen"])
                self.assertIn(status["status_reason"], {"gate_valid", "gate_expired", "gate_marked_used"})
            else:
                self.assertFalse(status["review_gate_seen"])
                self.assertFalse(status["review_gate_valid"])
            self.assertFalse(status["sent_to_chatgpt"])

        notification = json.loads(
            (ROOT / "reports" / "review_requests" / "notification_preview.json").read_text(
                encoding="utf-8"
            )
        )
        latest_review = json.loads(
            (ROOT / "reports" / "review_requests" / "latest.json").read_text(encoding="utf-8")
        )
        self.assertIn(
            notification["mode"],
            {
                "repo_only_preview",
                "live_feishu_notification_sent",
                "replacement_notification_preview_after_finalization",
            },
        )
        self.assertEqual(
            notification["review_target_commit"],
            latest_review["review_target_commit"],
        )
        self.assertEqual(notification["sent_to_feishu"], notification["mode"] == "live_feishu_notification_sent")
        if notification["mode"] == "replacement_notification_preview_after_finalization":
            self.assertTrue(notification["previous_notification_superseded"])
            self.assertFalse(notification["replacement_notification_sent"])
        if latest_review["stage"].startswith("Stage 2E.0"):
            self.assertTrue(notification["computer_use_executed"])
        else:
            self.assertFalse(notification["computer_use_executed"])

    def test_generated_prompt_is_public_only(self) -> None:
        prompt = (ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.md").read_text(
            encoding="utf-8"
        )
        forbidden = [
            "/" + "Users" + "/",
            "/" + "Volumes" + "/",
            "Feishu App Secret=",
            "OpenAI API key",
        ]
        for term in forbidden:
            self.assertNotIn(term, prompt)
        self.assertIn("https://github.com/leon-hxy/agentic_etf_desk", prompt)
        self.assertIn("最终交易由用户手动决定", prompt)
        if "Stage 3" in prompt and "major-stage review request" in prompt:
            self.assertIn("Manual ChatGPT major-stage review request", prompt)
            self.assertIn("reports/major_reviews/stage3/latest.md", prompt)
        else:
            self.assertIn("No ChatGPT review requested", prompt)
            self.assertIn("Manual major-stage ChatGPT review is deferred", prompt)
        self.assertLessEqual(len(prompt), 900)
        self.assertNotIn("local_private", prompt)
        self.assertNotIn("reports/relay_smoke", prompt)
        self.assertNotIn("review_files", prompt)
        self.assertNotIn("Computer Use", prompt)

    def test_review_relay_safety_script_passes(self) -> None:
        result = self.run_cmd(["scripts/safety/check_review_relay_safety.py", "--root", str(ROOT)])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["findings"])


if __name__ == "__main__":
    unittest.main()
