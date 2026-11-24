"""Das Nachweiswerkzeug darf Rohlogs nicht vernichten oder Fehler grün melden."""
import json
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools import run_gui_demo

ROOT = Path(__file__).resolve().parents[2]


class DemoEvidenceTests(unittest.TestCase):
    def test_localhost_profile_starts_real_entry_with_nonzero_port(self):
        command = run_gui_demo.server_command(
            "localhost", ROOT, sys.executable, 51234, Path("/tmp/messages.jsonl"))
        self.assertEqual(command, [sys.executable, "-u", str(ROOT / "varianten/localhost/start.py"),
                                   "server", "--port", "51234"])
        self.assertNotIn("--log-file", command)
        with self.assertRaises(ValueError):
            run_gui_demo.server_command("localhost", ROOT, sys.executable, 0, Path("/tmp/messages.jsonl"))
        direct = run_gui_demo.server_command(None, ROOT, sys.executable, 0, Path("/tmp/messages.jsonl"))
        self.assertIn(str(ROOT / "src/server.py"), direct)
        self.assertIn("--log-file", direct)

    @unittest.skipUnless(os.name == "posix", "Prozessgruppen-Signale nur auf macOS/Linux")
    def test_grouped_server_cleanup_reaps_started_process(self):
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                                   start_new_session=True)
        def cleanup():
            if process.poll() is None:
                process.kill()
            process.wait(timeout=3)
        self.addCleanup(cleanup)
        run_gui_demo.stop_server_process(process, grouped=True)
        self.assertIsNotNone(process.poll())

    def test_screenshot_validation_requires_both_game_windows(self):
        class Pixels:
            def __init__(self, values):
                self.values = values

            def get(self, x, y):
                return self.values[(x, y)]

        left, right = 10, 804
        samples = {}
        for origin in (left, right):
            samples[origin + 500, 100] = (20, 31, 44)
            samples[origin + 100, 170] = (35, 56, 74)
            samples[origin + 500, 250] = (27, 43, 61)
        self.assertTrue(run_gui_demo.game_windows_visible(Pixels(samples), left, right))
        samples[right + 100, 170] = (19, 19, 20)  # Discord statt Bobs Statuszeile
        self.assertFalse(run_gui_demo.game_windows_visible(Pixels(samples), left, right))

    def test_screenshot_validation_scales_retina_pixels(self):
        class Pixels:
            def get(self, x, y):
                # Retina: Titelleiste bei Punkt-y 50 grau, Fensterinhalt erst in Pixeln *2 blau.
                return (40, 40, 40) if y < 120 else (27, 43, 61)

        self.assertFalse(run_gui_demo.game_windows_visible(Pixels(), 10, 10))
        self.assertTrue(run_gui_demo.game_windows_visible(Pixels(), 10, 10, scale=2))

    def test_pair_layout_places_windows_together_and_crops_to_them(self):
        left, right, region = run_gui_demo.window_pair_layout(784, 899)
        self.assertEqual(right - left, 794)
        x, y, width, height = map(int, region.split(","))
        self.assertLessEqual(x, left)
        self.assertGreaterEqual(x + width, right + 784)
        self.assertLess(width, 1920)
        self.assertGreaterEqual(height, 899)

    def test_final_screenshot_option_is_available_for_finished_game(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/run_gui_demo.py"), "--help"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--final-screenshot", result.stdout)
        self.assertIn("--spectator", result.stdout)

    def spectator_messages(self):
        state = {"type": "state", "phase": "shooting", "turn": "B", "ownShips": [],
                 "shotsAtOpponent": {"B6": "hit"}, "shotsAtSelf": {}, "winner": None, "score": []}
        messages = []
        for step in range(3):
            if step == 1:
                state.update(turn="A", shotsAtSelf={"J10": "miss"})
            elif step == 2:
                state.update(phase="waiting", turn=None, shotsAtOpponent={}, shotsAtSelf={})
            for name in ("Alice", "Bob", "Zuschauer"):
                view = deepcopy(state)
                if name == "Bob":
                    view["shotsAtSelf"], view["shotsAtOpponent"] = view["shotsAtOpponent"], view["shotsAtSelf"]
                messages.append({"recipient": name, "message": view})
        return messages

    def test_spectator_update_audit_checks_every_public_state_and_reset(self):
        messages = self.spectator_messages()
        report = {"checks": []}
        run_gui_demo.verify_spectator_updates(messages, report)
        self.assertEqual(report["spectator_states_compared"], 3)
        for index, field, value in ((5, "shotsAtSelf", {}), (4, "turn", "B"),
                                    (8, "phase", "finished"), (2, "ownShips", [{"cells": ["A1"]}])):
            with self.subTest(index=index, field=field):
                broken = deepcopy(messages)
                broken[index]["message"][field] = value
                with self.assertRaises(AssertionError):
                    run_gui_demo.verify_spectator_updates(broken, {"checks": []})
        with self.assertRaises(AssertionError):
            run_gui_demo.verify_spectator_updates(messages[:5] + messages[6:], {"checks": []})

    def test_spectator_audit_follows_swapped_slots_after_rematch(self):
        messages = self.spectator_messages()
        swapped = {"type": "state", "phase": "shooting", "turn": "B", "ownShips": [],
                   "shotsAtOpponent": {"A1": "hit"}, "shotsAtSelf": {}, "winner": None, "score": []}
        messages += [{"recipient": "Alice", "message": {"type": "welcome", "slot": "B"}},
                     {"recipient": "Bob", "message": {"type": "welcome", "slot": "A"}}]
        for name in ("Alice", "Bob", "Zuschauer"):
            view = deepcopy(swapped)
            if name == "Alice":
                view["shotsAtSelf"], view["shotsAtOpponent"] = view["shotsAtOpponent"], view["shotsAtSelf"]
            messages.append({"recipient": name, "message": view})
        report = {"checks": []}
        run_gui_demo.verify_spectator_updates(messages, report)
        self.assertEqual(report["spectator_states_compared"], 4)

    def test_spectator_fleet_is_rejected_even_when_other_fields_are_valid(self):
        messages = self.spectator_messages()
        messages[2]["message"]["ownShips"] = [{"cells": ["A1"]}]
        with self.assertRaises(AssertionError):
            run_gui_demo.verify_private_states(messages, {"checks": []})

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

    def save_report(self, log, **report_fields):
        self.assertTrue(callable(getattr(run_gui_demo, "save_evidence", None)),
                        "Zentrale, fehlerkorrekte Nachweisspeicherung fehlt")
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        output = Path(directory.name)
        (output / "server.txt").write_text(log)
        report = {"checks": [], "result": "FAIL", **report_fields}
        run_gui_demo.save_evidence(output, report, [], completed=True)
        return json.loads((output / "result.json").read_text())

    def test_private_payload_in_log_is_saved_as_failure_even_after_completed_game(self):
        report = self.save_report('  -> [A] {"ownShips": [{"type": "Carrier"}]}\n')
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("Serverlog", report["error"])

    def test_clean_completed_game_is_saved_as_pass(self):
        report = self.save_report("  -> [A] type=state\n")
        self.assertEqual(report["result"], "PASS")

    def test_requested_but_unavailable_final_image_makes_report_fail(self):
        report = self.save_report(
            "  -> [A] type=state\n",
            final_screenshot_unavailable="Bild enthaelt nicht beide sichtbaren Spielfenster",
        )
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("Bildnachweis", report["error"])
        self.assertIn("final_screenshot_unavailable", report)

    def test_missing_spectator_rejection_capture_makes_report_fail(self):
        report = self.save_report("type=state\n", spectator_screenshot_unavailable="Keine Aufnahme")
        self.assertEqual(report["result"], "FAIL")


if __name__ == "__main__":
    unittest.main()
