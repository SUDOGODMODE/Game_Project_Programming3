"""Interaktiver Konsolenclient: Standardflotte, Schuesse und Zustandsabfrage."""
import argparse
import socket
import sys
import threading

from netz import send, read_messages

DEFAULT_FLEET = [
    {"type": "Carrier", "start": "A1", "direction": "h"},
    {"type": "Battleship", "start": "A2", "direction": "h"},
    {"type": "Cruiser", "start": "A3", "direction": "h"},
    {"type": "Submarine", "start": "A4", "direction": "h"},
    {"type": "Destroyer", "start": "A5", "direction": "h"},
]


def message_for_command(line: str) -> dict | None:
    """Uebersetzt eine Terminaleingabe; None bedeutet eine leere Eingabe.

    Auch ungueltige Schussfelder gehen an den Server: Er prueft die Regeln.
    """
    command = line.strip()
    if not command:
        return None
    if command.lower() in ("quit", "q"):
        return {"type": "leave"}
    if command.lower() == "state":
        return {"type": "getState"}
    return {"type": "shoot", "field": command.upper()}


def shot_result_text(message: dict, my_slot: str | None) -> str:
    """Formatiert das bestaetigte Schussergebnis und die folgende Zuganzeige."""
    sunk_text = ""
    if message.get("sunk"):
        sunk_text = f" - {message['sunk']} versenkt!"
    if message["turn"] is None:
        turn_text = " Gewonnen! q beendet den Client."
    elif message["turn"] == my_slot:
        turn_text = " Du bist am Zug."
    else:
        turn_text = " Der Gegner ist am Zug."
    return f"Schuss auf {message['field']}: {message['result']}{sunk_text}{turn_text}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Schiffe versenken im Terminal")
    parser.add_argument("host", nargs="?", default="127.0.0.1")
    parser.add_argument("name", nargs="?", default="Spieler")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    try:
        with socket.create_connection((args.host, args.port), timeout=5) as sock:
            sock.settimeout(None)
            send_lock = threading.Lock()
            print_lock = threading.Lock()

            def show(text):
                with print_lock:
                    print(text, flush=True)

            def send_message(message):
                # Haupt- und Empfangsthread senden auf denselben Socket.
                with send_lock:
                    send(sock, message)

            def listen():
                my_slot = None
                try:
                    for message in read_messages(sock):
                        kind = message.get("type")
                        if kind == "welcome":
                            my_slot = message["slot"]
                            show(f"Willkommen, {message['player']}! Du bist Spieler {my_slot}.")
                        elif kind == "waiting":
                            show("Warte auf Gegner.")
                        elif kind == "gameStart":
                            show(f"Neue Partie: {message['players']}. Standardflotte wird platziert.")
                            send_message({"type": "place", "ships": DEFAULT_FLEET})
                        elif kind == "placeAck":
                            show(f"Flotte platziert. Phase: {message['phase']}")
                        elif kind == "opponentLeft":
                            show(f"{message['player']} hat das Spiel verlassen. Runde zurueckgesetzt; warte auf Gegner.")
                        elif kind == "result":
                            show(shot_result_text(message, my_slot))
                        elif kind == "state":
                            show(f"Zustand -> Phase: {message['phase']}, am Zug: {message['turn']}, "
                                 f"eigene Schiffe: {len(message['ownShips'])}, "
                                 f"eigene Schuesse: {len(message['shotsAtOpponent'])}")
                        elif kind == "gameOver":
                            show(f"Spiel beendet. Gewinner: {message['winner']}. q beendet den Client.")
                        elif kind == "error":
                            show(f"Fehler: {message['code']} - {message['message']}")
                        else:
                            show(str(message))
                except (OSError, UnicodeError) as exc:
                    show(f"Empfang beendet: {exc}")
                finally:
                    show("Verbindung beendet")

            listener = threading.Thread(target=listen, daemon=True)
            listener.start()
            try:
                send_message({"type": "join", "player": args.name})
                show("Standardflotte: Zeilen 1-5, ab Spalte A. Befehle: C5, state, quit oder q.")
                show("Zug und Zustand kommen automatisch; state fragt sie zusaetzlich ab.")
                for line in sys.stdin:
                    message = message_for_command(line)
                    if message is None:
                        continue
                    send_message(message)
                    if message["type"] == "leave":
                        break
            finally:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                listener.join(timeout=1)
    except KeyboardInterrupt:
        print("Client beendet", flush=True)
    except OSError as exc:
        parser.exit(1, f"Verbindung fehlgeschlagen: {exc}\n")


if __name__ == "__main__":
    main()
