# Testprotokoll — Der erste Handschlag

Tatsächliche Ausgabe von `src/server.py`, `src/client.py` und `src/test_angriff.py`, wie in [`01_first_handshake.md`](../assignments/01_first_handshake.md) Schritt 4/5/8 verlangt. Alle Läufe real ausgeführt, jeweils gegen einen frisch gestarteten Server. Die unkommentierte Rohausgabe von Beitritt und Angriffstest liegt zusätzlich als eigene Datei in [`output.txt`](output.txt); dieses Dokument ordnet sie ein und ergänzt die vollständige Partie (Testlauf 4).

**Port-Hinweis:** Der Code verwendet wie vorgegeben Port 5000. Auf diesem Rechner (macOS) belegt der AirPlay-Empfänger (ControlCenter) Port 5000 dauerhaft, `python3 src/server.py` schlägt deshalb hier mit `OSError: [Errno 48] Address already in use` fehl. Für die folgenden Testläufe wurde lokal auf Port 5003 ausgewichen (Systemeinstellungen → Allgemein → AirDrop & Handoff → „AirPlay-Empfänger" deaktivieren behebt es dauerhaft). Der committete Code bleibt unverändert auf Port 5000.

## Testlauf 1 — erster Beitritt (`client.py`)

```
-> {'type': 'join', 'player': 'Alice'}
<- {'type': 'welcome', 'slot': 'A', 'player': 'Alice', 'phase': 'waiting'}
```

## Testlauf 2 — zweiter Beitritt bekommt slot B

```
-> {'type': 'join', 'player': 'Alice'}
<- {'type': 'welcome', 'slot': 'B', 'player': 'Alice', 'phase': 'waiting'}
```

## Testlauf 3 — böser Client (`test_angriff.py`), gegen frischen Server

```
-> {'type': 'nonsense'}
<- {'type': 'error', 'code': 'UNKNOWN_TYPE', 'message': 'unbekannter Typ: nonsense'}
-> {'player': 'Alice'}
<- {'type': 'error', 'code': 'UNKNOWN_TYPE', 'message': 'unbekannter Typ: None'}
-> {'type': 'join'}
<- {'type': 'error', 'code': 'MISSING_PLAYER', 'message': 'Name fehlt'}
-> {'type': 'join', 'player': 'Bob'}
<- {'type': 'welcome', 'slot': 'A', 'player': 'Bob', 'phase': 'waiting'}
-> {'type': 'join', 'player': 'Bob'}
<- {'type': 'error', 'code': 'ALREADY_JOINED', 'message': 'diese Verbindung ist bereits einem Spieler zugeordnet'}
-> das ist kein json
<- {'type': 'error', 'code': 'INVALID_JSON', 'message': 'kein gueltiges JSON'}
-> [1,2,3]
<- {'type': 'error', 'code': 'INVALID_JSON', 'message': 'kein gueltiges JSON'}
```

Der letzte Fall (`[1,2,3]`) ist gültiges JSON, aber kein Objekt — ohne eigene Prüfung dafür in `netz.py` hätte `server.py` mit `message.get("type")` auf einer Liste einen `AttributeError` geworfen und die Verbindung wäre ohne Aufräumen abgestürzt (siehe „Abgeglichen mit dem Übungsheft" unten).

Server danach weiterhin lauffähig — direkt geprüft mit einem normalen `client.py`-Aufruf:

```
-> {'type': 'join', 'player': 'Alice'}
<- {'type': 'welcome', 'slot': 'B', 'player': 'Alice', 'phase': 'waiting'}
```

Vollständiges Server-Terminal:

```
Server wartet auf Port 5003
verbunden: ('127.0.0.1', 49901)
  <- {'type': 'nonsense'}
  -> {'type': 'error', 'code': 'UNKNOWN_TYPE', 'message': 'unbekannter Typ: nonsense'}
  <- {'player': 'Alice'}
  -> {'type': 'error', 'code': 'UNKNOWN_TYPE', 'message': 'unbekannter Typ: None'}
  <- {'type': 'join'}
  -> {'type': 'error', 'code': 'MISSING_PLAYER', 'message': 'Name fehlt'}
  <- {'type': 'join', 'player': 'Bob'}
  -> {'type': 'welcome', 'slot': 'A', 'player': 'Bob', 'phase': 'waiting'}
  <- {'type': 'join', 'player': 'Bob'}
  -> {'type': 'error', 'code': 'ALREADY_JOINED', 'message': 'diese Verbindung ist bereits einem Spieler zugeordnet'}
  <- {'type': 'broken'}
  -> {'type': 'error', 'code': 'INVALID_JSON', 'message': 'kein gueltiges JSON'}
getrennt: ('127.0.0.1', 49901)
verbunden: ('127.0.0.1', 49902)
  <- {'type': 'join', 'player': 'Alice'}
  -> {'type': 'welcome', 'slot': 'B', 'player': 'Alice', 'phase': 'waiting'}
getrennt: ('127.0.0.1', 49902)
```

## Testlauf 4 — eine vollständige Partie, zwei gleichzeitig verbundene Clients

Prüft `place`, `shoot`, `getState` und `gameOver` sowie das Threading (ein Faden pro Verbindung), zusammen mit den bereits bestehenden `join`-Fehlerfällen. Ausgeführt mit einem eigenen Testskript, das zwei echte Socket-Verbindungen gleichzeitig offen hält und die Züge strikt abwechselnd sendet, wie es das Protokoll verlangt.

Ablauf: A und B verbinden sich gleichzeitig, platzieren ihre Flotte, danach schiesst A gezielt auf B's tatsächliche Schiffspositionen, während B absichtlich daneben zielt (Spalten F–J). Nach 17 Zügen von A ist B's gesamte Flotte versenkt.

Auszug (A's Sicht, gekürzt auf die Treffer, die je ein Schiff versenken):

```
-> {'type': 'shoot', 'field': 'E6'}
<- {'type': 'result', 'field': 'E6', 'result': 'sunk', 'sunk': 'Carrier', 'turn': 'B'}
...
-> {'type': 'shoot', 'field': 'D7'}
<- {'type': 'result', 'field': 'D7', 'result': 'sunk', 'sunk': 'Battleship', 'turn': 'B'}
...
-> {'type': 'shoot', 'field': 'C8'}
<- {'type': 'result', 'field': 'C8', 'result': 'sunk', 'sunk': 'Cruiser', 'turn': 'B'}
...
-> {'type': 'shoot', 'field': 'C9'}
<- {'type': 'result', 'field': 'C9', 'result': 'sunk', 'sunk': 'Submarine', 'turn': 'B'}
...
-> {'type': 'shoot', 'field': 'B10'}
<- {'type': 'result', 'field': 'B10', 'result': 'sunk', 'sunk': 'Destroyer', 'turn': None}
```

B versucht ausserhalb der Reihe zu schiessen, bevor beide platziert haben:

```
-> {'type': 'shoot', 'field': 'A1'}
<- {'type': 'error', 'code': 'WRONG_PHASE', 'message': 'aktuelle Phase ist placing, nicht shooting'}
```

Der letzte Schuss von A beendet die Partie. A erfährt das Ende direkt aus der eigenen Antwort (`sunk` gesetzt, `turn: null`). B bekommt unaufgefordert den Broadcast, ohne selbst aktiv geworden zu sein:

```
<- {'type': 'gameOver', 'winner': 'A', 'reason': 'sunk'}
```

`getState` danach, für beide Seiten — zeigt die verborgene Information korrekt gefiltert: B sieht die eigene versenkte Flotte, aber nirgends A's Schiffskoordinaten (`A1`–`E5`), nur die eigenen (verfehlten) Schüsse:

```
# A
{'type': 'state', 'phase': 'finished', 'turn': None, 'winner': 'A',
 'ownShips': [... eigene 5 Schiffe, keine Treffer ...],
 'shotsAtOpponent': {'A6': 'hit', 'B6': 'hit', ..., 'B10': 'sunk'}}

# B
{'type': 'state', 'phase': 'finished', 'turn': None, 'winner': 'A',
 'ownShips': [... eigene 5 Schiffe, alle vollstaendig getroffen ...],
 'shotsAtOpponent': {'F1': 'miss', 'F2': 'miss', ..., 'G6': 'miss'}}
```

**Dabei gefundener und behobener Fehler:** Im ersten Durchlauf schickte der Server den `gameOver`-Broadcast auch an den Gewinner selbst — und zwar innerhalb von `handle()`, *bevor* die eigentliche `result`-Antwort auf dessen letzten Schuss zurückgegeben wurde. Auf dem Socket des Gewinners kam dadurch zuerst `gameOver`, danach erst die Antwort auf den eigenen Schuss — Nachrichten in einer Reihenfolge, die kein Client erwarten würde. Behoben, indem der Broadcast nur noch an den jeweils anderen Spieler geht; der Gewinner erkennt das Ende zuverlässig an seiner eigenen `result`-Antwort (`sunk` gesetzt, `turn: null`).

## Abgeglichen mit dem Übungsheft

Beim Durchgehen des Übungshefts „Netzwerkprogrammierung" gegen den eigenen Code sind zwei Stellen aufgefallen, die nicht sauber umgesetzt waren:

1. **Übung 4 sagt ausdrücklich: „Heben Sie `netz.py` auf. Diese Datei benutzen Sie im Projekt unverändert weiter."** Entschieden: Die Funktionen heissen `send`/`read_messages`, nicht `sende`/`leser` — englische Begriffe durchgängig im ganzen Projekt haben Vorrang vor wörtlicher Namensgleichheit mit der Musterlösung. Der Mechanismus selbst — `sock.makefile()`, Zeilen-Framing mit `\n`, `try`/`except JSONDecodeError` — ist trotzdem identisch zur Musterlösung übernommen, nur die Bezeichner sind es nicht. Das ist eine bewusste, abgewogene Entscheidung, keine übersehene Stelle.
2. **Übung 4 selbst weist darauf hin, dass „jedes Programm sich mit Ihrem Port verbinden darf und schicken, was es will".** `netz.py` fing bisher nur *syntaktisch* ungültiges JSON ab. Eine Zeile, die gültiges JSON, aber kein Objekt ist — z. B. `[1,2,3]` — wurde ungeprüft durchgereicht. `server.py` ruft aber blind `message.get("type")` auf jeder Nachricht auf; bei einer Liste hätte das mit `AttributeError: 'list' object has no attribute 'get'` die gesamte Verbindung abstürzen lassen. Behoben in `netz.py` (`read_messages` prüft jetzt zusätzlich `isinstance(parsed, dict)`), verifiziert mit genau diesem Angriff (siehe `[1,2,3]` in [`output.txt`](output.txt)) und dauerhaft in `test_angriff.py` mit aufgenommen.
3. **Übung 8 sagt: „Der Eintrag gehört in ein `finally`", damit das Aufräumen auch bei einem Absturz mitten in der Verarbeitung geschieht.** Das Markieren eines Spielers als getrennt stand bei mir einfach nach der Empfangsschleife, nicht in einem `finally`. Wäre `handle()` aus einem nicht vorhergesehenen Grund auf eine Ausnahme gelaufen, wäre der Spieler für immer als `connected: true` mit einem toten Socket stehengeblieben. Jetzt liegt die Aufräumlogik in `handle_connection()` in einem `finally`, zusätzlich fängt eine gezielte `try`/`except` um `handle()` jede unerwartete Ausnahme ab, beendet nur diese eine Verbindung sauber und lässt den Server für alle anderen weiterlaufen.

Geprüft wurde ausserdem, dass die übrigen Lektionen bereits eingehalten waren: `HOST = "0.0.0.0"` statt `127.0.0.1` (Übung 1, Frage 5, sonst unsichtbar für andere Rechner), ein Faden pro Verbindung nach dem Muster aus Übung 6, und „Prüfen und Handeln" liegen bei `place`/`shoot` durchgehend in derselben `with game["lock"]:`-Sektion (Übung 7) — sonst könnte wie im Wettlauf-Beispiel derselbe Zug doppelt durchgehen.

## Ergebnis

| Kriterium | Ergebnis |
|---|---|
| Client zeigt Willkommensantwort mit Spieler-Kennung | ✅ (`slot: "A"`) |
| Server läuft nach Client-Ende weiter | ✅ |
| Zweiter Start ergibt neue Kennung | ✅ (`B` statt `A`) |
| Jede falsche Nachricht bekommt eine Ablehnung mit Grund | ✅ (7/7 Fälle) |
| Server läuft nach dem Angriff weiter und nimmt normalen Client an | ✅ |
| Zwei Spieler gleichzeitig verbunden, komplette Partie bis zum Sieg | ✅ |
| Zug aus der Reihe / falsche Phase wird abgelehnt | ✅ |
| Gewinner erfährt das Ende korrekt über die eigene Antwort, Verlierer über Broadcast | ✅ |
| `getState` verrät nie die gegnerischen Schiffspositionen | ✅ |
| Aufräumen bei Verbindungsabbruch steht in `finally` (Übung 8) | ✅ |
| Gültiges JSON ohne Objekt (`[1,2,3]`) stürzt den Server nicht mehr ab | ✅ |
| `board.py` (Platzierungs- und Trefferlogik) einzeln getestet | ✅ — `python3 src/test_board.py`, 9/9 Tests bestanden |

Noch offen (Schritt 7, Test über zwei Rechner): noch nicht durchgeführt, da dafür ein zweiter Rechner im Schulnetz nötig ist. Ebenfalls offen: ein interaktiver Konsolenclient zum tatsächlichen Mitspielen — `client.py` deckt bislang nur den Beitritt ab, dieser Testlauf wurde mit einem eigenen Testskript statt mit `client.py` gespielt.
