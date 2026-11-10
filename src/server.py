"""Spielserver: verwaltet Verbindungen; die Spielregeln stehen in spiel.py."""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import socket
import threading
from uuid import uuid4

import spiel
from netz import send, read_messages
from event_log import EventLog, MESSAGE_TYPES

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "5000"))
SLOTS = ("A", "B")


def log_message(direction: str, peer, message: dict, game=None, slot=None) -> None:
    """Nur bekannte Metadaten loggen, niemals Flotten oder freie Clienttexte."""
    kind = message.get("type")
    kind = kind if isinstance(kind, str) and kind in MESSAGE_TYPES else "unknown"
    code = message.get("code") if kind == "error" else None
    # Fehlercodes stammen ausschliesslich aus unseren eigenen Antwortobjekten.
    error = f" code={code}" if direction == "->" and code else ""
    print(f"  {direction} [{peer}] type={kind}{error}", flush=True)
    if game is not None:
        game["event_log"].record(direction, peer, message, slot=slot)


def new_game(log_file=None) -> dict:
    """Legt die gemeinsame Serververwaltung fuer alle Verbindungsworker an.

    players speichert Sockets und Namen, taken die belegten Slots. core
    verwaltet die eigentlichen Spielregeln, Flotten und Schuesse. lock
    schuetzt gemeinsame Aenderungen und die zugehoerige Nachrichtenfolge.
    """
    if log_file is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        log_file = Path(__file__).resolve().parents[1] / "logs" / f"{stamp}_{uuid4().hex[:8]}.jsonl"
    return {
        "event_log": EventLog(log_file),
        "lock": threading.Lock(),
        "core": spiel.BattleshipGame(),
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
        log_message("->", slot, message, game, slot)
    except OSError:
        pass  # Der Empfangsthread entfernt die Verbindung in finally.


def broadcast(game: dict, message: dict) -> None:
    """Schickt an alle angemeldeten Spieler. Die Spielsperre ist bereits gehalten."""
    for slot in list(game["taken"]):
        send_to(game, slot, message)


def send_states(game: dict) -> None:
    """Schickt jedem Spieler seine vollstaendige Sicht; Spielsperre ist gehalten."""
    for slot in list(game["taken"]):
        send_to(game, slot, {"type": "state", **game["core"].state(slot)})


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
    """Sendet die direkte Antwort, dann gegebenenfalls die gefilterten Sichten.

    Nach dem letzten Schuss folgen auf result beide state und erst danach
    gameOver. Abgelehnte Aktionen erhalten nur ihre private Fehlerantwort.
    """
    # Die Sperre schuetzt den gesamten Spielkern: pruefen, aendern und senden
    # bleiben zusammen. Der Kern selbst kennt keine Threads oder Sperren.
    # Kein freier Platz kann doppelt vergeben werden; welcome kommt
    # immer vor dem gameStart fuer dieselbe Verbindung.
    with game["lock"]:
        try:
            response = process(message, connection, game, sock)
        except spiel.RuleError as exc:
            response = {"type": "error", "code": exc.code, "message": str(exc)}
        if response is None:
            return

        slot = connection["slot"]
        if slot is None:
            send(sock, response)
            log_message("->", connection.get("peer", "nicht angemeldet"), response, game)
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
        if response["type"] in ("welcome", "placeAck", "result"):
            send_states(game)
        if response["type"] == "result" and game["core"].winner is not None:
            # Nach dem letzten Zug sehen beide erst ihren bestaetigten Zustand.
            broadcast(game, {
                "type": "gameOver",
                "winner": game["core"].winner,
                "reason": game["core"].reason,
            })


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
        send_states(game)


def handle_connection(sock: socket.socket, address, game: dict) -> None:
    print("verbunden:", address, flush=True)
    connection = {"slot": None, "leaving": False, "peer": address}
    try:
        for message in read_messages(sock):
            log_message("<-", address, message, game, connection["slot"])
            handle(message, connection, game, sock)
            if connection["leaving"]:
                break
    except (OSError, UnicodeError) as exc:
        print(f"Verbindung {address} beendet: {type(exc).__name__}", flush=True)
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
    parser.add_argument("--port", type=int, default=PORT,
                        help="TCP-Port (Standard: PORT-Umgebungsvariable oder 5000)")
    parser.add_argument("--log-file", type=Path, help="Neue JSONL-Datei; vorhandene Dateien werden abgelehnt")
    args = parser.parse_args()
    try:
        game = new_game(log_file=args.log_file)
    except OSError as exc:
        parser.exit(1, f"Nachrichtenlog konnte nicht angelegt werden: {exc}\n")
    connections = []
    print("Nachrichtenlog:", game["event_log"].path, flush=True)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((args.host, args.port))
            listener.listen()
            print("Server wartet auf Port", listener.getsockname()[1], flush=True)
            while True:
                sock, address = listener.accept()
                worker = threading.Thread(target=handle_connection, args=(sock, address, game), daemon=True)
                connections.append((sock, worker))
                worker.start()
    except KeyboardInterrupt:
        print("Server beendet", flush=True)
    except OSError as exc:
        parser.exit(1, f"Server konnte nicht gestartet werden: {exc}\n")
    finally:
        for sock, worker in connections:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()
        for sock, worker in connections:
            worker.join(timeout=3)
        game["event_log"].close()


if __name__ == "__main__":
    main()
