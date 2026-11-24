# Schiffe versenken

Netzwerkspiel in Python für das Modul Programming 3 an der HFTM, Max Rufener.

Zwei Spieler verbinden sich mit einem zentralen Server und spielen Schiffe
versenken auf einem 10×10-Raster. Der Server entscheidet über jeden Zug und
schickt danach jedem Fenster genau die Sicht, die ihm zusteht: die eigene
Flotte und alle Schüsse, nie die gegnerische Flotte. Weitere Clients schauen
als Zuschauer zu. Nach dem Spielende können beide eine Revanche verlangen;
der Server zählt die Siege.

Benötigt wird nur Python **3.12 oder neuer** mit tkinter, keine weiteren Pakete.

## Schnellstart

Im Projektordner drei Terminals öffnen und in dieser Reihenfolge starten.
Fehlt dem installierten Python tkinter (`ModuleNotFoundError: _tkinter`),
vorher in jedem Terminal die [virtuelle Umgebung](docs/guides/setup.md)
aktivieren: `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`).

```bash
python3 src/server.py
python3 src/client_gui.py 127.0.0.1 Alice
python3 src/client_gui.py 127.0.0.1 Bob
```

Ein vierter Client wird Zuschauer, auch während einer laufenden Partie:

```bash
python3 src/client_gui.py 127.0.0.1 Carla
```

Server und Clients verwenden unter macOS, Windows und Linux standardmässig
Port **5100** (nicht 5000, den unter macOS der AirPlay-Empfänger belegt).
Ist 5100 auf einem Rechner schon belegt, nimmt der Server selbst den
nächsten freien Port und zeigt den passenden Client-Befehl an, etwa:

```text
Server wartet auf Port 5101
Port 5100 ist belegt. Clients mit --port 5101 starten, etwa:
  python3 src/client_gui.py 127.0.0.1 Alice --port 5101
```

Wer selbst einen Port wählt (`--port 5200` beim Server und bei jedem
Client), bekommt genau diesen oder eine klare Fehlermeldung.

Für zwei Rechner statt `127.0.0.1` die IPv4-Adresse des
Serverrechners einsetzen; die Anleitungen [Auf einem Gerät](varianten/localhost/START.md)
und [Auf zwei Rechnern](varianten/zwei_rechner/START.md) erklären auch
Windows-Befehle und Firewall, die [Einrichtung](docs/guides/setup.md)
virtuelle Umgebung und tkinter.

## Bedienung

| Schritt | Im Fenster |
|---|---|
| Flotte setzen | Unter «Flotte planen» je Schiff Startfeld und Richtung (`h` nach rechts, `v` nach unten) eintragen oder «Neu mischen» drücken, dann «Flotte senden». Die Flotte: Carrier 5, Battleship 4, Cruiser 3, Submarine 3, Destroyer 2. |
| Schiessen | Wer am Zug ist, klickt ein Feld im «Zielraster». Wasser erscheint als Punkt, Treffer als X, ein versenkendes Feld mit Doppelring. Nach jedem gültigen Schuss ist der andere am Zug, auch nach einem Treffer. |
| Spielende | Wer zuerst alle gegnerischen Schiffe versenkt, gewinnt. Ein Unentschieden gibt es nicht. |
| Revanche | Der Knopf «Revanche» ist erst nach dem Spielende bedienbar. Erst wenn beide ihn gedrückt haben, startet der Server eine neue Partie; es beginnt, wer zuletzt nicht begonnen hat. Der Punktestand steht oben rechts, etwa «Alice 2 : 1 Bob». |
| Zuschauen | Ein Zuschauer sieht beide Schusslisten, aber keine Flotte. Seine Klicks lehnt der Server mit `SPECTATOR_ONLY` ab. |

Jeder Zug ist nur ein Wunsch an den Server. Lehnt er ab (zum Beispiel
ausser der Reihe oder auf ein schon beschossenes Feld), sieht nur der
Absender die Meldung, und das Brett bleibt unverändert.

## Aufbau

```text
 Fenster Alice            Server (server.py)                Fenster Bob
 client_gui.py            ─────────────────                 client_gui.py
 ┌──────────────┐  JSON   ┌───────────────────────────┐  JSON  ┌──────────────┐
 │ Empfangs-    │ ◄────── │ ein Thread je Verbindung  │ ─────► │ Empfangs-    │
 │ Thread→Queue │ ──────► │ with game["lock"]:        │ ◄───── │ Thread→Queue │
 │ Tk zeichnet  │  Zeile  │   prüfen → ändern → senden│  Zeile │ Tk zeichnet  │
 └──────────────┘         │            │              │        └──────────────┘
                          │            ▼              │
                          │  Spielkern spiel.py       │ ◄── Zuschauer:
                          │  Regeln und Zustand,      │     nur öffentliche Sicht
                          │  ohne Netz und Fenster    │
                          └───────────────────────────┘
```

- **Der Server entscheidet.** Alle Regeln stehen in `src/spiel.py`. Der
  Client prüft nichts, er schickt Wünsche und zeichnet nur, was der Server
  im Spielstand schickt. «Neu mischen» schlägt eine Flotte vor; ob sie gilt,
  entscheidet auch hier der Server.
- **Verborgene Information bleibt auf dem Server.** `state()` liefert einem
  Spieler nur seine Flotte, `public_state()` dem Zuschauer gar keine.
- **Threads.** Der Empfangsthread des Clients schreibt nur in eine Queue;
  das Tk-Fenster holt sie im Hauptthread ab und zeichnet an einer Stelle.
- **Sperre.** Im Server liegen Prüfen, Ändern und Versenden in derselben
  Sperre, damit zwei gleichzeitige Züge sich nicht überholen.
- **Robustheit.** Schliesst ein Spieler hart, erfährt es der andere
  (`opponentLeft`) und der Server nimmt einen neuen Spieler an. Kaputtes
  JSON und unbekannte Nachrichten werden abgelehnt, nicht abgestürzt.

Nachrichten, Pflichtfelder und Beispiele stehen in [PROTOKOLL.md](PROTOKOLL.md)
(Version 0.8, maschinenlesbar in [protocol.json](docs/protocol/protocol.json)),
die Spielregeln in [REGELN.md](REGELN.md).

## Tests

Alle Tests laufen mit der Standardbibliothek vom Projektordner aus:

```bash
python3 -m unittest discover
```

Sie prüfen den Spielkern ohne Netz (`tests/core/`) und den echten Server
über TCP-Verbindungen (`tests/network/`, `tests/integration/`), unter
anderem Ablehnungen, harte Verbindungsabbrüche, kaputtes JSON, Zuschauer
und Revanche. Ein Test spielt die Beispiele aus `PROTOKOLL.md` gegen den
Server ab, damit Protokoll und Code übereinstimmen. Die Fenstertests
brauchen eine grafische Sitzung; ohne sie werden sie übersprungen.

```bash
python3 tools/run_tests.py --core          # schneller Kernlauf ohne Netz und Fenster
python3 tools/run_tests.py --require-gui   # alles, Fenstertests dürfen nicht fehlen
```

Die beiden eigenständigen Testdateien aus Meilenstein 6 laufen auch direkt
in `src/`: `cd src && python3 -m unittest -v test_spiel test_netz`.

Nachweisläufe mit echten Fenstern und Bildschirmaufnahmen sowie das
Abgabepaket beschreibt die [Testanleitung](docs/development/testing.md).

## Dateiverzeichnis

```text
Game_Project_Programming3/
├── README.md                    diese Datei
├── REGELN.md                    verbindliche Spielregeln
├── PROTOKOLL.md                 Nachrichtenkatalog mit Beispielen (Version 0.8)
│
├── src/                         ── das Spiel ──
│   ├── spiel.py                 Spielkern: Regeln und Zustand, ohne Netz und Fenster
│   ├── server.py                Spielserver: Verbindungen, Sperre, Zuschauer, Revanche
│   ├── netz.py                  eine JSON-Nachricht pro Zeile über TCP
│   ├── client_gui.py            grafischer Client (Tk)
│   ├── gui/                     Bausteine des Fensters
│   │   ├── client_view.py         Brettzeichen und Punktestand aus dem Serverzustand
│   │   ├── sea_cell.py            ein Feld im Raster
│   │   ├── ship_art.py            Schiffsgrafiken aus SVG
│   │   └── ship_effects.py        Sprengungseffekt beim Versenken
│   ├── fleet_setup.py           Flottenvorschlag für «Neu mischen»
│   ├── event_log.py             Nachrichtenprotokoll des Servers (logs/*.jsonl)
│   ├── play.py                  Konsolenclient
│   ├── local_game.py            Partie ohne Netz an einer Tastatur
│   ├── client.py                einfacher Beitrittsclient (Meilenstein 3)
│   ├── board.py                 alter Importname für spiel.py
│   ├── testclient.py            fensterloser Client für test_netz.py
│   ├── test_spiel.py            Regeltests (Meilenstein 5/6)
│   └── test_netz.py             Netztests mit eigenem Serverprozess (Meilenstein 6)
│
├── tests/                       ── python3 -m unittest discover ──
│   ├── fixtures.py              feste Testflotten
│   ├── core/                    Spielkern, Flottenvorschlag, Brettanzeige
│   ├── network/                 Server über echte TCP-Verbindungen, Angriffe
│   ├── integration/             Revanche, ganze Partien, Startvarianten
│   ├── gui/                     Fenster, Zustandsverteilung, Protokollabgleich
│   ├── graphics/                Bilder, SVG-Flotte, Effekte, Port
│   └── additional/              Nachrichtenlog und Abgabepaket
│
├── bilder/                      Schiffsbild und SVG-Flotte, mit Herkunft
├── varianten/                   Startprofile: localhost/ und zwei_rechner/
├── tools/                       Teststarter, Fenster-Nachweislauf, Abgabepaket
└── docs/
    ├── protocol/protocol.json   Nachrichtenkatalog maschinenlesbar
    ├── guides/                  Einrichtung, Bedienung, Rückfall
    ├── development/             Architektur, Lesereihenfolge, Testanleitung
    ├── report/                  Abschlussbericht, Vorführung, Abnahme M7
    └── evidence/                Rohnachweise der Fensterläufe M7 und M8
```

Jeder Serverstart schreibt ein neues Nachrichtenprotokoll nach `logs/`
(Zeit, Richtung, Slot und Typ, keine Inhalte). `logs/`, `dist/` und lokale
Arbeitsdateien schliesst `.gitignore` aus.

## Was nicht geht

- Ein Server führt genau einen Tisch mit zwei Spielern; weitere Clients werden Zuschauer.
- Kein Wiederverbinden: Geht ein Spieler, wird die Partie verworfen, ohne Sieger und ohne Wartefrist. Ein physischer Verbindungsverlust fällt erst auf, wenn die Socket-Schicht ihn meldet.
- Der Punktestand gilt nur für die aktuelle Paarung im laufenden Server. Er beginnt nach einem Spielerabgang bei 0 und wird nicht gespeichert.
- Das Zuschauerfenster verwendet die Spielertexte des Clients (etwa «Verloren»); eine eigene Rollenanzeige fehlt.
- Der Konsolenclient `src/play.py` kann keine Revanche verlangen; das geht nur im grafischen Client.
- Die Verbindung ist unverschlüsseltes TCP ohne Anmeldung; gedacht für das lokale Netz.
- Geprüft ist das Spiel lokal über `127.0.0.1`; ein Lauf über zwei getrennte Rechner ist nicht nachgewiesen.
