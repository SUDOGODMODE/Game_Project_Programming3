"""M2: Zwei Personen spielen ohne Netzwerk abwechselnd an einer Tastatur."""
import sys

import board


def read_input(prompt):
    value = input(prompt).strip()
    if value.lower() == "q":
        raise EOFError
    return value


def hand_over(slot):
    """Verdeckt die bisherige Anzeige vor der Tastaturuebergabe im Terminal."""
    if sys.stdin.isatty():
        print("\033[2J\033[3J\033[H", end="", flush=True)
        read_input(f"Tastatur an Spieler {slot}; Enter zum Fortfahren (q beendet): ")
        print("\033[2J\033[3J\033[H", end="", flush=True)


def show_boards(state):
    own = {}
    for ship in state["ownShips"]:
        for cell in ship["cells"]:
            own[cell] = "X" if cell in ship["hits"] else "S"
    shots = {cell: "o" if result == "miss" else "X"
             for cell, result in state["shotsAtOpponent"].items()}
    print("Eigenes Brett: S Schiff, X getroffen; Zielbrett: o Wasser, X Treffer")
    print("    " + " ".join(board.COLUMNS) + "        " + " ".join(board.COLUMNS))
    for row in range(1, board.GRID_SIZE + 1):
        own_row = " ".join(own.get(f"{column}{row}", ".") for column in board.COLUMNS)
        target_row = " ".join(shots.get(f"{column}{row}", ".") for column in board.COLUMNS)
        print(f"{row:2}  {own_row}    {row:2}  {target_row}")


def place_fleet(game, slot):
    while True:
        print(f"Spieler {slot} platziert seine Flotte.")
        placement = []
        for ship in board.FLEET:
            while True:
                parts = read_input(f"{ship['type']} ({ship['size']} Felder), Start Richtung (z.B. A1 h): ").split()
                if len(parts) == 2:
                    placement.append({"type": ship["type"], "start": parts[0], "direction": parts[1]})
                    break
                print("Fehler: Bitte Start und Richtung h/v eingeben.")
        try:
            game.place_fleet(slot, placement)
        except board.RuleError as error:
            print(f"Fehler: {error}. Bitte die Flotte erneut eingeben.")
        else:
            show_boards(game.state(slot))
            return


def main():
    print("Schiffe versenken fuer zwei Personen. q beendet das Spiel.")
    game = board.BattleshipGame()
    game.start()
    try:
        for slot in ("A", "B"):
            hand_over(slot)
            place_fleet(game, slot)
        while game.phase == "shooting":
            slot = game.turn
            hand_over(slot)
            show_boards(game.state(slot))
            while True:
                field = read_input(f"Spieler {slot}, Schuss (z.B. C5): ")
                try:
                    result = game.shoot(slot, field)
                except board.RuleError as error:
                    print(f"Fehler: {error}")
                else:
                    break
            label = {"hit": "Treffer", "miss": "Wasser", "sunk": "Versenkt"}[result["result"]]
            if result["sunk"]:
                label += f" ({result['sunk']})"
            print(f"Spieler {slot}: {result['field']} -> {label}")
            if sys.stdin.isatty() and game.phase == "shooting":
                read_input("Enter zur Tastaturuebergabe (q beendet): ")
    except (EOFError, KeyboardInterrupt):
        print("\nSpiel abgebrochen.")
        return
    print(f"Spieler {game.winner} gewinnt!")


if __name__ == "__main__":
    main()
