import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


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
        self.assertEqual(self.handoff["stage"], "Stage 2A.6 completed")
        self.assertEqual(self.review["stage"], "Stage 2A.6 completed")
        self.assertTrue(self.review_target_commit)
        self.assertEqual(self.review_target_commit, self.review.get("review_target_commit"))
        self.assertIn("handoff_generated_from_head", self.handoff)
        self.assertIn("commit_binding_note", self.handoff)
        self.assertIn("review_target_commit is the commit to review", self.handoff["commit_binding_note"])
        self.assertIsNone(self.handoff.get("handoff_commit"))

    def test_review_target_commit_is_valid_stage2a6_commit(self) -> None:
        target = str(self.review_target_commit)
        result = git("cat-file", "-e", f"{target}^{{commit}}")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        subject = git("show", "-s", "--format=%s", target)
        self.assertEqual(subject.returncode, 0, msg=subject.stderr)
        self.assertIn("stage2a.6", subject.stdout.lower())
        self.assertNotIn("stage2a.5", subject.stdout.lower())

    def test_prompts_and_relay_status_bind_same_review_target(self) -> None:
        target = str(self.review_target_commit)
        prompt = read_text("reports/review_requests/chatgpt_review_prompt.md")
        fallback = read_text("reports/review_requests/manual_fallback_prompt.md")
        relay_status = read_json("reports/review_requests/relay_status.json")

        self.assertIn(target, prompt)
        self.assertIn(target, fallback)
        self.assertEqual(relay_status["expected_commit"], target)

    def test_review_target_does_not_point_to_stage2a5(self) -> None:
        target = str(self.review_target_commit)
        subject = git("show", "-s", "--format=%s", target)
        self.assertEqual(subject.returncode, 0, msg=subject.stderr)
        self.assertNotIn("stage2a.5", subject.stdout.lower())


if __name__ == "__main__":
    unittest.main()
