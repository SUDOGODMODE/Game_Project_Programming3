"""test_board.py: Tests fuer board.py, ohne Netzwerk und ohne externe Bibliothek.

Ausfuehren: python3 src/test_board.py
Bricht bei der ersten fehlgeschlagenen Behauptung mit AssertionError ab und
druckt sonst "alle Tests bestanden".
"""
import board


def test_parse_cell():
    assert board.parse_cell("A1") == (0, 0)
    assert board.parse_cell("C5") == (2, 4)
    assert board.parse_cell("J10") == (9, 9)
    assert board.parse_cell("K1") is None  # Spalte ausserhalb
    assert board.parse_cell("A11") is None  # Zeile ausserhalb
    assert board.parse_cell("A0") is None  # Zeile 0 gibt es nicht
    assert board.parse_cell("") is None
    assert board.parse_cell(None) is None


def test_ship_cells_horizontal_and_vertical():
    assert board.ship_cells("B2", "h", 3) == ["B2", "C2", "D2"]
    assert board.ship_cells("B2", "v", 3) == ["B2", "B3", "B4"]
    assert board.ship_cells("I1", "h", 3) is None  # I1,J1,K1 -> K1 ragt raus
    assert board.ship_cells("A9", "v", 3) is None  # A9,A10,A11 -> A11 ragt raus
    assert board.ship_cells("A1", "d", 2) is None  # ungueltige Richtung


VALID_FLEET = [
    {"type": "Carrier", "start": "A1", "direction": "h"},
    {"type": "Battleship", "start": "A2", "direction": "h"},
    {"type": "Cruiser", "start": "A3", "direction": "h"},
    {"type": "Submarine", "start": "A4", "direction": "h"},
    {"type": "Destroyer", "start": "A5", "direction": "h"},
]


def test_validate_placement_accepts_valid_fleet():
    ok, code, message = board.validate_placement(VALID_FLEET)
    assert ok is True
    assert code is None and message is None


def test_validate_placement_rejects_overlap():
    overlapping = [dict(s) for s in VALID_FLEET]
    overlapping[1] = {"type": "Battleship", "start": "A1", "direction": "h"}  # ueberlappt Carrier
    ok, code, _ = board.validate_placement(overlapping)
    assert ok is False
    assert code == "INVALID_PLACEMENT"


def test_validate_placement_rejects_wrong_ship_count():
    ok, code, _ = board.validate_placement(VALID_FLEET[:-1])
    assert ok is False
    assert code == "INVALID_PLACEMENT"


def test_validate_placement_rejects_out_of_bounds():
    broken = [dict(s) for s in VALID_FLEET]
    broken[0] = {"type": "Carrier", "start": "G1", "direction": "h"}  # G1..K1, K1 existiert nicht
    ok, code, _ = board.validate_placement(broken)
    assert ok is False
    assert code == "INVALID_PLACEMENT"


def test_validate_placement_rejects_garbage_input():
    ok, code, _ = board.validate_placement("nicht mal eine Liste")
    assert ok is False
    assert code == "INVALID_PLACEMENT"

    ok, code, _ = board.validate_placement(["kein dict"] * 5)
    assert ok is False
    assert code == "INVALID_PLACEMENT"


def test_apply_shot_hit_miss_sunk():
    ships = board.build_ships([{"type": "Destroyer", "start": "B2", "direction": "h"}])
    # Destroyer: B2, C2

    result, sunk = board.apply_shot(ships, "F9")
    assert (result, sunk) == ("miss", None)

    result, sunk = board.apply_shot(ships, "B2")
    assert (result, sunk) == ("hit", None)
    assert not board.all_sunk(ships)

    result, sunk = board.apply_shot(ships, "C2")
    assert (result, sunk) == ("hit", "Destroyer")
    assert board.all_sunk(ships)


def test_all_sunk_false_until_every_ship_is_down():
    ships = board.build_ships([
        {"type": "Destroyer", "start": "A1", "direction": "h"},
        {"type": "Submarine", "start": "C1", "direction": "h"},
    ])
    board.apply_shot(ships, "A1")
    board.apply_shot(ships, "B1")
    assert board.all_sunk(ships) is False  # Destroyer versenkt, Submarine noch nicht
    board.apply_shot(ships, "C1")
    board.apply_shot(ships, "D1")
    board.apply_shot(ships, "E1")
    assert board.all_sunk(ships) is True


def run_all():
    tests = [obj for name, obj in globals().items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"  ok  {test.__name__}")
    print(f"alle Tests bestanden ({len(tests)})")


if __name__ == "__main__":
    run_all()
