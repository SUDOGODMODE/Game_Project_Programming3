"""Echte Fensteraktionen: private Schiffsverluste und sichere Effekt-Lebensdauer."""
import select
import threading
import unittest

from tests.meilenstein_04 import test_gui as gui_helpers


class GraphicsIntegrationTests(unittest.TestCase):
    requires_gui = True
    setUpClass = classmethod(gui_helpers.GuiTests.setUpClass.__func__)
    setUp = gui_helpers.GuiTests.setUp
    tearDown = gui_helpers.GuiTests.tearDown

    def own_ship(self, hits=()):
        return {"type": "Destroyer", "cells": ["A1", "B1"], "hits": list(hits)}

    def test_only_last_confirmed_own_hit_starts_effect_and_reset_cancels_it(self):
        callbacks = set(self.root.tk.call("after", "info"))
        errors = []
        self.root.report_callback_exception = lambda *error: errors.append(error)
        self.window.draw_state(gui_helpers.state())
        self.window.process_message({"type": "result", "field": "C1", "result": "sunk"})
        self.window.draw_state(gui_helpers.state(shotsAtOpponent={"C1": "sunk"}))
        self.assertFalse(self.window.effects.active)
        self.window.draw_state(gui_helpers.state(ownShips=[self.own_ship(("A1",))]))
        self.assertFalse(self.window.effects.active)
        self.window.draw_state(gui_helpers.state(
            phase="finished", turn=None, winner="B",
            ownShips=[self.own_ship(("A1", "B1"))],
            shotsAtSelf={"A1": "hit", "B1": "sunk"},
        ))
        self.assertTrue(self.window.effects.active)
        self.assertTrue(self.window.own_buttons["A1"].find_withtag("explosion"))
        self.assertFalse(any(cell.find_withtag("explosion") for cell in self.window.target_buttons.values()))
        self.window.draw_state(gui_helpers.state(phase="waiting", turn=None, ownShips=[]))
        self.assertFalse(self.window.effects.active)
        self.assertFalse(any(cell.find_withtag("explosion") for cell in self.window.own_buttons.values()))
        self.assertEqual(set(self.root.tk.call("after", "info")), callbacks)
        self.root.update()
        self.assertEqual(errors, [])

    def test_quick_disable_enable_keeps_the_next_loss_detectable(self):
        self.window.draw_state(gui_helpers.state())
        callbacks = set(self.root.tk.call("after", "info"))
        self.window.effects_enabled.set(False)
        self.window._toggle_effects()
        self.window.effects_enabled.set(True)
        self.window._toggle_effects()
        self.window.draw_state(gui_helpers.state(ownShips=[self.own_ship(("A1", "B1"))]))
        self.assertTrue(self.window.effects.active)
        self.assertTrue(self.window.own_buttons["A1"].find_withtag("explosion"))
        self.window.effects_enabled.set(False)
        self.window._toggle_effects()
        self.assertFalse(self.window.effects.active)
        self.assertEqual(set(self.root.tk.call("after", "info")), callbacks)

    def test_disconnect_clears_running_effect_before_window_close(self):
        self.window.draw_state(gui_helpers.state())
        self.window.draw_state(gui_helpers.state(ownShips=[self.own_ship(("A1", "B1"))]))
        self.assertTrue(self.window.effects.active)
        self.window.process_message({"type": "disconnected", "message": "Testende"})
        self.assertFalse(self.window.effects.active)
        self.assertFalse(any(cell.find_withtag("explosion") for cell in self.window.own_buttons.values()))
        self.window.close()
        self.window.send_thread.join(1)
        self.window.receive_thread.join(1)
        self.assertFalse(self.window.send_thread.is_alive())
        self.assertFalse(self.window.receive_thread.is_alive())

    def test_keyboard_target_actions_stay_on_tk_thread_and_send_only_requests(self):
        self.window.draw_state(gui_helpers.state())
        self.root.deiconify()
        self.root.update()
        target = self.window.target_buttons["A1"]
        target.focus_force()
        self.root.update()
        thread_ids = []
        original = self.window.shoot

        def record_shot(field):
            thread_ids.append(threading.get_ident())
            original(field)

        self.window.shoot = record_shot
        target.event_generate("<Return>")
        self.root.update()
        self.assertEqual(self.peer.read(), {"type": "shoot", "field": "A1"})
        target.event_generate("<Right>")
        self.root.update()
        self.assertEqual(self.root.focus_get(), self.window.target_buttons["B1"])
        self.window.target_buttons["B1"].event_generate("<space>")
        self.root.update()
        self.assertEqual(self.peer.read(), {"type": "shoot", "field": "B1"})
        self.assertEqual(thread_ids, [threading.get_ident()] * 2)
        self.assertEqual(target.cget("text"), "")
        self.assertEqual(self.window.target_buttons["B1"].cget("text"), "")
        self.window.draw_state(gui_helpers.state(phase="waiting", ownShips=[], turn=None))
        self.window.target_buttons["B1"].event_generate("<Return>")
        self.root.update()
        self.assertEqual(select.select([self.remote], [], [], .05)[0], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
