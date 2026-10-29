"""Lokale TCP- und CLI-Tests; ausführen mit python tools/run_tests.py --milestone 03.

Jeder Test startet einen eigenen Server auf einem freien Loopback-Port.
Zeitlimits begrenzen das Warten auf Nachrichten und Prozesse.
"""
import ast
from pathlib import Path
import queue
import socket
import subprocess
import sys
import threading
import time
import unittest

import server
import os
from tests.fixtures import FLEET, FLEET_CELLS, MISSES

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
from netz import read_messages, send


TIMEOUT = 2.0
END = object()


class Peer:
    """TCP-Testclient mit Nachrichtenwarteschlange und Zeitlimit."""

    def __init__(self, address):
        self.sock = socket.create_connection(address, timeout=TIMEOUT)
        self.sock.settimeout(None)
        self.messages = queue.Queue()
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        try:
            for message in read_messages(self.sock):
                self.messages.put(message)
        except OSError:
            pass
        finally:
            self.messages.put(END)

    def send(self, message):
        send(self.sock, message)

    def receive(self, timeout=TIMEOUT):
        try:
            message = self.messages.get(timeout=timeout)
        except queue.Empty:
            raise AssertionError("server did not send the expected message before the deadline") from None
        if message is END:
            raise AssertionError("server closed the connection before the expected message")
        return message

    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()
        self.reader.join(TIMEOUT)


class LoopbackServer:
    """Startet den lokalen Server und räumt Sockets und Threads auf."""

    def __init__(self):
        self.game = server.new_game()
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.listener.bind(("127.0.0.1", 0))
        except OSError:
            self.listener.close()
            raise
        self.listener.listen()
        self.listener.settimeout(0.1)
        self.address = self.listener.getsockname()
        self.stopped = threading.Event()
        self.handlers = []
        self.sockets = []
        self.errors = queue.Queue()
        self.acceptor = threading.Thread(target=self._accept, daemon=True)
        self.acceptor.start()

    def _accept(self):
        while not self.stopped.is_set():
            try:
                sock, address = self.listener.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            self.sockets.append(sock)
            worker = threading.Thread(target=self._serve, args=(sock, address), daemon=True)
            self.handlers.append(worker)
            worker.start()

    def _serve(self, sock, address):
        try:
            server.handle_connection(sock, address, self.game)
        except Exception as error:
            self.errors.put(error)

    def close(self):
        self.stopped.set()
        self.listener.close()
        self.acceptor.join(TIMEOUT)
        for sock in self.sockets:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()
        for worker in self.handlers:
            worker.join(TIMEOUT)
        if any(worker.is_alive() for worker in self.handlers):
            raise AssertionError("server handler failed to stop during cleanup")
        if not self.errors.empty():
            raise AssertionError(f"server handler raised: {self.errors.get()!r}")


class CliClient:
    """Startet ein Clientskript mit steuerbarer Standardeingabe."""

    def __init__(self, address, name, script="client.py"):
        self.process = subprocess.Popen(
            [sys.executable, "-u", str(SRC / script),
             address[0], name, "--port", str(address[1])],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
        self.messages = queue.Queue()
        self.lines = queue.Queue()
        self.output = []
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        for line in self.process.stdout:
            self.output.append(line.rstrip())
            self.lines.put(line.rstrip())
            if line.lstrip().startswith("<-"):
                try:
                    self.messages.put(ast.literal_eval(line.lstrip()[2:].strip()))
                except (ValueError, SyntaxError):
                    self.messages.put({"invalid_client_output": line})
        self.messages.put(END)
        self.lines.put(END)

    def receive(self, timeout=TIMEOUT):
        try:
            message = self.messages.get(timeout=timeout)
        except queue.Empty:
            raise AssertionError(f"client displayed no expected server event: {self.output!r}") from None
        if message is END:
            raise AssertionError(f"client ended before expected event: {self.output!r}")
        return message

    def quit(self):
        self.process.stdin.write("q\n")
        self.process.stdin.flush()
        return self.process.wait(timeout=TIMEOUT)

    def command(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def wait_output(self, text):
        deadline = time.monotonic() + TIMEOUT
        while True:
            try:
                line = self.lines.get(timeout=max(0.001, deadline - time.monotonic()))
            except queue.Empty:
                raise AssertionError(f"client did not display {text!r}: {self.output!r}") from None
            if line is END:
                raise AssertionError(f"client ended before displaying {text!r}: {self.output!r}")
            if text.casefold() in line.casefold():
                return line

    def kill(self):
        self.process.kill()
        self.process.wait(timeout=TIMEOUT)

    def close(self):
        if self.process.poll() is None:
            self.kill()
        self.reader.join(TIMEOUT)
        self.process.stdin.close()
        self.process.stdout.close()


class NetworkTests(unittest.TestCase):
    def setUp(self):
        self.server = LoopbackServer()
        self.addCleanup(self.server.close)

    def peer(self):
        peer = Peer(self.server.address)
        self.addCleanup(peer.close)
        return peer

    def assert_message(self, peer, message_type, **fields):
        message = peer.receive()
        self.assertEqual(message.get("type"), message_type, message)
        for key, expected in fields.items():
            self.assertEqual(message.get(key), expected, message)
        return message

    def assert_state(self, peer, phase, **fields):
        state = self.assert_message(peer, "state", phase=phase, **fields)
        self.assertEqual(set(state), {"type", "phase", "turn", "ownShips",
                                     "shotsAtOpponent", "shotsAtSelf", "winner"})
        return state

    def assert_lobby(self, peer, message_type, **fields):
        """Jeder Lobbywechsel muss unmittelbar seinen leeren Gesamtzustand liefern."""
        event = self.assert_message(peer, message_type, **fields)
        phase = "placing" if message_type == "gameStart" else "waiting"
        self.assert_state(peer, phase, turn=None, ownShips=[], shotsAtOpponent={},
                          shotsAtSelf={}, winner=None)
        return event

    def assert_quiet(self, peer):
        try:
            message = peer.messages.get(timeout=0.1)
        except queue.Empty:
            return
        self.fail(f"unexpected extra message: {message!r}")

    def join_pair(self):
        alice, bob = self.peer(), self.peer()
        alice.send({"type": "join", "player": "Alice"})
        self.assert_message(alice, "welcome", slot="A", player="Alice")
        self.assert_lobby(alice, "waiting", reason="warte auf Gegner")
        bob.send({"type": "join", "player": "Bob"})
        self.assert_message(bob, "welcome", slot="B", player="Bob")
        players = [{"slot": "A", "player": "Alice"}, {"slot": "B", "player": "Bob"}]
        self.assert_lobby(alice, "gameStart", phase="placing", players=players)
        self.assert_lobby(bob, "gameStart", phase="placing", players=players)
        return alice, bob

    def state(self, peer, phase, **fields):
        peer.send({"type": "getState"})
        return self.assert_state(peer, phase, **fields)

    def fresh_state(self, peer, phase="waiting"):
        state = self.state(peer, phase, turn=None, ownShips=[], shotsAtOpponent={}, shotsAtSelf={}, winner=None)
        return state

    def place_pair(self, alice, bob):
        self.opponents = {alice: bob, bob: alice}
        alice.send({"type": "place", "ships": FLEET})
        self.assert_message(alice, "placeAck", phase="placing")
        a = self.assert_state(alice, "placing", turn=None, shotsAtOpponent={}, shotsAtSelf={})
        self.assertEqual(len(a["ownShips"]), 5)
        self.assert_state(bob, "placing", turn=None, ownShips=[], shotsAtOpponent={}, shotsAtSelf={})
        bob.send({"type": "place", "ships": FLEET})
        self.assert_message(bob, "placeAck", phase="shooting")
        for peer in (alice, bob):
            state = self.assert_state(peer, "shooting", turn="A", shotsAtOpponent={}, shotsAtSelf={})
            self.assertEqual(len(state["ownShips"]), 5)

    def shoot(self, shooter, field, **fields):
        shooter.send({"type": "shoot", "field": field})
        result = self.assert_message(shooter, "result", field=field, **fields)
        phase = "finished" if result["turn"] is None else "shooting"
        state = self.assert_state(shooter, phase, turn=result["turn"])
        self.assertEqual(state["shotsAtOpponent"][field], result["result"])
        if phase == "shooting":
            other = self.assert_state(self.opponents[shooter], phase, turn=result["turn"])
            self.assertEqual(other["shotsAtSelf"][field], result["result"])
        return result

    def finish_game(self, alice, bob):
        for index, field in enumerate(FLEET_CELLS):
            result = self.shoot(alice, field)
            if index == len(FLEET_CELLS) - 1:
                self.assertEqual(result, {"type": "result", "field": "B5", "result": "sunk",
                                          "sunk": "Destroyer", "turn": None})
                self.assert_message(bob, "gameOver", winner="A", reason="sunk")
                self.assert_state(bob, "finished", turn=None, winner="A")
            else:
                self.assertEqual(result["turn"], "B")
                self.assertIn(result["result"], ("hit", "sunk"))
                self.shoot(bob, MISSES[index], result="miss", sunk=None, turn="A")

    def test_first_join_receives_waiting_without_starting_game(self):
        alice = self.peer()
        alice.send({"type": "join", "player": "Alice"})
        self.assert_message(alice, "welcome", slot="A", player="Alice", phase="waiting")
        self.assert_lobby(alice, "waiting", reason="warte auf Gegner")
        alice.send({"type": "getState"})
        self.assert_message(alice, "state", phase="waiting", turn=None, ownShips=[], winner=None)
        alice.send({"type": "place", "ships": FLEET})
        self.assert_message(alice, "error", code="WRONG_PHASE")
        self.assert_quiet(alice)

    def test_second_join_sends_unsolicited_start_to_both_players(self):
        alice = self.peer()
        bob = self.peer()
        alice.send({"type": "join", "player": "Alice"})
        self.assert_message(alice, "welcome", slot="A")
        self.assert_lobby(alice, "waiting")
        bob.send({"type": "join", "player": "Bob"})
        self.assert_message(bob, "welcome", slot="B", player="Bob", phase="placing")
        players = [{"slot": "A", "player": "Alice"}, {"slot": "B", "player": "Bob"}]
        self.assert_lobby(alice, "gameStart", phase="placing", players=players)
        self.assert_lobby(bob, "gameStart", phase="placing", players=players)

    def test_third_player_is_rejected_without_changing_the_two_player_game(self):
        alice, bob = self.join_pair()
        carol = self.peer()
        carol.send({"type": "join", "player": "Carol"})
        self.assert_message(carol, "error", code="GAME_FULL")
        carol.send({"type": "getState"})
        self.assert_message(carol, "error", code="NOT_JOINED")
        self.fresh_state(alice, "placing")
        self.fresh_state(bob, "placing")

    def test_simultaneous_joins_admit_exactly_two_distinct_slots(self):
        # Kapazitätsprüfung und Slotvergabe müssen unter derselben Sperre erfolgen.
        peers = [self.peer() for _ in range(6)]
        barrier = threading.Barrier(len(peers))
        failures = queue.Queue()

        def join(peer, name):
            try:
                barrier.wait(timeout=TIMEOUT)
                peer.send({"type": "join", "player": name})
            except Exception as error:
                failures.put(error)

        threads = [threading.Thread(target=join, args=(peer, f"Player{index}"))
                   for index, peer in enumerate(peers)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(TIMEOUT)
            self.assertFalse(thread.is_alive(), "concurrent join sender failed to finish")
        self.assertTrue(failures.empty(), list(failures.queue))
        admitted = []
        rejected = []
        for index, peer in enumerate(peers):
            message = peer.receive()
            if message.get("type") == "welcome":
                self.assertEqual(message["player"], f"Player{index}")
                admitted.append((peer, message))
            else:
                self.assertEqual(message.get("type"), "error", message)
                self.assertEqual(message.get("code"), "GAME_FULL", message)
                rejected.append(peer)
        self.assertEqual(len(admitted), 2)
        self.assertEqual(len(rejected), 4)
        self.assertEqual({message["slot"] for _, message in admitted}, {"A", "B"})
        players = sorted([{"slot": m["slot"], "player": m["player"]} for _, m in admitted],
                         key=lambda player: player["slot"])
        for peer, _ in admitted:
            event = peer.receive()
            if event.get("type") == "waiting":
                self.assertEqual(event["reason"], "warte auf Gegner")
                self.assert_state(peer, "waiting", turn=None, ownShips=[], shotsAtOpponent={},
                                  shotsAtSelf={}, winner=None)
                event = peer.receive()
            self.assertEqual(event, {"type": "gameStart", "phase": "placing", "players": players})
            self.assert_state(peer, "placing", turn=None, ownShips=[], shotsAtOpponent={},
                              shotsAtSelf={}, winner=None)
            self.fresh_state(peer, "placing")

    def test_duplicate_join_does_not_rename_or_restart_game(self):
        alice, bob = self.join_pair()
        alice.send({"type": "join", "player": "Mallory"})
        self.assert_message(alice, "error", code="ALREADY_JOINED")
        self.fresh_state(alice, "placing")
        self.fresh_state(bob, "placing")
        alice.close()
        self.assert_lobby(bob, "opponentLeft", slot="A", player="Alice")

    def test_malformed_and_unjoined_requests_keep_connection_usable(self):
        peer = self.peer()
        peer.sock.sendall(b"not JSON\n[1, 2, 3]\n42\n")
        for _ in range(3):
            self.assert_message(peer, "error", code="INVALID_JSON")
        for message, code in [
            ({"type": "nonsense"}, "UNKNOWN_TYPE"),
            ({"player": "Alice"}, "UNKNOWN_TYPE"),
            ({"type": "join"}, "MISSING_PLAYER"),
            ({"type": "join", "player": "   "}, "MISSING_PLAYER"),
            ({"type": "join", "player": 17}, "MISSING_PLAYER"),
            ({"type": "getState"}, "NOT_JOINED"),
            ({"type": "leave"}, "NOT_JOINED"),
        ]:
            with self.subTest(message=message):
                peer.send(message)
                self.assert_message(peer, "error", code=code)
        peer.send({"type": "join", "player": "Alice"})
        self.assert_message(peer, "welcome", slot="A", player="Alice", phase="waiting")
        self.assert_lobby(peer, "waiting", reason="warte auf Gegner")

    def test_disconnect_before_join_does_not_notify_or_claim_a_slot(self):
        alice = self.peer()
        alice.send({"type": "join", "player": "Alice"})
        self.assert_message(alice, "welcome", slot="A")
        self.assert_lobby(alice, "waiting")
        anonymous = self.peer()
        anonymous.send({"type": "getState"})
        self.assert_message(anonymous, "error", code="NOT_JOINED")
        anonymous.close()
        self.fresh_state(alice)
        bob = self.peer()
        bob.send({"type": "join", "player": "Bob"})
        self.assert_message(bob, "welcome", slot="B")
        self.assert_lobby(alice, "gameStart", phase="placing")
        self.assert_lobby(bob, "gameStart", phase="placing")

    def test_explicit_leave_notifies_once_resets_boards_and_reuses_slot_b(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        self.shoot(alice, "A1", result="hit", turn="B")
        self.shoot(bob, "A1", result="hit", turn="A")
        bob.send({"type": "leave"})
        self.assert_lobby(alice, "opponentLeft", slot="B", player="Bob")
        self.fresh_state(alice)
        self.assert_quiet(alice)
        self.assertIs(bob.messages.get(timeout=TIMEOUT), END, "leave must close its TCP connection")
        carol = self.peer()
        carol.send({"type": "join", "player": "Carol"})
        self.assert_message(carol, "welcome", slot="B", phase="placing")
        players = [{"slot": "A", "player": "Alice"}, {"slot": "B", "player": "Carol"}]
        self.assert_lobby(alice, "gameStart", phase="placing", players=players)
        self.assert_lobby(carol, "gameStart", phase="placing", players=players)
        self.fresh_state(carol, "placing")
        self.place_pair(alice, carol)

    def test_eof_from_slot_a_keeps_b_and_reuses_first_free_slot_a(self):
        # Nach dem Abgang von A ist A frei; die Spielerzahl allein würde B erneut vergeben.
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        alice.close()
        self.assert_lobby(bob, "opponentLeft", slot="A", player="Alice")
        self.fresh_state(bob)
        self.assert_quiet(bob)
        carol = self.peer()
        carol.send({"type": "join", "player": "Carol"})
        self.assert_message(carol, "welcome", slot="A", phase="placing")
        players = [{"slot": "A", "player": "Carol"}, {"slot": "B", "player": "Bob"}]
        self.assert_lobby(bob, "gameStart", phase="placing", players=players)
        self.assert_lobby(carol, "gameStart", phase="placing", players=players)
        self.fresh_state(bob, "placing")
        self.fresh_state(carol, "placing")

    def test_last_player_departure_allows_new_first_player_to_wait(self):
        alice = self.peer()
        alice.send({"type": "join", "player": "Alice"})
        self.assert_message(alice, "welcome", slot="A")
        self.assert_lobby(alice, "waiting")
        alice.send({"type": "leave"})
        self.assertIs(alice.messages.get(timeout=TIMEOUT), END)
        carol = self.peer()
        carol.send({"type": "join", "player": "Carol"})
        self.assert_message(carol, "welcome", slot="A", phase="waiting")
        self.assert_lobby(carol, "waiting", reason="warte auf Gegner")
        self.fresh_state(carol)

    def test_state_exposes_own_fleet_and_shots_without_opponents_fleet(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        self.shoot(alice, "A1", result="hit", turn="B")
        alice_state = self.state(alice, "shooting", turn="B", shotsAtOpponent={"A1": "hit"}, winner=None)
        bob_state = self.state(bob, "shooting", turn="B", shotsAtOpponent={}, winner=None)
        for state in (alice_state, bob_state):
            self.assertEqual(set(state), {"type", "phase", "turn", "ownShips", "shotsAtOpponent", "shotsAtSelf", "winner"})
            self.assertEqual(len(state["ownShips"]), 5)
            self.assertEqual(state["ownShips"][0]["cells"], ["A1", "B1", "C1", "D1", "E1"])
        self.assertEqual(alice_state["ownShips"][0]["hits"], [])
        self.assertEqual(bob_state["ownShips"][0]["hits"], ["A1"])

    def test_complete_game_preserves_validation_turns_results_and_game_over(self):
        alice, bob = self.join_pair()
        alice.send({"type": "place", "ships": []})
        self.assert_message(alice, "error", code="INVALID_PLACEMENT")
        self.place_pair(alice, bob)
        bob.send({"type": "shoot", "field": "A1"})
        self.assert_message(bob, "error", code="NOT_YOUR_TURN")
        alice.send({"type": "shoot", "field": "K1"})
        self.assert_message(alice, "error", code="CELL_OUT_OF_BOUNDS")
        self.finish_game(alice, bob)
        self.state(alice, "finished", turn=None, winner="A")
        self.state(bob, "finished", turn=None, winner="A")
        alice.send({"type": "shoot", "field": "J10"})
        self.assert_message(alice, "error", code="WRONG_PHASE")

    def test_duplicate_shot_keeps_the_turn_and_prior_result(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        self.shoot(alice, "A1", result="hit", turn="B")
        self.shoot(bob, "J1", result="miss", turn="A")
        alice.send({"type": "shoot", "field": "A1"})
        self.assert_message(alice, "error", code="DUPLICATE_SHOT")
        self.state(alice, "shooting", turn="A", shotsAtOpponent={"A1": "hit"})

    def test_departure_after_finished_game_clears_winner_for_replacement(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        self.finish_game(alice, bob)
        alice.send({"type": "leave"})
        self.assert_lobby(bob, "opponentLeft", slot="A", player="Alice")
        self.fresh_state(bob)
        carol = self.peer()
        carol.send({"type": "join", "player": "Carol"})
        self.assert_message(carol, "welcome", slot="A", phase="placing")
        self.assert_lobby(bob, "gameStart", phase="placing")
        self.assert_lobby(carol, "gameStart", phase="placing")
        self.fresh_state(bob, "placing")

    def test_wrong_type_shot_field_is_rejected_without_changing_game(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        for field in (17, None, [], {}, True):
            with self.subTest(field=field):
                alice.send({"type": "shoot", "field": field})
                self.assert_message(alice, "error", code="CELL_OUT_OF_BOUNDS")
                self.state(alice, "shooting", turn="A", shotsAtOpponent={})
                self.state(bob, "shooting", turn="A", shotsAtOpponent={})

    def test_out_of_bounds_shots_do_not_advance_turn_or_broadcast_state(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        for field in ("K1", "A0", "A11", ""):
            with self.subTest(field=field):
                alice.send({"type": "shoot", "field": field})
                self.assert_message(alice, "error", code="CELL_OUT_OF_BOUNDS")
                self.state(alice, "shooting", turn="A", shotsAtOpponent={})
                self.state(bob, "shooting", turn="A", shotsAtOpponent={})

    def test_missing_shot_field_is_rejected_and_valid_shot_still_works(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        alice.send({"type": "shoot"})
        self.assert_message(alice, "error", code="CELL_OUT_OF_BOUNDS")
        self.shoot(alice, "A1", result="hit", turn="B")

    def test_unrecognized_type_does_not_change_an_active_game(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        alice.send({"type": "grantVictory", "winner": "A"})
        self.assert_message(alice, "error", code="UNKNOWN_TYPE")
        self.state(alice, "shooting", turn="A", shotsAtOpponent={}, winner=None)
        self.state(bob, "shooting", turn="A", shotsAtOpponent={}, winner=None)

    def test_invalid_json_does_not_disconnect_a_joined_player(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        alice.sock.sendall(b'{"type": "shoot",\n')
        self.assert_message(alice, "error", code="INVALID_JSON")
        self.state(alice, "shooting", turn="A", shotsAtOpponent={})
        self.state(bob, "shooting", turn="A", shotsAtOpponent={})
        self.shoot(alice, "A1", result="hit", turn="B")

    def test_out_of_turn_shot_does_not_damage_ships_or_notify_opponent(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        bob.send({"type": "shoot", "field": "A1"})
        self.assert_message(bob, "error", code="NOT_YOUR_TURN")
        alice_state = self.state(alice, "shooting", turn="A", shotsAtOpponent={})
        bob_state = self.state(bob, "shooting", turn="A", shotsAtOpponent={})
        self.assertEqual(alice_state["ownShips"][0]["hits"], [])
        self.assertEqual(bob_state["ownShips"][0]["hits"], [])

    def test_disconnect_racing_a_shot_notifies_once_and_leaves_fresh_waiting_state(self):
        alice, bob = self.join_pair()
        self.place_pair(alice, bob)
        barrier = threading.Barrier(2)
        failures = queue.Queue()

        def race(action):
            try:
                barrier.wait(timeout=TIMEOUT)
                action()
            except Exception as error:
                failures.put(error)

        threads = [
            threading.Thread(target=race, args=(lambda: alice.send({"type": "shoot", "field": "A1"}),)),
            threading.Thread(target=race, args=(bob.close,)),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(TIMEOUT)
            self.assertFalse(thread.is_alive())
        self.assertTrue(failures.empty(), list(failures.queue))
        events = []
        deadline = time.monotonic() + TIMEOUT
        while True:
            event = alice.receive(timeout=max(0.001, deadline - time.monotonic()))
            events.append(event)
            if event.get("type") == "opponentLeft":
                self.assertEqual(event, {"type": "opponentLeft", "slot": "B", "player": "Bob"})
                break
            self.assertIn(event.get("type"), ("result", "error", "state"), event)
            if event.get("type") == "error":
                self.assertEqual(event.get("code"), "WRONG_PHASE")
            elif event.get("type") == "state":
                self.assertEqual(event["phase"], "shooting")
                self.assertEqual(event["turn"], "B")
                self.assertEqual(event["shotsAtOpponent"], {"A1": "hit"})
        self.assert_state(alice, "waiting", turn=None, ownShips=[], shotsAtOpponent={},
                          shotsAtSelf={}, winner=None)
        alice.send({"type": "getState"})
        while True:
            event = alice.receive()
            events.append(event)
            if event.get("type") == "state":
                self.assertEqual(event, {"type": "state", "phase": "waiting", "turn": None,
                                         "ownShips": [], "shotsAtOpponent": {},
                                         "shotsAtSelf": {}, "winner": None})
                break
            self.assertEqual(event.get("type"), "error", event)
            self.assertEqual(event.get("code"), "WRONG_PHASE", event)
        self.assertEqual(sum(event.get("type") == "opponentLeft" for event in events), 1)
        self.assert_quiet(alice)

    def cli(self, name):
        client = CliClient(self.server.address, name)
        self.addCleanup(client.close)
        return client

    def cli_pair(self):
        alice = self.cli("Alice")
        self.assert_message(alice, "welcome", slot="A", player="Alice")
        self.assert_lobby(alice, "waiting", reason="warte auf Gegner")
        self.assertIsNone(alice.process.poll(), "client must wait for stdin after welcome")
        bob = self.cli("Bob")
        self.assert_message(bob, "welcome", slot="B", player="Bob")
        self.assert_lobby(bob, "gameStart", phase="placing")
        self.assert_lobby(alice, "gameStart", phase="placing")
        return alice, bob

    def test_real_client_listens_while_idle_and_q_notifies_survivor_once(self):
        alice, bob = self.cli_pair()
        self.assertEqual(bob.quit(), 0)
        self.assert_lobby(alice, "opponentLeft", slot="B", player="Bob")
        self.assert_quiet(alice)
        self.assertIsNone(alice.process.poll())
        self.assertEqual(alice.quit(), 0)

    def test_killing_real_client_notifies_survivor_and_server_accepts_replacement(self):
        alice, bob = self.cli_pair()
        bob.kill()
        self.assert_lobby(alice, "opponentLeft", slot="B", player="Bob")
        self.assert_quiet(alice)
        carol = self.cli("Carol")
        self.assert_message(carol, "welcome", slot="B", player="Carol")
        players = [{"slot": "A", "player": "Alice"}, {"slot": "B", "player": "Carol"}]
        self.assert_lobby(alice, "gameStart", phase="placing", players=players)
        self.assert_lobby(carol, "gameStart", phase="placing", players=players)
        self.assertEqual(carol.quit(), 0)
        self.assert_lobby(alice, "opponentLeft", slot="B", player="Carol")
        self.assertEqual(alice.quit(), 0)

    def run_process(self, command, **kwargs):
        try:
            return subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, timeout=TIMEOUT, **kwargs)
        except subprocess.TimeoutExpired as error:
            self.fail(f"CLI process did not finish before the deadline: {error.stdout!r}")

    def test_play_and_attack_scripts_can_be_imported_without_connecting_or_reading_stdin(self):
        for module in ("play", "tests.meilenstein_03.test_angriff"):
            with self.subTest(module=module):
                result = self.run_process(
                    [sys.executable, "-c", f"import sys; sys.argv = ['import-check', '\\0']; import {module}; print('IMPORT_OK')"],
                    cwd=ROOT, env={**os.environ, "PYTHONPATH": str(SRC)},
                )
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(result.stdout.strip(), "IMPORT_OK")

    def test_actual_attack_script_matches_direct_replies_despite_waiting_event(self):
        result = self.run_process(
            [sys.executable, "-u", str(ROOT / "tools" / "check_handshake.py"),
             self.server.address[0], "--port", str(self.server.address[1])],
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        replies = [ast.literal_eval(line.lstrip()[2:].strip())
                   for line in result.stdout.splitlines() if line.lstrip().startswith("<-")]
        direct_replies = [reply for reply in replies if reply.get("type") in ("welcome", "error")]
        self.assertEqual([reply.get("code") for reply in direct_replies],
                         ["UNKNOWN_TYPE", "UNKNOWN_TYPE", "MISSING_PLAYER", None,
                          "ALREADY_JOINED", "INVALID_JSON", "INVALID_JSON"])
        self.assertEqual(direct_replies[3]["player"], "Bob")

    def test_real_play_waits_places_on_start_and_replaces_fleet_after_disconnect(self):
        alice = CliClient(self.server.address, "Alice", script="play.py")
        self.addCleanup(alice.close)
        alice.wait_output("Willkommen")
        alice.wait_output("warte auf Gegner")
        alice.command("state")
        first_state = alice.wait_output("Zustand -> Phase: waiting")
        self.assertIn("eigene Schiffe: 0", first_state)
        self.assertFalse(any("Flotte platziert" in line for line in alice.output))
        bob = self.peer()
        bob.send({"type": "join", "player": "Bob"})
        self.assert_message(bob, "welcome", slot="B")
        self.assert_lobby(bob, "gameStart", phase="placing")
        alice.wait_output("Flotte platziert")
        self.assert_state(bob, "placing", turn=None, ownShips=[])
        bob.send({"type": "place", "ships": FLEET})
        self.assert_message(bob, "placeAck", phase="shooting")
        self.assert_state(bob, "shooting", turn="A")
        self.state(bob, "shooting", turn="A")
        bob.close()
        alice.wait_output("Bob hat das Spiel verlassen")
        alice.command("state")
        reset_state = alice.wait_output("Zustand -> Phase: waiting")
        self.assertIn("eigene Schiffe: 0", reset_state)
        carol = self.peer()
        carol.send({"type": "join", "player": "Carol"})
        self.assert_message(carol, "welcome", slot="B")
        self.assert_lobby(carol, "gameStart", phase="placing")
        alice.wait_output("Flotte platziert")
        self.assert_state(carol, "placing", turn=None, ownShips=[])
        carol.send({"type": "place", "ships": FLEET})
        self.assert_message(carol, "placeAck", phase="shooting")
        self.assert_state(carol, "shooting", turn="A")
        self.state(carol, "shooting", turn="A")
        alice.command("state")
        final_state = alice.wait_output("Zustand -> Phase: shooting")
        self.assertIn("eigene Schiffe: 5", final_state)
        self.assertEqual(sum("Flotte platziert" in line for line in alice.output), 2)
        self.assertFalse(any("WRONG_PHASE" in line for line in alice.output))
        self.assertEqual(alice.quit(), 0)
        self.assert_lobby(carol, "opponentLeft", slot="A", player="Alice")


if __name__ == "__main__":
    unittest.main(verbosity=2, buffer=True)
