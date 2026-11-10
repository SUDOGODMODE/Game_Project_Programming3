"""Berechnet Brettzeichen aus einem bestaetigten Serverzustand, ohne Tk.

Das Fenster zeichnet die Zeichen anschliessend auf seine Widgets. So bleiben
Spielzustand und Darstellung getrennt und die Anzeigeentscheidungen schnell
testbar.
"""

SHOT_SYMBOLS = {"miss": "·", "hit": "X", "sunk": "#"}


def board_symbols(state: dict) -> tuple[dict, dict, dict]:
    """Gibt eigene Zeichen, Zielzeichen und Schiffsausschnitte zurueck.

    Die drei Woerterbuecher enthalten nur bekannte Felder. Leere Felder
    ergaenzt das Fenster beim Zeichnen. Schiffsausschnitte sind Tupel aus
    (Schiffstyp, Feldindex, Feldanzahl, vertikal). Ein bestaetigter Schuss
    auf das eigene Brett hat Vorrang vor dem Schiffssymbol.
    """
    own_symbols = {}
    target_symbols = {}
    segments = {}

    for ship in state.get("ownShips", []):
        cells = ship.get("cells", [])
        vertical = len(cells) > 1 and cells[0][0] == cells[1][0]
        for index, field in enumerate(cells):
            own_symbols[field] = "S"
            segments[field] = (ship["type"], index, len(cells), vertical)
        for field in ship.get("hits", []):
            own_symbols[field] = "X"

    for field, result in state.get("shotsAtSelf", {}).items():
        if result in SHOT_SYMBOLS:
            own_symbols[field] = SHOT_SYMBOLS[result]
    for field, result in state.get("shotsAtOpponent", {}).items():
        if result in SHOT_SYMBOLS:
            target_symbols[field] = SHOT_SYMBOLS[result]

    return own_symbols, target_symbols, segments
