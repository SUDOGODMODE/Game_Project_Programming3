"""server.py: nimmt Verbindungen an und spielt eine komplette Partie Schiffe versenken.

Ein Faden pro Verbindung, damit Spieler A und B gleichzeitig verbunden sein
koennen (das war im Meilenstein "Der erste Handschlag" noch nicht gefordert
und dort explizit als naechster Schritt angekuendigt - hier bereits mit
umgesetzt, weil ohne Threading kein echtes Spiel zwischen zwei Menschen
moeglich ist). Der Spielzustand liegt zentral in `game` und wird ueber
`game["lock"]` gegen gleichzeitigen Zugriff aus mehreren Faeden geschuetzt.
Nachrichten an einen einzelnen Socket laufen immer ueber `send_to()`, egal
ob es die direkte Antwort auf die eigene Anfrage ist oder ein Broadcast
(z.B. `gameOver`) von einem anderen Faden - sonst koennten sich zwei
gleichzeitige sendall()-Aufrufe auf demselben Socket vermischen.
"""
import socket
import threading

import board
from netz import send, read_messages

HOST, PORT = "0.0.0.0", 5000
SLOTS = ("A", "B")


def other_slot(slot: str) -> str:
    return "B" if slot == "A" else "A"


def new_game() -> dict:
    return {
        "lock": threading.Lock(),
        "phase": "waiting",
        "turn": None,
        "winner": None,
        "reason": None,
        "taken": [],
        "players": {
            slot: {
                "connected": False,
                "sock": None,
                "send_lock": threading.Lock(),
                "name": None,
                "fleet_placed": False,
                "ships": [],
                "shots_at_opponent": {},
            }
            for slot in SLOTS
        },
    }


def send_to(game: dict, slot: str, message: dict) -> None:
    """Schickt `message` an den Socket von `slot`, serialisiert pro Spieler.

    Tut nichts, wenn der Spieler gerade nicht verbunden ist. Eine tote
    Verbindung (OSError beim Senden) wird stillschweigend ignoriert - der
    naechste Verbindungsabbruch-Code raeumt das ueber "getrennt" ohnehin auf.
    """
    player = game["players"][slot]
    sock = player["sock"]
    if sock is None:
        return
    with player["send_lock"]:
        try:
            send(sock, message)
        except OSError:
            pass


def handle(message: dict, connection: dict, game: dict, sock) -> dict | None:
    """Entscheidet anhand von `type`, was zu tun ist. Gibt die direkte Antwort zurueck
    (oder None, wenn keine Antwort vorgesehen ist, z.B. bei "leave")."""
    msg_type = message.get("type")

    if msg_type == "join":
        with game["lock"]:
            if connection["slot"] is not None:
                return {"type": "error", "code": "ALREADY_JOINED", "message": "diese Verbindung ist bereits einem Spieler zugeordnet"}
            if len(game["taken"]) >= len(SLOTS):
                return {"type": "error", "code": "GAME_FULL", "message": "es sind bereits zwei Spieler verbunden"}
            player_name = message.get("player")
            if not isinstance(player_name, str) or not player_name.strip():
                return {"type": "error", "code": "MISSING_PLAYER", "message": "Name fehlt"}

            slot = SLOTS[len(game["taken"])]
            game["taken"].append(slot)
            connection["slot"] = slot
            player = game["players"][slot]
            player["connected"] = True
            player["sock"] = sock
            player["name"] = player_name
            if len(game["taken"]) == len(SLOTS):
                game["phase"] = "placing"
            return {"type": "welcome", "slot": slot, "player": player_name, "phase": game["phase"]}

    slot = connection["slot"]
    if slot is None and msg_type in ("place", "shoot", "getState", "leave"):
        return {"type": "error", "code": "NOT_JOINED", "message": "bitte zuerst mit 'join' beitreten"}

    if msg_type in ("place", "shoot", "getState", "leave"):
        assert slot is not None  # durch die Pruefung oben sichergestellt

    if msg_type == "place":
        with game["lock"]:
            if game["phase"] != "placing":
                return {"type": "error", "code": "WRONG_PHASE", "message": f"aktuelle Phase ist {game['phase']}, nicht placing"}
            player = game["players"][slot]
            if player["fleet_placed"]:
                return {"type": "error", "code": "WRONG_PHASE", "message": "Flotte wurde bereits platziert"}
            ok, code, error_message = board.validate_placement(message.get("ships"))
            if not ok:
                return {"type": "error", "code": code, "message": error_message}
            player["ships"] = board.build_ships(message.get("ships"))
            player["fleet_placed"] = True
            if all(game["players"][s]["fleet_placed"] for s in SLOTS):
                game["phase"] = "shooting"
                game["turn"] = "A"
            return {"type": "placeAck", "phase": game["phase"]}

    if msg_type == "shoot":
        opponent_slot = other_slot(slot)
        broadcast = None
        with game["lock"]:
            if game["phase"] != "shooting":
                return {"type": "error", "code": "WRONG_PHASE", "message": f"aktuelle Phase ist {game['phase']}, nicht shooting"}
            if game["turn"] != slot:
                return {"type": "error", "code": "NOT_YOUR_TURN", "message": f"Spieler {slot} ist nicht am Zug"}
            field = message.get("field")
            if not board.cell_in_bounds(field):
                return {"type": "error", "code": "CELL_OUT_OF_BOUNDS", "message": f"{field} liegt ausserhalb des 10x10-Rasters"}
            me = game["players"][slot]
            if field in me["shots_at_opponent"]:
                return {"type": "error", "code": "DUPLICATE_SHOT", "message": f"auf {field} wurde bereits geschossen"}

            opponent = game["players"][opponent_slot]
            result, sunk_type = board.apply_shot(opponent["ships"], field)
            outcome = "sunk" if sunk_type else result
            me["shots_at_opponent"][field] = outcome

            if board.all_sunk(opponent["ships"]):
                game["phase"] = "finished"
                game["winner"] = slot
                game["reason"] = "sunk"
                game["turn"] = None
                broadcast = {"type": "gameOver", "winner": slot, "reason": "sunk"}
            else:
                game["turn"] = opponent_slot

            response = {"type": "result", "field": field, "result": outcome, "sunk": sunk_type, "turn": game["turn"]}

        if broadcast is not None:
            # nur an den Gegner schicken: der Schuetze bekommt das Ergebnis
            # ohnehin per `response` (sunk + turn: null zeigen das Ende an),
            # ein zusaetzlicher Broadcast an sich selbst wuerde vor dieser
            # Antwort ankommen und die Reihenfolge auf dem eigenen Socket
            # durcheinanderbringen.
            send_to(game, opponent_slot, broadcast)
        return response

    if msg_type == "getState":
        with game["lock"]:
            me = game["players"][slot]
            own_ships = [{"type": s["type"], "cells": list(s["cells"]), "hits": list(s["hits"])} for s in me["ships"]]
            return {
                "type": "state",
                "phase": game["phase"],
                "turn": game["turn"],
                "ownShips": own_ships,
                "shotsAtOpponent": dict(me["shots_at_opponent"]),
                "winner": game["winner"],
            }

    if msg_type == "leave":
        with game["lock"]:
            game["players"][slot]["connected"] = False
            game["players"][slot]["sock"] = None
        return None

    if msg_type == "broken":
        return {"type": "error", "code": "INVALID_JSON", "message": "kein gueltiges JSON"}

    return {"type": "error", "code": "UNKNOWN_TYPE", "message": f"unbekannter Typ: {msg_type}"}


def handle_connection(sock: socket.socket, address, game: dict) -> None:
    print("verbunden:", address)
    connection = {"slot": None}
    try:
        with sock:
            for message in read_messages(sock):
                print(f"  <- [{address}]", message)
                try:
                    response = handle(message, connection, game, sock)
                except Exception as exc:  # noqa: BLE001 - Uebung 8: ein Faden darf nicht unbemerkt sterben
                    print(f"  !! [{address}] Fehler bei der Verarbeitung, Verbindung wird beendet: {exc!r}")
                    break
                if response is None:
                    continue
                if connection["slot"] is not None:
                    send_to(game, connection["slot"], response)
                else:
                    send(sock, response)
                print(f"  -> [{address}]", response)
    finally:
        # Steht bewusst in finally, nicht einfach nach der Schleife: so wird
        # der Spieler auch dann als getrennt markiert, wenn oben eine nicht
        # vorhergesehene Ausnahme auftritt - sonst bliebe er als "connected"
        # stehen, obwohl sein Socket laengst tot ist (Uebung 8).
        if connection["slot"] is not None:
            with game["lock"]:
                game["players"][connection["slot"]]["connected"] = False
                game["players"][connection["slot"]]["sock"] = None
        print("getrennt:", address)


def main() -> None:
    game = new_game()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((HOST, PORT))
        listener.listen()
        print("Server wartet auf Port", PORT)
        while True:
            sock, address = listener.accept()
            thread = threading.Thread(target=handle_connection, args=(sock, address, game), daemon=True)
            thread.start()


if __name__ == "__main__":
    main()
