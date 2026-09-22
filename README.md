# Schiffe versenken

Ein verteiltes Schiffe-versenken für zwei Spieler — Projektarbeit im Modul *Programming 3* an der HFTM, Aufgabe «Verteiltes Spiel» (Einzelarbeit, Max Rufener).

Der Server hält den gesamten Spielstand und ist die einzige Wahrheit im Spiel. Die Clients zeigen nur an und schicken Wünsche — sie entscheiden nichts selbst und wissen nie mehr, als sie dürfen.

## Inhalt

- [Stand des Projekts](#stand-des-projekts)
- [Wie das Spiel abläuft](#wie-das-spiel-abläuft)
- [Protokoll und Code](#protokoll-und-code)
- [Projektstruktur](#projektstruktur)
- [Ausführen](#ausführen)
- [Getestet](#getestet)
- [Was noch fehlt](#was-noch-fehlt)

## Stand des Projekts

| Meilenstein | Ziel | Stand |
|---|---|---|
| M1 · Spielwahl | ein freigegebenes Spiel | erledigt — Formular in `Projekt/Dokumente/Auftrag1_Spielwahl_ausgefuellt.pdf` |
| M2 · Spielkern ohne Netz | getestete Klasse, am Tisch spielbar | `board.py` steht und ist einzeln getestet (`test_board.py`) |
| M3 · Das Protokoll | ein Nachrichtenkatalog, den Fremde lesen können | vollständig, alle sieben Nachrichten implementiert |
| M4 · Der Server | zwei Konsolenclients, die eine Partie spielen | Server spielt eine komplette Partie korrekt durch; `client.py` selbst kann bisher nur beitreten, nicht mitspielen |
| M5 · Client und Robustheit | Server, der den bösen Client übersteht | Server läuft mit Threading, übersteht kaputte Nachrichten (`test_angriff.py`); Reconnect nach Verbindungsabbruch fehlt |
| M6 · Die Oberfläche | grafischer Client | offen |
| M7 · Härtung und Fremdtest | Partie über das Schulnetz | offen |
| M8 · Abgabe und Demo | Vorführung, Bericht, Reflexion | offen |

Erstwunsch im Formular war eigentlich Vier gewinnt, Zweitwunsch Schiffe versenken — die gesamte bisherige Arbeit (Protokoll, Referenzcode, eigene Notizen) ist auf Schiffe versenken ausgelegt.

## Wie das Spiel abläuft

Ein Spieler verbindet sich, meldet sich mit einem Namen an und bekommt vom Server eine Kennung zugewiesen — `A` oder `B`, je nachdem wer zuerst da war. Der Client entscheidet das nicht selbst, er kann sich weder aussuchen, wer er ist, noch sich als der andere Spieler ausgeben, weil keine einzige Nachricht überhaupt ein Feld dafür hat: der Server weiss immer aus der Verbindung, wer gerade spricht.

Sobald beide verbunden sind, platziert jeder seine Flotte — fünf Schiffe unterschiedlicher Grösse, geprüft auf Überlappung und Rasterüberstand. Danach wird abwechselnd geschossen, bis die gesamte gegnerische Flotte versenkt ist. Jeder Client sieht dabei ausschliesslich sein eigenes Raster und die Ergebnisse seiner eigenen Schüsse — nie, wo die Schiffe des Gegners tatsächlich stehen.

```json
{"type": "join", "player": "Alice"}
→ {"type": "welcome", "slot": "A", "player": "Alice", "phase": "waiting"}

{"type": "shoot", "field": "C5"}
→ {"type": "result", "field": "C5", "result": "sunk", "sunk": "Destroyer", "turn": "B"}
```

Kommt eine Nachricht zur falschen Zeit, mit falschem Feld oder gar nicht als gültiges JSON an, antwortet der Server mit `error` und einem Code statt zu verstummen oder abzustürzen — siehe [`docs/evidence/01_client_server_output.md`](docs/evidence/01_client_server_output.md).

## Protokoll und Code

Das Protokoll in [`docs/protocol/protocol.json`](docs/protocol/protocol.json) ist keine Beschreibung neben dem Code, sondern dessen Quelle. Eine neue Nachricht entsteht zuerst dort als Eintrag, erst danach als weiterer Fall in `handle()` in `server.py`.

- **`netz.py`** — die reine Transportschicht. Verpackt ein Dictionary als JSON-Zeile und liest sie auf der Gegenseite wieder ein. Kennt keinen einzigen Nachrichtennamen des Spiels.
- **`board.py`** — die Spielregeln, komplett ohne Netzwerk: Schiffe platzieren, Überlappung und Rasterüberstand prüfen, Treffer eintragen, erkennen, wann ein Schiff versenkt ist. Lässt sich einzeln testen und importieren, ohne einen Server zu starten.
- **`server.py`** — nimmt Verbindungen an (ein Faden pro Verbindung) und entscheidet über `message["type"]`, was zu tun ist: `join`, `place`, `shoot`, `getState`, `leave`. Ruft für alles, was mit Schiffen zu tun hat, nur `board.py` auf, statt die Logik zu duplizieren.
- **`client.py`** — verbindet sich, schickt eine `join`-Nachricht, zeigt die Antwort. Deckt bewusst nur den Beitritt ab, siehe „Was noch fehlt".
- **`test_angriff.py`** — der böse Zwilling von `client.py`. Schickt absichtlich kaputte, unvollständige und doppelte Nachrichten.

## Projektstruktur

```
Game_Project_Programming3/
├── README.md
├── .gitignore
├── src/                            ausführbarer Code, flach (kein Package)
│   ├── netz.py                         Transportschicht: JSON-Zeilen senden/lesen
│   ├── board.py                        Spielregeln ohne Netzwerk
│   ├── test_board.py                   Tests für board.py
│   ├── server.py                       nimmt Verbindungen an, spielt die Partie
│   ├── client.py                       verbindet sich und tritt bei
│   └── test_angriff.py                 schickt absichtlich ungültige Nachrichten
└── docs/
    ├── assignments/                Aufgabenstellungen, unverändert wie gestellt
    │   └── 01_first_handshake.md
    ├── evidence/                   reale Testausgaben als Beleg
    │   └── 01_client_server_output.md
    └── protocol/
        └── protocol.json               der eigene, verbindliche Nachrichtenkatalog
```

`src/` bleibt bewusst flach statt als Package: Schritt 7 des ersten Meilensteins verlangt, dass jemand anderes `client.py` direkt gegen meinen Server startet, ohne vorher irgendetwas zu installieren. `python3 src/client.py <ip>` reicht — Python findet die anderen Module automatisch im selben Ordner.

Kursunterlagen ausserhalb des eigentlichen Codes (Auftragsformulare, Spielkatalog) liegen unter `Projekt/Dokumente/`, nicht in diesem Repository. Kursübungen ohne Bezug zu diesem Spiel liegen unter `Programming3/uebungen_referenzen/`.

## Ausführen

Braucht nur Python 3, sonst nichts — keine externen Abhängigkeiten.

```bash
# Terminal 1
python3 src/server.py

# Terminal 2 — ohne Angabe verbindet sich der Client zu localhost
python3 src/client.py [server-ip]

# optional: den Server mit absichtlich kaputten Nachrichten löchern
python3 src/test_angriff.py [server-ip]

# die Spielregeln fuer sich alleine testen, ohne Server
python3 src/test_board.py
```

## Getestet

Alles hier wurde real ausgeführt, nicht nur geschrieben:

- `board.py`: 9 eigenständige Tests (`test_board.py`) für Feld-Parsing, Schiffsplatzierung, Überlappung, Treffer und Versenken.
- Beitritt: erster und zweiter Client bekommen korrekt die Kennungen `A` und `B`.
- `test_angriff.py`: alle sechs Angriffsversuche laufen in einen passenden Fehlercode statt in einen Absturz, der Server läuft danach normal weiter.
- Eine komplette Partie mit zwei gleichzeitig verbundenen Clients: platzieren, abwechselnd schiessen, bis eine Flotte versenkt ist, `gameOver` kommt korrekt beim Verlierer an, `getState` verrät nie die gegnerischen Schiffspositionen.

Dabei ist ein echter Fehler aufgefallen und wurde behoben: Der Server schickte dem Gewinner den `gameOver`-Broadcast ursprünglich *vor* der eigentlichen Antwort auf dessen eigenen letzten Schuss — zwei Nachrichten kamen dadurch in unerwarteter Reihenfolge auf demselben Socket an. Details und die vollständige Ein-/Ausgabe stehen in [`docs/evidence/01_client_server_output.md`](docs/evidence/01_client_server_output.md).

Ein Stolperstein beim Testen auf diesem Rechner: macOS belegt Port 5000 serienmässig mit dem AirPlay-Empfänger, was den Server mit `OSError: Address already in use` scheitern lässt. Abhilfe entweder über Systemeinstellungen → AirDrop & Handoff → AirPlay-Empfänger deaktivieren, oder testweise einen anderen Port verwenden. Der committete Code bleibt auf dem vorgegebenen Port 5000.

## Was noch fehlt

**Ein spielbarer Client.** `client.py` deckt bisher nur den Beitritt ab (Ergebnis des ersten Meilensteins). Der Server kann bereits eine komplette Partie korrekt durchspielen — getestet wurde das mit einem eigenen Testskript, das zwei Sockets gleichzeitig steuert, nicht mit `client.py` selbst. Es fehlt also noch ein Client, mit dem ein Mensch tatsächlich am Terminal Schiffe platzieren und schiessen kann.

**Reconnect.** Bricht die Verbindung mitten in der Partie ab, merkt der Server das (`connected: false`), wartet aber nicht auf eine Wiederverbindung und wertet die Partie auch nicht automatisch als Aufgabe — beides ist im Protokoll als Vorschlag notiert, aber nicht umgesetzt.

**Die Flotte** (`fleet` in `protocol.json`, die klassischen fünf Schiffstypen) ist plausibel, aber nicht gegen einen echten Spielekatalog bestätigt — die bereitgestellte Datei enthält bislang nur das leere Auftrag-1-Formular, keine Vorgaben zu Schiffstypen.

**M6–M8** (Oberfläche, Fremdtest über das Schulnetz, Abgabe) sind noch nicht begonnen.
