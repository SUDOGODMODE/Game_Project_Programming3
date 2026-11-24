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
PORT = int(os.environ.get("PORT", "5100"))
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

    players speichert Sockets, Namen, Verbindung und Siege, taken die belegten
    Slots. spectators enthaelt die Zuschauerverbindungen unter derselben Sperre.
    rematch enthaelt die Slots mit offenem Revanchewunsch. core verwaltet die
    eigentlichen Spielregeln, Flotten und Schuesse der laufenden Partie. lock
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
        "spectators": [],
        "rematch": set(),
        "players": {
            slot: {
                "sock": None,
                "name": None,
                "connection": None,
                "wins": 0,
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


def send_spectator(game: dict, connection: dict, message: dict) -> None:
    """Sendet ohne Spielerslot; ein verschwundener Zuschauer stoppt keinen Rundruf."""
    try:
        send(connection["sock"], message)
        log_message("->", connection.get("peer", "Zuschauer"), message, game)
    except OSError:
        pass  # Der Empfangsthread entfernt die Verbindung in finally.


def broadcast(game: dict, message: dict) -> None:
    """Schickt an Spieler und Zuschauer. Die Spielsperre ist bereits gehalten."""
    for slot in list(game["taken"]):
        send_to(game, slot, message)
    for connection in game["spectators"]:
        send_spectator(game, connection, message)


def state_for(game: dict, slot) -> dict:
    """Gefilterte Sicht des Kerns plus Punktestand; slot None ist die Zuschauersicht."""
    view = game["core"].public_state() if slot is None else game["core"].state(slot)
    score = [
        {"slot": s, "player": game["players"][s]["name"], "wins": game["players"][s]["wins"]}
        for s in SLOTS if s in game["taken"]
    ]
    return {"type": "state", **view, "score": score}


def send_states(game: dict) -> None:
    """Schickt private Spielersichten und die oeffentliche Sicht unter der Sperre."""
    for slot in list(game["taken"]):
        send_to(game, slot, state_for(game, slot))
    for connection in game["spectators"]:
        send_spectator(game, connection, state_for(game, None))


def send_game_start(game: dict) -> None:
    """Gleiche Startmeldung mit beiden Spielern an Spieler und Zuschauer."""
    broadcast(game, {
        "type": "gameStart",
        "phase": game["core"].phase,
        "players": [
            {"slot": s, "player": game["players"][s]["name"]}
            for s in SLOTS
        ],
    })


def start_rematch(game: dict) -> None:
    """Neue Partie als neues Kernobjekt; die Slots tauschen, damit der andere beginnt.

    Der Kern laesst immer A beginnen. Wer zuletzt B war, wird deshalb A.
    Jeder Spieler erfaehrt seinen neuen Slot ueber ein erneutes welcome.
    """
    game["rematch"].clear()
    players = game["players"]
    players["A"], players["B"] = players["B"], players["A"]
    for slot in SLOTS:
        players[slot]["connection"]["slot"] = slot
    game["core"] = spiel.BattleshipGame()
    game["core"].start()
    for slot in SLOTS:
        send_to(game, slot, {"type": "welcome", "slot": slot, "player": players[slot]["name"],
                             "phase": game["core"].phase})
    send_game_start(game)
    send_states(game)


def process(message: dict, connection: dict, game: dict, sock) -> dict | None:
    """Verarbeitet eine Nachricht unter der Sperre und erstellt die direkte Antwort."""
    msg_type = message.get("type")
    core = game["core"]

    if msg_type == "join":
        if connection["slot"] is not None or connection.get("spectator"):
            return {"type": "error", "code": "ALREADY_JOINED", "message": "diese Verbindung ist bereits angemeldet"}
        name = message.get("player")
        if not isinstance(name, str) or not name.strip():
            return {"type": "error", "code": "MISSING_PLAYER", "message": "Name fehlt"}
        if len(game["taken"]) >= len(SLOTS):
            connection.update(spectator=True, sock=sock)
            game["spectators"].append(connection)
            return {"type": "spectator", "player": name, "phase": core.phase}

        slot = next(s for s in SLOTS if s not in game["taken"])
        game["taken"].append(slot)
        connection["slot"] = slot
        game["players"][slot].update(sock=sock, name=name, connection=connection)
        if len(game["taken"]) == len(SLOTS):
            core.start()
        return {"type": "welcome", "slot": slot, "player": name, "phase": core.phase}

    slot = connection["slot"]
    spectator = connection.get("spectator", False)
    if slot is None and not spectator and msg_type in ("place", "shoot", "getState", "leave", "rematch"):
        return {"type": "error", "code": "NOT_JOINED", "message": "bitte zuerst mit 'join' beitreten"}
    if spectator and msg_type in ("place", "shoot"):
        return {"type": "error", "code": "SPECTATOR_ONLY", "message": "Zuschauer duerfen nicht platzieren oder schiessen"}

    if msg_type == "place":
        return {"type": "placeAck", **core.place_fleet(slot, message.get("ships"))}
    if msg_type == "shoot":
        return {"type": "result", **core.shoot(slot, message.get("field"))}
    if msg_type == "getState":
        return state_for(game, None if spectator else slot)
    if msg_type == "rematch":
        if spectator:
            return {"type": "error", "code": "SPECTATOR_ONLY", "message": "Zuschauer koennen keine Revanche verlangen"}
        if core.phase != "finished":
            return {"type": "error", "code": "WRONG_PHASE",
                    "message": f"aktuelle Phase ist {core.phase}; Revanche erst nach Spielende"}
        if slot in game["rematch"]:
            return {"type": "error", "code": "DUPLICATE_REMATCH", "message": "Revanche bereits verlangt"}
        game["rematch"].add(slot)
        return {"type": "rematchRequested", "slot": slot, "player": game["players"][slot]["name"]}
    if msg_type == "leave":
        connection["leaving"] = True
        return None
    if msg_type == "broken":
        return {"type": "error", "code": "INVALID_JSON", "message": "kein gueltiges JSON"}
    return {"type": "error", "code": "UNKNOWN_TYPE", "message": f"unbekannter Typ: {msg_type}"}


def handle(message: dict, connection: dict, game: dict, sock) -> None:
    """Sendet die direkte Antwort, dann gegebenenfalls die gefilterten Sichten.

    Nach dem letzten Schuss folgen auf result alle state und erst danach
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
        if response["type"] == "rematchRequested":
            # Der erste Wunsch geht an alle; der zweite startet sofort die neue Partie.
            if len(game["rematch"]) < len(SLOTS):
                broadcast(game, response)
            else:
                start_rematch(game)
            return

        slot = connection["slot"]
        if slot is None:
            send(sock, response)
            log_message("->", connection.get("peer", "nicht angemeldet"), response, game)
        else:
            send_to(game, slot, response)

        if response["type"] == "spectator":
            send_spectator(game, connection, state_for(game, None))
        if response["type"] == "welcome":
            if len(game["taken"]) < len(SLOTS):
                send_to(game, slot, {"type": "waiting", "reason": "warte auf Gegner"})
            else:
                send_game_start(game)
        if response["type"] == "result" and game["core"].winner is not None:
            # Der Punkt steht schon in den Endzustaenden; es gibt kein Unentschieden.
            game["players"][game["core"].winner]["wins"] += 1
        if response["type"] in ("welcome", "placeAck", "result"):
            send_states(game)
        if response["type"] == "result" and game["core"].winner is not None:
            # Nach dem letzten Zug sehen alle erst ihren bestaetigten Zustand.
            broadcast(game, {
                "type": "gameOver",
                "winner": game["core"].winner,
                "reason": game["core"].reason,
            })


def remove_player(connection: dict, game: dict) -> None:
    """Entfernt Zuschauer still; ein Spielerabgang verwirft Partie, Wuensche und Punktestand."""
    with game["lock"]:
        if connection.get("spectator"):
            game["spectators"].remove(connection)
            connection["spectator"] = False
            return
        slot = connection["slot"]
        if slot is None:
            return
        player = game["players"][slot]
        name = player["name"]
        player.update(sock=None, name=None, connection=None)
        game["taken"].remove(slot)
        connection["slot"] = None
        game["rematch"].clear()
        for entry in game["players"].values():
            entry["wins"] = 0
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


def bind_listener(host: str, port: int, attempts: int = 1) -> socket.socket:
    """Bindet den ersten freien Port ab port; nach attempts Versuchen gilt der letzte Fehler."""
    for candidate in range(port, port + attempts):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.name != "nt":
            # Unter Windows liesse SO_REUSEADDR einen belegten Port mitbenutzen.
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind((host, candidate))
            return listener
        except OSError:
            listener.close()
            if candidate == port + attempts - 1:
                raise
    raise ValueError("attempts muss mindestens 1 sein")


def main() -> None:
    parser = argparse.ArgumentParser(description="Schiffe-versenken-Server")
    parser.add_argument("--host", default=HOST, help="Bindeadresse (Standard: alle Netzwerkkarten)")
    parser.add_argument("--port", type=int,
                        help="TCP-Port (Standard: PORT-Umgebungsvariable oder 5100; "
                             "ist 5100 belegt, der naechste freie)")
    parser.add_argument("--log-file", type=Path, help="Neue JSONL-Datei; vorhandene Dateien werden abgelehnt")
    args = parser.parse_args()
    try:
        game = new_game(log_file=args.log_file)
    except OSError as exc:
        parser.exit(1, f"Nachrichtenlog konnte nicht angelegt werden: {exc}\n")
    connections = []
    print("Nachrichtenlog:", game["event_log"].path, flush=True)
    # Nur der Standardport weicht aus; einen selbst gewaehlten Port nimmt der Server genau.
    chosen = args.port is None and "PORT" not in os.environ
    port = PORT if args.port is None else args.port
    try:
        with bind_listener(args.host, port, attempts=20 if chosen else 1) as listener:
            listener.listen()
            actual = listener.getsockname()[1]
            print("Server wartet auf Port", actual, flush=True)
            if actual != port:
                print(f"Port {port} ist belegt. Clients mit --port {actual} starten, etwa:\n"
                      f"  python3 src/client_gui.py 127.0.0.1 Alice --port {actual}", flush=True)
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
