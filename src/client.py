"""Beitrittsclient: hoert auch ohne eigene Anfrage weiter zu."""
import argparse
import socket
import sys
import threading

from netz import send, read_messages


def receive(sock: socket.socket) -> None:
    try:
        for message in read_messages(sock):
            print("<-", message, flush=True)
    except (OSError, UnicodeError) as exc:
        print("Empfang beendet:", exc, flush=True)
    finally:
        print("Verbindung beendet", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Beitreten und Servermeldungen anzeigen")
    parser.add_argument("host", nargs="?", default="127.0.0.1")
    parser.add_argument("name", nargs="?", default="Alice")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    try:
        with socket.create_connection((args.host, args.port), timeout=5) as sock:
            sock.settimeout(None)
            listener = threading.Thread(target=receive, args=(sock,), daemon=True)
            listener.start()
            try:
                message = {"type": "join", "player": args.name}
                send(sock, message)
                print("->", message, flush=True)
                print("Enter q zum Beenden.", flush=True)
                for line in sys.stdin:
                    if line.strip().lower() == "q":
                        break
            finally:
                # shutdown beendet auch das blockierende makefile-Lesen.
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
