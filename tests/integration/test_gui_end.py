"""Nach dem Spielende ist eine Anfrage per Klick und ihre Ablehnung sichtbar."""
import socket
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from tests import gui_helpers as hilfen


class EndklickTests(hilfen.GuiTestCase):
    requires_gui = True

    def setUp(self):
        self.root = hilfen.tk.Tk()
        self.root.withdraw()
        self.local, self.remote = socket.socketpair()
        self.peer = hilfen.Peer(self.remote)
        self.window = hilfen.client_gui.BattleshipWindow(self.root, self.local, "Alice")
        self.assertEqual(self.peer.read(), {"type": "join", "player": "Alice"})
        self.window.process_message({"type": "welcome", "slot": "A", "player": "Alice"})

    def tearDown(self):
        self.window.close()
        self.remote.close()
        try:
            self.root.destroy()
        except hilfen.tk.TclError:
            pass

    def test_freies_zielfeld_nach_ende_sendet_anfrage_und_zeigt_ablehnung(self):
        ende = hilfen.state(phase="finished", turn=None, winner="A",
                           shotsAtOpponent={"A1": "sunk"})
        self.window.draw_state(ende)
        vorher = self.board_snapshot()
        self.assertEqual(str(self.window.target_buttons["H10"].cget("state")), "normal")
        self.window.target_buttons["H10"].invoke()
        self.assertEqual(self.peer.read(), {"type": "shoot", "field": "H10"})
        self.assertEqual(self.board_snapshot(), vorher)
        self.window.process_message({"type": "error", "code": "WRONG_PHASE",
                                     "message": "aktuelle Phase ist finished, nicht shooting"})
        self.assertIn("finished", self.window.status_var.get())
        self.assertEqual(self.board_snapshot(), vorher)


if __name__ == "__main__":
    unittest.main(verbosity=2)
