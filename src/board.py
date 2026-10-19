"""Spielkern fuer Schiffe versenken: Regeln und Zustand, ohne Netzwerk."""
from __future__ import annotations

from copy import deepcopy

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
    """C5 ergibt (2, 4): Spalte und Zeile ab null. Ungültige Felder ergeben None."""
    if not isinstance(cell, str) or len(cell) < 2:
        return None
    column_letter = cell[0].upper()
    row_part = cell[1:]
    if column_letter not in COLUMNS or not row_part.isascii() or not row_part.isdigit():
        return None
    row_part = row_part.lstrip("0")
    if not row_part or len(row_part) > 2:
        return None
    row = int(row_part) - 1
    column = COLUMNS.index(column_letter)
    if not (0 <= row < GRID_SIZE):
        return None
    return column, row


def cell_in_bounds(cell: str) -> bool:
    return parse_cell(cell) is not None


def canonical_cell(cell: str) -> str | None:
    """Gibt dieselbe Schreibweise fuer jedes gueltige Feld zurueck."""
    parsed = parse_cell(cell)
    if parsed is None:
        return None
    column, row = parsed
    return f"{COLUMNS[column]}{row + 1}"


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

    for ship in ships:
        if not isinstance(ship, dict):
            return False, "INVALID_PLACEMENT", "jedes Schiff muss ein Objekt sein"
        ship_type = ship.get("type")
        start = ship.get("start", "")
        direction = ship.get("direction", "")
        if not isinstance(ship_type, str) or ship_type not in sizes_by_type:
            return False, "INVALID_PLACEMENT", f"unbekannter Schiffstyp: {ship_type}"
        seen_types.append(ship_type)
        cells = ship_cells(start, direction, sizes_by_type[ship_type])
        if cells is None:
            return False, "INVALID_PLACEMENT", f"{ship_type} bei {start} ragt ueber den Rand oder hat ein ungueltiges Format"
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
    field = canonical_cell(field)
    for ship in ships:
        if field in ship["cells"] and field not in ship["hits"]:
            ship["hits"].append(field)
            if len(ship["hits"]) == len(ship["cells"]):
                return "hit", ship["type"]
            return "hit", None
    return "miss", None


def all_sunk(ships: list[dict]) -> bool:
    return all(len(ship["hits"]) == len(ship["cells"]) for ship in ships)


class RuleError(ValueError):
    """Eine abgelehnte Aktion mit Fehlercode und lesbarem Grund."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


class BattleshipGame:
    """Fuehrt eine Partie; der Server kuemmert sich um Verbindungen und Sperren."""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self.phase = "waiting"
        self.turn = None
        self.winner = None
        self.reason = None
        self.players = {
            slot: {"fleet_placed": False, "ships": [], "shots_at_opponent": {}}
            for slot in ("A", "B")
        }

    def start(self) -> None:
        """Beginnt eine neue Partie, sobald der Server zwei Spieler hat."""
        self.reset()
        self.phase = "placing"

    def _player(self, slot: str) -> dict:
        if not isinstance(slot, str) or slot not in self.players:
            raise RuleError("INVALID_PLAYER", "unbekannter Spieler")
        return self.players[slot]

    def place_fleet(self, slot: str, placement) -> dict:
        player = self._player(slot)
        if self.phase != "placing":
            raise RuleError("WRONG_PHASE", f"aktuelle Phase ist {self.phase}, nicht placing")
        if player["fleet_placed"]:
            raise RuleError("WRONG_PHASE", "Flotte wurde bereits platziert")
        ok, code, message = validate_placement(placement)
        if not ok:
            raise RuleError(code, message)
        player["ships"] = build_ships(placement)
        player["fleet_placed"] = True
        if all(entry["fleet_placed"] for entry in self.players.values()):
            self.phase = "shooting"
            self.turn = "A"
        return {"phase": self.phase}

    def check_shot(self, slot: str, field: str) -> tuple[str, str] | None:
        """None bei einem erlaubten Schuss, sonst Fehlercode und Grund."""
        player = self._player(slot)
        if self.phase != "shooting":
            return "WRONG_PHASE", f"aktuelle Phase ist {self.phase}, nicht shooting"
        if self.turn != slot:
            return "NOT_YOUR_TURN", f"Spieler {slot} ist nicht am Zug"
        cell = canonical_cell(field)
        if cell is None:
            return "CELL_OUT_OF_BOUNDS", f"{field} liegt ausserhalb des 10x10-Rasters"
        if cell in player["shots_at_opponent"]:
            return "DUPLICATE_SHOT", f"auf {cell} wurde bereits geschossen"
        return None

    def shoot(self, slot: str, field: str) -> dict:
        rejected = self.check_shot(slot, field)
        if rejected is not None:
            raise RuleError(*rejected)
        cell = canonical_cell(field)
        opponent_slot = "B" if slot == "A" else "A"
        opponent = self.players[opponent_slot]
        result, sunk_type = apply_shot(opponent["ships"], cell)
        outcome = "sunk" if sunk_type else result
        self.players[slot]["shots_at_opponent"][cell] = outcome
        if all_sunk(opponent["ships"]):
            self.phase = "finished"
            self.winner = slot
            self.reason = "sunk"
            self.turn = None
        else:
            self.turn = opponent_slot
        return {"field": cell, "result": outcome, "sunk": sunk_type, "turn": self.turn}

    def state(self, slot: str) -> dict:
        """Eine unabhaengige Kopie der eigenen Sicht, ohne gegnerische Schiffe."""
        player = self._player(slot)
        return {
            "phase": self.phase,
            "turn": self.turn,
            "ownShips": deepcopy(player["ships"]),
            "shotsAtOpponent": dict(player["shots_at_opponent"]),
            "winner": self.winner,
        }
