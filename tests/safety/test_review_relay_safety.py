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
        self.assertFalse((ROOT / "local_private" / "review_gate.json").exists())
        self.assertFalse((ROOT / "local_private" / "notification_state.json").exists())

    def test_relay_preview_commands_work_without_real_gate(self) -> None:
        commands = [
            ["scripts/review_relay/build_chatgpt_review_prompt.py"],
            ["scripts/review_relay/check_review_gate.py"],
            ["scripts/review_relay/render_manual_fallback_prompt.py"],
            ["scripts/review_relay/render_notification_preview.py"],
        ]
        for command in commands:
            result = self.run_cmd(command)
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        status = json.loads((ROOT / "reports" / "review_requests" / "relay_status.json").read_text())
        self.assertEqual(status["relay_stage"], "draft_only")
        self.assertFalse(status["computer_use_executed"])
        self.assertTrue(status["chatgpt_prompt_generated"])
        self.assertTrue(status["manual_fallback_available"])
        self.assertTrue(status["review_gate_required"])
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
        self.assertEqual(notification["mode"], "repo_only_preview")
        self.assertEqual(
            notification["review_target_commit"],
            latest_review["review_target_commit"],
        )
        self.assertFalse(notification["sent_to_feishu"])
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
        self.assertIn("repo 是 public，不需要 GitHub connector", prompt)
        self.assertIn("最终交易由用户手动决定", prompt)

    def test_review_relay_safety_script_passes(self) -> None:
        result = self.run_cmd(["scripts/safety/check_review_relay_safety.py", "--root", str(ROOT)])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["findings"])


if __name__ == "__main__":
    unittest.main()
