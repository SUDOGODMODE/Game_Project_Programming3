"""M0: Sendet eine Nachricht an den Echo-Server und liest die ganze Antwort."""
import argparse
import socket


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", nargs="?", default="127.0.0.1")
    parser.add_argument("message", nargs="?", default="hallo netz")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_intermixed_args()
    try:
        with socket.create_connection((args.host, args.port), timeout=10) as connection:
            connection.sendall((args.message + "\n").encode("utf-8"))
            connection.shutdown(socket.SHUT_WR)
            chunks = []
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                chunks.append(data)
        print("Antwort:", b"".join(chunks).decode("utf-8").rstrip("\n"))
    except OSError as error:
        parser.exit(1, f"Verbindungsfehler: {error}\n")


if __name__ == "__main__":
    main()
