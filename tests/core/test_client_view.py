"""Brettdarstellung ohne Tk berechnen und damit schnell prüfen."""
from copy import deepcopy
import unittest

from gui.client_view import board_symbols, score_text


class BoardSymbolsTests(unittest.TestCase):
    def test_own_ships_and_both_players_shots_keep_their_symbols(self):
        state = {
            "ownShips": [{"type": "Destroyer", "cells": ["A1", "B1"], "hits": ["A1"]}],
            "shotsAtSelf": {"A1": "hit", "J10": "miss"},
            "shotsAtOpponent": {"C7": "miss", "D8": "hit", "E8": "sunk"},
        }
        original = deepcopy(state)

        own, target, segments = board_symbols(state)

        self.assertEqual(own, {"A1": "X", "B1": "S", "J10": "·"})
        self.assertEqual(target, {"C7": "·", "D8": "X", "E8": "#"})
        self.assertEqual(segments, {
            "A1": ("Destroyer", 0, 2, False),
            "B1": ("Destroyer", 1, 2, False),
        })
        self.assertEqual(state, original)

    def test_empty_state_clears_both_boards(self):
        self.assertEqual(board_symbols({"ownShips": [], "shotsAtSelf": {}, "shotsAtOpponent": {}}), ({}, {}, {}))

    def test_vertical_ship_segments_keep_orientation_and_order(self):
        _, _, segments = board_symbols({
            "ownShips": [{"type": "Cruiser", "cells": ["C2", "C3", "C4"], "hits": []}],
        })
        self.assertEqual(segments["C2"], ("Cruiser", 0, 3, True))
        self.assertEqual(segments["C4"], ("Cruiser", 2, 3, True))


class ScoreTextTests(unittest.TestCase):
    def test_score_shows_both_names_with_wins_in_slot_order(self):
        score = [{"slot": "A", "player": "Alice", "wins": 2}, {"slot": "B", "player": "Bob", "wins": 1}]
        self.assertEqual(score_text(score), "Alice 2 : 1 Bob")

    def test_score_with_one_or_no_player(self):
        self.assertEqual(score_text([{"slot": "A", "player": "Alice", "wins": 0}]), "Alice 0")
        self.assertEqual(score_text([]), "")


if __name__ == "__main__":
    unittest.main()
