"""Zustandsverteilung, Ablehnungen und Geheimhaltung am Servereingang."""
import copy
import io
import json
import socket
import unittest
from contextlib import redirect_stdout

import server
from tests.fixtures import FLEET


class Wire:
    """Fängt die tatsächlich serialisierten TCP-Nachrichten eines Slots auf."""

    def __init__(self):
        self.messages = []

    def sendall(self, data):
        self.messages.extend(json.loads(line) for line in data.decode().splitlines())

    def take(self):
        messages, self.messages = self.messages, []
        return messages


class StateTests(unittest.TestCase):
    def setUp(self):
        self.game = server.new_game()
        self.alice, self.bob = Wire(), Wire()
        self.a = {"slot": None, "leaving": False}
        self.b = {"slot": None, "leaving": False}

    def handle(self, message, connection, wire):
        with redirect_stdout(io.StringIO()):
            server.handle(message, connection, self.game, wire)

    def pair(self):
        self.handle({"type": "join", "player": "Alice"}, self.a, self.alice)
        self.alice.take()
        self.handle({"type": "join", "player": "Bob"}, self.b, self.bob)
        self.alice.take()
        self.bob.take()

    def place(self):
        self.pair()
        self.handle({"type": "place", "ships": FLEET}, self.a, self.alice)
        self.alice.take()
        self.bob.take()
        different = copy.deepcopy(FLEET)
        for ship in different:
            ship["start"] = "F" + ship["start"][1:]
        self.handle({"type": "place", "ships": different}, self.b, self.bob)
        return self.alice.take(), self.bob.take()

    def test_each_successful_join_sends_lobby_then_full_state_to_every_player(self):
        self.handle({"type": "join", "player": "Alice"}, self.a, self.alice)
        messages = self.alice.take()
        self.assertEqual([m["type"] for m in messages], ["welcome", "waiting", "state"])
        self.assertEqual(messages[-1], {"type": "state", "phase": "waiting", "turn": None,
                                       "ownShips": [], "shotsAtOpponent": {},
                                       "shotsAtSelf": {}, "winner": None})
        self.handle({"type": "join", "player": "Bob"}, self.b, self.bob)
        self.assertEqual([m["type"] for m in self.alice.take()], ["gameStart", "state"])
        self.assertEqual([m["type"] for m in self.bob.take()], ["welcome", "gameStart", "state"])

    def test_place_and_shot_push_separate_complete_views_after_direct_reply(self):
        a, b = self.place()
        self.assertEqual([m["type"] for m in a], ["state"])
        self.assertEqual([m["type"] for m in b], ["placeAck", "state"])
        self.assertEqual(a[-1]["ownShips"][0]["cells"], ["A1", "B1", "C1", "D1", "E1"])
        self.assertEqual(b[-1]["ownShips"][0]["cells"], ["F1", "G1", "H1", "I1", "J1"])
        self.handle({"type": "shoot", "field": "F1"}, self.a, self.alice)
        a, b = self.alice.take(), self.bob.take()
        self.assertEqual([m["type"] for m in a], ["result", "state"])
        self.assertEqual([m["type"] for m in b], ["state"])
        self.assertEqual(a[-1]["shotsAtOpponent"], {"F1": "hit"})
        self.assertEqual(b[-1]["shotsAtSelf"], {"F1": "hit"})
        self.assertEqual(a[-1]["ownShips"][0]["hits"], [])
        self.assertEqual(b[-1]["ownShips"][0]["hits"], ["F1"])
        self.assertNotIn("F1", json.dumps(a[-1]["ownShips"]))

    def test_rejections_are_private_and_preserve_both_complete_states(self):
        self.place()
        for message, connection, wire, other, code in [
            ({"type": "shoot", "field": "A1"}, self.b, self.bob, self.alice, "NOT_YOUR_TURN"),
            ({"type": "shoot", "field": "K1"}, self.a, self.alice, self.bob, "CELL_OUT_OF_BOUNDS"),
            ({"type": "place", "ships": []}, self.a, self.alice, self.bob, "WRONG_PHASE"),
        ]:
            with self.subTest(code=code):
                before = copy.deepcopy(self.game["core"].__dict__)
                self.handle(message, connection, wire)
                replies = wire.take()
                self.assertEqual(len(replies), 1)
                self.assertEqual(replies[0]["type"], "error")
                self.assertEqual(replies[0]["code"], code)
                self.assertEqual(other.take(), [])
                self.assertEqual(self.game["core"].__dict__, before)

    def test_departure_pushes_empty_state_and_replacement_gets_fresh_round(self):
        self.place()
        self.handle({"type": "shoot", "field": "F1"}, self.a, self.alice)
        self.alice.take()
        self.bob.take()
        with redirect_stdout(io.StringIO()):
            server.remove_player(self.b, self.game)
        messages = self.alice.take()
        self.assertEqual([m["type"] for m in messages], ["opponentLeft", "state"])
        self.assertEqual(messages[-1], {"type": "state", "phase": "waiting", "turn": None,
                                       "ownShips": [], "shotsAtOpponent": {},
                                       "shotsAtSelf": {}, "winner": None})
        replacement = {"slot": None, "leaving": False}
        self.handle({"type": "join", "player": "Carol"}, replacement, self.bob)
        messages = self.alice.take()
        self.assertEqual([m["type"] for m in messages], ["gameStart", "state"])
        self.assertEqual(messages[-1]["phase"], "placing")
        self.assertEqual(messages[-1]["ownShips"], [])
        self.assertEqual(messages[-1]["shotsAtSelf"], {})

    def test_server_logs_metadata_without_fleets_or_untrusted_type_and_error_text(self):
        sender, receiver = socket.socketpair()
        self.addCleanup(sender.close)
        self.addCleanup(receiver.close)
        secret = "SECRET_FLEET_MARKER"
        payloads = [{"type": "join", "player": secret},
                    {"type": "place", "ships": FLEET},
                    {"type": {"fleet": secret}},
                    {"type": "shoot", "field": secret}]
        sender.sendall("".join(json.dumps(m) + "\n" for m in payloads).encode())
        sender.shutdown(socket.SHUT_WR)
        output = io.StringIO()
        with redirect_stdout(output):
            server.handle_connection(receiver, ("127.0.0.1", 12345), self.game)
        log = output.getvalue()
        self.assertNotIn(secret, log)
        self.assertNotIn("Carrier", log)
        self.assertNotIn("ownShips", log)
        self.assertNotIn("start", log)
        self.assertIn("place", log)
        self.assertIn("UNKNOWN_TYPE", log)


if __name__ == "__main__":
    unittest.main(verbosity=2)
