"""Schickt absichtlich falsche Nachrichten und prueft die direkten Antworten."""
import argparse
import socket

from netz import send, read_messages

PUSH_TYPES = ("waiting", "gameStart", "opponentLeft")


def next_response(messages):
    for message in messages:
        print("<-", message, flush=True)
        if message.get("type") not in PUSH_TYPES:
            return message
    raise AssertionError("Server hat die Verbindung vor der Antwort beendet")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fehlerhafte Handshake-Nachrichten testen")
    parser.add_argument("host", nargs="?", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    with socket.create_connection((args.host, args.port), timeout=5) as sock:
        messages = read_messages(sock)
        attempts = [
            ({"type": "nonsense"}, "UNKNOWN_TYPE"),
            ({"player": "Alice"}, "UNKNOWN_TYPE"),
            ({"type": "join"}, "MISSING_PLAYER"),
            ({"type": "join", "player": "Bob"}, None),
            ({"type": "join", "player": "Bob"}, "ALREADY_JOINED"),
        ]
        for message, expected_code in attempts:
            send(sock, message)
            print("->", message, flush=True)
            response = next_response(messages)
            if expected_code is None:
                assert response["type"] == "welcome", response
            else:
                assert response["type"] == "error" and response["code"] == expected_code, response
        for raw in (b"das ist kein json\n", b"[1,2,3]\n"):
            sock.sendall(raw)
            print("->", raw.decode().strip(), flush=True)
            response = next_response(messages)
            assert response["type"] == "error" and response["code"] == "INVALID_JSON", response
    print("Alle Handshake-Angriffe wie erwartet abgelehnt.", flush=True)


if __name__ == "__main__":
    main()
