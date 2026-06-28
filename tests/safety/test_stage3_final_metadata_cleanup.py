import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAJOR_JSON = "reports/major_reviews/stage3/latest.json"
MAJOR_MD = "reports/major_reviews/stage3/latest.md"
REVIEW_TARGET_ROLE = "stage3_major_package_review_target"
BRANCH_HEAD_ROLE = "latest_stage3_branch_head_including_finalization_fixes"
CONCLUSION_SCOPE = "sample_data_pipeline_validation_only"


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


class Stage3FinalMetadataCleanupTest(unittest.TestCase):
    def test_review_target_and_latest_branch_head_have_distinct_roles(self) -> None:
        major = read_json(MAJOR_JSON)
        review_target = major["review_target_commit"]
        latest_branch_head = major["latest_branch_head"]
        current_branch_head = major["current_branch_head"]

        self.assertEqual(major["review_target_commit_role"], REVIEW_TARGET_ROLE)
        self.assertEqual(major["latest_branch_head_role"], BRANCH_HEAD_ROLE)
        self.assertEqual(major["current_branch_head_role"], BRANCH_HEAD_ROLE)
        self.assertEqual(current_branch_head, latest_branch_head)
        self.assertNotEqual(review_target, latest_branch_head)

        for commit in (review_target, latest_branch_head, current_branch_head):
            result = git("cat-file", "-e", f"{commit}^{{commit}}")
            self.assertEqual(result.returncode, 0, commit)

        ancestor = git("merge-base", "--is-ancestor", review_target, latest_branch_head)
        self.assertEqual(ancestor.returncode, 0, "review target must be an ancestor of latest branch head")

    def test_human_readable_metadata_explains_commit_roles(self) -> None:
        text = read_text(MAJOR_MD)
        self.assertIn("review_target_commit", text)
        self.assertIn("latest_branch_head", text)
        self.assertIn("current_branch_head", text)
        self.assertIn("Stage 3 major package audit target", text)
        self.assertIn("includes finalization fixes", text)

    def test_stage3_conclusion_is_sample_pipeline_validation_only(self) -> None:
        payload = read_json(MAJOR_JSON)
        self.assertEqual(payload["stage3_conclusion_scope"], CONCLUSION_SCOPE)
        self.assertTrue(payload["sample_data_pipeline_validation_only"])
        self.assertFalse(payload["formal_investment_evidence"])
        self.assertTrue(payload["data_boundary"]["sample_data_only"])
        self.assertFalse(payload["data_boundary"]["real_data_used"])
        self.assertTrue(payload["data_boundary"]["not_investment_basis"])

        text = read_text(MAJOR_MD)
        self.assertIn("sample-data pipeline validation only", text)
        self.assertIn("not formal investment evidence", text)
        self.assertIn("not investment basis", text)

    def test_latest_handoff_records_stage31_wp1_real_data_boundary(self) -> None:
        handoff = read_json("reports/codex_handoff/latest.json")
        self.assertEqual(
            handoff["stage"],
            "Stage 3.1 WP1 real data ingestion and cache completed_internal_review",
        )
        self.assertTrue(handoff["data_boundary"]["real_data_used"])
        self.assertFalse(handoff["data_boundary"]["sample_data_only"])
        self.assertEqual(handoff["data_boundary"]["source"], "yahoo_chart_public")


if __name__ == "__main__":
    unittest.main()
