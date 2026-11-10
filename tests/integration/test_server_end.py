"""Server-Endfolge an der wirklichen Serialisierung pruefen."""
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


class EndfolgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.game = server.new_game(log_file=Path(self.temp.name) / "m5.jsonl")
        self.addCleanup(self.game["event_log"].close)
        self.chronik = []
        self.alice = Draht("A", self.chronik)
        self.bob = Draht("B", self.chronik)
        self.a = {"slot": None, "leaving": False}
        self.b = {"slot": None, "leaving": False}
        self.senden({"type": "join", "player": "Alice"}, self.a, self.alice)
        self.senden({"type": "join", "player": "Bob"}, self.b, self.bob)
        self.senden({"type": "place", "ships": FLEET}, self.a, self.alice)
        andere_flotte = copy.deepcopy(FLEET)
        for schiff in andere_flotte:
            schiff["start"] = "F" + schiff["start"][1:]
        self.senden({"type": "place", "ships": andere_flotte}, self.b, self.bob)
        self.alice.leeren()
        self.bob.leeren()
        self.chronik.clear()

    def senden(self, nachricht, verbindung, draht):
        with redirect_stdout(io.StringIO()):
            server.handle(nachricht, verbindung, self.game, draht)

    def beenden(self):
        for feld, wasser in zip(ZIELE[:-1], MISSES):
            self.senden({"type": "shoot", "field": feld}, self.a, self.alice)
            self.senden({"type": "shoot", "field": wasser}, self.b, self.bob)
        self.alice.leeren()
        self.bob.leeren()
        self.chronik.clear()
        self.senden({"type": "shoot", "field": "G5"}, self.a, self.alice)

    def test_sieg_sendet_erst_result_dann_beide_sichten_dann_beide_enden(self):
        self.beenden()
        self.assertEqual([(slot, n["type"]) for slot, n in self.chronik], [
            ("A", "result"), ("A", "state"), ("B", "state"),
            ("A", "gameOver"), ("B", "gameOver"),
        ])
        self.assertEqual(self.chronik[0][1]["turn"], None)
        for slot, nachricht in self.chronik[1:3]:
            self.assertEqual((nachricht["phase"], nachricht["winner"], nachricht["turn"]),
                             ("finished", "A", None))
            self.assertEqual(nachricht["ownShips"][0]["cells"],
                             ["A1", "B1", "C1", "D1", "E1"] if slot == "A"
                             else ["F1", "G1", "H1", "I1", "J1"])
        self.assertEqual(self.chronik[3][1], {"type": "gameOver", "winner": "A", "reason": "sunk"})
        self.assertEqual(self.chronik[4][1], self.chronik[3][1])

    def test_schuss_nach_ende_bleibt_privat_und_aendert_nichts(self):
        self.beenden()
        self.alice.leeren()
        self.bob.leeren()
        vorher = copy.deepcopy(self.game["core"].__dict__)
        self.senden({"type": "shoot", "field": "H10"}, self.a, self.alice)
        self.assertEqual([n["type"] for n in self.alice.leeren()], ["error"])
        self.assertEqual(self.bob.leeren(), [])
        self.assertEqual(self.game["core"].__dict__, vorher)


if __name__ == "__main__":
    unittest.main(verbosity=2)
