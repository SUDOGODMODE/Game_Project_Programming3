"""Echo-CLI-Integration aus Projektphase M0."""
from pathlib import Path
import re
import selectors
import signal
import subprocess
import sys
import unittest
SRC = Path(__file__).resolve().parents[2] / "src"


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

if __name__ == "__main__":
    unittest.main()
