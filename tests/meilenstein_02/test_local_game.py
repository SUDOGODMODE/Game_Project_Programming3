"""Netzfreie Zweipersonenpartie aus Projektphase M2."""
from pathlib import Path
import os
import subprocess
import sys
import unittest
from tests.fixtures import FLEET_CELLS as TARGETS, MISSES
if os.name == "posix":
    import pty
SRC = Path(__file__).resolve().parents[2] / "src"
PLACEMENTS = ["A1 h", "A2 h", "A3 h", "A4 h", "A5 h"]


class TestLocalGameCLI(unittest.TestCase):
    def run_game(self, commands):
        completed = subprocess.run(
            [sys.executable, str(SRC / "local_game.py")],
            input="\n".join(commands) + ("\n" if commands else ""),
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return completed.stdout

    def test_complete_match_retries_bad_input_without_consuming_a_turn(self):
        commands = ["ungueltig", *PLACEMENTS, *PLACEMENTS, "K1"]
        for index, target in enumerate(TARGETS):
            if index == 1:
                commands.append("A1")  # Derselbe Schuss darf keinen Zug verbrauchen.
            commands.append(target)
            if index < len(MISSES):
                commands.append(MISSES[index])
        output = self.run_game(commands)
        self.assertEqual(output.count(" -> "), 33)
        self.assertEqual(output.count("Fehler:"), 3)
        self.assertIn("Spieler A: A1 -> Treffer", output)
        self.assertIn("Spieler B: J1 -> Wasser", output)
        self.assertIn("Spieler A: B5 -> Versenkt (Destroyer)", output)
        self.assertEqual(output.count("Spieler A gewinnt!"), 1)
        self.assertNotIn("abgebrochen", output)

    def test_invalid_fleet_is_retried_before_other_player_places(self):
        output = self.run_game(["J1 h", *PLACEMENTS[1:], *PLACEMENTS, *PLACEMENTS, "q"])
        self.assertIn("Fehler:", output)
        self.assertEqual(output.count("Spieler A platziert seine Flotte."), 2)
        self.assertEqual(output.count("Spieler B platziert seine Flotte."), 1)
        self.assertIn("Spiel abgebrochen.", output)
        self.assertNotIn("gewinnt", output)

    def test_quit_and_eof_abort_without_announcing_a_winner(self):
        for commands in (["q"], []):
            with self.subTest(commands=commands):
                output = self.run_game(commands)
                self.assertIn("Spiel abgebrochen.", output)
                self.assertNotIn("gewinnt", output)

    @unittest.skipUnless(os.name == "posix", "Terminaltest benoetigt POSIX")
    def test_terminal_announces_winner_without_another_handover(self):
        commands = ["", *PLACEMENTS, "", *PLACEMENTS]
        shots = []
        for index, target in enumerate(TARGETS):
            shots.append(target)
            if index < len(MISSES):
                shots.append(MISSES[index])
        for index, shot in enumerate(shots):
            commands.extend(["", shot])  # Tastatur an den aktiven Spieler.
            if index < len(shots) - 1:
                commands.append("")  # Ergebnis lesen, bevor die Anzeige geloescht wird.
        master, terminal = pty.openpty()
        try:
            game = subprocess.Popen(
                [sys.executable, str(SRC / "local_game.py")],
                stdin=terminal, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            os.write(master, ("\n".join(commands) + "\n").encode())
            try:
                output, error = game.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                game.kill()
                output, error = game.communicate()
                self.assertIn("Spieler A: B5 -> Versenkt (Destroyer)", output)
                self.fail("Die fertige Partie wartet noch auf eine Tastaturuebergabe")
            self.assertEqual(game.returncode, 0, error)
            self.assertIn("Spieler A gewinnt!", output)
        finally:
            os.close(master)
            os.close(terminal)

if __name__ == "__main__":
    unittest.main()
