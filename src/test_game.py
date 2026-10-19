"""Tests fuer eine ganze Partie, ohne Server oder Netzwerk."""
import copy
import unittest

import board


FLEET = [
    {"type": "Carrier", "start": "A1", "direction": "h"},
    {"type": "Battleship", "start": "A2", "direction": "h"},
    {"type": "Cruiser", "start": "A3", "direction": "h"},
    {"type": "Submarine", "start": "A4", "direction": "h"},
    {"type": "Destroyer", "start": "A5", "direction": "h"},
]


class TestBattleshipGame(unittest.TestCase):
    def new_game(self, ready=False):
        game = board.BattleshipGame()
        if ready:
            game.start()
            game.place_fleet("A", FLEET)
            game.place_fleet("B", FLEET)
        return game

    def assert_rule_error(self, code, action, *args):
        with self.assertRaises(board.RuleError) as raised:
            action(*args)
        self.assertEqual(raised.exception.code, code)
        self.assertTrue(str(raised.exception))

    def test_shooting_waits_for_both_fleets(self):
        game = self.new_game()
        self.assert_rule_error("WRONG_PHASE", game.shoot, "A", "A1")
        game.start()
        self.assertEqual(game.place_fleet("A", FLEET), {"phase": "placing"})
        self.assert_rule_error("WRONG_PHASE", game.shoot, "A", "A1")
        self.assertEqual(game.place_fleet("B", FLEET), {"phase": "shooting"})
        self.assertEqual(game.turn, "A")

    def test_wrong_turn_does_not_change_either_board(self):
        game = self.new_game(ready=True)
        before = copy.deepcopy(game.players)
        self.assert_rule_error("NOT_YOUR_TURN", game.shoot, "B", "A1")
        self.assertEqual(game.players, before)
        self.assertEqual(game.turn, "A")

    def test_aliases_hit_the_same_cell_and_cannot_be_repeated(self):
        game = self.new_game(ready=True)
        self.assertEqual(game.shoot("A", "a01"), {
            "field": "A1", "result": "hit", "sunk": None, "turn": "B",
        })
        game.shoot("B", "J10")
        self.assert_rule_error("DUPLICATE_SHOT", game.shoot, "A", "A1")
        self.assert_rule_error("DUPLICATE_SHOT", game.shoot, "A", "a001")
        self.assertEqual(game.state("A")["shotsAtOpponent"], {"A1": "hit"})

    def test_invalid_fields_are_rejected_without_changing_the_turn(self):
        game = self.new_game(ready=True)
        for field in (None, True, 12, [], {}, "A²", "A١", "K1", "A0", "A11", ""):
            with self.subTest(field=field):
                self.assert_rule_error("CELL_OUT_OF_BOUNDS", game.shoot, "A", field)
                self.assertEqual(game.turn, "A")
                self.assertEqual(game.state("A")["shotsAtOpponent"], {})

    def test_bad_fleet_is_rejected_without_partial_placement(self):
        game = self.new_game()
        game.start()
        bad_type = copy.deepcopy(FLEET)
        bad_type[0]["type"] = []
        overlap = copy.deepcopy(FLEET)
        overlap[1]["start"] = "A1"
        for placement in (bad_type, overlap, FLEET[:-1], None):
            with self.subTest(placement=placement):
                self.assert_rule_error("INVALID_PLACEMENT", game.place_fleet, "A", placement)
                self.assertEqual(game.state("A")["ownShips"], [])
        game.place_fleet("A", FLEET)
        self.assert_rule_error("WRONG_PHASE", game.place_fleet, "A", FLEET)

    def test_state_contains_only_own_fleet_and_copies_nested_data(self):
        game = self.new_game()
        game.start()
        game.place_fleet("A", FLEET)
        other_fleet = copy.deepcopy(FLEET)
        for ship in other_fleet:
            ship["start"] = "F" + ship["start"][1:]
        game.place_fleet("B", other_fleet)
        game.shoot("A", "F1")
        game.shoot("B", "A1")
        state = game.state("A")
        self.assertEqual(set(state), {"phase", "turn", "ownShips", "shotsAtOpponent", "winner"})
        self.assertEqual(state["ownShips"][0]["cells"], ["A1", "B1", "C1", "D1", "E1"])
        self.assertEqual(state["ownShips"][0]["hits"], ["A1"])
        state["ownShips"][0]["cells"].clear()
        state["ownShips"][0]["hits"].clear()
        state["shotsAtOpponent"].clear()
        unchanged = game.state("A")
        self.assertEqual(unchanged["ownShips"][0]["hits"], ["A1"])
        self.assertEqual(len(unchanged["ownShips"][0]["cells"]), 5)
        self.assertEqual(unchanged["shotsAtOpponent"], {"F1": "hit"})

    def test_full_match_finishes_only_when_the_whole_fleet_is_sunk(self):
        game = self.new_game(ready=True)
        targets = [
            "A1", "B1", "C1", "D1", "E1", "A2", "B2", "C2", "D2",
            "A3", "B3", "C3", "A4", "B4", "C4", "A5", "B5",
        ]
        misses = [
            "J1", "J2", "J3", "J4", "J5", "J6", "J7", "J8",
            "J9", "J10", "I1", "I2", "I3", "I4", "I5", "I6",
        ]
        sunk = []
        for index, target in enumerate(targets):
            result = game.shoot("A", target)
            if result["sunk"]:
                sunk.append(result["sunk"])
            if index < len(misses):
                self.assertEqual(game.phase, "shooting")
                self.assertIsNone(game.winner)
                self.assertEqual(game.shoot("B", misses[index])["result"], "miss")
        self.assertEqual(sunk, ["Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"])
        self.assertEqual(result, {"field": "B5", "result": "sunk", "sunk": "Destroyer", "turn": None})
        self.assertEqual((game.phase, game.winner, game.reason), ("finished", "A", "sunk"))
        self.assert_rule_error("WRONG_PHASE", game.shoot, "B", "H10")
        self.assert_rule_error("WRONG_PHASE", game.place_fleet, "A", FLEET)

    def test_reset_and_start_clear_the_previous_match(self):
        game = self.new_game(ready=True)
        game.shoot("A", "A1")
        game.reset()
        self.assertEqual((game.phase, game.turn, game.winner, game.reason), ("waiting", None, None, None))
        for slot in ("A", "B"):
            self.assertEqual(game.state(slot)["ownShips"], [])
            self.assertEqual(game.state(slot)["shotsAtOpponent"], {})
            self.assertFalse(game.players[slot]["fleet_placed"])
        game.start()
        self.assertEqual(game.place_fleet("B", FLEET), {"phase": "placing"})
        self.assertEqual(game.place_fleet("A", FLEET), {"phase": "shooting"})

    def test_unknown_player_is_rejected(self):
        game = self.new_game(ready=True)
        for slot in (None, [], "C"):
            with self.subTest(slot=slot):
                self.assert_rule_error("INVALID_PLAYER", game.place_fleet, slot, FLEET)
                self.assert_rule_error("INVALID_PLAYER", game.shoot, slot, "A1")
                self.assert_rule_error("INVALID_PLAYER", game.state, slot)


class TestBoardInput(unittest.TestCase):
    def test_unicode_digits_are_not_coordinates(self):
        for field in ("A²", "A١"):
            with self.subTest(field=field):
                try:
                    parsed = board.parse_cell(field)
                except ValueError:
                    self.fail("Ungueltige Koordinaten muessen ohne Ausnahme abgewiesen werden")
                self.assertIsNone(parsed)

    def test_unhashable_ship_type_is_a_placement_error(self):
        placement = copy.deepcopy(FLEET)
        placement[0]["type"] = []
        try:
            ok, code, _ = board.validate_placement(placement)
        except TypeError:
            self.fail("Ein falscher Schiffstyp muss eine normale Ablehnung liefern")
        self.assertFalse(ok)
        self.assertEqual(code, "INVALID_PLACEMENT")

    def test_shot_helper_normalizes_coordinates(self):
        ships = board.build_ships([{"type": "Destroyer", "start": "A1", "direction": "h"}])
        self.assertEqual(board.apply_shot(ships, "a01"), ("hit", None))
        self.assertEqual(ships[0]["hits"], ["A1"])


if __name__ == "__main__":
    unittest.main()
