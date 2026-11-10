"""Das Spiel über echte TCP-Verbindungen und einen Serverprozess prüfen.

Jeder Test erhält einen frischen Prozess und einen freien Port. Weder ein
Fenster noch ein von Hand gestarteter Server ist für diesen Lauf nötig.
"""

import copy
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest

from testclient import Testclient
from test_spiel import FLOTTE, TREFFER, WASSER


HOST = "127.0.0.1"
QUELLORDNER = Path(__file__).resolve().parent
# Für den Mutationsnachweis darf SERVER auf eine isolierte Serverkopie zeigen.
SERVER = Path(os.environ.get("SERVER", QUELLORDNER / "server.py")).resolve()


def freier_port():
    """Lässt das Betriebssystem einen freien Testport wählen."""
    with socket.socket() as probe:
        probe.bind((HOST, 0))
        return probe.getsockname()[1]


class NetzTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.port = freier_port()
        self.fehlerdatei = open(Path(self.temp.name) / "server.stderr", "w+")
        self.addCleanup(self.fehlerdatei.close)
        umgebung = dict(os.environ, PORT=str(self.port))
        # Auch eine Serverkopie ausserhalb von src muss spiel/netz importieren.
        bisheriger_pfad = umgebung.get("PYTHONPATH")
        umgebung["PYTHONPATH"] = str(QUELLORDNER) + (os.pathsep + bisheriger_pfad if bisheriger_pfad else "")
        self.server = subprocess.Popen(
            [sys.executable, str(SERVER), "--host", HOST,
             "--log-file", str(Path(self.temp.name) / "server.jsonl")],
            cwd=QUELLORDNER, env=umgebung,
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=self.fehlerdatei,
        )
        self.addCleanup(self._server_stoppen)
        self._warte_auf_server()

    def _warte_auf_server(self):
        """Verhindert einen Verbindungsversuch, bevor der Prozess lauscht."""
        ende = time.monotonic() + 5
        while time.monotonic() < ende:
            if self.server.poll() is not None:
                break
            try:
                with socket.create_connection((HOST, self.port), timeout=0.2):
                    return
            except OSError:
                time.sleep(0.02)
        self.fehlerdatei.flush()
        self.fehlerdatei.seek(0)
        self.fail(f"Server startete nicht auf Port {self.port}: {self.fehlerdatei.read()}")

    def _server_stoppen(self):
        if self.server.poll() is None:
            self.server.terminate()
        try:
            self.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server.kill()
            self.server.wait(timeout=5)

    def verbinde(self, name=None):
        client = Testclient(HOST, self.port, name)
        self.addCleanup(client.schliessen)
        return client

    def meldung(self, client, typ, **felder):
        nachricht = client.erwarte(typ)
        for feld, wert in felder.items():
            self.assertEqual(nachricht[feld], wert, nachricht)
        return nachricht

    def zwei_spieler(self):
        alice = self.verbinde("Alice")
        self.meldung(alice, "welcome", slot="A", player="Alice")
        self.meldung(alice, "waiting")
        self.meldung(alice, "state", phase="waiting", turn=None)

        bob = self.verbinde("Bob")
        self.meldung(bob, "welcome", slot="B", player="Bob")
        for client in (alice, bob):
            self.meldung(client, "gameStart", phase="placing")
            self.meldung(client, "state", phase="placing", turn=None)
        return alice, bob

    def platziere(self, alice, bob, flotte_b=None):
        if flotte_b is None:
            flotte_b = FLOTTE
        alice.schicke({"type": "place", "ships": FLOTTE})
        self.meldung(alice, "placeAck", phase="placing")
        self.meldung(alice, "state", phase="placing")
        self.meldung(bob, "state", phase="placing")

        bob.schicke({"type": "place", "ships": flotte_b})
        self.meldung(bob, "placeAck", phase="shooting")
        sicht_a = self.meldung(alice, "state", phase="shooting", turn="A")
        sicht_b = self.meldung(bob, "state", phase="shooting", turn="A")
        return sicht_a, sicht_b

    def schuss(self, spieler, gegner, feld):
        spieler.schicke({"type": "shoot", "field": feld})
        ergebnis = self.meldung(spieler, "result", field=feld)
        eigene_sicht = self.meldung(spieler, "state")
        andere_sicht = self.meldung(gegner, "state")
        self.assertEqual(eigene_sicht["shotsAtOpponent"][feld], ergebnis["result"])
        self.assertEqual(andere_sicht["shotsAtSelf"][feld], ergebnis["result"])
        self.assertEqual(eigene_sicht["turn"], andere_sicht["turn"])
        return ergebnis, eigene_sicht, andere_sicht

    def test_erster_spieler_bekommt_welcome_waiting_und_state(self):
        alice = self.verbinde("Alice")
        self.meldung(alice, "welcome", slot="A", phase="waiting")
        self.meldung(alice, "waiting", reason="warte auf Gegner")
        self.meldung(alice, "state", phase="waiting", ownShips=[])

    def test_zweiter_spieler_startet_die_partie_fuer_beide(self):
        alice, bob = self.zwei_spieler()
        spieler = [{"slot": "A", "player": "Alice"}, {"slot": "B", "player": "Bob"}]
        for client in (alice, bob):
            start = next(n for n in client.alle if n["type"] == "gameStart")
            self.assertEqual(start["players"], spieler)

    def test_anfangszustand_kommt_ohne_get_state(self):
        alice, bob = self.zwei_spieler()
        for client in (alice, bob):
            start = client.alle[-1]
            self.assertEqual((start["phase"], start["turn"], start["ownShips"]),
                             ("placing", None, []))

    def test_dritter_spieler_bekommt_game_full(self):
        self.zwei_spieler()
        carla = self.verbinde("Carla")
        self.meldung(carla, "error", code="GAME_FULL")

    def test_join_ohne_namen_bekommt_missing_player(self):
        namenlos = self.verbinde()
        namenlos.schicke({"type": "join"})
        self.meldung(namenlos, "error", code="MISSING_PLAYER")

    def test_zweites_join_bekommt_already_joined(self):
        alice = self.verbinde("Alice")
        self.meldung(alice, "welcome")
        self.meldung(alice, "waiting")
        self.meldung(alice, "state")
        alice.schicke({"type": "join", "player": "Nochmals"})
        self.meldung(alice, "error", code="ALREADY_JOINED")

    def test_aktionen_vor_join_bekommen_not_joined(self):
        gast = self.verbinde()
        for nachricht in ({"type": "place", "ships": FLOTTE},
                          {"type": "shoot", "field": "A1"},
                          {"type": "getState"}, {"type": "leave"}):
            with self.subTest(typ=nachricht["type"]):
                gast.schicke(nachricht)
                self.meldung(gast, "error", code="NOT_JOINED")

    def test_unbekannter_typ_bekommt_unknown_type(self):
        gast = self.verbinde()
        gast.schicke({"type": "tanzen"})
        antwort = self.meldung(gast, "error", code="UNKNOWN_TYPE")
        self.assertIn("tanzen", antwort["message"])

    def test_kaputtes_json_bekommt_invalid_json(self):
        gast = self.verbinde()
        gast.sock.sendall(b'{"type": "shoot", feld\n')
        self.meldung(gast, "error", code="INVALID_JSON")
        gast.schicke({"type": "join", "player": "Alice"})
        self.meldung(gast, "welcome", slot="A")

    def test_ungueltige_flotte_bekommt_invalid_placement(self):
        alice, bob = self.zwei_spieler()
        alice.schicke({"type": "place", "ships": []})
        self.meldung(alice, "error", code="INVALID_PLACEMENT")
        alice.keine("state")
        bob.keine("state")

    def test_platzierung_ohne_gegner_bekommt_wrong_phase(self):
        alice = self.verbinde("Alice")
        self.meldung(alice, "welcome")
        self.meldung(alice, "waiting")
        self.meldung(alice, "state")
        alice.schicke({"type": "place", "ships": FLOTTE})
        self.meldung(alice, "error", code="WRONG_PHASE")

    def test_schuss_vor_beiden_flotten_wird_abgelehnt(self):
        alice, bob = self.zwei_spieler()
        alice.schicke({"type": "shoot", "field": "A1"})
        self.meldung(alice, "error", code="WRONG_PHASE")
        bob.keine("state")

    def test_ein_schuss_erreicht_beide_spieler(self):
        alice, bob = self.zwei_spieler()
        self.platziere(alice, bob)
        ergebnis, sicht_a, sicht_b = self.schuss(alice, bob, "A1")
        self.assertEqual(ergebnis["result"], "hit")
        self.assertEqual(sicht_a["turn"], "B")
        self.assertEqual(sicht_b["ownShips"][0]["hits"], ["A1"])

    def test_ganze_partie_mit_33_schuessen_bis_zum_sieg(self):
        alice, bob = self.zwei_spieler()
        self.platziere(alice, bob)
        anzahl = 0
        for index, feld in enumerate(TREFFER):
            ergebnis, sicht_a, sicht_b = self.schuss(alice, bob, feld)
            anzahl += 1
            if index == len(TREFFER) - 1:
                self.assertEqual((ergebnis["result"], ergebnis["turn"]), ("sunk", None))
                self.assertEqual((sicht_a["phase"], sicht_b["phase"]), ("finished", "finished"))
                for client in (alice, bob):
                    self.meldung(client, "gameOver", winner="A", reason="sunk")
            else:
                self.assertEqual(ergebnis["turn"], "B")
                gegenzug, _, _ = self.schuss(bob, alice, WASSER[index])
                self.assertEqual((gegenzug["result"], gegenzug["turn"]), ("miss", "A"))
                anzahl += 1
        self.assertEqual(anzahl, 33)

    def test_falscher_spieler_bekommt_not_your_turn(self):
        alice, bob = self.zwei_spieler()
        self.platziere(alice, bob)
        bob.schicke({"type": "shoot", "field": "A1"})
        self.meldung(bob, "error", code="NOT_YOUR_TURN")

    def test_feld_ausserhalb_bekommt_cell_out_of_bounds(self):
        alice, bob = self.zwei_spieler()
        self.platziere(alice, bob)
        alice.schicke({"type": "shoot", "field": "K1"})
        self.meldung(alice, "error", code="CELL_OUT_OF_BOUNDS")

    def test_doppelbeschuss_bekommt_duplicate_shot(self):
        alice, bob = self.zwei_spieler()
        self.platziere(alice, bob)
        self.schuss(alice, bob, "A1")
        self.schuss(bob, alice, "J1")
        alice.schicke({"type": "shoot", "field": "A1"})
        self.meldung(alice, "error", code="DUPLICATE_SHOT")
        alice.schicke({"type": "getState"})
        self.meldung(alice, "state", turn="A")

    def test_ablehnung_ist_privat_und_aendert_keinen_zustand(self):
        alice, bob = self.zwei_spieler()
        self.platziere(alice, bob)
        bob.schicke({"type": "shoot", "field": "A1"})
        self.meldung(bob, "error", code="NOT_YOUR_TURN")
        alice.keine("state")
        self.assertFalse(any(n["type"] == "error" for n in alice.alle))
        bob.keine("state")
        for client in (alice, bob):
            client.schicke({"type": "getState"})
            stand = self.meldung(client, "state", turn="A")
            self.assertEqual(stand["shotsAtOpponent"], {})
            self.assertEqual(stand["shotsAtSelf"], {})

    def test_jeder_sieht_nur_seine_eigene_flotte(self):
        alice, bob = self.zwei_spieler()
        andere_flotte = copy.deepcopy(FLOTTE)
        for schiff in andere_flotte:
            schiff["start"] = "F" + schiff["start"][1:]
        sicht_a, sicht_b = self.platziere(alice, bob, andere_flotte)
        self.assertEqual(sicht_a["ownShips"][0]["cells"], ["A1", "B1", "C1", "D1", "E1"])
        self.assertEqual(sicht_b["ownShips"][0]["cells"], ["F1", "G1", "H1", "I1", "J1"])
        self.assertNotIn("F1", str(sicht_a["ownShips"]))
        self.assertNotIn("A1", str(sicht_b["ownShips"]))

    def test_harter_abbruch_meldet_opponent_left(self):
        alice, bob = self.zwei_spieler()
        bob.schliessen()
        self.meldung(alice, "opponentLeft", slot="B", player="Bob")
        self.meldung(alice, "state", phase="waiting", ownShips=[])

    def test_server_lebt_nach_hartem_abbruch_und_vergibt_slot_erneut(self):
        alice, bob = self.zwei_spieler()
        bob.schliessen()
        self.meldung(alice, "opponentLeft", slot="B", player="Bob")
        self.meldung(alice, "state", phase="waiting")
        carla = self.verbinde("Carla")
        self.meldung(carla, "welcome", slot="B", player="Carla")
        self.meldung(alice, "gameStart", phase="placing")
        self.meldung(alice, "state", phase="placing")
        self.meldung(carla, "gameStart", phase="placing")
        self.meldung(carla, "state", phase="placing")
        self.assertIsNone(self.server.poll(), "Serverprozess ist gestorben")


if __name__ == "__main__":
    unittest.main(verbosity=2)
