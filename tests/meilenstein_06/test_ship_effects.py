"""Bestaetigte eigene Schiffsverluste auf echten Tk-Canvas-Feldern animieren."""
from __future__ import annotations

import importlib.util
import time
import unittest

from tests.meilenstein_04 import test_gui as gui_helpers

tk = gui_helpers.tk
if importlib.util.find_spec("ship_effects") is not None:
    import ship_effects
else:
    ship_effects = None


def destroyer(hits=(), cells=("A1", "B1")):
    return {"type": "Destroyer", "cells": list(cells), "hits": list(hits)}


class ShipEffectsTests(unittest.TestCase):
    requires_gui = True
    setUpClass = classmethod(gui_helpers.GuiTests.setUpClass.__func__)

    def setUp(self):
        self.assertIsNotNone(ship_effects, "ship_effects.py mit ShipEffects fehlt")
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.errors = []
        self.root.report_callback_exception = lambda *error: self.errors.append(error)
        self.cells = {}
        for index, field in enumerate(("A1", "B1", "C1", "D1")):
            canvas = tk.Canvas(self.root, width=32, height=32, highlightthickness=0)
            canvas.grid(row=0, column=index)
            canvas.create_rectangle(0, 0, 32, 32, fill="#123c55", tags="board")
            self.cells[field] = canvas
        self.root.update_idletasks()
        self.enabled = True
        self.effects = ship_effects.ShipEffects(
            self.root, self.cells, enabled=lambda: self.enabled,
        )
        self.addCleanup(self.effects.close)

    def explosion_items(self):
        return [
            (canvas, item)
            for canvas in self.cells.values()
            for item in canvas.find_withtag("explosion")
        ]

    def assert_explosion_visible(self):
        self.assertTrue(self.effects.active, "Ein neuer Schiffsverlust muss animieren")
        items = self.explosion_items()
        self.assertTrue(items, "Die Animation muss sichtbare Canvas-Elemente zeichnen")
        self.assertTrue(any(
            canvas.itemcget(item, "state") != "hidden" and canvas.bbox(item)
            for canvas, item in items
        ))

    def wait_for_finish(self, timeout=3):
        deadline = time.monotonic() + timeout
        while self.effects.active and time.monotonic() < deadline:
            self.root.update()
            time.sleep(0.005)
        self.assertFalse(self.effects.active, "Die kleine Explosion muss von selbst enden")
        self.assertFalse(self.explosion_items(), "Beendete Effekte muessen verschwinden")
        self.assertEqual(self.errors, [], "Tk-Callbacks duerfen keine Fehler ausloesen")

    def assert_cancelled(self, pending_before):
        self.assertFalse(self.effects.active)
        self.assertFalse(self.explosion_items())
        self.assertEqual(set(self.root.tk.call("after", "info")), pending_before)
        self.root.update()
        self.assertEqual(self.errors, [])
        self.assertTrue(all(canvas.find_withtag("board") for canvas in self.cells.values()))

    def test_only_last_confirmed_hit_starts_a_visible_temporary_explosion(self):
        self.effects.observe([destroyer()])
        self.effects.observe([destroyer(("A1",))])
        self.assertFalse(self.effects.active)
        self.assertFalse(self.explosion_items())
        self.effects.observe([destroyer(("A1", "B1"))])
        self.assert_explosion_visible()
        self.wait_for_finish()

    def test_initially_sunk_ship_and_repeated_states_do_not_replay(self):
        self.effects.observe([destroyer(("A1", "B1"))])
        self.assertFalse(self.effects.active, "Ein erster Zustand ist keine neue Versenkung")
        self.assertFalse(self.explosion_items())
        self.effects.reset()
        self.effects.observe([destroyer(("A1",))])
        sunk = destroyer(("A1", "B1"))
        self.effects.observe([sunk])
        self.assert_explosion_visible()
        self.effects.observe([sunk])
        self.wait_for_finish()
        self.effects.observe([sunk])
        self.assertFalse(self.effects.active)
        self.assertFalse(self.explosion_items())

    def test_disabled_effects_consume_the_loss_without_later_replay(self):
        self.effects.observe([destroyer()])
        self.enabled = False
        sunk = destroyer(("A1", "B1"))
        self.effects.observe([sunk])
        self.assertFalse(self.effects.active)
        self.assertFalse(self.explosion_items())
        self.enabled = True
        self.effects.observe([sunk])
        self.assertFalse(self.effects.active, "Einschalten darf alte Verluste nicht nachholen")
        self.assertFalse(self.explosion_items())

    def test_same_type_at_new_cells_is_a_new_ship_identity(self):
        self.effects.observe([destroyer()])
        self.effects.observe([destroyer(("C1", "D1"), cells=("C1", "D1"))])
        self.assertFalse(self.effects.active, "Ein erstmals gesehenes Schiff ist kein Uebergang")
        self.assertFalse(self.explosion_items())

    def test_empty_state_cancels_and_allows_new_round_transition(self):
        pending_before = set(self.root.tk.call("after", "info"))
        self.effects.observe([destroyer()])
        self.effects.observe([destroyer(("A1", "B1"))])
        self.assert_explosion_visible()
        self.effects.observe([])
        self.assert_cancelled(pending_before)
        self.effects.observe([destroyer()])
        self.effects.observe([destroyer(("A1", "B1"))])
        self.assert_explosion_visible()

    def test_reset_cancels_callbacks_and_preserves_the_board(self):
        pending_before = set(self.root.tk.call("after", "info"))
        self.effects.observe([destroyer()])
        self.effects.observe([destroyer(("A1", "B1"))])
        self.assert_explosion_visible()
        self.effects.reset()
        self.assert_cancelled(pending_before)

    def test_close_cancels_callbacks_and_remains_safe_when_called_twice(self):
        pending_before = set(self.root.tk.call("after", "info"))
        self.effects.observe([destroyer()])
        self.effects.observe([destroyer(("A1", "B1"))])
        self.assert_explosion_visible()
        self.effects.close()
        self.effects.close()
        self.assert_cancelled(pending_before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
