import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPECTED_AGENTS = {
    "market_data_agent",
    "etf_research_agent",
    "etf_strategy_agent",
    "backtest_agent",
    "risk_agent",
    "trade_ticket_agent",
    "portfolio_journal_agent",
    "report_agent",
}
FORBIDDEN_AGENTS = {
    "_".join(("execution", "agent")),
    "_".join(("order", "agent")),
    "_".join(("broker", "agent")),
    "_".join(("auto", "trader")),
    "_".join(("live", "trader")),
}


class OpenClawAgentsSafetyTest(unittest.TestCase):
    def test_openclaw_agent_draft_exists_and_has_expected_research_roles(self) -> None:
        path = ROOT / "configs" / "openclaw" / "openclaw_agents_draft.json"
        self.assertTrue(path.exists())
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["stage"], "Stage 2B repo-only draft")
        self.assertFalse(payload["apply_to_real_openclaw"])
        self.assertEqual({agent["agent_id"] for agent in payload["agents"]}, EXPECTED_AGENTS)

    def test_openclaw_agent_draft_has_no_forbidden_agents_or_write_access(self) -> None:
        path = ROOT / "configs" / "openclaw" / "openclaw_agents_draft.json"
        text = path.read_text(encoding="utf-8").lower()
        for forbidden in FORBIDDEN_AGENTS:
            self.assertNotIn(forbidden, text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        for agent in payload["agents"]:
            self.assertEqual(agent["broker_access"], "write_forbidden")
            self.assertEqual(agent["order_placement"], "forbidden")
            self.assertEqual(agent["allowed_outputs"], payload["allowed_outputs"])

    def test_openclaw_readme_keeps_repo_only_boundary(self) -> None:
        text = (ROOT / "configs" / "openclaw" / "README.md").read_text(encoding="utf-8")
        self.assertIn("repo-only", text)
        self.assertIn("不得应用到真实 ~/.openclaw", text)
        self.assertIn("最终交易由用户手动决定", text)


if __name__ == "__main__":
    unittest.main()
