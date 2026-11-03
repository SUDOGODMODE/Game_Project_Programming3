"""Eigenstaendige Regeltests fuer den Schiffe-versenken-Kern (Kurs-M5)."""
import copy
import unittest

from spiel import BattleshipGame, RuleError


FLOTTE = [
    {"type": "Carrier", "start": "A1", "direction": "h"},
    {"type": "Battleship", "start": "A2", "direction": "h"},
    {"type": "Cruiser", "start": "A3", "direction": "h"},
    {"type": "Submarine", "start": "A4", "direction": "h"},
    {"type": "Destroyer", "start": "A5", "direction": "h"},
]
TREFFER = ("A1", "B1", "C1", "D1", "E1", "A2", "B2", "C2", "D2",
           "A3", "B3", "C3", "A4", "B4", "C4", "A5", "B5")
WASSER = ("J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8", "J9",
          "J10", "I1", "I2", "I3", "I4", "I5", "I6")


class TestSpiel(unittest.TestCase):
    def spiel(self, bereit=False):
        spiel = BattleshipGame()
        if bereit:
            spiel.start()
            spiel.place_fleet("A", copy.deepcopy(FLOTTE))
            spiel.place_fleet("B", copy.deepcopy(FLOTTE))
        return spiel

    def abgelehnt(self, spiel, code, aktion, *argumente):
        vorher = copy.deepcopy(spiel.__dict__)
        with self.assertRaises(RuleError) as gefangen:
            aktion(*argumente)
        self.assertEqual(gefangen.exception.code, code)
        self.assertTrue(str(gefangen.exception))
        self.assertEqual(spiel.__dict__, vorher)

    def test_anfang_und_start_trennen_warten_vom_platzieren(self):
        spiel = self.spiel()
        self.assertEqual((spiel.phase, spiel.turn, spiel.winner), ("waiting", None, None))
        self.assertEqual(spiel.state("A")["ownShips"], [])
        spiel.start()
        self.assertEqual((spiel.phase, spiel.turn), ("placing", None))

    def test_platzieren_vor_start_wird_ohne_aenderung_abgelehnt(self):
        spiel = self.spiel()
        self.abgelehnt(spiel, "WRONG_PHASE", spiel.place_fleet, "A", FLOTTE)

    def test_schiessen_vor_beiden_flotten_wird_abgelehnt(self):
        spiel = self.spiel()
        spiel.start()
        spiel.place_fleet("A", FLOTTE)
        self.abgelehnt(spiel, "WRONG_PHASE", spiel.shoot, "A", "A1")

    def test_falsche_schiffszahl_wird_abgelehnt(self):
        spiel = self.spiel()
        spiel.start()
        self.abgelehnt(spiel, "INVALID_PLACEMENT", spiel.place_fleet, "A", FLOTTE[:-1])

    def test_ueberlappung_wird_abgelehnt(self):
        spiel = self.spiel()
        spiel.start()
        flotte = copy.deepcopy(FLOTTE)
        flotte[1]["start"] = "A1"
        self.abgelehnt(spiel, "INVALID_PLACEMENT", spiel.place_fleet, "A", flotte)

    def test_rasterueberstand_wird_abgelehnt(self):
        spiel = self.spiel()
        spiel.start()
        flotte = copy.deepcopy(FLOTTE)
        flotte[0]["start"] = "J10"
        self.abgelehnt(spiel, "INVALID_PLACEMENT", spiel.place_fleet, "A", flotte)

    def test_zweite_platzierung_wird_abgelehnt(self):
        spiel = self.spiel()
        spiel.start()
        spiel.place_fleet("A", FLOTTE)
        self.abgelehnt(spiel, "WRONG_PHASE", spiel.place_fleet, "A", FLOTTE)

    def test_nach_beiden_platzierungen_beginnt_a(self):
        spiel = self.spiel(bereit=True)
        self.assertEqual((spiel.phase, spiel.turn), ("shooting", "A"))

    def test_falscher_spieler_verbraucht_keinen_zug(self):
        spiel = self.spiel(bereit=True)
        self.abgelehnt(spiel, "NOT_YOUR_TURN", spiel.shoot, "B", "A1")

    def test_ungueltiges_feld_und_bool_werden_abgelehnt(self):
        spiel = self.spiel(bereit=True)
        for feld in ("K1", "A0", "A11", None, True, 1):
            with self.subTest(feld=feld):
                self.abgelehnt(spiel, "CELL_OUT_OF_BOUNDS", spiel.shoot, "A", feld)

    def test_treffer_wechselt_den_spieler(self):
        spiel = self.spiel(bereit=True)
        self.assertEqual(spiel.shoot("A", "A1"),
                         {"field": "A1", "result": "hit", "sunk": None, "turn": "B"})
        self.assertEqual(spiel.turn, "B")

    def test_wasser_wechselt_den_spieler(self):
        spiel = self.spiel(bereit=True)
        self.assertEqual(spiel.shoot("A", "J10"),
                         {"field": "J10", "result": "miss", "sunk": None, "turn": "B"})

    def test_doppelter_schuss_verbraucht_keinen_zug(self):
        spiel = self.spiel(bereit=True)
        spiel.shoot("A", "A1")
        spiel.shoot("B", "J10")
        self.abgelehnt(spiel, "DUPLICATE_SHOT", spiel.shoot, "A", "a01")

    def test_letztes_schiffsfeld_meldet_versenkt(self):
        spiel = self.spiel(bereit=True)
        for index, feld in enumerate(TREFFER[:-1]):
            spiel.shoot("A", feld)
            spiel.shoot("B", WASSER[index])
        self.assertEqual(spiel.shoot("A", "B5"),
                         {"field": "B5", "result": "sunk", "sunk": "Destroyer", "turn": None})

    def test_gesamte_flotte_versenkt_beendet_ohne_spielerwechsel(self):
        spiel = self.spiel(bereit=True)
        for feld, wasser in zip(TREFFER[:-1], WASSER):
            spiel.shoot("A", feld)
            spiel.shoot("B", wasser)
        spiel.shoot("A", "B5")
        self.assertEqual((spiel.phase, spiel.turn, spiel.winner), ("finished", None, "A"))

    def test_nach_dem_sieg_wird_auch_ein_freies_feld_abgelehnt(self):
        spiel = self.spiel(bereit=True)
        for feld, wasser in zip(TREFFER[:-1], WASSER):
            spiel.shoot("A", feld)
            spiel.shoot("B", wasser)
        spiel.shoot("A", "B5")
        self.abgelehnt(spiel, "WRONG_PHASE", spiel.shoot, "A", "H10")

    def test_unbekannter_spieler_wird_abgelehnt(self):
        spiel = self.spiel(bereit=True)
        self.abgelehnt(spiel, "INVALID_PLAYER", spiel.shoot, "C", "A1")

    def test_geheime_flotte_bleibt_auch_im_endzustand_verborgen(self):
        spiel = self.spiel()
        spiel.start()
        spiel.place_fleet("A", FLOTTE)
        andere = copy.deepcopy(FLOTTE)
        for schiff in andere:
            schiff["start"] = "F" + schiff["start"][1:]
        spiel.place_fleet("B", andere)
        ziele = ("F1", "G1", "H1", "I1", "J1", "F2", "G2", "H2", "I2",
                 "F3", "G3", "H3", "F4", "G4", "H4", "F5", "G5")
        for feld, wasser in zip(ziele[:-1], WASSER):
            spiel.shoot("A", feld)
            spiel.shoot("B", wasser)
        spiel.shoot("A", "G5")
        sicht_a = spiel.state("A")
        sicht_b = spiel.state("B")
        self.assertEqual((sicht_a["phase"], sicht_a["winner"]), ("finished", "A"))
        self.assertEqual(sicht_a["ownShips"][0]["cells"],
                         ["A1", "B1", "C1", "D1", "E1"])
        self.assertNotIn("F1", str(sicht_a["ownShips"]))
        self.assertEqual(sicht_b["ownShips"][0]["cells"],
                         ["F1", "G1", "H1", "I1", "J1"])

    def test_zustand_ist_eine_unabhaengige_kopie(self):
        spiel = self.spiel(bereit=True)
        sicht = spiel.state("A")
        sicht["ownShips"][0]["cells"].clear()
        sicht["shotsAtOpponent"]["J10"] = "hit"
        self.assertEqual(spiel.state("A")["ownShips"][0]["cells"],
                         ["A1", "B1", "C1", "D1", "E1"])
        self.assertEqual(spiel.state("A")["shotsAtOpponent"], {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
