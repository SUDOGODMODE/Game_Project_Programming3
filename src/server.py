"""Spielserver: verwaltet Verbindungen; die Spielregeln stehen in board.py."""
import argparse
import socket
import threading

import board
from netz import send, read_messages

HOST, PORT = "0.0.0.0", 5000
SLOTS = ("A", "B")


def new_game() -> dict:
    return {
        "lock": threading.Lock(),
        "core": board.BattleshipGame(),
        "taken": [],
        "players": {
            slot: {
                "sock": None,
                "name": None,
            }
            for slot in SLOTS
        },
    }


def send_to(game: dict, slot: str, message: dict) -> None:
    """Die Spielsperre ist gehalten; ein toter Socket stoppt keinen Broadcast."""
    player = game["players"][slot]
    sock = player["sock"]
    if sock is None:
        return
    try:
        send(sock, message)
        print(f"  -> [{slot}]", message, flush=True)
    except OSError:
        pass  # Der Empfangsthread entfernt die Verbindung in finally.


def broadcast(game: dict, message: dict) -> None:
    """Schickt an alle angemeldeten Spieler. Die Spielsperre ist bereits gehalten."""
    for slot in list(game["taken"]):
        send_to(game, slot, message)


def process(message: dict, connection: dict, game: dict, sock) -> dict | None:
    """Verarbeitet eine Nachricht unter der Sperre und erstellt die direkte Antwort."""
    msg_type = message.get("type")
    core = game["core"]

    if msg_type == "join":
        if connection["slot"] is not None:
            return {"type": "error", "code": "ALREADY_JOINED", "message": "diese Verbindung ist bereits einem Spieler zugeordnet"}
        if len(game["taken"]) >= len(SLOTS):
            return {"type": "error", "code": "GAME_FULL", "message": "es sind bereits zwei Spieler verbunden"}
        name = message.get("player")
        if not isinstance(name, str) or not name.strip():
            return {"type": "error", "code": "MISSING_PLAYER", "message": "Name fehlt"}

        slot = next(s for s in SLOTS if s not in game["taken"])
        game["taken"].append(slot)
        connection["slot"] = slot
        game["players"][slot].update(sock=sock, name=name)
        if len(game["taken"]) == len(SLOTS):
            core.start()
        return {"type": "welcome", "slot": slot, "player": name, "phase": core.phase}

    slot = connection["slot"]
    if slot is None and msg_type in ("place", "shoot", "getState", "leave"):
        return {"type": "error", "code": "NOT_JOINED", "message": "bitte zuerst mit 'join' beitreten"}

    if msg_type == "place":
        return {"type": "placeAck", **core.place_fleet(slot, message.get("ships"))}
    if msg_type == "shoot":
        return {"type": "result", **core.shoot(slot, message.get("field"))}
    if msg_type == "getState":
        return {"type": "state", **core.state(slot)}
    if msg_type == "leave":
        connection["leaving"] = True
        return None
    if msg_type == "broken":
        return {"type": "error", "code": "INVALID_JSON", "message": "kein gueltiges JSON"}
    return {"type": "error", "code": "UNKNOWN_TYPE", "message": f"unbekannter Typ: {msg_type}"}


def handle(message: dict, connection: dict, game: dict, sock) -> None:
    # Kritischer Abschnitt: pruefen, aendern und senden bleiben zusammen.
    # Kein freier Platz kann doppelt vergeben werden; welcome kommt
    # immer vor dem gameStart fuer dieselbe Verbindung.
    with game["lock"]:
        try:
            response = process(message, connection, game, sock)
        except board.RuleError as exc:
            response = {"type": "error", "code": exc.code, "message": str(exc)}
        if response is None:
            return

        slot = connection["slot"]
        if slot is None:
            send(sock, response)
            print("  -> [nicht angemeldet]", response, flush=True)
        else:
            send_to(game, slot, response)

        if response["type"] == "welcome":
            if len(game["taken"]) < len(SLOTS):
                send_to(game, slot, {"type": "waiting", "reason": "warte auf Gegner"})
            else:
                broadcast(game, {
                    "type": "gameStart",
                    "phase": game["core"].phase,
                    "players": [
                        {"slot": s, "player": game["players"][s]["name"]}
                        for s in SLOTS
                    ],
                })
        elif response["type"] == "result" and game["core"].winner is not None:
            # Der Schuetze erkennt das Ende an result.turn == None.
            opponent = next(s for s in SLOTS if s != slot)
            send_to(game, opponent, {"type": "gameOver", "winner": slot, "reason": "sunk"})


def remove_player(connection: dict, game: dict) -> None:
    """Gibt den Platz genau einmal frei und verwirft die abgebrochene Partie."""
    slot = connection["slot"]
    if slot is None:
        return
    with game["lock"]:
        player = game["players"][slot]
        name = player["name"]
        player.update(sock=None, name=None)
        game["taken"].remove(slot)
        connection["slot"] = None
        game["core"].reset()
        broadcast(game, {"type": "opponentLeft", "slot": slot, "player": name})


def handle_connection(sock: socket.socket, address, game: dict) -> None:
    print("verbunden:", address, flush=True)
    connection = {"slot": None, "leaving": False}
    try:
        for message in read_messages(sock):
            print(f"  <- [{address}]", message, flush=True)
            handle(message, connection, game, sock)
            if connection["leaving"]:
                break
    except (OSError, UnicodeError) as exc:
        print(f"Verbindung {address} beendet: {exc}", flush=True)
    finally:
        remove_player(connection, game)
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()
        print("getrennt:", address, flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Schiffe-versenken-Server")
    parser.add_argument("--host", default=HOST, help="Bindeadresse (Standard: alle Netzwerkkarten)")
    parser.add_argument("--port", type=int, default=PORT, help="TCP-Port (Standard: 5000)")
    args = parser.parse_args()
    game = new_game()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((args.host, args.port))
            listener.listen()
            print("Server wartet auf Port", listener.getsockname()[1], flush=True)
            while True:
                sock, address = listener.accept()
                threading.Thread(target=handle_connection, args=(sock, address, game), daemon=True).start()
    except KeyboardInterrupt:
        print("Server beendet", flush=True)
    except OSError as exc:
        parser.exit(1, f"Server konnte nicht gestartet werden: {exc}\n")


if __name__ == "__main__":
    main()
