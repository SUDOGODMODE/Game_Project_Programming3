"""client.py: verbindet sich, tritt bei und zeigt die Antwort."""
import socket
import sys

from netz import send, read_messages

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000

with socket.create_connection((HOST, PORT)) as sock:
    responses = read_messages(sock)

    join_message = {"type": "join", "player": "Alice"}
    send(sock, join_message)
    print("->", join_message)
    print("<-", next(responses))
