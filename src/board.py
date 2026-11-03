"""Kompatibilitaetseinstieg fuer aeltere Importe; Regeln leben in spiel.py."""

from spiel import (
    GRID_SIZE, COLUMNS, FLEET, FLEET_SIZE,
    parse_cell, cell_in_bounds, canonical_cell, ship_cells,
    validate_placement, build_ships, apply_shot, all_sunk,
    RuleError, BattleshipGame,
)
