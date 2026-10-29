"""Echte Tk-Oberflaeche mit lokalen Socketpaaren pruefen (kein Widgetersatz)."""
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
import weakref

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


class GuiTests(unittest.TestCase):
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

    def test_all_target_buttons_send_their_own_coordinate_without_drawing(self):
        self.window.draw_state(state())
        before = self.board_snapshot()
        expected = {f"{letter}{row}" for letter in "ABCDEFGHIJ" for row in range(1, 11)}
        self.assertEqual(set(self.window.own_buttons), expected)
        self.assertEqual(set(self.window.target_buttons), expected)
        for field in sorted(expected):
            self.window.target_buttons[field].invoke()
            self.assertEqual(self.peer.read(), {"type": "shoot", "field": field})
        self.assertEqual(self.board_snapshot(), before)

    def test_full_state_renders_both_boards_including_incoming_misses_and_clears(self):
        self.window.draw_state(state(
            ownShips=[{"type": "Destroyer", "cells": ["A1", "B1"], "hits": ["A1"]}],
            shotsAtSelf={"A1": "hit", "J10": "miss"},
            shotsAtOpponent={"C7": "miss", "D8": "hit", "E8": "sunk"},
        ))
        self.assertEqual(self.window.own_buttons["A1"].cget("text"), "X")
        self.assertEqual(self.window.own_buttons["B1"].cget("text"), "S")
        self.assertEqual(self.window.own_buttons["J10"].cget("text"), "·")
        self.assertEqual(self.window.target_buttons["C7"].cget("text"), "·")
        self.assertEqual(self.window.target_buttons["D8"].cget("text"), "X")
        self.assertEqual(self.window.target_buttons["E8"].cget("text"), "#")
        self.assertEqual(self.window.target_buttons["A1"].cget("text"), "")
        self.window.draw_state(state(phase="waiting", turn=None, ownShips=[]))
        self.assertTrue(all(not text for text, _ in self.board_snapshot()))

    def test_placement_controls_send_individual_fleet_without_speculative_drawing(self):
        self.window.draw_state(state(phase="placing", turn=None, ownShips=[]))
        before = self.board_snapshot()
        self.window.placement_vars["Carrier"][0].set("J1")
        self.window.placement_vars["Carrier"][1].set("v")
        self.window.place_button.invoke()
        request = self.peer.read()
        self.assertEqual(request["type"], "place")
        self.assertEqual(len(request["ships"]), 5)
        self.assertEqual(request["ships"][0], {"type": "Carrier", "start": "J1", "direction": "v"})
        self.assertEqual(self.board_snapshot(), before)

    def test_randomize_produces_valid_varying_candidates_only(self):
        from board import validate_placement
        self.window.draw_state(state(phase="placing", turn=None, ownShips=[]))
        before = self.board_snapshot()
        fleets = set()
        for _ in range(5):
            self.window.randomize_button.invoke()
            self.window.place_button.invoke()
            fleet = self.peer.read()["ships"]
            self.assertTrue(validate_placement(fleet)[0])
            fleets.add(json.dumps(fleet, sort_keys=True))
        self.assertGreater(len(fleets), 1)
        self.assertEqual(self.board_snapshot(), before)

    def test_error_is_readable_and_does_not_change_boards(self):
        self.window.draw_state(state())
        before = self.board_snapshot()
        self.peer.send({"type": "error", "code": "NOT_YOUR_TURN", "message": "Spieler A ist nicht am Zug"})
        self.pump_until(lambda: "NOT_YOUR_TURN" in self.window.status_var.get())
        self.assertIn("nicht am Zug", self.window.status_var.get())
        self.assertEqual(self.board_snapshot(), before)

    def test_results_and_acknowledgements_do_not_draw_before_state(self):
        self.window.draw_state(state())
        before = self.board_snapshot()
        self.window.process_message({"type": "result", "field": "A1", "result": "hit", "sunk": None, "turn": "B"})
        self.window.process_message({"type": "placeAck", "phase": "shooting"})
        self.assertEqual(self.board_snapshot(), before)

    def test_lobby_events_preserve_confirmed_boards_until_server_state(self):
        confirmed = state(shotsAtOpponent={"J10": "miss"})
        for event in (
            {"type": "gameStart", "players": {"A": "Alice", "B": "Carol"}},
            {"type": "opponentLeft", "player": "Bob"},
        ):
            with self.subTest(event=event["type"]):
                self.window.process_message(confirmed)
                before = self.board_snapshot()
                self.window.process_message(event)
                self.assertEqual(self.board_snapshot(), before)
                self.assertEqual(self.window.last_state, confirmed)
        # Erst die ausdrueckliche, gefilterte Gesamtsicht leert die Raster.
        self.window.process_message(state(phase="waiting", turn=None, ownShips=[]))
        self.assertTrue(all(not text for text, _ in self.board_snapshot()))

    def test_receive_queue_drains_on_main_thread_and_renders_last_message(self):
        main_thread = threading.get_ident()
        calls = []
        actual_process = self.window.process_message
        actual_draw = self.window.draw_state
        def record_process(message):
            calls.append(threading.get_ident())
            actual_process(message)
        def record_draw(message):
            calls.append(threading.get_ident())
            actual_draw(message)
        self.window.process_message = record_process
        self.window.draw_state = record_draw
        for row in range(1, 11):
            self.peer.send(state(shotsAtOpponent={f"J{row}": "miss"}))
        self.pump_until(lambda: self.window.target_buttons["J10"].cget("text") == "·")
        self.assertGreaterEqual(len(calls), 20)
        self.assertEqual(set(calls), {main_thread})
        self.assertEqual(self.window.target_buttons["J1"].cget("text"), "")

    def test_idle_socket_does_not_block_tk_after_callbacks(self):
        ticks = []
        self.root.after(10, lambda: ticks.append(True))
        start = time.monotonic()
        self.pump_until(lambda: bool(ticks), timeout=0.5)
        self.assertLess(time.monotonic() - start, 0.5)

    def test_stalled_send_runs_in_worker_and_does_not_block_tk(self):
        # Ein echtes Socketpaar bleibt die Transportgrenze. Nur sendall wird
        # angehalten, um einen langsamen Empfaenger reproduzierbar nachzubilden.
        self.transport.paused = True
        try:
            self.window.shoot("J10")
            self.assertTrue(self.transport.entered.wait(0.5))
            ticks = []
            self.root.after(10, lambda: ticks.append(True))
            self.pump_until(lambda: bool(ticks), timeout=0.5)
            self.assertNotEqual(self.transport.send_threads, [threading.get_ident()])
            self.transport.release.set()
            self.assertEqual(self.peer.read(), {"type": "shoot", "field": "J10"})
        finally:
            self.transport.release.set()

    def test_get_state_button_sends_request(self):
        before = self.board_snapshot()
        self.window.refresh_button.invoke()
        self.assertEqual(self.peer.read(), {"type": "getState"})
        self.assertEqual(self.board_snapshot(), before)

    def test_waiting_turn_and_winner_status(self):
        self.window.draw_state(state(phase="waiting", turn=None, ownShips=[]))
        self.assertIn("Warte", self.window.status_var.get())
        self.window.draw_state(state(phase="placing", turn=None, ownShips=[]))
        self.assertIn("Flotte", self.window.status_var.get())
        self.window.draw_state(state(turn="A"))
        self.assertIn("Du bist am Zug", self.window.status_var.get())
        self.window.draw_state(state(turn="B"))
        self.assertIn("Gegner", self.window.status_var.get())
        self.window.draw_state(state(phase="finished", turn=None, winner="A"))
        self.assertIn("Gewonnen", self.window.status_var.get())
        self.window.draw_state(state(phase="finished", turn=None, winner="B"))
        self.assertIn("Verloren", self.window.status_var.get())

    def test_opponent_leaving_clears_boards_and_replacement_enables_placement(self):
        self.window.draw_state(state(shotsAtOpponent={"J10": "miss"}))
        self.window.process_message({"type": "opponentLeft", "player": "Bob"})
        # Der Server sendet unmittelbar nach opponentLeft den leeren Zustand;
        # der Abbruchgrund muss danach noch lesbar sein.
        self.window.process_message(state(phase="waiting", turn=None, ownShips=[]))
        self.assertTrue(all(not text for text, _ in self.board_snapshot()))
        self.assertIn("verlassen", self.window.status_var.get())
        self.assertEqual(str(self.window.place_button.cget("state")), "disabled")
        self.window.process_message({"type": "gameStart", "players": {"A": "Alice", "B": "Carol"}})
        self.window.process_message(state(phase="placing", turn=None, ownShips=[]))
        self.assertEqual(str(self.window.place_button.cget("state")), "normal")
        self.assertIn("Flotte", self.window.status_var.get())

    def test_server_close_disables_requests_and_is_visible(self):
        self.window.draw_state(state())
        self.remote.shutdown(socket.SHUT_RDWR)
        self.remote.close()
        self.pump_until(lambda: "Verbindung beendet" in self.window.status_var.get())
        self.assertEqual(self.window.target_buttons["A1"].cget("state"), "disabled")
        self.assertEqual(str(self.window.refresh_button.cget("state")), "disabled")

    def test_window_cross_closes_socket_and_workers_promptly(self):
        # Tk-Variablen duerfen nicht bis zum letzten Worker-Verweis am Fenster
        # haengen: ihr Destruktor ruft Tcl auf und muss im Hauptthread laufen.
        finalizer_threads = []
        def finalized(variable):
            finalizer_threads.append(threading.get_ident())
        variables = [weakref.ref(self.window.status_var, finalized)] + [
            weakref.ref(variable, finalized)
            for pair in self.window.placement_vars.values() for variable in pair
        ]
        close_command = self.root.protocol("WM_DELETE_WINDOW")
        self.assertTrue(close_command)
        start = time.monotonic()
        self.root.tk.call(close_command)
        self.assertLess(time.monotonic() - start, 0.3)
        self.assertTrue(all(variable() is None for variable in variables))
        self.assertEqual(finalizer_threads, [threading.get_ident()] * 11)
        self.remote.settimeout(1)
        self.assertEqual(self.remote.recv(4096), b"")
        self.window.receive_thread.join(1)
        self.window.send_thread.join(1)
        self.assertFalse(self.window.receive_thread.is_alive())
        self.assertFalse(self.window.send_thread.is_alive())
        self.window.close()  # zweimaliges Schliessen bleibt sicher


if __name__ == "__main__":
    unittest.main(verbosity=2)
