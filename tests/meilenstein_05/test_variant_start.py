"""Zwei Startprofile erzeugen sichere, vom Arbeitsverzeichnis unabhaengige Befehle."""
import importlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class VariantCommandTests(unittest.TestCase):
    def command_for(self, profile, role, *, server_ip=None, port=5100, name=None, root=None):
        launcher = importlib.import_module("tools.variant_start")
        return launcher.command_for(profile, role, server_ip=server_ip, port=port,
                                    name=name, root=root or ROOT, python="/test/python")

    def test_localhost_server_binds_only_loopback(self):
        self.assertEqual(self.command_for("localhost", "server"),
                         ["/test/python", "-u", str(ROOT / "src/server.py"),
                          "--host", "127.0.0.1", "--port", "5100"])

    def test_localhost_clients_both_target_loopback(self):
        for role, name in (("alice", "Alice"), ("bob", "Bob")):
            with self.subTest(role=role):
                self.assertEqual(self.command_for("localhost", role, name=name),
                                 ["/test/python", str(ROOT / "src/client_gui.py"),
                                  "127.0.0.1", name, "--port", "5100"])

    def test_localhost_rejects_supplied_foreign_server_address(self):
        for role, name in (("server", None), ("alice", "Alice"), ("bob", "Bob")):
            with self.subTest(role=role):
                with self.assertRaises(ValueError):
                    self.command_for("localhost", role, server_ip="192.0.2.40", name=name)

    def test_two_rechner_server_binds_all_interfaces_but_alice_uses_loopback(self):
        self.assertEqual(self.command_for("zwei_rechner", "server"),
                         ["/test/python", "-u", str(ROOT / "src/server.py"),
                          "--host", "0.0.0.0", "--port", "5100"])
        self.assertEqual(self.command_for("zwei_rechner", "alice", name="Alice"),
                         ["/test/python", str(ROOT / "src/client_gui.py"),
                          "127.0.0.1", "Alice", "--port", "5100"])

    def test_two_rechner_bob_needs_explicit_ipv4_host(self):
        self.assertEqual(self.command_for("zwei_rechner", "bob", server_ip="192.0.2.40", name="Bob"),
                         ["/test/python", str(ROOT / "src/client_gui.py"),
                          "192.0.2.40", "Bob", "--port", "5100"])
        with self.assertRaises(ValueError):
            self.command_for("zwei_rechner", "bob", name="Bob")

    def test_two_rechner_bob_rejects_non_host_addresses(self):
        for address in ("", "127.0.0.1", "127.0.0.2", "0.0.0.0", "255.255.255.255",
                        "224.0.0.1", "::1", "server.local", "999.1.2.3"):
            with self.subTest(address=address):
                with self.assertRaises(ValueError):
                    self.command_for("zwei_rechner", "bob", server_ip=address, name="Bob")

    def test_two_rechner_bob_accepts_dot_255_when_it_can_be_a_host(self):
        # Ohne Netzmaske ist 192.168.1.255 z.B. in einem /23-Netz ein Host.
        self.assertEqual(
            self.command_for("zwei_rechner", "bob", server_ip="192.168.1.255", name="Bob"),
            ["/test/python", str(ROOT / "src/client_gui.py"),
             "192.168.1.255", "Bob", "--port", "5100"],
        )
        with self.assertRaises(ValueError):
            self.command_for("zwei_rechner", "bob", server_ip="255.255.255.255", name="Bob")

    def test_client_name_must_be_supplied(self):
        for name in (None, "", "   "):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    self.command_for("localhost", "alice", name=name)

    def test_invalid_port_or_role_is_rejected(self):
        for port in (0, -1, 65536, True, "5100"):
            with self.subTest(port=port):
                with self.assertRaises(ValueError):
                    self.command_for("localhost", "server", port=port)
        for profile, role in (("local", "server"), ("localhost", "client")):
            with self.subTest(profile=profile, role=role):
                with self.assertRaises(ValueError):
                    self.command_for(profile, role)

    def test_commands_use_extracted_root_even_from_foreign_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            extracted = base / "unpacked" / "Game_Project_Programming3"
            extracted.mkdir(parents=True)
            elsewhere = base / "elsewhere"
            elsewhere.mkdir()
            original = Path.cwd()
            try:
                os.chdir(elsewhere)
                command = self.command_for("zwei_rechner", "bob", server_ip="192.0.2.40",
                                           name="Bob", root=extracted)
            finally:
                os.chdir(original)
            self.assertEqual(command[1], str(extracted / "src/client_gui.py"))
            self.assertNotIn(str(elsewhere), " ".join(command))

    def test_each_profile_entrypoint_has_help_from_foreign_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            for profile in ("localhost", "zwei_rechner"):
                entry = ROOT / "varianten" / profile / "start.py"
                result = subprocess.run([sys.executable, str(entry), "--help"], cwd=directory,
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--name", result.stdout)
                self.assertIn("server", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
