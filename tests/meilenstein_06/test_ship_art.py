"""Delivered vector fleet and actual Canvas scaling/rotation, without SVG packages."""
import os
from pathlib import Path
import tempfile
import unittest

from board import FLEET
import ship_art
from tests.meilenstein_04 import test_gui as gui_helpers


class ShipAssetTests(unittest.TestCase):
    def test_every_fleet_type_loads_from_a_foreign_working_directory(self):
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                for entry in FLEET:
                    with self.subTest(ship=entry["type"]):
                        artwork = ship_art.load_svg(entry["type"])
                        self.assertEqual((artwork.width, artwork.height), (entry["size"] * 40, 40))
                        self.assertTrue(artwork.shapes)
                        self.assertTrue(ship_art.SHIP_ASSETS[entry["type"]].is_file())
                        self.assertTrue(ship_art.SHIP_NAMES[entry["type"]])
            finally:
                os.chdir(original)


class ShipCanvasTests(unittest.TestCase):
    requires_gui = True
    tk = gui_helpers.tk
    setUpClass = classmethod(gui_helpers.GuiTests.setUpClass.__func__)

    def setUp(self):
        self.root = self.tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.canvas = self.tk.Canvas(self.root, width=40, height=40)

    def test_all_ships_draw_outside_cell_and_rotate_clockwise(self):
        # A cell Canvas may receive a complete ship starting before its left edge.
        # Rotating this same artwork must keep all paint, tags and shape order.
        for entry in FLEET:
            with self.subTest(ship=entry["type"]):
                self.canvas.delete("all")
                length = entry["size"] * 40
                horizontal = ship_art.draw_svg(self.canvas, entry["type"], -40, 5,
                                               length, 32, tags=("fleet", "own"))
                horizontal_coords = [self.canvas.coords(item) for item in horizontal]
                self.assertTrue(horizontal)
                self.assertLess(self.canvas.bbox(*horizontal)[0], 0)
                self.assertGreater(self.canvas.bbox(*horizontal)[2], 20)
                vertical = ship_art.draw_svg(self.canvas, entry["type"], 7, -20,
                                             length, 32, vertical=True, tags=("fleet",))
                self.assertEqual(len(horizontal), len(vertical))
                for original, item in zip(horizontal_coords, vertical):
                    self.assertIn("fleet", self.canvas.gettags(item))
                    painted = self.canvas.coords(item)
                    # Independent rotation of the already scaled horizontal
                    # coordinates around the upper-left corner of its box.
                    expected_pairs = [(7 + 32 - (original[i + 1] - 5),
                                       -20 + original[i] + 40)
                                      for i in range(0, len(original), 2)]
                    if self.canvas.type(item) in ("rectangle", "oval"):
                        xs, ys = zip(*expected_pairs)
                        expected = (min(xs), min(ys), max(xs), max(ys))
                    else:
                        expected = tuple(number for point in expected_pairs for number in point)
                    self.assertEqual(len(painted), len(expected))
                    for actual, wanted in zip(painted, expected):
                        self.assertAlmostEqual(actual, wanted)


if __name__ == "__main__":
    unittest.main()
