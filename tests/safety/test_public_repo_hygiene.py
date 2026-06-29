import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class PublicRepoHygieneTest(unittest.TestCase):
    def run_script(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "scripts/safety/check_public_repo_hygiene.py",
                "--root",
                str(root),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_public_repo_hygiene_passes(self) -> None:
        result = self.run_script(ROOT)
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")

    def test_public_repo_hygiene_detects_private_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.md").write_text(
                "local path: /" + "Users" + "/example/.tool\npid: 12345\n",
                encoding="utf-8",
            )
            result = self.run_script(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        reasons = {finding["reason"] for finding in payload["findings"]}
        self.assertIn("absolute user path", reasons)
        self.assertIn("real pid line", reasons)

    def test_public_repo_hygiene_detects_live_preflight_config_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report_dir = root / "reports" / "live_preflight"
            report_dir.mkdir(parents=True)
            (report_dir / "stage2d1_live_preflight_report.json").write_text(
                '{"env_key_names": ["KIMI_API_KEY"], "provider_filter": true}\n',
                encoding="utf-8",
            )
            result = self.run_script(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        reasons = {finding["reason"] for finding in payload["findings"]}
        self.assertIn("public live preflight config fingerprint", reasons)

    def test_public_repo_hygiene_detects_credentialed_urls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            url = "https://user:" + "example-secret" + "@example.com/repo.git"
            (root / "remote.txt").write_text(f"origin={url}\n", encoding="utf-8")
            result = self.run_script(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        reasons = {finding["reason"] for finding in payload["findings"]}
        self.assertIn("credentialed url", reasons)

    def test_public_repo_hygiene_detects_committed_local_private_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            private_dir = root / "local_private"
            private_dir.mkdir()
            (private_dir / "README.md").write_text("safe placeholder\n", encoding="utf-8")
            (private_dir / ".gitkeep").write_text("", encoding="utf-8")
            (private_dir / "runtime_detail.json").write_text('{"private": true}\n', encoding="utf-8")
            result = self.run_script(root)
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn(
            {
                "file": "local_private/runtime_detail.json",
                "reason": "local private detail file",
            },
            payload["findings"],
        )


if __name__ == "__main__":
    unittest.main()
