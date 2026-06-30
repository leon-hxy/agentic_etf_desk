import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STAGE = "Stage 3.1 major review package ready"
STATUS = "stage3_1_major_review_package_ready"
BRANCH = "stage/stage3.1-real-etf-data"
WORK_PACKAGES = [
    "WP1 real data ingestion and cache",
    "WP2 real data quality and monthly panel",
    "WP3 formal backtest and evidence package",
]
FORBIDDEN_VISIBLE_STAGES = [
    "Stage 3.1A",
    "Stage 3.1B",
    "Stage 3.1C",
    "Stage 3.1D",
    "Stage 3.1E",
    "Stage 3.1F",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read(path))


class Stage31ScopeConsolidationTest(unittest.TestCase):
    def test_stage31_manifest_defines_one_major_stage_and_three_work_packages(self) -> None:
        manifest = read("ops/stages/stage3_1.yaml")

        self.assertIn("stage: Stage 3.1 Real ETF Historical Data MVP", manifest)
        self.assertIn(f"status: {STATUS}", manifest)
        self.assertIn(f"construction_branch: {BRANCH}", manifest)
        self.assertIn("stage_type: major_stage", manifest)
        self.assertIn("user_visible_substages_allowed: false", manifest)
        self.assertIn("business_code_started: true", manifest)
        self.assertIn("scope_consolidation_only: false", manifest)
        self.assertIn("status: completed_internal_review", manifest)
        self.assertNotIn("status: ready", manifest)

        for work_package in WORK_PACKAGES:
            self.assertIn(work_package, manifest)

        for visible_stage in FORBIDDEN_VISIBLE_STAGES:
            self.assertIn(visible_stage, manifest)

        self.assertEqual(manifest.count("label: WP"), 3)
        self.assertEqual(manifest.count("review: codex_internal_review"), 3)
        self.assertEqual(manifest.count("chatgpt_review_requested: false"), 3)
        self.assertEqual(manifest.count("user_notification: false"), 3)
        self.assertIn("trigger: only after WP3 completes", manifest)
        self.assertIn("reports/major_reviews/stage3_1/latest.md", manifest)
        self.assertIn("reports/major_reviews/stage3_1/latest.json", manifest)

    def test_stage31_runner_state_blocks_user_visible_substages_and_wp_notifications(self) -> None:
        state = read_json("ops/runners/stage3_1_runner_state.json")

        self.assertEqual(state["stage"], "Stage 3.1 Real ETF Historical Data MVP")
        self.assertEqual(state["status"], "wp3_completed_major_review_package_ready")
        self.assertEqual(state["branch"], BRANCH)
        self.assertFalse(state["user_visible_substages_allowed"])
        self.assertTrue(state["business_code_started"])
        self.assertEqual(state["current_work_package"], "Stage 3.1 major review package ready")
        self.assertEqual(
            state["completed_work_packages"],
            [
                "wp1_real_data_ingestion_and_cache",
                "wp2_real_data_quality_and_monthly_panel",
                "wp3_formal_backtest_and_evidence_package",
            ],
        )
        self.assertEqual(len(state["work_packages"]), 3)

        for package in state["work_packages"]:
            self.assertEqual(package["review_route"], "codex_internal_review")
            self.assertFalse(package["chatgpt_review_requested"])
            self.assertFalse(package["user_notification"])

        self.assertEqual(state["major_review_route"], "manual_chatgpt_review")
        self.assertTrue(state["major_review_package_required_after_wp3"])
        self.assertTrue(state["notify_user_only_after_wp3_major_package"])
        self.assertFalse(state["notify_user_before_wp3_major_package"])
        self.assertFalse(state["chatgpt_review_for_work_packages_allowed"])
        self.assertFalse(state["computer_use_allowed"])
        self.assertFalse(state["real_config_changes_allowed"])

    def test_latest_handoff_and_review_request_match_stage31_scope(self) -> None:
        loop_state = read_json("ops/state/loop_state.json")
        handoff = read_json("reports/codex_handoff/latest.json")
        review = read_json("reports/review_requests/latest.json")
        handoff_md = read("reports/codex_handoff/latest.md")
        review_md = read("reports/review_requests/latest.md")

        for payload in (loop_state, handoff, review):
            self.assertTrue(payload["stage3_1_scope_consolidated"])
            self.assertTrue(payload["stage3_1_wp1_completed_internal_review"])
            self.assertTrue(payload["stage3_1_wp2_completed_internal_review"])
            self.assertTrue(payload["stage3_1_wp3_completed_internal_review"])
            self.assertTrue(payload["stage3_1_major_review_package_ready"])
            self.assertTrue(payload["stage3_1_major_stage"])
            self.assertFalse(payload["stage3_1_user_visible_substages_allowed"])
            self.assertTrue(payload["stage3_1_business_code_started"])
            self.assertEqual(payload["stage3_1_branch"], BRANCH)
            self.assertEqual(payload["stage3_1_work_packages"], WORK_PACKAGES)
            self.assertEqual(payload["wp_review_route"], "codex_internal_review")
            self.assertFalse(payload["wp_chatgpt_review_requested"])
            self.assertFalse(payload["wp_user_notification"])
            self.assertFalse(payload["notify_user_before_wp3_major_package"])
            self.assertTrue(payload["notify_user_after_wp3_major_package"])
        self.assertEqual(handoff["stage"], "v1.0 final review completed / ready for merge")
        self.assertEqual(review["stage"], "v1.0 final review completed / ready for merge")
        self.assertEqual(review["review_level"], "final_program_review")
        self.assertIn("Stage 3.1 real ETF data", review["evidence_context"])

        for text in (handoff_md,):
            self.assertIn("Stage 3.1 is one major stage", text)
            self.assertIn("WP1 real data ingestion and cache", text)
            self.assertIn("WP2 real data quality and monthly panel", text)
            self.assertIn("WP3 formal backtest and evidence package", text)
            self.assertIn("Codex internal review only", text)
            self.assertIn("Only after WP3 completes", text)
            self.assertIn("Final trading is manually decided by the user", text)
        self.assertIn("Stage 3.1 real ETF data", review_md)
        self.assertIn("Final trading is manually decided by the user", review_md)

    def test_stage31_templates_exist_without_user_visible_substages(self) -> None:
        required_paths = [
            "configs/codex_automation/stage3_1_runner_prompt.md",
            "reports/internal_reviews/stage3_1/wp_internal_review_template.md",
            "reports/internal_reviews/stage3_1/wp_internal_review_template.json",
            "reports/major_reviews/stage3_1/template.md",
            "reports/major_reviews/stage3_1/template.json",
        ]
        for path in required_paths:
            self.assertTrue((ROOT / path).exists(), path)

        prompt = read("configs/codex_automation/stage3_1_runner_prompt.md")
        self.assertIn("Do not create user-visible Stage 3.1A", prompt)
        self.assertIn("Do not request ChatGPT review for WP1, WP2, or WP3", prompt)
        self.assertIn("Do not notify the user for WP1, WP2, or WP3", prompt)
        self.assertIn("Do not run Computer Use", prompt)
        self.assertIn("Do not connect brokers", prompt)
        self.assertIn("Do not place orders", prompt)

        template = read_json("reports/major_reviews/stage3_1/template.json")
        self.assertFalse(template["chatgpt_review_for_wp1_wp2_wp3"])
        self.assertFalse(template["user_notification_before_wp3_package"])


if __name__ == "__main__":
    unittest.main()
