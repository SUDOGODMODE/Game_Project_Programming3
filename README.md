# Schiffe versenken

Python-Netzwerkspiel im Modul Programming 3 an der HFTM, Max Rufener.
Zwei Spieler verbinden sich mit einem zentralen Server. Der Server
entscheidet über jede Aktion und verteilt nach jedem Zug die vollständige,
für den jeweiligen Spieler erlaubte Sicht an beide Clients — die eigene
Flotte bleibt dabei stets verborgen.

**Vor der Abgabe selbst ergänzen:** [persönliche Reflexion](docs/report/meine_reflexion.md).

## Variante wählen

Die beiden Startprofile verwenden denselben Spielkern, Server, GUI-Client,
Bilder und dasselbe Protokoll. Sie unterscheiden sich darin, wo die drei
Prozesse laufen und an welche Adresse sie sich binden beziehungsweise
verbinden. Python **3.12 oder neuer** mit tkinter ist erforderlich; weitere
Python-Pakete braucht das Spiel nicht.

| Variante | Geräte | Startanleitung |
|---|---|---|
| **localhost** | Server und zwei Spielfenster auf einem Gerät, auch ohne LAN | [Auf einem Gerät starten](varianten/localhost/START.md) |
| **zwei Rechner** | Server und erster Client auf Rechner 1, zweiter Client auf Rechner 2 | [Auf zwei Rechnern starten](varianten/zwei_rechner/START.md) |

Für einen schnellen Start auf **einem Gerät** im Projektordner drei
Terminals öffnen und die Befehle in dieser Reihenfolge ausführen:

```bash
python3 src/server.py
python3 src/client_gui.py 127.0.0.1 Alice
python3 src/client_gui.py 127.0.0.1 Bob
```

Der Server verwendet ohne Angabe Port 5000; die Clients verbinden sich
ebenfalls mit Port 5000. `PORT=5099 python3 src/server.py` wählt unter
macOS/Linux einen anderen Serverport. Dann brauchen **beide** Clients
zusätzlich `--port 5099`. Für zwei Rechner die tatsächliche IPv4-Adresse
des Serverrechners einsetzen; die verlinkte Anleitung erklärt die
Einrichtung und Windows-Befehle.

Im Repository liegen die beiden Einstiege unter `varianten/localhost/` und
`varianten/zwei_rechner/`; die [gemeinsame Einrichtung](docs/guides/setup.md)
erklärt Python, virtuelle Umgebung und tkinter.

## Projektstruktur

```text
src/                          Spielprogramme und Netzwerk; spiel.py ist der Regelkern,
                              board.py bietet den älteren Importnamen an
  gui/                        Interne Brett-, SVG- und Effektmodule; client_gui.py bleibt Einstieg
tests/
  fixtures.py                 Gemeinsame feste Testdaten
  core/                       Brett, Spielkern, lokale Partie
  network/                    Transport, Lobby, TCP/CLI
  gui/                        Zustandsverteilung, echte GUI-Tests, Teststarter
  integration/                Regelkern-Endfolge und Startvarianten
  graphics/                   Netz-/Porttests, Bildanzeige, SVG-Flotte, Effekte
  additional/                 Zusatzprüfungen für Nachrichtenlog und Abgabepaket
tools/                        Gemeinsamer Teststart und lokale Nachweise
varianten/
  localhost/                 Startprofil und Anleitung für ein Gerät
  zwei_rechner/              Startprofil und Anleitung für zwei Geräte
bilder/                       Schiffsbild, Herkunft und SVG-Flotte
docs/
  guides/                     Einrichtung und Bedienung
  development/                Architektur, Tests und Weiterentwicklung
  protocol/                   Strukturierter Nachrichtenkatalog
  report/                     Technischer Entwurf, persönliche Reflexion, Vorführung
REGELN.md                     Verbindliche Spielregeln
PROTOKOLL.md                  Lesbarer Nachrichtenkatalog, Protokoll 0.6
```

## Tests

Wenn du den Code kennenlernen willst, beginne mit dem kurzen Kernlauf. Er
prüft Brett, Platzierung, Schüsse und Zugfolge ohne Netzwerk, Tk-Fenster
oder fremde Prozesse. Danach prüfst du den geänderten Teil und zum Schluss
die vollständige Anwendung. Die [Lesereihenfolge durch den Code](docs/development/code_lesen.md)
führt von einer Spielaktion über Server und Client bis zu den Tests.

```bash
python3 tools/run_tests.py --core
python3 tools/run_tests.py --group network
python3 -m unittest discover
python3 tools/run_tests.py --group graphics --require-gui
python3 tools/run_tests.py
python3 tools/run_tests.py --require-gui
```

Die beiden eigenständigen Testdateien lassen sich auch direkt im Ordner
`src/` ausführen:

```bash
cd src
python3 -m unittest -v test_spiel test_netz
cd ..
```

`test_spiel.py` prüft die Spielregeln, `test_netz.py` den Server über
echte TCP-Verbindungen mit einem eigenen Serverprozess pro Fall.

`--core` ist die schnelle Rückmeldung beim Lernen und Ändern der Regeln.
Für Änderungen an Server oder Oberfläche reicht ein Kernlauf nicht; die
Gesamtsuite braucht lokale TCP-Ports und für `--require-gui` eine
grafische Sitzung. Ein übersprungener GUI-Test gilt nicht als bestandener
GUI-Nachweis. Die [Testanleitung](docs/development/testing.md) nennt
gezielte Befehle und eine vollständige lokale Partie mit zwei echten
Fenstern.

Reproduzierbare vollständige lokale TCP-Partie mit zwei echten Fenstern:

```bash
python3 tools/run_gui_demo.py --output "<neuer_ausgabeordner>"
```

Unter macOS ergänzt `--screenshot` eine Aufnahme beider Fenster, wenn sie
nebeneinander auf den Bildschirm passen. Ohne Ausgabeangabe entsteht ein
neuer zeitgestempelter Ordner; vorhandene Ordner werden nicht
überschrieben.

## Bild, Nachrichtenlogs und Abgabepaket

Das dekorative [Schiffsbild](bilder/README.md) ist 256×256 Pixel gross und
wird mit 64×64 Pixeln im Tk-Hauptthread angezeigt; Herkunft und Hashes
stehen in `bilder/`. Es ist keine Flotten- oder Zuganzeige.

Die Oberfläche in Meerblau zeigt die eigene bestätigte Flotte mit fünf
SVG-Schiffstypen aus `bilder/flotte/`. Ein kleiner Canvas-Renderer zeichnet
deren Grundformen ohne zusätzliche Pakete. Wasser erscheint als Punkt,
Treffer als X und der versenkende Treffer mit einem Doppelring. Auf dem
Zielraster bleibt die Gegnerflotte verborgen.

Wird ein eigenes Schiff neu vollständig getroffen, läuft dort einmalig ein
rund 1,15 Sekunden langer Sprengungseffekt. "Sprengungseffekte" schaltet
die Animationen aus und ein; Reset, Verbindungsende und Fensterschliessen
räumen laufende Effekte auf.

Jeder Serverstart erzeugt eine neue JSONL-Datei unter `logs/` im Projekt.
Optional:

```bash
python3 -u src/server.py --host 127.0.0.1 --port 5100 --log-file "<neuer_logpfad.jsonl>"
python3 tools/build_submission.py --output "<neues_abgabearchiv.zip>"
```

Logs enthalten für jede empfangene und erfolgreich gesendete Nachricht
UTC-ISO-Zeit, Richtung, Verbindung/Slot, bekannten Typ und bei
Serverfehlern einen bekannten Code. Keine Payloads, Namen oder freien
Clienttexte. Vorhandene Logs werden nicht überschrieben.

Ohne `--output` erzeugt das Abgabewerkzeug einen Zeitstempelnamen in
`dist/`. Das Paket enthält Programmcode, Bilder, Tests, Tools,
Dokumentation, vorhandene Nachweise und die benachbarten
Originalunterlagen `Dokumente/`. Es schliesst `.git`, virtuelle
Umgebungen, Caches, lokale Geheimnisse, Laufzeitlogs sowie lokales
Entwicklungswerkzeug aus. `SHA256SUMS.json` enthält die Hashes aller
übrigen ZIP-Dateien, `ABGABESTATUS.md` die offenen menschlichen Aufgaben.
Der [Vorführleitfaden](docs/report/vorfuehrung.md) beschreibt die Abnahme.

## Weitere Programme

`src/local_game.py` spielt ohne Netz an einer Tastatur. `src/play.py` ist
der Konsolen-Spielclient mit Standardflotte; `src/client.py` bleibt als
Lobby-/Nachrichtenclient erhalten.

[Architektur](docs/development/architecture.md),
[Entwicklungs- und Testablauf](docs/development/testing.md),
[Regeln](REGELN.md) und [Protokoll](PROTOKOLL.md) gehören zusammen.
Änderungen nur lokal durchführen; Commits, Pushes und GitHub-Schritte
übernimmt der Projektverantwortliche.

## Offen

Menschliches Gegenlesen von Regeln und Protokoll, eine reale Partie mit
zwei Personen an einer Tastatur, ein echter Lauf über zwei getrennte
Rechner mit Server-Terminalausgabe sowie die Livevorführung bleiben dem
Projektverantwortlichen vorbehalten.
