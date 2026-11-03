"""Nach dem Spielende ist eine Anfrage per Klick und ihre Ablehnung sichtbar."""
import socket
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from tests.meilenstein_04 import test_gui as hilfen


class EndklickTests(unittest.TestCase):
    requires_gui = True
    setUpClass = classmethod(hilfen.GuiTests.setUpClass.__func__)

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
        vorher = hilfen.GuiTests.board_snapshot(self)
        self.assertEqual(str(self.window.target_buttons["H10"].cget("state")), "normal")
        self.window.target_buttons["H10"].invoke()
        self.assertEqual(self.peer.read(), {"type": "shoot", "field": "H10"})
        self.assertEqual(hilfen.GuiTests.board_snapshot(self), vorher)
        self.window.process_message({"type": "error", "code": "WRONG_PHASE",
                                     "message": "aktuelle Phase ist finished, nicht shooting"})
        self.assertIn("finished", self.window.status_var.get())
        self.assertEqual(hilfen.GuiTests.board_snapshot(self), vorher)


if __name__ == "__main__":
    unittest.main(verbosity=2)
