"""netz.py: Nachrichtenprotokoll ueber TCP - eine JSON-Nachricht pro Zeile.

Ein einzelnes recv() liefert keine vollstaendige Nachricht, sondern nur so
viele Bytes, wie gerade im Empfangspuffer stehen - das kann weniger oder
mehr als eine Nachricht sein, und TCP kennt von sich aus keine Nachrichten-
grenzen (Uebung 3 im Uebungsheft "Netzwerkprogrammierung"). Deshalb
verwendet dieses Modul ein einfaches Zeilen-Framing: jede Nachricht ist
genau eine Zeile JSON, abgeschlossen mit "\\n". sock.makefile() puffert die
eingehenden Bytes intern und liefert damit zuverlaessig eine vollstaendige
Zeile nach der anderen, unabhaengig davon, wie die TCP-Pakete tatsaechlich
ankommen oder zerstueckelt werden (Uebung 4).

Begriffe folgen dem eigenen Protokoll (docs/protocol/protocol.json):
jede Nachricht ist ein dict mit einem englischen "type"-Feld, und auch die
Funktionsnamen hier sind bewusst Englisch, konsistent mit dem Rest des
Codes und der Dokumentation.
"""
from __future__ import annotations

import json
from typing import Iterator

ENCODING = "utf-8"


def send(sock, message: dict) -> None:
    """Serialisiert `message` als JSON und schickt sie als eine Zeile.

    Wirft die ueblichen Socket-Fehler (z.B. BrokenPipeError,
    ConnectionResetError) unveraendert weiter, wenn die Gegenseite die
    Verbindung bereits geschlossen hat - der Aufrufer sieht dann denselben
    Fehler wie bei jedem anderen sendall().
    """
    line = json.dumps(message, ensure_ascii=False) + "\n"
    sock.sendall(line.encode(ENCODING))


def read_messages(sock) -> Iterator[dict]:
    """Liefert eintreffende Nachrichten einzeln, sobald je eine volle Zeile da ist.

    Bricht die Gegenseite die Verbindung ab, endet die Schleife von selbst
    (makefile liefert dann keine weiteren Zeilen mehr, der Generator ist
    einfach erschoepft). Eine Zeile, die kein gueltiges JSON ist, fuehrt
    nicht zum Absturz: Es wird eine Ersatznachricht vom Typ "broken"
    geliefert, und der Aufrufer entscheidet selbst, was damit passiert
    (siehe server.py: handle()).

    Dasselbe gilt fuer eine Zeile, die zwar gueltiges JSON ist, aber kein
    Objekt - z.B. eine blosse Zahl, Zeichenkette oder Liste wie "[1,2,3]".
    json.loads liefert dafuer keinen JSONDecodeError, aber auch kein dict;
    ein Aufrufer, der blind message.get("type") aufruft, wuerde sonst mit
    einem AttributeError abstuerzen - genau die Art von Angriff, die
    Uebung 4 vorwegnimmt: "Jedes Programm darf sich mit Ihrem Port
    verbinden und schicken, was es will."
    """
    stream = sock.makefile("r", encoding=ENCODING, newline="\n")
    for line in stream:
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            yield {"type": "broken"}
            continue
        if not isinstance(parsed, dict):
            yield {"type": "broken"}
            continue
        yield parsed
