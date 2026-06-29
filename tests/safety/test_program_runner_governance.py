import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "ops/program_runner/README.md",
    "ops/program_runner/roadmap.yaml",
    "ops/program_runner/program_runner_state.json",
    "ops/program_runner/program_runner.md",
    "ops/program_runner/approval_queue.json",
    "ops/program_runner/heartbeat_log.md",
    "ops/program_runner/blocked_reason.md",
    "configs/codex_automation/program_runner_heartbeat_prompt.md",
    "configs/codex_automation/program_runner_manual_trigger_prompt.md",
    "reports/program_reviews/README.md",
    "reports/program_reviews/final/README.md",
    "reports/internal_reviews/program/README.md",
    "ops/templates/program_internal_review_template.md",
    "ops/templates/program_internal_review_template.json",
]

MAJOR_STAGES = [
    "Stage 3.2",
    "Stage 4",
    "Stage 5",
    "Stage 6",
]

REVIEWERS = [
    "Security Reviewer",
    "Domain / Quant Reviewer",
    "Integration Reviewer",
    "Test / Reproducibility Reviewer",
    "Public Repo Hygiene Reviewer",
]

BROKER_ACCESS_ALLOWED_FIELD = "_".join(("broker", "write", "allowed"))
BROKER_ACCESS_SURFACE_FIELD = "_".join(("broker", "write", "surface"))

STATUSES = [
    "ready",
    "running",
    "work_package_in_progress",
    "internal_review_in_progress",
    "fixing_findings",
    "tests_running",
    "committed_and_pushed",
    "next_work_package_ready",
    "approval_required",
    "blocked",
    "final_review_ready",
    "completed",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def read_json(path: str) -> dict:
    return json.loads(read(path))


def parse_roadmap_stage_blocks(text: str) -> list[dict[str, object]]:
    stages: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    in_goals = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- id: stage_"):
            current = {"id": stripped.split(":", 1)[1].strip(), "goals": []}
            stages.append(current)
            in_goals = False
            continue
        if current is None:
            continue
        if stripped.startswith("name:"):
            current["name"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("title:"):
            current["title"] = stripped.split(":", 1)[1].strip().strip('"')
        elif stripped.startswith("user_visible_review_gate:"):
            current["user_visible_review_gate"] = stripped.split(":", 1)[1].strip()
        elif stripped == "goals:":
            in_goals = True
        elif in_goals and stripped.startswith("- "):
            goals = current["goals"]
            assert isinstance(goals, list)
            goals.append(stripped[2:].strip().strip('"'))
    return stages


class ProgramRunnerGovernanceTest(unittest.TestCase):
    def test_required_program_runner_files_exist(self) -> None:
        for path in REQUIRED_PATHS:
            self.assertTrue((ROOT / path).exists(), path)

    def test_roadmap_exposes_four_major_stages_and_no_user_visible_minor_gates(self) -> None:
        text = read("ops/program_runner/roadmap.yaml")

        self.assertIn("program: agentic_etf_desk", text)
        self.assertIn("mode: autonomous_until_final_review", text)
        self.assertIn("final_review_only: true", text)
        self.assertEqual(text.count("id: stage_"), 4)
        stages = parse_roadmap_stage_blocks(text)
        self.assertEqual([stage["name"] for stage in stages], MAJOR_STAGES)
        self.assertEqual(len(stages), 4)
        for stage in MAJOR_STAGES:
            self.assertIn(stage, text)
        for stage in stages:
            self.assertEqual(stage["user_visible_review_gate"], "false")
            self.assertTrue(stage["goals"])

        required_goal_fragments = [
            "second-source or alternate-source validation",
            "price discrepancy checks",
            "benchmark comparison preserved for every strategy",
            "strategy conclusion grading",
            "Feishu command routing for ETF research",
            "OpenClaw agents draft or safe integration plan",
            "trade tickets must pass risk_agent review before actionable suggestions",
            "manual holdings CSV import",
            "reject holdings or trades outside configs/universe/etf_universe.yaml",
            "adoption / rejection journal",
            "schedule dry-runs",
            "public repo hygiene",
            "final v1.0 review package",
        ]
        for fragment in required_goal_fragments:
            self.assertIn(fragment, text)

        self.assertIn("notify_user_only_on:", text)
        self.assertIn("- blocked", text)
        self.assertIn("- approval_required", text)
        self.assertIn("- final_review_ready", text)
        self.assertIn("chatgpt_review_policy: final_program_review_only", text)
        self.assertIn("minor_review_policy: codex_internal_review", text)
        self.assertIn("auto_trading_allowed: false", text)
        self.assertIn("trade_tickets_require_risk_agent_review: true", text)
        self.assertIn("every_strategy_requires_benchmark: true", text)
        self.assertIn("manual_imports_must_use_etf_universe_allowlist: true", text)
        self.assertIn("construction_branch: stage/v1-autonomous-completion", text)
        self.assertNotIn("Stage 3.2A", text)
        self.assertNotIn("Stage 4A", text)

    def test_runner_state_enforces_autonomous_final_review_only_mode(self) -> None:
        state = read_json("ops/program_runner/program_runner_state.json")
        blocked_reason = read("ops/program_runner/blocked_reason.md")

        expected_required = {
            "program": "agentic_etf_desk",
            "mode": "autonomous_until_final_review",
            "current_major_stage": "Stage 3.2",
            "current_work_package": None,
            "status": "blocked",
            "final_review_only": True,
            "notify_user_only_on": [
                "blocked",
                "approval_required",
                "final_review_ready",
            ],
            "chatgpt_review_policy": "final_program_review_only",
            "minor_review_policy": "codex_internal_review",
            "computer_use_allowed": False,
            "real_config_changes_allowed_without_approval": False,
            BROKER_ACCESS_ALLOWED_FIELD: False,
            "auto_trading_allowed": False,
            "final_review_package": "reports/program_reviews/final/latest.md",
        }
        for key, value in expected_required.items():
            self.assertEqual(state[key], value)
        self.assertEqual(state["stable_branch"], "main")
        self.assertEqual(state["construction_branch"], "stage/v1-autonomous-completion")
        self.assertEqual(
            state["stage3_1_prerequisite"]["description"],
            "Stage 3.1 must be merged into main before Stage 3.2 business work begins.",
        )
        self.assertTrue(state["stage3_1_prerequisite"]["verify_before_work_package"])
        self.assertTrue(state["git_push_allowed_after_public_repo_hygiene_checks"])
        self.assertEqual(state["final_review_package_json"], "reports/program_reviews/final/latest.json")
        self.assertIn("status: blocked", blocked_reason)
        self.assertIn("Stage 3.1 prerequisite is not satisfied", blocked_reason)

    def test_branching_policy_includes_autonomous_completion_branch(self) -> None:
        text = read("docs/branching_policy.md")

        self.assertIn("stage/v1-autonomous-completion", text)
        self.assertIn("After Stage 3.1 is merged into main", text)
        self.assertIn("Stage 3.2 through Stage 6 use final v1.0 program review only", text)
        self.assertIn("Do not request ChatGPT review for internal Program Runner work packages", text)
        self.assertIn("Stage 3E is historical Stage 3 governance", text)

    def test_program_runner_state_machine_and_work_package_contract(self) -> None:
        text = read("ops/program_runner/program_runner.md")

        for status in STATUSES:
            self.assertIn(status, text)
        for reviewer in REVIEWERS:
            self.assertIn(reviewer, text)

        required_steps = [
            "Read `ops/program_runner/roadmap.yaml`",
            "Read `AGENTS.md`, `docs/security_policy.md`, and `docs/branching_policy.md`",
            "Verify the current branch is `stage/v1-autonomous-completion`",
            "Verify Stage 3.1 is merged into `main`",
            "Implement the work package",
            "Spawn reviewer subagents",
            "risk_agent` review",
            "simulated separate reviewer passes",
            "Record `reviewer_mode`",
            "Generate internal review markdown and JSON",
            "Fix findings",
            "Run the full safety and smoke test suite",
            "Update `ops/program_runner/program_runner_state.json`",
            "Commit and push",
            "Continue to the next work package without user notification",
        ]
        for step in required_steps:
            self.assertIn(step, text)

        self.assertIn("Do not run Computer Use", text)
        self.assertIn("Do not modify real runtime configuration", text)
        self.assertIn("Git pushes to the configured repository remote are allowed", text)
        self.assertIn("Final trading is manually decided by the user", text)

    def test_approval_queue_defers_live_or_sensitive_actions(self) -> None:
        queue = read_json("ops/program_runner/approval_queue.json")

        self.assertEqual(queue["program"], "agentic_etf_desk")
        self.assertEqual(queue["status"], "empty")
        self.assertEqual(queue["items"], [])
        self.assertEqual(queue["default_action_if_not_approved"], "skip_or_defer")

        required_triggers = [
            "modify real hermes configuration",
            "modify real openclaw configuration",
            "modify real Feishu gateway",
            "restart a service",
            "install dependencies",
            "secret or API key required",
            "send to a real external service other than git push after public repo hygiene checks",
            "access non-public data source",
            "rewrite git history",
            "access broker account",
            "trade, order, or account-changing capability",
        ]
        self.assertEqual(queue["approval_required_for"], required_triggers)
        self.assertEqual(
            queue["safe_external_service_exceptions"],
            [
                "git push to the configured repository remote after public repo hygiene, secret, forbidden-surface, and relevant safety tests pass"
            ],
        )

        schema = queue["approval_item_schema"]
        for field in (
            "id",
            "status",
            "created_at",
            "work_package",
            "reason",
            "requested_action",
            "files_or_services_touched",
            "risks",
            "rollback_plan",
            "next_safe_action",
            "user_notification_message",
            "default_action_if_not_approved",
        ):
            self.assertIn(field, schema)
        self.assertEqual(schema["status"], "pending")
        self.assertEqual(schema["default_action_if_not_approved"], "skip_or_defer")

    def test_internal_review_templates_define_required_reviewer_sections(self) -> None:
        template = read_json("ops/templates/program_internal_review_template.json")
        markdown = read("ops/templates/program_internal_review_template.md")

        required_keys = [
            "major_stage",
            "work_package",
            "commit",
            "changed_files",
            "reviewer_mode",
            "security_reviewer",
            "domain_quant_reviewer",
            "integration_reviewer",
            "test_reproducibility_reviewer",
            "public_repo_hygiene_reviewer",
            "findings",
            "fixes_applied",
            "tests",
            "pass_fail",
            "requires_user_attention",
            "promote_to_next_work_package",
        ]
        self.assertEqual(list(template.keys()), required_keys)
        self.assertIn("Final trading is manually decided by the user", markdown)
        self.assertTrue(template["domain_quant_reviewer"]["risk_agent_review_required_for_trade_tickets"])
        self.assertFalse(
            template["domain_quant_reviewer"]["trade_tickets_actionable_without_risk_agent_review"]
        )
        for reviewer in REVIEWERS:
            self.assertIn(reviewer, markdown)

    def test_review_directories_and_final_package_contract_are_documented(self) -> None:
        root_readme = read("reports/program_reviews/README.md")
        final_readme = read("reports/program_reviews/final/README.md")
        internal_readme = read("reports/internal_reviews/program/README.md")

        self.assertIn("final v1.0 ChatGPT review", root_readme)
        self.assertIn("Do not request ChatGPT review for internal work packages", root_readme)
        self.assertIn("latest.md", final_readme)
        self.assertIn("latest.json", final_readme)
        for fragment in (
            "project goals",
            "completed stages",
            "strategy evidence conclusion",
            "research/backtest/scenario evidence, not formal investment proof",
            "data source notes",
            "backtest limitations",
            "security boundaries",
            "Hermes/Feishu status",
            "OpenClaw agent status",
            "ETF-only",
            "automatic trading surface",
            "secrets touched",
            "live configs modified",
            "all tests",
            "internal reviews summary",
            "long-term operating pilot",
            "not investment advice",
            "Final trading is manually decided by the user",
        ):
            self.assertIn(fragment, final_readme)
        self.assertIn("codex_internal_review", internal_readme)
        self.assertIn("reviewer_mode", internal_readme)
        self.assertIn("risk_agent review status", internal_readme)

    def test_automation_prompts_resume_without_computer_use_or_live_changes(self) -> None:
        heartbeat = read("configs/codex_automation/program_runner_heartbeat_prompt.md")
        manual = read("configs/codex_automation/program_runner_manual_trigger_prompt.md")

        for prompt in (heartbeat, manual):
            self.assertIn("Read `ops/program_runner/program_runner_state.json`", prompt)
            self.assertIn("Verify the current branch is `stage/v1-autonomous-completion`", prompt)
            self.assertIn("Verify Stage 3.1 is merged into `main`", prompt)
            self.assertIn("work_package_in_progress", prompt)
            self.assertIn("committed_and_pushed", prompt)
            self.assertIn("risk_agent", prompt)
            self.assertIn("Do not run Computer Use", prompt)
            self.assertIn("Do not modify real runtime configuration", prompt)
            self.assertIn("Do not connect broker write interfaces", prompt)
            self.assertIn("Do not place orders", prompt)
            self.assertIn("Final trading is manually decided by the user", prompt)

        self.assertIn("Use Codex App thread automation", heartbeat)
        self.assertIn("Every 10 to 30 minutes", heartbeat)
        self.assertIn("Complete at most one work package per wake", heartbeat)
        self.assertIn("If `status=final_review_ready`, stop", heartbeat)
        self.assertIn("update runner state, then commit and push", heartbeat)
        self.assertIn("commit and push", heartbeat)
        self.assertIn("Do not request ChatGPT review until final_review_ready", manual)

    def test_forbidden_surface_scanner_rejects_true_broker_access_allowed_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "safe.yaml").write_text(
                f"{BROKER_ACCESS_ALLOWED_FIELD}: false\n", encoding="utf-8"
            )
            unsafe = root / "unsafe.yaml"
            unsafe.write_text(f"{BROKER_ACCESS_ALLOWED_FIELD}: true\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "safety" / "check_forbidden_surfaces.py"),
                    "--root",
                    str(root),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["findings"][0]["file"], "unsafe.yaml")

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "safe.yaml").write_text(
                f"{BROKER_ACCESS_ALLOWED_FIELD}: false\n{BROKER_ACCESS_SURFACE_FIELD}:\n",
                encoding="utf-8",
            )
            safe_result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "safety" / "check_forbidden_surfaces.py"),
                    "--root",
                    str(root),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(safe_result.returncode, 0, safe_result.stdout)


if __name__ == "__main__":
    unittest.main()
