"""Lokale CLI-Tests fuer Echo und die netzfreie Konsolenpartie."""
from pathlib import Path
import os
import re
import selectors
import signal
import subprocess
import sys
import unittest

if os.name == "posix":
    import pty


SRC = Path(__file__).resolve().parent
PLACEMENTS = ["A1 h", "A2 h", "A3 h", "A4 h", "A5 h"]
TARGETS = [
    "A1", "B1", "C1", "D1", "E1", "A2", "B2", "C2", "D2",
    "A3", "B3", "C3", "A4", "B4", "C4", "A5", "B5",
]
MISSES = [
    "J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8",
    "J9", "J10", "I1", "I2", "I3", "I4", "I5", "I6",
]


class TestEchoCLI(unittest.TestCase):
    def test_server_answers_complete_messages_from_sequential_clients(self):
        server = subprocess.Popen(
            [sys.executable, str(SRC / "echo_server.py"), "--host", "127.0.0.1", "--port", "0"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(server.stdout, selectors.EVENT_READ)
                self.assertTrue(selector.select(5), "Echo-Server meldet keinen Start")
            announcement = server.stdout.readline()
            match = re.search(r"Port (\d+)", announcement)
            error = server.stderr.read() if server.poll() is not None else ""
            self.assertIsNotNone(match, f"Echo-Server startet nicht: {announcement!r} {error}")
            port = match.group(1)
            for message in (None, "ab x " * 1500):
                args = [sys.executable, str(SRC / "echo_client.py"), "127.0.0.1", "--port", port]
                if message is not None:
                    args.append(message)
                response = subprocess.run(args, capture_output=True, text=True, timeout=5)
                self.assertEqual(response.returncode, 0, response.stderr)
                expected = "HALLO NETZ" if message is None else "AB X " * 1500
                self.assertEqual(response.stdout, f"Antwort: {expected}\n")
        finally:
            if server.poll() is None:
                server.send_signal(signal.SIGINT)
            try:
                server.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.communicate()
        self.assertEqual(server.returncode, 0, "Echo-Server beendet sich mit einem Fehler")


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
