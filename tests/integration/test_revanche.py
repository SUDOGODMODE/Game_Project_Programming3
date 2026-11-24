"""Revanche, Punktestand und Ablehnungen an der wirklichen Serialisierung pruefen."""
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout

import server
from tests.fixtures import FLEET, MISSES


ZIELE = ("F1", "G1", "H1", "I1", "J1", "F2", "G2", "H2", "I2",
         "F3", "G3", "H3", "F4", "G4", "H4", "F5", "G5")
ANDERE_FLOTTE = copy.deepcopy(FLEET)
for _schiff in ANDERE_FLOTTE:
    _schiff["start"] = "F" + _schiff["start"][1:]


class Draht:
    def __init__(self, name, chronik):
        self.name = name
        self.chronik = chronik
        self.nachrichten = []

    def sendall(self, daten):
        for zeile in daten.decode().splitlines():
            nachricht = json.loads(zeile)
            self.nachrichten.append(nachricht)
            self.chronik.append((self.name, nachricht))

    def leeren(self):
        nachrichten, self.nachrichten = self.nachrichten, []
        return nachrichten


class RevancheTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.game = server.new_game(log_file=Path(temp.name) / "m8.jsonl")
        self.addCleanup(self.game["event_log"].close)
        self.chronik = []
        self.alice = Draht("Alice", self.chronik)
        self.bob = Draht("Bob", self.chronik)
        self.carla = Draht("Carla", self.chronik)
        self.a = {"slot": None, "leaving": False}
        self.b = {"slot": None, "leaving": False}
        self.z = {"slot": None, "leaving": False}
        self.senden({"type": "join", "player": "Alice"}, self.a, self.alice)
        self.senden({"type": "join", "player": "Bob"}, self.b, self.bob)
        self.senden({"type": "join", "player": "Carla"}, self.z, self.carla)
        self.leeren()

    def senden(self, nachricht, verbindung, draht):
        with redirect_stdout(io.StringIO()):
            server.handle(nachricht, verbindung, self.game, draht)

    def leeren(self):
        for draht in (self.alice, self.bob, self.carla):
            draht.leeren()
        self.chronik.clear()

    def partie(self, erster, zweiter):
        """Platziert beide Flotten; der Spieler in Slot A versenkt alles."""
        self.senden({"type": "place", "ships": FLEET}, *erster)
        self.senden({"type": "place", "ships": ANDERE_FLOTTE}, *zweiter)
        for feld, wasser in zip(ZIELE[:-1], MISSES):
            self.senden({"type": "shoot", "field": feld}, *erster)
            self.senden({"type": "shoot", "field": wasser}, *zweiter)
        self.senden({"type": "shoot", "field": ZIELE[-1]}, *erster)
        self.assertEqual(self.game["core"].phase, "finished")

    def wunsch(self, verbindung, draht):
        self.senden({"type": "rematch"}, verbindung, draht)

    def test_revanche_bei_laufender_partie_nur_dem_absender_abgelehnt(self):
        self.wunsch(self.a, self.alice)
        self.assertEqual([(name, n["type"], n.get("code")) for name, n in self.chronik],
                         [("Alice", "error", "WRONG_PHASE")])
        self.assertEqual(self.game["rematch"], set())

    def test_zuschauer_und_doppelter_wunsch_nur_dem_absender_abgelehnt(self):
        self.partie((self.a, self.alice), (self.b, self.bob))
        self.leeren()
        self.wunsch(self.z, self.carla)
        self.assertEqual([(name, n["type"], n.get("code")) for name, n in self.chronik],
                         [("Carla", "error", "SPECTATOR_ONLY")])
        self.wunsch(self.a, self.alice)
        self.leeren()
        self.wunsch(self.a, self.alice)
        self.assertEqual([(name, n["type"], n.get("code")) for name, n in self.chronik],
                         [("Alice", "error", "DUPLICATE_REMATCH")])
        for _, nachricht in self.chronik:
            self.assertTrue(nachricht["message"])

    def test_erster_wunsch_meldet_alle_und_startet_noch_nichts(self):
        self.partie((self.a, self.alice), (self.b, self.bob))
        kern = self.game["core"]
        self.leeren()
        self.wunsch(self.a, self.alice)
        meldung = {"type": "rematchRequested", "slot": "A", "player": "Alice"}
        self.assertEqual(self.chronik, [("Alice", meldung), ("Bob", meldung), ("Carla", meldung)])
        self.assertIs(self.game["core"], kern)
        self.assertEqual(kern.phase, "finished")

    def test_punktestand_steht_im_endzustand_aller(self):
        self.partie((self.a, self.alice), (self.b, self.bob))
        erwartet = [{"slot": "A", "player": "Alice", "wins": 1}, {"slot": "B", "player": "Bob", "wins": 0}]
        for draht in (self.alice, self.bob, self.carla):
            zustand = [n for n in draht.leeren() if n["type"] == "state"][-1]
            self.assertEqual((zustand["phase"], zustand["score"]), ("finished", erwartet))

    def test_zwei_wuensche_starten_neues_objekt_und_der_andere_beginnt(self):
        self.partie((self.a, self.alice), (self.b, self.bob))
        alter_kern = self.game["core"]
        self.wunsch(self.a, self.alice)
        self.leeren()
        self.wunsch(self.b, self.bob)

        self.assertIsNot(self.game["core"], alter_kern)
        self.assertEqual(self.game["rematch"], set())
        self.assertEqual((self.a["slot"], self.b["slot"]), ("B", "A"))
        self.assertEqual([(name, n["type"]) for name, n in self.chronik], [
            ("Bob", "welcome"), ("Alice", "welcome"),
            ("Bob", "gameStart"), ("Alice", "gameStart"), ("Carla", "gameStart"),
            ("Bob", "state"), ("Alice", "state"), ("Carla", "state"),
        ])
        self.assertEqual(self.chronik[0][1], {"type": "welcome", "slot": "A", "player": "Bob", "phase": "placing"})
        self.assertEqual(self.chronik[1][1], {"type": "welcome", "slot": "B", "player": "Alice", "phase": "placing"})
        self.assertEqual(self.chronik[2][1]["players"],
                         [{"slot": "A", "player": "Bob"}, {"slot": "B", "player": "Alice"}])
        punktestand = [{"slot": "A", "player": "Bob", "wins": 0}, {"slot": "B", "player": "Alice", "wins": 1}]
        leer = {"type": "state", "phase": "placing", "turn": None, "ownShips": [],
                "shotsAtOpponent": {}, "shotsAtSelf": {}, "winner": None, "score": punktestand}
        for _, zustand in self.chronik[5:]:
            self.assertEqual(zustand, leer)

        # Bob beginnt jetzt als A; sein Sieg zaehlt fuer ihn, nicht fuer den Slot.
        self.leeren()
        self.partie((self.b, self.bob), (self.a, self.alice))
        zustand = [n for n in self.carla.leeren() if n["type"] == "state"][-1]
        self.assertEqual(zustand["score"], [{"slot": "A", "player": "Bob", "wins": 1},
                                            {"slot": "B", "player": "Alice", "wins": 1}])

    def test_erster_schuss_der_revanche_kommt_vom_anderen_spieler(self):
        self.partie((self.a, self.alice), (self.b, self.bob))
        self.wunsch(self.b, self.bob)
        self.wunsch(self.a, self.alice)
        self.senden({"type": "place", "ships": FLEET}, self.a, self.alice)
        self.senden({"type": "place", "ships": ANDERE_FLOTTE}, self.b, self.bob)
        self.leeren()
        self.senden({"type": "shoot", "field": "A1"}, self.a, self.alice)
        self.assertEqual([n.get("code") for n in self.alice.leeren()], ["NOT_YOUR_TURN"])
        self.senden({"type": "shoot", "field": "A1"}, self.b, self.bob)
        self.assertEqual(self.bob.leeren()[0]["type"], "result")

    def test_abgang_verwirft_offenen_wunsch_und_punktestand(self):
        self.partie((self.a, self.alice), (self.b, self.bob))
        self.wunsch(self.a, self.alice)
        self.leeren()
        with redirect_stdout(io.StringIO()):
            server.remove_player(self.b, self.game)
        self.assertEqual(self.game["rematch"], set())
        zustand = [n for n in self.alice.leeren() if n["type"] == "state"][-1]
        self.assertEqual(zustand["score"], [{"slot": "A", "player": "Alice", "wins": 0}])
        self.wunsch(self.a, self.alice)
        self.assertEqual([n.get("code") for n in self.alice.leeren()], ["WRONG_PHASE"])

    def test_abgang_nach_slottausch_gibt_den_richtigen_slot_frei(self):
        self.partie((self.a, self.alice), (self.b, self.bob))
        self.wunsch(self.a, self.alice)
        self.wunsch(self.b, self.bob)
        with redirect_stdout(io.StringIO()):
            server.remove_player(self.b, self.game)  # Bob ist nach dem Tausch A
        self.assertEqual(self.game["taken"], ["B"])
        self.assertEqual(self.game["players"]["B"]["name"], "Alice")
        dana = {"slot": None, "leaving": False}
        self.senden({"type": "join", "player": "Dana"}, dana, Draht("Dana", self.chronik))
        self.assertEqual((dana["slot"], self.a["slot"], self.z.get("spectator")), ("A", "B", True))

    def test_revanche_vor_join_wird_abgelehnt(self):
        fremd = Draht("Fremd", self.chronik)
        self.wunsch({"slot": None, "leaving": False}, fremd)
        self.assertEqual([n.get("code") for n in fremd.leeren()], ["NOT_JOINED"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
