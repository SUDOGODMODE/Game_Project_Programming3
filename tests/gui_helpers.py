"""Gemeinsame echte Tk-/Socket-Fixturen, ohne eigene entdeckbare Tests."""
from __future__ import annotations

import importlib.util
import json
import select
import socket
import subprocess
import sys
import threading
import time
import unittest

try:
    import tkinter as tk
except ImportError:
    tk = None

if importlib.util.find_spec("client_gui") is not None:
    import client_gui
else:
    client_gui = None


def state(**changes):
    result = {
        "type": "state", "phase": "shooting", "turn": "A",
        "ownShips": [{"type": "Destroyer", "cells": ["A1", "B1"], "hits": []}],
        "shotsAtOpponent": {}, "shotsAtSelf": {}, "winner": None,
    }
    result.update(changes)
    return result


class Peer:
    def __init__(self, sock):
        self.sock = sock
        self.buffer = b""

    def read(self, timeout=1):
        deadline = time.monotonic() + timeout
        while b"\n" not in self.buffer:
            ready, _, _ = select.select([self.sock], [], [], max(0, deadline - time.monotonic()))
            if not ready:
                raise AssertionError("Client hat keine Nachricht gesendet")
            chunk = self.sock.recv(4096)
            if not chunk:
                raise AssertionError("Client hat vor der Nachricht geschlossen")
            self.buffer += chunk
        line, self.buffer = self.buffer.split(b"\n", 1)
        return json.loads(line)

    def send(self, message):
        self.sock.sendall((json.dumps(message) + "\n").encode())


class ControlledSocket:
    """Echter Transport mit optional angehaltenem Versand fuer den Lasttest."""
    def __init__(self, sock):
        self.sock = sock
        self.paused = False
        self.entered = threading.Event()
        self.release = threading.Event()
        self.send_threads = []

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def sendall(self, payload):
        if self.paused:
            self.send_threads.append(threading.get_ident())
            self.entered.set()
            self.release.wait(2)
        self.sock.sendall(payload)


class TkDisplayTestCase(unittest.TestCase):
    requires_gui = True

    @classmethod
    def setUpClass(cls):
        if tk is None:
            raise unittest.SkipTest("tkinter ist nicht installiert")
        # Auf macOS kann fehlender GUI-Zugriff Tk() mit SIGABRT beenden.
        # Die getrennte Probe macht diese fehlende Umgebung als Skip sichtbar.
        probe = subprocess.run(
            [sys.executable, "-c", "import tkinter as t; r=t.Tk(); r.destroy()"],
            capture_output=True, timeout=10,
        )
        if probe.returncode:
            detail = probe.stderr.decode(errors="replace").strip().splitlines()
            raise unittest.SkipTest("Echtes Tk/Display nicht verfuegbar: " + (detail[-1] if detail else str(probe.returncode)))


class GuiTestCase(TkDisplayTestCase):
    """Fenster mit echtem Socketpaar; alle Ressourcen bleiben pro Test getrennt."""

    def setUp(self):
        self.assertIsNotNone(client_gui, "client_gui.py mit echter BattleshipWindow fehlt")
        self.root = tk.Tk()
        self.root.withdraw()
        self.local, self.remote = socket.socketpair()
        self.peer = Peer(self.remote)
        self.transport = ControlledSocket(self.local)
        self.window = client_gui.BattleshipWindow(self.root, self.transport, "Alice")
        self.assertEqual(self.peer.read(), {"type": "join", "player": "Alice"})
        self.window.process_message({"type": "welcome", "slot": "A", "player": "Alice"})

    def tearDown(self):
        if hasattr(self, "window"):
            self.window.close()
        if hasattr(self, "remote"):
            self.remote.close()
        if hasattr(self, "root"):
            try:
                self.root.destroy()
            except tk.TclError:
                pass

    def pump_until(self, condition, timeout=1):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.root.update()
            if condition():
                return
            time.sleep(0.005)
        self.fail("GUI-Bedingung wurde nicht rechtzeitig erreicht")

    def board_snapshot(self):
        return [
            (button.cget("text"), button.cget("background"))
            for grid in (self.window.own_buttons, self.window.target_buttons)
            for button in grid.values()
        ]

