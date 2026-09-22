# HFTM · Projekt · Meilenstein

## Der erste Handschlag

Dein Client meldet sich mit einer Nachricht aus deinem eigenen Protokoll beim Server an. Der Server erkennt, was die Nachricht will, vergibt dir eine Spieler-ID und antwortet. Über zwei Rechner.

## Einstieg

### Worum es heute geht

Dein Protokollentwurf beschreibt, welche Nachrichten es in deinem Spiel gibt. Bis jetzt steht er nur auf Papier. Heute schickst du zum ersten Mal eine dieser Nachrichten wirklich über das Netz, und der Server antwortet mit einer anderen.

Dabei stellen sich zwei Fragen, die dein ganzes Projekt tragen:

Woran erkennt der Server, was eine Nachricht von ihm will? Und wer entscheidet, wer du im Spiel bist?

Die Antwort auf die erste Frage ist das Feld `type` in jeder Nachricht. Die Antwort auf die zweite ist: der Server. Er vergibt die Spieler-ID, nicht der Client. Beides baust du heute ein.

Der ganze Ablauf besteht aus zwei Nachrichten:

```
Client                                          Server
  |                                               |
  |  {"type": "join", "player": "Alice"}          |
  | --------------------------------------------> |
  |                                               |  liest type,
  |                                               |  vergibt ID 1
  |  {"type": "welcome", "playerId": 1, ...}      |
  | <-------------------------------------------- |
  |                                               |
```

Du gehst in zwei Runden vor. Zuerst bringst du eine fertige, geprüfte Version zum Laufen (Schritt 2 bis 5). Erst wenn sie läuft, baust du sie auf dein eigenes Protokoll um (Schritt 6). So weisst du bei jedem Fehler, ob er im Netzcode liegt oder in deiner Anpassung.

## Schritt 1 — Protokoll vorbereiten

Für heute brauchst du aus deinem Protokoll nur drei Nachrichten: die Beitrittsnachricht vom Client, die Willkommensantwort vom Server und eine Ablehnung vom Server. Prüfe sie gegen drei Regeln.

### Regel 1: Der Typ steht in der Nachricht selbst

Viele Entwürfe sind so aufgebaut:

```json
"join": {
    "request": { "player": "Alice" },
    ...
}
```

Im Dokument ist klar, dass das ein `join` ist, weil es darunter steht. Über die Leitung geht aber nur das, was in `request` steht:

```json
{"player": "Alice"}
```

Daran kann der Server nicht erkennen, was gemeint ist. Deshalb gehört der Typ in die Nachricht:

```json
{"type": "join", "player": "Alice"}
```

Das gilt auch für jede Antwort des Servers. Der Client muss ebenfalls erkennen können, ob er ein Willkommen oder eine Ablehnung bekommen hat. Steht deine Antwort im Entwurf nur als `response` unter `join`, hat sie noch keinen eigenen Typnamen. Gib ihr einen, zum Beispiel `welcome`.

### Regel 2: Der Client schickt keine Spieler-ID

Wenn der Client beim Beitritt seine ID mitschickt, kann er sich jede ID aussuchen, auch die des Gegners. Der Client schickt nur seinen Namen. Die ID vergibt der Server und teilt sie in der Antwort mit.

### Regel 3: Es gibt eine Ablehnung mit Grund

Der Server muss auf jede Nachricht antworten können, auch auf eine falsche. Dafür brauchst du eine Nachricht wie `{"type": "rejected", "reason": "..."}`.

### Weiter, wenn

- [ ] Du hast deine drei Nachrichten für heute als vollständige JSON-Zeilen aufgeschrieben, jede mit Typfeld.
- [ ] In der Beitrittsnachricht steht keine Spieler-ID.

## Schritt 2 — netz.py

Lege einen neuen Ordner für dein Projekt an. Darin kommt als Erstes `netz.py`. Diese Datei hast du in Übung 4 gebaut, hier steht sie nochmals vollständig. Warum sie so aussieht, steht im Skript in Kapitel 2.3 und 2.4: Ein `recv` ist keine Nachricht, deshalb schickst du jede Nachricht als eine Zeile, und `makefile` setzt die Zeilen auf der Gegenseite wieder zusammen.

```python
"""netz.py: Nachrichten als JSON-Zeilen senden und lesen."""
import json


def sende(sock, nachricht: dict) -> None:
    zeile = json.dumps(nachricht, ensure_ascii=False) + "\n"
    sock.sendall(zeile.encode("utf-8"))


def leser(sock):
    datei = sock.makefile("r", encoding="utf-8", newline="\n")
    for zeile in datei:
        zeile = zeile.strip()
        if not zeile:
            continue
        try:
            yield json.loads(zeile)
        except json.JSONDecodeError:
            yield {"type": "kaputt"}
```

`sende` macht aus einem Dictionary eine JSON-Zeile mit `\n` am Ende und schickt sie mit `sendall`.

`leser` liefert eine Nachricht nach der anderen. Die Schleife endet, wenn die Gegenseite die Verbindung schliesst.

Kommt eine Zeile, die kein JSON ist, stürzt nichts ab. Stattdessen kommt eine Nachricht vom Typ `kaputt`, und der Server entscheidet, was er damit tut.

Wenn dein Protokoll `typ` statt `type` verwendet, ändere es auch in der letzten Zeile. Der Schlüssel muss überall gleich heissen.

## Schritt 3 — Der Server

Lege `server.py` im selben Ordner an.

```python
"""server.py: nimmt Verbindungen nacheinander an und fuehrt den Handschlag aus."""
import socket

from netz import sende, leser

HOST, PORT = "0.0.0.0", 5000


def behandeln(nachricht, verbindung, zaehler):
    """Entscheidet anhand von type, was zu tun ist. Gibt die Antwort zurueck."""
    typ = nachricht.get("type")

    if typ == "join":
        if verbindung["spieler_id"] is not None:
            return {"type": "rejected", "reason": "bereits beigetreten"}
        name = nachricht.get("player")
        if not isinstance(name, str) or not name.strip():
            return {"type": "rejected", "reason": "Name fehlt"}
        verbindung["spieler_id"] = zaehler["naechste_id"]
        zaehler["naechste_id"] += 1
        return {"type": "welcome", "playerId": verbindung["spieler_id"], "player": name}

    if typ == "kaputt":
        return {"type": "rejected", "reason": "kein gueltiges JSON"}

    return {"type": "rejected", "reason": f"unbekannter Typ: {typ}"}


def main():
    zaehler = {"naechste_id": 1}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as horcher:
        horcher.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        horcher.bind((HOST, PORT))
        horcher.listen()
        print("Server wartet auf Port", PORT)
        while True:
            sock, adresse = horcher.accept()
            print("verbunden:", adresse)
            verbindung = {"spieler_id": None}
            with sock:
                for nachricht in leser(sock):
                    print("  <-", nachricht)
                    antwort = behandeln(nachricht, verbindung, zaehler)
                    sende(sock, antwort)
                    print("  ->", antwort)
            print("getrennt:", adresse)


if __name__ == "__main__":
    main()
```

`behandeln` ist die einzige Stelle, an der entschieden wird. Sie schaut auf `type` und gibt die passende Antwort zurück. Für jede neue Nachricht in deinem Protokoll kommt später hier ein weiteres `if` dazu.

`nachricht.get("type")` statt `nachricht["type"]`: Fehlt das Feld, kommt `None`, und die Nachricht wird abgelehnt. Mit eckigen Klammern würde der Server mit einem `KeyError` abstürzen.

`verbindung` gehört zu genau einer Verbindung. Darin merkt sich der Server, welche Spieler-ID dieser Client bekommen hat. Deshalb muss der Client seine ID nie mitschicken: Der Server weiss aus der Verbindung, wer spricht. Das ist Regel 2 aus Schritt 1, umgesetzt.

`zaehler` lebt über alle Verbindungen hinweg und zählt die IDs hoch. Er ist ein Dictionary, damit `behandeln` ihn verändern kann.

Die äussere `while True`-Schleife nimmt Verbindungen nacheinander an. Geht ein Client, wartet der Server auf den nächsten, statt sich zu beenden.

`HOST = "0.0.0.0"` heisst: auf allen Netzwerkkarten. Nur so erreicht dich in Schritt 7 ein anderer Rechner.

Starte den Server im linken Terminal:

```
$ python3 server.py
Server wartet auf Port 5000
```

Lass ihn laufen. Er wartet jetzt in `accept()`.

## Schritt 4 — Der Client

Lege `client.py` im selben Ordner an.

```python
"""client.py: verbindet sich, tritt bei und zeigt die Antwort."""
import socket
import sys

from netz import sende, leser

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000

with socket.create_connection((HOST, PORT)) as sock:
    antworten = leser(sock)

    beitritt = {"type": "join", "player": "Alice"}
    sende(sock, beitritt)
    print("->", beitritt)
    print("<-", next(antworten))
```

`sys.argv[1]` ist die Server-Adresse, die du beim Start mitgibst. Ohne Angabe verbindet sich der Client mit dem eigenen Rechner.

`next(antworten)` holt genau eine Nachricht aus dem Leser und wartet, bis sie da ist.

### Vor dem Start schriftlich

Was gibt der Client aus, und was der Server? Schreib beide Ausgaben hin. Und: Welche Spieler-ID bekommst du, wenn du den Client ein zweites Mal startest?

Starte den Client im rechten Terminal:

```
$ python3 client.py
-> {'type': 'join', 'player': 'Alice'}
<- {'type': 'welcome', 'playerId': 1, 'player': 'Alice'}
```

Im Server-Terminal steht:

```
verbunden: ('127.0.0.1', 43664)
  <- {'type': 'join', 'player': 'Alice'}
  -> {'type': 'welcome', 'playerId': 1, 'player': 'Alice'}
getrennt: ('127.0.0.1', 43664)
```

Beim zweiten Start bekommst du die ID 2. Der Server hat sich die letzte vergebene ID gemerkt, der Client weiss davon nichts.

### Weiter, wenn

- [ ] Der Client zeigt die Willkommensantwort mit einer Spieler-ID.
- [ ] Der Server läuft nach dem Ende des Clients weiter.
- [ ] Ein zweiter Start ergibt eine neue ID.

## Schritt 5 — Der böse Client

Ein Server, der nur mit dem eigenen Client funktioniert, ist kein Server. Jedes Programm darf sich mit deinem Port verbinden und schicken, was es will. Dieses Skript schickt absichtlich falsche Nachrichten.

```python
"""test_angriff.py: schickt absichtlich falsche Nachrichten."""
import socket
import sys

from netz import sende, leser

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000

with socket.create_connection((HOST, PORT)) as sock:
    antworten = leser(sock)
    versuche = [
        {"type": "quatsch"},
        {"player": "Alice"},
        {"type": "join"},
        {"type": "join", "player": "Bob"},
        {"type": "join", "player": "Bob"},
    ]
    for n in versuche:
        sende(sock, n)
        print("->", n)
        print("<-", next(antworten))
    sock.sendall(b"das ist kein json\n")
    print("-> das ist kein json")
    print("<-", next(antworten))
```

### Vor dem Start schriftlich

Welche Antwort erwartest du auf jede der sechs Nachrichten? Achte besonders auf den zweiten Beitritt von Bob.

```
$ python3 test_angriff.py
-> {'type': 'quatsch'}
<- {'type': 'rejected', 'reason': 'unbekannter Typ: quatsch'}
-> {'player': 'Alice'}
<- {'type': 'rejected', 'reason': 'unbekannter Typ: None'}
-> {'type': 'join'}
<- {'type': 'rejected', 'reason': 'Name fehlt'}
-> {'type': 'join', 'player': 'Bob'}
<- {'type': 'welcome', 'playerId': 2, 'player': 'Bob'}
-> {'type': 'join', 'player': 'Bob'}
<- {'type': 'rejected', 'reason': 'bereits beigetreten'}
-> das ist kein json
<- {'type': 'rejected', 'reason': 'kein gueltiges JSON'}
```

Die zweite Nachricht ist genau der Fall aus Regel 1: eine Beitrittsnachricht ohne Typ. Der Server kann nichts damit anfangen und lehnt sie ab. Der zweite Beitritt von Bob wird abgelehnt, weil sich der Server gemerkt hat, dass diese Verbindung schon eine ID hat.

### Weiter, wenn

- [ ] Jede falsche Nachricht bekommt eine Ablehnung mit Grund.
- [ ] Der Server läuft danach weiter und nimmt einen normalen Client an.

## Schritt 6 — Auf dein eigenes Protokoll umbauen

Jetzt läuft eine geprüfte Version. Erst jetzt ersetzt du die Namen durch die aus deinem Protokoll. Ändere eine Sache, teste, dann die nächste.

| Datei | Was du änderst |
|---|---|
| `client.py` | Die Beitrittsnachricht: Typname und Felder aus deinem Protokoll, dein Name. |
| `server.py` | In `behandeln`: den Typnamen im `if`, den Namen des Feldes, aus dem der Spielername gelesen wird, und die Willkommensantwort mit Typname und Feldern aus deinem Protokoll. |
| `server.py` | Die Ablehnungen: Typname und Feldname aus deinem Protokoll. |
| `test_angriff.py` | Die beiden Beitritte von Bob in deinem Format. |
| Protokolldatei | Alles, was du beim Umbau geändert hast, nachtragen. Code und Protokoll müssen übereinstimmen. |

### Typische Stelle, an der es klemmt

Du hast den Typnamen im Client geändert, aber nicht im Server, oder umgekehrt. Der Server antwortet dann mit `unbekannter Typ` und nennt dir den Namen, den er bekommen hat. Vergleiche ihn Zeichen für Zeichen mit dem im `if`. Gross- und Kleinschreibung zählt.

### Weiter, wenn

- [ ] Client und Server verwenden die Nachrichten aus deinem Protokoll.
- [ ] Der böse Client aus Schritt 5 läuft auch mit deinem Format durch.
- [ ] Die Protokolldatei stimmt mit dem Code überein.

## Schritt 7 — Über zwei Rechner

Bis jetzt lief alles auf deinem Rechner. Jetzt verbindet sich jemand anderes mit deinem Server.

1. Finde deine IP-Adresse: `ipconfig` unter Windows, `ip addr` unter Linux, `ifconfig` oder die Systemeinstellungen unter macOS. Du suchst eine Adresse im Schulnetz, nicht `127.0.0.1`.
2. Starte deinen Server.
3. Jemand aus der Klasse startet deinen Client auf seinem Rechner, mit deiner Adresse: `python3 client.py 192.168.1.42`
4. Danach umgekehrt: Du startest deinen Client gegen den Server der anderen Person.

Unter Windows fragt die Firewall beim ersten Start des Servers nach. Erlaube den Zugriff für private Netzwerke.

### Weiter, wenn

- [ ] Ein Client auf einem anderen Rechner hat von deinem Server eine Willkommensantwort bekommen.
- [ ] In deinem Server-Terminal steht als Adresse nicht `127.0.0.1`, sondern die des anderen Rechners.

## Schritt 8 — Nachweis

Du gibst ab:

- die Ausgabe deines Server-Terminals aus Schritt 7, auf der die fremde Adresse zu sehen ist,
- die Ausgabe des bösen Clients aus Schritt 6, mit deinem Format,
- `netz.py`, `server.py`, `client.py`, `test_angriff.py`,
- deine angepasste Protokolldatei.

## Hilfe — Wenn es nicht geht

| Was du siehst | Ursache |
|---|---|
| `ConnectionRefusedError` | Der Server läuft nicht, oder Port bzw. Adresse stimmen nicht. |
| `OSError: Address already in use` | Ein alter Server läuft noch. Schliess das andere Terminal oder beende ihn mit Strg-C. |
| Der Client hängt und zeigt keine Antwort | Du schickst ohne `\n` am Ende, etwa mit `sock.sendall` statt `sende`. Der Server wartet dann auf das Ende der Zeile, das nie kommt. Nimm immer `sende`. |
| Ein zweiter Client hängt, solange der erste verbunden ist | Kein Fehler. Dieser Server bedient Verbindungen nacheinander. Mehrere gleichzeitig kommen im nächsten Meilenstein. |
| `KeyError: 'type'` im Server | Du hast `nachricht["type"]` statt `nachricht.get("type")` geschrieben. |
| `StopIteration` im Client | Der Server hat die Verbindung geschlossen, bevor er geantwortet hat. Meist ist er abgestürzt. Schau ins Server-Terminal. |
| Immer `unbekannter Typ` | Typname im Client und im Server verschieden, oder `type` und `typ` gemischt. |
| Lokal geht es, über das Netz nicht | Firewall, falsche IP-Adresse, oder die beiden Rechner sind in verschiedenen Netzen. |

## Ausblick — Was noch fehlt

Dein Server kennt jetzt deine Nachrichten und entscheidet, wer du bist. Zwei Dinge kann er noch nicht.

Er bedient nur einen Client auf einmal. Für ein Spiel müssen beide Spieler gleichzeitig verbunden sein. Das ist Übung 6 im Übungsheft: ein Faden pro Verbindung.

Und wenn ein Spieler zieht, erfährt der andere nichts. Dafür muss der Server Nachrichten von sich aus an alle Verbundenen schicken, nicht nur als Antwort. Beides zusammen ist der nächste Meilenstein.
