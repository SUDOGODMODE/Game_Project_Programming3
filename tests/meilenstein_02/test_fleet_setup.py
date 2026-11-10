"""Zufallsflotte als reine Funktion statt als Tk-Widgetlogik prüfen."""
import random
import unittest

from fleet_setup import random_placement
from spiel import FLEET, validate_placement


class RandomPlacementTests(unittest.TestCase):
    def placement(self, seed):
        return random_placement(random.Random(seed))

    def test_generated_fleet_is_complete_and_valid(self):
        for seed in (0, 1, 42):
            with self.subTest(seed=seed):
                ships = self.placement(seed)
                self.assertEqual([ship["type"] for ship in ships], [ship["type"] for ship in FLEET])
                self.assertTrue(validate_placement(ships)[0])

    def test_same_seed_repeats_the_same_fleet(self):
        self.assertEqual(self.placement(17), self.placement(17))


if __name__ == "__main__":
    unittest.main()
