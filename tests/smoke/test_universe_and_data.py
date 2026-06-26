import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class UniverseAndDataSmokeTest(unittest.TestCase):
    def run_cmd(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_universe_is_readable_and_allowed_entries_are_plain_etfs(self) -> None:
        result = self.run_cmd(["scripts/data/validate_universe.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertGreaterEqual(payload["allowed_count"], 8)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["disallowed_leveraged_or_inverse"], 0)

    def test_data_pipeline_uses_universe_and_builds_price_panel(self) -> None:
        download = self.run_cmd(
            [
                "scripts/data/download_prices.py",
                "--source",
                "sample",
                "--start",
                "2024-01-02",
                "--end",
                "2024-01-08",
            ]
        )
        self.assertEqual(download.returncode, 0, msg=download.stdout + download.stderr)

        build = self.run_cmd(["scripts/data/build_price_panel.py"])
        self.assertEqual(build.returncode, 0, msg=build.stdout + build.stderr)

        panel = ROOT / "data" / "processed" / "price_panel.csv"
        metadata = ROOT / "data" / "processed" / "price_panel_metadata.json"
        self.assertTrue(panel.exists())
        self.assertTrue(metadata.exists())

        payload = json.loads(metadata.read_text(encoding="utf-8"))
        self.assertEqual(payload["universe_file"], "configs/universe/etf_universe.yaml")
        self.assertEqual(payload["source"], "sample")
        self.assertTrue(payload["symbols"])
        self.assertFalse(payload["unknown_symbols"])

    def test_data_pipeline_rejects_symbol_outside_universe(self) -> None:
        result = self.run_cmd(
            [
                "scripts/data/download_prices.py",
                "--source",
                "sample",
                "--symbols",
                "AAPL",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not allowed by universe", result.stderr)

    def test_smoke_report_is_generated(self) -> None:
        result = self.run_cmd(["scripts/reports/write_stage2a_smoke_report.py"])
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        md_path = ROOT / "reports" / "stage2a_smoke_report.md"
        json_path = ROOT / "reports" / "stage2a_smoke_report.json"
        self.assertTrue(md_path.exists())
        self.assertTrue(json_path.exists())

        md_text = md_path.read_text(encoding="utf-8")
        self.assertIn("Final trading is manually decided by the user", md_text)

        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["stage"], "2A")
        self.assertEqual(payload["scope"], "repo-only")


if __name__ == "__main__":
    unittest.main()

