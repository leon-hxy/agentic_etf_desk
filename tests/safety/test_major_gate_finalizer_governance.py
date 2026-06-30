import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_STAGE = "Stage 3.1 major review package ready"
FINALIZATION_FIXES = ["Stage 3F", "Stage 3F.1"]
TARGET_JSON_PATHS = [
    "reports/major_reviews/stage3/latest.json",
    "reports/review_requests/chatgpt_review_prompt.json",
    "reports/review_requests/notification_preview.json",
    "reports/review_requests/relay_status.json",
]
TARGET_MD_PATHS = [
    "reports/major_reviews/stage3/latest.md",
    "reports/review_requests/chatgpt_review_prompt.md",
    "reports/review_requests/manual_fallback_prompt.md",
    "reports/review_requests/notification_preview.md",
    "reports/review_requests/relay_status.md",
]


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class MajorGateFinalizerGovernanceTest(unittest.TestCase):
    def test_runner_treats_finalization_fixes_as_internal_process(self) -> None:
        state = read_json("ops/runners/stage3_runner_state.json")

        self.assertEqual(state["status"], "major_stage_ready")
        self.assertIn(state["current_minor_stage"], (None, "Stage 3 completed"))
        self.assertIsNone(state["current_task"])
        self.assertEqual(state["completed_minor_stages"], ["Stage 3A", "Stage 3B", "Stage 3C", "Stage 3D"])
        self.assertEqual(state["major_package_status"], "major_package_generated")
        self.assertEqual(state["finalization_status"], "completed")
        self.assertEqual(state["finalization_fixes"], FINALIZATION_FIXES)
        self.assertEqual(state["finalization_review_route"], "codex_internal_review")
        self.assertFalse(state["chatgpt_review_for_finalization_fixes_allowed"])
        self.assertTrue(state["manual_chatgpt_review_ready"])
        self.assertTrue(state["feishu_notification_sent"])
        self.assertTrue(state["previous_notifications_superseded"])

    def test_major_package_is_the_only_chatgpt_review_target(self) -> None:
        major = read_json("reports/major_reviews/stage3/latest.json")
        handoff = read_json("reports/codex_handoff/latest.json")
        review_request = read_json("reports/review_requests/latest.json")
        prompt = read_json("reports/review_requests/chatgpt_review_prompt.json")

        self.assertEqual(major["stage"], "Stage 3 major review package")
        self.assertEqual(major["status"], "major_review_package_ready")
        if review_request["review_level"] == "final_program_review":
            self.assertEqual(review_request["review_target"], "v1.0 final review package")
            self.assertEqual(review_request["review_target_md"], "reports/program_reviews/final/latest.md")
            self.assertEqual(review_request["final_review_verdict"], "conditional_pass")
        else:
            self.assertIn(
                review_request["review_level"],
                {"major_stage", "scope_consolidation", "work_package_internal_review"},
            )
            self.assertIn(
                review_request["review_target"],
                {
                    "Stage 3 major review package",
                    "Stage 3.1 scope consolidation",
                    "Stage 3.1 WP1 real data ingestion and cache",
                    "Stage 3.1 WP2 real data quality and monthly panel",
                    "Stage 3.1 major review package",
                },
            )
            self.assertIn(
                review_request["chatgpt_review_targets"],
                [
                    ["reports/major_reviews/stage3/latest.md"],
                    ["reports/major_reviews/stage3_1/latest.md", "reports/major_reviews/stage3_1/latest.json"],
                    [],
                ],
            )
        self.assertTrue(review_request.get("include_finalization_fixes_as_context", True))
        self.assertFalse(review_request.get("request_chatgpt_review_for_finalization_fixes", False))
        self.assertEqual(prompt["review_target"], "Stage 3 major review package")
        self.assertFalse(prompt["request_chatgpt_review_for_finalization_fixes"])
        self.assertIn(handoff["stage"], {EXPECTED_STAGE, "v1.0 final review completed / ready for merge"})
        if handoff["stage"] == EXPECTED_STAGE:
            self.assertEqual(
                handoff["next_recommended_stage"],
                "Manual ChatGPT major-stage review by user",
            )
            self.assertTrue(handoff["finalization_fixes_internal_reviewed"])
        else:
            self.assertEqual(handoff["next_safe_action"], "merge_to_main_after_tests")
            self.assertTrue(handoff["evidence_context"]["stage3_1"]["finalization_fixes_internal_reviewed"])

        for payload in (major, handoff, review_request, prompt):
            self.assertNotEqual(payload.get("stage"), "Stage 3F major_gate_feishu_notification_sent")
            self.assertNotEqual(payload.get("stage"), "Stage 3F.1 review_target_commit_consistency_fixed")

    def test_notification_is_allowed_only_after_finalization_completed(self) -> None:
        preview = read_json("reports/review_requests/notification_preview.json")
        relay = read_json("reports/review_requests/relay_status.json")

        self.assertEqual(preview["finalization_status"], "completed")
        self.assertTrue(preview["notification_after_finalization"])
        self.assertTrue(preview["previous_notification_superseded"])
        self.assertTrue(preview["replacement_notification_preview_generated"])
        self.assertFalse(preview["replacement_notification_sent"])
        self.assertEqual(relay["relay_stage"], "stage3_major_gate_finalized_manual_review_ready")
        self.assertEqual(relay["finalization_status"], "completed")
        self.assertEqual(relay["review_target_consistency_status"], "passed")
        self.assertFalse(relay["request_chatgpt_review_for_finalization_fixes"])

    def test_review_target_commit_is_consistent_across_review_artifacts(self) -> None:
        target = read_json("reports/major_reviews/stage3/latest.json")["review_target_commit"]
        self.assertTrue(target)

        for path in TARGET_JSON_PATHS:
            payload = read_json(path)
            value = payload.get("review_target_commit") or payload.get("expected_commit")
            self.assertEqual(value, target, path)

        for path in TARGET_MD_PATHS:
            text = read_text(path)
            self.assertIn(target, text, path)

    def test_finalization_internal_review_records_reviewer_passes_and_safety(self) -> None:
        payload = read_json("reports/internal_reviews/stage3/stage3_major_gate_finalization.json")

        self.assertEqual(payload["status"], "completed_internal_review")
        self.assertEqual(payload["finalization_fixes"], FINALIZATION_FIXES)
        self.assertFalse(payload["chatgpt_review_requested_for_finalization_fixes"])
        self.assertEqual(payload["manual_chatgpt_review_scope"], "Stage 3 major review package only")
        self.assertFalse(payload["requires_user_attention"])

        for reviewer in ("security_reviewer", "domain_reviewer", "integration_reviewer", "test_reviewer"):
            self.assertEqual(payload[reviewer]["result"], "pass", reviewer)

        safety = payload["safety_flags"]
        self.assertFalse(safety["computer_use_executed"])
        self.assertFalse(safety["secrets_touched"])
        self.assertFalse(safety["auto_trading_surface"])
        self.assertFalse(safety["broker_surface"])


if __name__ == "__main__":
    unittest.main()
