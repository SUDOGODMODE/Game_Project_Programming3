"""Actual Tk image pixels, cwd independence and main-thread object lifetime."""
import gc
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest
import weakref

from tests.meilenstein_04 import test_gui as gui_helpers

tk, client_gui = gui_helpers.tk, gui_helpers.client_gui

ROOT = Path(__file__).resolve().parents[2]


class ImageTests(unittest.TestCase):
    requires_gui = True
    setUpClass = classmethod(gui_helpers.GuiTests.setUpClass.__func__)

    def test_real_asset_is_visible_from_foreign_cwd_and_released_on_tk_thread(self):
        root = tk.Tk()
        root.withdraw()
        local, remote = socket.socketpair()
        self.addCleanup(remote.close)
        def destroy_root():
            try: root.destroy()
            except tk.TclError: pass
        self.addCleanup(destroy_root)
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                window = client_gui.BattleshipWindow(root, local, 'Image test')
            finally:
                os.chdir(original_cwd)
        self.addCleanup(window.close)
        self.assertEqual(gui_helpers.Peer(remote).read(), {'type': 'join', 'player': 'Image test'})
        self.assertIsInstance(getattr(window, 'ship_image', None), tk.PhotoImage, 'Actual own PNG image is missing')
        image = window.ship_image
        self.assertIn(image.width(), (64, 128))
        self.assertEqual(image.width(), image.height())
        self.assertEqual(str(window.ship_image_label.cget('image')), str(image))
        root.update_idletasks()
        self.assertTrue(window.ship_image_label.winfo_manager())
        pngs = list((ROOT / 'bilder').glob('*.png'))
        self.assertTrue(pngs, 'No original PNG delivered in bilder/')
        matched = False
        for path in pngs:
            original = tk.PhotoImage(master=root, file=str(path))
            if original.width() != original.height() or original.width() not in (64, 128, 256):
                continue
            factor = original.width() // image.width()
            if factor < 1 or original.width() % image.width():
                continue
            candidate = original.subsample(factor)
            coords = [(x, y) for x in range(0, image.width(), 7) for y in range(0, image.height(), 7)]
            if all(candidate.get(x, y) == image.get(x, y) and candidate.transparency_get(x, y) == image.transparency_get(x, y) for x, y in coords):
                matched = True
                self.assertTrue(any(original.transparency_get(x, y) for x, y in ((0, 0), (0, original.height()-1), (original.width()-1, 0), (original.width()-1, original.height()-1))))
                self.assertTrue(any(not image.transparency_get(x, y) for x, y in coords), 'Image must contain visible artwork')
        self.assertTrue(matched, 'Displayed pixels must come from the actual delivered PNG')
        finalizers = []
        reference = weakref.ref(image, lambda ref: finalizers.append(threading.get_ident()))
        del image
        gc.collect()
        self.assertIsNotNone(reference(), 'Tk image reference vanished during window lifetime')
        window.close()
        gc.collect()
        self.assertIsNone(reference(), 'Window retains PhotoImage after close')
        self.assertEqual(finalizers, [threading.get_ident()])
