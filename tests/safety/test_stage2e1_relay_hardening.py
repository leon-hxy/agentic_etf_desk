import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 2E.1 ChatGPT relay target and input delivery hardened"
STAGE2F = "Stage 2F.1 branch governance and Stage 3 task plan completed"
STAGE3B = "Stage 3B completed_internal_review"
STAGE3C = "Stage 3C completed_internal_review"
STAGE3D = "Stage 3D completed_internal_review"
STAGE3E = "Stage 3E major_review_package_ready"
STAGE3F = "Stage 3F major_gate_feishu_notification_sent"
STAGE3F1 = "Stage 3F.1 review_target_commit_consistency_fixed"
STAGE3_CLOSEOUT = "Stage 3 sample-data pipeline validation merged to main"
STAGE3_READY = "Stage 3.1 major review package ready"
FINAL_STAGE = "v1.0 final review completed / ready for merge"
LOCAL_TARGET_CONFIG = "local_private/chatgpt_review_target.json"
MAX_SHORT_PROMPT_CHARS = 900


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Stage2E1RelayHardeningTest(unittest.TestCase):
    def test_short_review_prompt_is_public_and_small(self) -> None:
        latest = read_json(ROOT / "reports" / "review_requests" / "latest.json")
        prompt_json = read_json(ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.json")
        prompt_md = read_text(ROOT / "reports" / "review_requests" / "chatgpt_review_prompt.md")
        prompt = prompt_json["prompt"]

        known_stages = {STAGE, STAGE2F, STAGE3B, STAGE3C, STAGE3D, STAGE3E, STAGE3F, STAGE3F1, STAGE3_CLOSEOUT, STAGE3_READY, FINAL_STAGE}
        self.assertIn(latest["stage"], known_stages)
        self.assertIn(prompt_json["stage"], known_stages)
        self.assertEqual(prompt_md.strip(), prompt.strip())
        self.assertLessEqual(len(prompt), MAX_SHORT_PROMPT_CHARS)
        self.assertIn("https://github.com/leon-hxy/agentic_etf_desk", prompt)
        if prompt_json["stage"] == latest["stage"]:
            self.assertIn(latest["review_target_commit"], prompt)
        else:
            self.assertIn(prompt_json["review_target_commit"], prompt)
        for required_path in (
            "reports/review_requests/latest.md",
            "reports/review_requests/latest.json",
            "reports/codex_handoff/latest.md",
            "reports/codex_handoff/latest.json",
        ):
            self.assertIn(required_path, prompt)

        forbidden_prompt_fragments = [
            "/" + "Users" + "/",
            "/" + "Volumes" + "/",
            "local_private",
            "AGENTS.md",
            "docs/security_policy.md",
            "reports/relay_smoke",
            "review_files",
            "OpenAI API key",
            "token=",
            "secret=",
            "auth=",
        ]
        for fragment in forbidden_prompt_fragments:
            self.assertNotIn(fragment, prompt)

    def test_relay_status_declares_target_modes_and_input_contract(self) -> None:
        status = read_json(ROOT / "reports" / "review_requests" / "relay_status.json")
        if status["relay_stage"] in {
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
            self.assertIn(status["stage"], {STAGE2F, "Stage 3A data source plan completed", STAGE3B, STAGE3C, STAGE3D, STAGE3E, STAGE3F, STAGE3F1, STAGE3_CLOSEOUT, STAGE3_READY})
            self.assertTrue(status["chatgpt_computer_use_auto_review_deprecated"])
            self.assertEqual(status["major_review_route"], "manual_chatgpt_review_for_major_stage")
            self.assertFalse(status["computer_use_executed"])
            self.assertFalse(status["sent_to_chatgpt"])
            self.assertIn(
                status["input_delivery_contract"]["prompt_entry_method"],
                {"user_manual_copy_only", "not_applicable_small_stage_self_review"},
            )
            self.assertIn(
                status["failure_policy"],
                {"manual_review_required_for_major_stage", "notify_user_on_blocker_only"},
            )
            return

        self.assertEqual(status["relay_stage"], "stage2e1_relay_hardening_repo_only")
        self.assertEqual(status["stage"], STAGE)
        self.assertEqual(status["target_conversation_mode"], "dedicated_review_thread")
        self.assertEqual(status["recommended_target_mode"], "dedicated_review_thread")
        self.assertEqual(
            status["supported_target_modes"],
            ["dedicated_review_thread", "existing_conversation_url"],
        )
        self.assertEqual(status["existing_conversation_url_source"], LOCAL_TARGET_CONFIG)
        self.assertIsNone(status["existing_conversation_url_public_value"])
        self.assertFalse(status["computer_use_executed"])
        self.assertFalse(status["sent_to_chatgpt"])
        self.assertEqual(status["status_reason"], "repo_only_relay_hardening_ready_no_live_send")

        delivery = status["input_delivery_contract"]
        self.assertEqual(delivery["prompt_kind"], "short_review_prompt")
        self.assertEqual(delivery["prompt_entry_method"], "paste_or_clipboard_insert")
        self.assertTrue(delivery["long_prompt_typing_forbidden"])
        self.assertTrue(delivery["pre_send_safety_check_required"])
        self.assertEqual(delivery["pre_send_safety_check_status"], "pass")
        self.assertLessEqual(delivery["max_prompt_chars"], MAX_SHORT_PROMPT_CHARS)

        self.assertEqual(
            status["failure_stop_conditions"],
            [
                "target_conversation_mismatch",
                "input_box_residual_draft_detected",
                "prompt_split_detected",
                "sent_message_not_confirmed",
            ],
        )
        self.assertEqual(status["failure_policy"], "mark_failed_and_stop")

    def test_existing_conversation_url_source_is_local_private_and_not_tracked(self) -> None:
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", LOCAL_TARGET_CONFIG],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(ignored.returncode, 0)

        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", LOCAL_TARGET_CONFIG],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(tracked.returncode, 0)

    def test_public_artifacts_do_not_publish_existing_conversation_url(self) -> None:
        public_text = "\n".join(
            read_text(ROOT / rel)
            for rel in (
                "reports/review_requests/latest.md",
                "reports/review_requests/latest.json",
                "reports/review_requests/chatgpt_review_prompt.md",
                "reports/review_requests/chatgpt_review_prompt.json",
                "reports/review_requests/relay_status.md",
                "reports/review_requests/relay_status.json",
                "reports/codex_handoff/latest.md",
                "reports/codex_handoff/latest.json",
            )
        )
        self.assertNotIn("chatgpt.com/c/", public_text)
        self.assertNotIn("existing_conversation_url\": \"http", public_text)


if __name__ == "__main__":
    unittest.main()
