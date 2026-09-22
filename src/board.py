"""board.py: Spielregeln fuer Schiffe versenken, komplett ohne Netzwerk.

Reine Funktionen auf einfachen Datentypen (Listen, Dicts, Strings) - lassen
sich einzeln testen (siehe test_board.py) und werden von server.py nur noch
aufgerufen, nicht neu implementiert. Ein Schiff wird durchgehend als
{"type": str, "cells": [str, ...], "hits": [str, ...]} dargestellt.
"""
from __future__ import annotations

GRID_SIZE = 10
COLUMNS = "ABCDEFGHIJ"

FLEET = [
    {"type": "Carrier", "size": 5},
    {"type": "Battleship", "size": 4},
    {"type": "Cruiser", "size": 3},
    {"type": "Submarine", "size": 3},
    {"type": "Destroyer", "size": 2},
]


def parse_cell(cell: str) -> tuple[int, int] | None:
    """"C5" -> (2, 4) als (Spalte, Zeile), beides 0-indexiert. None bei ungueltigem Format."""
    if not isinstance(cell, str) or len(cell) < 2:
        return None
    column_letter = cell[0].upper()
    row_part = cell[1:]
    if column_letter not in COLUMNS or not row_part.isdigit():
        return None
    row = int(row_part) - 1
    column = COLUMNS.index(column_letter)
    if not (0 <= row < GRID_SIZE):
        return None
    return column, row


def cell_in_bounds(cell: str) -> bool:
    return parse_cell(cell) is not None


def ship_cells(start: str, direction: str, size: int) -> list[str] | None:
    """Berechnet die von einem Schiff belegten Felder. None, wenn es dabei ueber den Rand ragt."""
    parsed = parse_cell(start)
    if parsed is None or direction not in ("h", "v"):
        return None
    column, row = parsed
    cells = []
    for offset in range(size):
        c = column + offset if direction == "h" else column
        r = row if direction == "h" else row + offset
        if not (0 <= c < GRID_SIZE and 0 <= r < GRID_SIZE):
            return None
        cells.append(f"{COLUMNS[c]}{r + 1}")
    return cells


def validate_placement(ships) -> tuple[bool, str | None, str | None]:
    """Prueft eine vollstaendige Flotte gegen FLEET (Regel 4, Auftrag 1) und Ueberlappung.

    Gibt (ok, code, message) zurueck; code/message sind None, wenn ok True ist.
    """
    if not isinstance(ships, list):
        return False, "INVALID_PLACEMENT", "ships muss eine Liste sein"

    if len(ships) != len(FLEET):
        return False, "INVALID_PLACEMENT", f"erwarte {len(FLEET)} Schiffe, bekommen: {len(ships)}"

    sizes_by_type = {f["type"]: f["size"] for f in FLEET}
    seen_types = []
    all_cells: list[str] = []
    computed: list[list[str]] = []

    for ship in ships:
        if not isinstance(ship, dict):
            return False, "INVALID_PLACEMENT", "jedes Schiff muss ein Objekt sein"
        ship_type = ship.get("type")
        start = ship.get("start", "")
        direction = ship.get("direction", "")
        if ship_type not in sizes_by_type:
            return False, "INVALID_PLACEMENT", f"unbekannter Schiffstyp: {ship_type}"
        seen_types.append(ship_type)
        cells = ship_cells(start, direction, sizes_by_type[ship_type])
        if cells is None:
            return False, "INVALID_PLACEMENT", f"{ship_type} bei {start} ragt ueber den Rand oder hat ein ungueltiges Format"
        computed.append(cells)
        all_cells.extend(cells)

    if sorted(seen_types) != sorted(sizes_by_type.keys()):
        return False, "INVALID_PLACEMENT", "Flotte stimmt nicht mit der vorgegebenen Zusammensetzung ueberein"

    if len(all_cells) != len(set(all_cells)):
        return False, "INVALID_PLACEMENT", "Schiffe ueberlappen sich"

    return True, None, None


FLEET_SIZE = {f["type"]: f["size"] for f in FLEET}


def build_ships(placement: list[dict]) -> list[dict]:
    """Wandelt validierte Platzierungsdaten in die interne Schiffs-Repraesentation um."""
    ships = []
    for ship in placement:
        cells = ship_cells(ship["start"], ship["direction"], FLEET_SIZE[ship["type"]])
        ships.append({"type": ship["type"], "cells": cells, "hits": []})
    return ships


def apply_shot(ships: list[dict], field: str) -> tuple[str, str | None]:
    """Traegt einen Schuss auf `field` in die Schiffsliste ein.

    Gibt (result, sunk_type) zurueck: result ist "hit" oder "miss";
    sunk_type ist der Schiffstyp, falls dieser Schuss das Schiff vollstaendig
    versenkt hat, sonst None.
    """
    for ship in ships:
        if field in ship["cells"] and field not in ship["hits"]:
            ship["hits"].append(field)
            if len(ship["hits"]) == len(ship["cells"]):
                return "hit", ship["type"]
            return "hit", None
    return "miss", None


def all_sunk(ships: list[dict]) -> bool:
    return all(len(ship["hits"]) == len(ship["cells"]) for ship in ships)
