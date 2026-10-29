"""Das Nachweiswerkzeug darf Rohlogs nicht vernichten oder Fehler grün melden."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools import run_gui_demo

ROOT = Path(__file__).resolve().parents[2]


class DemoEvidenceTests(unittest.TestCase):
    def test_existing_evidence_directory_is_refused_without_modifying_any_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "old_evidence"
            output.mkdir()
            originals = {"server.txt": "Originaler Nachweis\n", "result.json": '{"result":"PASS"}\n'}
            for name, content in originals.items():
                (output / name).write_text(content)
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/run_gui_demo.py"), "--output", str(output)],
                capture_output=True, text=True, timeout=10,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual({p.name: p.read_text() for p in output.iterdir()}, originals)
            self.assertIn("existiert bereits", result.stderr)

    def save_report(self, log):
        self.assertTrue(callable(getattr(run_gui_demo, "save_evidence", None)),
                        "Zentrale, fehlerkorrekte Nachweisspeicherung fehlt")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        output = Path(directory.name)
        (output / "server.txt").write_text(log)
        report = {"checks": [], "result": "FAIL"}
        run_gui_demo.save_evidence(output, report, [], completed=True)
        return json.loads((output / "result.json").read_text())

    def test_private_payload_in_log_is_saved_as_failure_even_after_completed_game(self):
        report = self.save_report('  -> [A] {"ownShips": [{"type": "Carrier"}]}\n')
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("Serverlog", report["error"])

    def test_clean_completed_game_is_saved_as_pass(self):
        report = self.save_report("  -> [A] type=state\n")
        self.assertEqual(report["result"], "PASS")


if __name__ == "__main__":
    unittest.main()
