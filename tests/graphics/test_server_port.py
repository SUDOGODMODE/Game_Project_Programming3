"""Der Server lässt sich für isolierte Netztests auf einen Port setzen."""
import ast
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import tempfile
import time
import unittest


SERVER = Path(__file__).resolve().parents[2] / "src" / "server.py"


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class ServerPortTests(unittest.TestCase):
    def check_server_listens(self, environment_port, command_port=None):
        expected_port = command_port or environment_port
        with tempfile.TemporaryDirectory() as temp:
            command = [sys.executable, str(SERVER), "--host", "127.0.0.1",
                       "--log-file", str(Path(temp) / "server.jsonl")]
            if command_port is not None:
                command += ["--port", str(command_port)]
            environment = dict(os.environ, PORT=str(environment_port))
            process = subprocess.Popen(command, env=environment,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    if process.poll() is not None:
                        self.fail(f"Server beendet: {process.stderr.read().decode(errors='replace')}")
                    try:
                        with socket.create_connection(("127.0.0.1", expected_port), timeout=0.2):
                            return
                    except OSError:
                        time.sleep(0.05)
                self.fail(f"Server lauscht nicht auf {expected_port}")
            finally:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
                process.stderr.close()

    def test_port_aus_umgebungsvariable(self):
        self.check_server_listens(free_port())

    def test_cli_port_hat_vorrang(self):
        self.check_server_listens(free_port(), free_port())

    def test_belegter_standardport_weicht_auf_den_naechsten_freien_aus(self):
        import server
        with socket.socket() as fremd:
            fremd.bind(("127.0.0.1", 0))
            fremd.listen()
            belegt = fremd.getsockname()[1]
            with server.bind_listener("127.0.0.1", belegt, attempts=20) as listener:
                self.assertGreater(listener.getsockname()[1], belegt)
            with self.assertRaises(OSError):
                server.bind_listener("127.0.0.1", belegt, attempts=1)

    def test_server_und_clients_teilen_einen_standardport_ausser_5000(self):
        # Port 5000 belegt unter macOS der AirPlay-Empfaenger.
        source = SERVER.parent
        server_default = re.search(r'os\.environ\.get\("PORT", "(\d+)"\)',
                                   (source / "server.py").read_text(encoding="utf-8")).group(1)
        defaults = {"server.py": int(server_default)}
        for name in ("client_gui.py", "client.py", "play.py"):
            for node in ast.walk(ast.parse((source / name).read_text(encoding="utf-8"))):
                if (isinstance(node, ast.Call) and node.args
                        and isinstance(node.args[0], ast.Constant) and node.args[0].value == "--port"):
                    defaults[name] = next(k.value.value for k in node.keywords if k.arg == "default")
        self.assertEqual(defaults, dict.fromkeys(("server.py", "client_gui.py", "client.py", "play.py"), 5100))


if __name__ == "__main__":
    unittest.main()
