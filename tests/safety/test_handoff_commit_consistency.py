import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_STAGE = "Stage 2F.1 branch governance and Stage 3 task plan completed"
PREVIOUS_STAGE_COMMITS = {
    "8a1b03f" + "8078c9593f4730cf87785b4663ed05855",
    "c837110" + "53e6570bb447315e603c0a0701b9086b2",
    "83eeec" + "88ddda138b310aa7d41078919ee0f9b12d",
    "d40315a" + "ea238db28b1bdf857efa4052b250634c4",
    "acd9995" + "d7c48c24f1d381158ac72afb7579e0039",
    "3991a8c" + "083d73a42ff2879b53ad009a022d7ed02",
    "630433a" + "5cef96756811950738f4cf8dd8b4c820e",
    "a60f314" + "c39bf73274ffb6daff5ad902bf63b9293",
    "6db0e41" + "9622fefbcac9554900b1efb36890a959e",
    "9f06d64" + "67fb0bb5194affa43d5230c4d1f8c057b",
    "3a8076c" + "14c1918ad0e2225356c2acade63ba42c3",
    "336f28e" + "40fbb7fde70a63e55caebd346d28cb34a",
    "1d82b80" + "83c86613d9d516958aee704d0d8c65b2c",
    "59374cc" + "173da8cf57dfd1b8f98d27ef3338573e5",
    "88e31e9" + "daedcabb070469600f4fe2437a42c150c",
    "7dc1f0a" + "0dd7287105ba9add47588b2e37943d997",
    "d30169e" + "512f260dd5b29eb328d0f41c73cc927a9",
    "74215dd" + "69814c07fd5c3fd3937ccee15f9be8e8f",
    "23cebeb" + "ed1d07f0b35e66b284ec0891b427d8716",
    "9ac1dd8" + "b96fe98bae4bd676966293f03e0908047",
    "5a5d68e" + "2e34c6203ee2ab784dbbe3fa9a1cf1a6d",
    "f7fa73b" + "79ab1e3886c69bfd6ca5874a662acbb75",
    "2006d60" + "f237a9b47f34236fd7dd299e9bbdb4f86",
    "2371423" + "0ebda5bbaa16c27fac9efdf8d76663911",
}
JSON_TARGET_PATHS = [
    "reports/review_requests/latest.json",
    "reports/codex_handoff/latest.json",
    "reports/review_requests/chatgpt_review_prompt.json",
]
TEXT_TARGET_PATHS = [
    "reports/review_requests/chatgpt_review_prompt.md",
    "reports/review_requests/manual_fallback_prompt.md",
    "reports/review_requests/latest.md",
    "reports/codex_handoff/latest.md",
]
RELAY_STATUS_JSON = "reports/review_requests/relay_status.json"


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class HandoffCommitConsistencyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.handoff = read_json("reports/codex_handoff/latest.json")
        self.review = read_json("reports/review_requests/latest.json")
        self.review_target_commit = self.handoff.get("review_target_commit")

    def test_latest_json_files_declare_review_target_commit(self) -> None:
        self.assertEqual(
            self.handoff["stage"],
            EXPECTED_STAGE,
        )
        self.assertEqual(
            self.review["stage"],
            EXPECTED_STAGE,
        )
        self.assertEqual(
            self.handoff["loop_state_stage"],
            EXPECTED_STAGE,
        )
        self.assertEqual(
            self.review["loop_state_stage"],
            EXPECTED_STAGE,
        )
        self.assertTrue(self.review_target_commit)
        self.assertNotIn(self.review_target_commit, PREVIOUS_STAGE_COMMITS)
        self.assertEqual(self.review_target_commit, self.review.get("review_target_commit"))
        self.assertEqual(self.handoff.get("current_repo_head"), self.review.get("current_repo_head"))
        self.assertEqual(
            self.handoff.get("current_repo_head"),
            self.handoff.get("handoff_generated_from_head"),
        )
        self.assertIn("handoff_generated_from_head", self.handoff)
        self.assertIn("commit_binding_note", self.handoff)
        self.assertIn("review_target_commit", self.handoff["commit_binding_note"])
        self.assertIn("commit to review", self.handoff["commit_binding_note"])
        self.assertIsNone(self.handoff.get("handoff_commit"))

    def test_review_target_commit_is_valid_stage2f_commit(self) -> None:
        target = str(self.review_target_commit)
        result = git("cat-file", "-e", f"{target}^{{commit}}")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        subject = git("show", "-s", "--format=%s", target)
        self.assertEqual(subject.returncode, 0, msg=subject.stderr)
        self.assertIn("stage2f.1", subject.stdout.lower())
        self.assertNotIn("stage2a", subject.stdout.lower())

    def test_recorded_current_head_is_valid_git_commit(self) -> None:
        current_repo_head = str(self.handoff.get("current_repo_head"))
        result = git("cat-file", "-e", f"{current_repo_head}^{{commit}}")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_all_json_artifacts_bind_same_review_target(self) -> None:
        target = str(self.review_target_commit)
        for path in JSON_TARGET_PATHS:
            payload = read_json(path)
            self.assertEqual(payload["review_target_commit"], target, path)
            self.assertNotIn(payload["review_target_commit"], PREVIOUS_STAGE_COMMITS, path)

        prompt_payload = read_json("reports/review_requests/chatgpt_review_prompt.json")
        self.assertEqual(prompt_payload["gate"]["expected_commit"], target)
        relay_status = read_json("reports/review_requests/relay_status.json")
        self.assertEqual(relay_status["review_target_commit"], target)
        self.assertEqual(relay_status["expected_commit"], target)
        self.assertEqual(relay_status["relay_stage"], "stage2f1_branch_governance_manual_only")
        self.assertTrue(relay_status["chatgpt_computer_use_auto_review_deprecated"])

    def test_human_readable_artifacts_include_review_target(self) -> None:
        target = str(self.review_target_commit)
        for path in TEXT_TARGET_PATHS:
            content = read_text(path)
            self.assertIn("review_target_commit", content, path)
            self.assertIn(target, content, path)

    def test_review_status_md_includes_review_target(self) -> None:
        target = str(self.review_target_commit)
        status = read_text("reports/review_requests/relay_status.md")
        self.assertIn("Expected commit", status)
        self.assertIn(target, status)

    def test_relay_status_json_binds_same_review_target(self) -> None:
        target = str(self.review_target_commit)
        relay_status = read_json(RELAY_STATUS_JSON)
        self.assertEqual(relay_status["review_target_commit"], target)
        self.assertEqual(relay_status["expected_commit"], target)
        self.assertFalse(relay_status["sent_to_chatgpt"])
        self.assertFalse(relay_status["computer_use_executed"])

    def test_review_target_does_not_point_to_old_stage(self) -> None:
        target = str(self.review_target_commit)
        subject = git("show", "-s", "--format=%s", target)
        self.assertEqual(subject.returncode, 0, msg=subject.stderr)
        self.assertNotIn("stage2a", subject.stdout.lower())

    def test_previous_stage_commit_is_absent_from_review_artifacts(self) -> None:
        paths = JSON_TARGET_PATHS + TEXT_TARGET_PATHS + [RELAY_STATUS_JSON]
        for path in paths:
            content = read_text(path)
            for old_commit in PREVIOUS_STAGE_COMMITS:
                self.assertNotIn(old_commit, content, path)

    def test_handoff_commit_consistency_script_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/safety/check_handoff_commit_consistency.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["findings"])


if __name__ == "__main__":
    unittest.main()
