import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(path: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, path, "--root", str(ROOT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class SafetyChecksTest(unittest.TestCase):
    def assert_script_passes(self, script_path: str) -> dict:
        result = run_script(script_path)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"{script_path} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        return json.loads(result.stdout)

    def test_forbidden_surface_scan_passes(self) -> None:
        payload = self.assert_script_passes("scripts/safety/check_forbidden_surfaces.py")
        self.assertEqual(payload["status"], "pass")

    def test_secret_leak_scan_passes(self) -> None:
        payload = self.assert_script_passes("scripts/safety/check_secret_leaks.py")
        self.assertEqual(payload["status"], "pass")

    def test_universe_only_scan_passes(self) -> None:
        payload = self.assert_script_passes("scripts/safety/check_universe_only.py")
        self.assertEqual(payload["status"], "pass")

    def test_report_template_keeps_manual_trading_disclaimer(self) -> None:
        template = ROOT / "reports" / "trade_ticket_template.md"
        self.assertTrue(template.exists(), "reports/trade_ticket_template.md is required")
        text = template.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", text)


if __name__ == "__main__":
    unittest.main()

