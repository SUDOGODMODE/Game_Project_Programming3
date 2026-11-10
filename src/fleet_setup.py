"""Erstellt eine gueltige Flottenvorlage ohne GUI-Abhaengigkeiten."""

from spiel import COLUMNS, FLEET, GRID_SIZE, ship_cells


def random_placement(rng) -> list[dict]:
    """Waehlt fuer jeden Schiffstyp eine freie Lage mit ``rng.choice``.

    Ein uebergebener ``random.Random(seed)`` macht den Vorschlag fuer Tests
    reproduzierbar. Die GUI uebergibt das normale ``random``-Modul.
    """
    occupied = set()
    placement = []
    for ship in FLEET:
        candidates = []
        for letter in COLUMNS:
            for row in range(1, GRID_SIZE + 1):
                for direction in ("h", "v"):
                    start = f"{letter}{row}"
                    cells = ship_cells(start, direction, ship["size"])
                    if cells is not None and not occupied.intersection(cells):
                        candidates.append((start, direction, cells))
        start, direction, cells = rng.choice(candidates)
        occupied.update(cells)
        placement.append({"type": ship["type"], "start": start, "direction": direction})
    return placement
