"""test_angriff.py: schickt absichtlich falsche Nachrichten."""
import socket
import sys

from netz import send, read_messages

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000

with socket.create_connection((HOST, PORT)) as sock:
    responses = read_messages(sock)
    attempts = [
        {"type": "nonsense"},
        {"player": "Alice"},
        {"type": "join"},
        {"type": "join", "player": "Bob"},
        {"type": "join", "player": "Bob"},
    ]
    for a in attempts:
        send(sock, a)
        print("->", a)
        print("<-", next(responses))
    sock.sendall(b"das ist kein json\n")
    print("-> das ist kein json")
    print("<-", next(responses))

    # gueltiges JSON, aber kein Objekt - haette ohne den isinstance-Check in
    # netz.py einen AttributeError ausgeloest, sobald der Server versucht,
    # message.get("type") auf einer Liste aufzurufen.
    sock.sendall(b"[1,2,3]\n")
    print("-> [1,2,3]")
    print("<-", next(responses))
