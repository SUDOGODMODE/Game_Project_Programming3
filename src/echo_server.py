"""M0: Ein einfacher TCP-Server schreibt empfangene Bytes gross zurueck."""
import argparse
import socket


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((args.host, args.port))
            listener.listen()
            print(f"warte auf Port {listener.getsockname()[1]} ...", flush=True)
            while True:
                connection, address = listener.accept()
                with connection:
                    print("verbunden mit", address, flush=True)
                    try:
                        while True:
                            data = connection.recv(1024)
                            if not data:
                                break
                            connection.sendall(data.upper())
                    except ConnectionError:
                        print("Verbindung unterbrochen", flush=True)
                print("Gegenseite hat geschlossen", flush=True)
    except KeyboardInterrupt:
        print("\nEcho-Server beendet.")


if __name__ == "__main__":
    main()
