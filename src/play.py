"""play.py: interaktiver Client, mit dem sich eine echte Partie spielen laesst.

client.py bleibt unveraendert der Beitritts-Client aus dem ersten
Meilenstein ("Der erste Handschlag") - das ist die dort geforderte und
dokumentierte Abgabe. Dieses Skript deckt das ganze Protokoll ab: beitreten,
Flotte platzieren, schiessen, Zustand abfragen, und zeigt eingehende
Nachrichten laufend an, auch unaufgeforderte wie gameOver. Dafuer liest ein
Hintergrundfaden staendig vom Socket, waehrend im Vordergrund auf Eingaben
gewartet wird - sonst wuerde ein blockierendes input() den Zug des Gegners
verpassen, bis man selbst wieder etwas eingibt.
"""
import socket
import sys
import threading
import time

from netz import send, read_messages

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000
PLAYER = sys.argv[2] if len(sys.argv) > 2 else (input("Dein Name: ").strip() or "Spieler")

# Standardflotte: alle fuenf Schiffe nebeneinander in den Zeilen 1-5, Spalte A.
# Von Hand platzieren waere moeglich (eine "place"-Nachricht mit eigenen
# Koordinaten schicken), fuer eine spielbare Partie am Terminal reicht eine
# feste, gueltige Aufstellung.
DEFAULT_FLEET = [
    {"type": "Carrier", "start": "A1", "direction": "h"},
    {"type": "Battleship", "start": "A2", "direction": "h"},
    {"type": "Cruiser", "start": "A3", "direction": "h"},
    {"type": "Submarine", "start": "A4", "direction": "h"},
    {"type": "Destroyer", "start": "A5", "direction": "h"},
]

my_slot = None
placed = threading.Event()
game_over = threading.Event()
print_lock = threading.Lock()


def show(text: str) -> None:
    """Druckt eine Zeile und danach wieder die Eingabeaufforderung."""
    with print_lock:
        print(text)
        print("> ", end="", flush=True)


def place_when_ready(sock) -> None:
    """Versucht zu platzieren, sobald der zweite Spieler beigetreten ist.

    Es gibt keine Push-Nachricht im Protokoll, die meldet, wann der Gegner
    beitritt - der Server antwortet auf ein zu frueh geschicktes "place"
    einfach mit WRONG_PHASE ("aktuelle Phase ist waiting"), solange noch
    niemand zweites da ist. Ein einziger fester Versuch nach dem Beitritt
    wuerde also genau dann scheitern, wenn der Gegner etwas langsamer ist,
    und ohne Wiederholung bliebe die Partie fuer immer in "waiting" haengen.
    Deshalb wird "place" hier wiederholt, bis entweder placeAck kommt
    (siehe listen()) oder die Partie vorbei ist.
    """
    while not placed.is_set() and not game_over.is_set():
        send(sock, {"type": "place", "ships": DEFAULT_FLEET})
        time.sleep(0.5)


def listen(messages) -> None:
    """Laeuft im Hintergrund und zeigt jede ankommende Nachricht sofort an."""
    global my_slot
    for message in messages:
        kind = message.get("type")
        if kind == "welcome":
            my_slot = message["slot"]
            show(f"\nWillkommen, {message['player']}! Du bist Spieler {my_slot}. Phase: {message['phase']}")
        elif kind == "placeAck":
            placed.set()
            show(f"\nFlotte platziert. Phase: {message['phase']}")
        elif kind == "result":
            zusatz = f" - {message['sunk']} versenkt!" if message.get("sunk") else ""
            if message.get("turn") is None:
                zug = " Spiel beendet."
            elif message["turn"] == my_slot:
                zug = " Du bist am Zug."
            else:
                zug = " Der Gegner ist am Zug."
            show(f"\nSchuss auf {message['field']}: {message['result']}{zusatz}{zug}")
        elif kind == "state":
            show(
                f"\nZustand -> Phase: {message['phase']}, am Zug: {message['turn']}, "
                f"eigene Schiffe: {len(message['ownShips'])}, "
                f"eigene Schuesse: {len(message['shotsAtOpponent'])}"
            )
        elif kind == "gameOver":
            sieger = "Du hast" if message["winner"] == my_slot else "Der Gegner hat"
            show(f"\n{sieger} gewonnen! (Grund: {message['reason']})")
            game_over.set()
        elif kind == "error":
            # WRONG_PHASE waehrend der eigene Platzierungsversuch noch
            # laeuft ist der erwartete, stille Fall aus place_when_ready()
            # und wird nicht extra gemeldet - alles andere schon.
            if message.get("code") == "WRONG_PHASE" and not placed.is_set():
                continue
            show(f"\nFehler: {message['code']} - {message['message']}")
        else:
            show(f"\n{message}")


def main() -> None:
    with socket.create_connection((HOST, PORT)) as sock:
        messages = read_messages(sock)
        threading.Thread(target=listen, args=(messages,), daemon=True).start()

        send(sock, {"type": "join", "player": PLAYER})
        threading.Thread(target=place_when_ready, args=(sock,), daemon=True).start()

        print(f"Verbunden als {PLAYER}. Standardflotte wird automatisch platziert (Zeilen 1-5, Spalte A),")
        print("sobald der zweite Spieler beigetreten ist.")
        print("Befehle: <Feld> schiesst (z.B. C5), 'state' zeigt den Zustand, 'quit' verlaesst das Spiel.\n")

        while not game_over.is_set():
            try:
                befehl = input("> ").strip()
            except EOFError:
                break
            if not befehl:
                continue
            if befehl.lower() == "quit":
                send(sock, {"type": "leave"})
                break
            if befehl.lower() == "state":
                send(sock, {"type": "getState"})
                continue
            send(sock, {"type": "shoot", "field": befehl.upper()})

        time.sleep(0.3)  # letzte Antworten noch anzeigen lassen, bevor der Socket schliesst


if __name__ == "__main__":
    main()
