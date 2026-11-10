# Tests und Weiterentwicklung

## Gemeinsamer Teststart

Im Projektordner mit aktivierter Umgebung. Die Bash-Beispiele verwenden
`python3`; unter Windows nach Aktivierung der `.venv` stattdessen `python`
verwenden (siehe [Setup](../guides/setup.md)):

```bash
python3 tools/run_tests.py --core
python3 tools/run_tests.py
python3 tools/run_tests.py --group core
python3 tools/run_tests.py --group network
python3 tools/run_tests.py --group gui
python3 tools/run_tests.py --group integration
python3 tools/run_tests.py --group graphics --require-gui
python3 tools/run_tests.py --require-gui --report-json "<neuer_testbericht.json>"
```

**Lernweg:** Starte nach einer Änderung am Spielkern zuerst `--core`.
Dieses Profil lädt nur Brett- und Spielregeltests, einschließlich der
eigenständigen Kurstests aus `src/test_spiel.py`. Es bindet keinen TCP-Port,
öffnet kein Tk-Fenster und startet keinen fremden Prozess. Prüfe danach mit
`--group <name>` den betroffenen Bereich; `network` und `integration`
enthalten zusätzlich lokale Konsolenpartien beziehungsweise Netzwerkfälle,
`gui` und `graphics` echte GUI-Fälle. Vor einer
Übergabe führe die gesamte Suite mit `--require-gui` aus und spiele bei
GUI-/Netzänderungen zusätzlich die unten beschriebene lokale Demo durch.
`--core` und `--group` sind alternative Auswahlen.

Die Netzwerktestsuite liegt unter `src/test_netz.py`; der Ordner
`tests/graphics/` enthält die Grafikprüfungen als eigene Testgruppe.
Nachrichtenlog und Abgabepaket sind Zusatzfunktionen:
Ihre Tests liegen unter `tests/additional/` und werden im Gesamtlauf immer
mitgesammelt. Die Paketprüfung kann zusätzlich einzeln gestartet werden:

```bash
python3 -m unittest -v tests.additional.test_packaging
```

Der Teststarter bietet die Gruppen `core`, `network`, `gui`, `integration`
und `graphics` an.

Der Starter setzt Quell-/Projektpfade, sammelt alle `unittest`-Tests ein und
liefert bei einem Fehler Exitcode 1. Der absolute Skriptpfad funktioniert
auch aus einem anderen Arbeitsverzeichnis. Keine externe Testbibliothek.
Die alten neun Brettprüfungen sind ebenfalls in der Sammlung enthalten.

Den Platzhalter für den Bericht durch einen neuen Dateipfad ersetzen.
Vorhandene Berichte werden **vor Testbeginn** abgelehnt. `--require-gui`
verlangt mindestens einen mit `requires_gui = True` markierten Test und
bestandene Ausführung aller gefundenen GUI-Tests. Klassen-Skip, Test-Skip,
übersprungener Subtest und `expectedFailure` genügen für die GUI-Abnahme
nicht. Eine reine Konsolensuite kann deshalb mit diesem Schalter nicht als
GUI-Erfolg ausgegeben werden. Ohne Schalter gilt das portable unittest-
Verhalten, einschliesslich ehrlich gemeldeter Skips.

Der JSON-Bericht enthält Umgebung (Python, Plattform, Tk-Version ohne
zusätzliches Fenster), Auswahl, UTC-Startzeit, Gesamtdauer, tatsächliche
Test-IDs mit Ergebnis/Dauer/Grund sowie getrennte Fixture-/Subtestereignisse.
`tests_run` zählt die echten `startTest`-Aufrufe; ein `setUpClass`-Fehler
erfindet keine Testausführung. `failures`, `errors` und `skipped` sind die
unittest-Ereigniszahlen und können Klassen- oder Subtestereignisse enthalten;
sie sind deshalb nicht zwangsläufig eine disjunkte Aufteilung von
`tests_run`. `passed` zählt erfolgreich abgeschlossene Testmethoden.
`gui` nennt gefundene/ausgeführte/übersprungene GUI-Prüfungen und konkrete
Abnahmeprobleme. Der Gesamtstatus verbindet unittest-Erfolg mit diesen
strengen Bedingungen.

| Ordner | Schwerpunkt und Prüfart |
|---|---|
| `tests/core/` | Brett, Kernphasen, ganze Partie, geheime Kopien, reine GUI-Vorbereitung, lokale CLI |
| `tests/network/` | Transport über Socketpaare; echte TCP-/CLI-Prozesse, Lobby, Angriffe, Partie, Wettläufe, Abbruch und Ersatz |
| `tests/gui/` | Serverzustände/Privatheit/Logs; echte Tk-Widgets mit Socketpaaren, Eingaben, Zeichnen, Threadgrenzen und Lebenszyklus |
| `tests/integration/` | Eigenständige Kurstests aus `src/test_spiel.py`, Server-Endfolge, GUI-Ende und Startvarianten |
| `tests/graphics/` | Netz-/Porttests; PNG-Pixel und PhotoImage-Lebensdauer; SVG-Flotte, Canvas-Drehung, eigene Sprengungseffekte und Tastaturbedienung |
| `tests/additional/test_event_log.py` | Zusatzprüfung: sofort persistente Nachrichtenmetadaten, parallele Schreiber, Privatheit, Überschreibschutz, tatsächlicher Handler |
| `tests/additional/test_packaging.py` | Zusatzprüfung: echte ZIP-Dateien, Laufzeitabhängigkeiten, Originalquellen, Ausschlüsse, unabhängige SHA256-Prüfung |

Feste Testflotten stehen in `tests/fixtures.py`. Sie sind keine Vorgabe für
GUI-Flotten.

Die Flotte in `src/test_spiel.py` steht absichtlich noch einmal in dieser
Datei: Der Kursbefehl `python3 -m unittest -v test_spiel.py` aus `src/`
funktioniert damit unabhängig von den gemeinsamen Testdaten.

TCP-Tests brauchen freie lokale Ports. Tk-Tests prüfen zuerst in einem
Unterprozess, ob tkinter und ein Display funktionieren; andernfalls melden
sie einen begründeten Skip. **Ein Skip ist kein GUI-Nachweis.** Unter Windows
ist ein POSIX-Terminaltest nicht verfügbar. Die tatsächlich geprüfte
Umgebung steht in den Ergebnissen.

Die vorhandenen Grafikprüfungen unter `tests/graphics/` sind nach Verhalten getrennt:

- `test_image.py`: erhaltenes transparentes PNG, echte Anzeigepixel und
  Freigabe von `PhotoImage` im Tk-Hauptthread.
- `test_ship_art.py`: alle fünf SVG-Quellen aus fremdem Arbeitsverzeichnis
  sowie Skalierung, senkrechte Drehung, Tags und Zeichnen über Zellgrenzen
  auf einem echten Canvas. Der Renderer benötigt keine Zusatzpakete.
- `test_ship_effects.py`: Sprengung erst beim neuen vollständigen eigenen
  Treffer, begrenzte Dauer, kein Wiederholen bei initialen/wiederholten
  Zuständen, Abschaltung und Aufräumen bei Reset oder Schliessen.
- `test_graphics_integration.py`: bestätigte Zustände im echten Fenster,
  eigene statt gegnerische Effekte, Verbindungsende, Effektschalter und
  Zielrasterbedienung mit Pfeiltasten sowie Enter/Leertaste.

Diese Liste beschreibt den Prüfumfang.

## Handshake-Angriffe

Frischen separaten Server starten, dann:

```bash
python3 tools/check_handshake.py 127.0.0.1 --port 5100
```

Prüft fehlende Felder, Doppelbeitritt, unbekannte Typen und kaputtes JSON.
Ungefragte Zustände werden von direkten Antworten unterschieden. Die
TCP-Suite prüft diesen echten Skriptaufruf ebenfalls automatisch.

## Zwei Fenster und vollständige TCP-Partie

```bash
python3 tools/run_gui_demo.py --output "<ausgabeordner>"
```

Startet einen echten Serverprozess, zwei echte Tk-Fenster und zwei TCP-Clients.
Das Werkzeug bedient die normalen Platzierungs- und Schussknöpfe und prüft
Treffer/Wasser in beiden Ansichten, private Ablehnungen, 33 gültige Schüsse,
Sieg, Fensterkreuz, Reset und Ersatzbeitritt. Es speichert `server.txt`,
`client_messages.jsonl`, `server_messages.jsonl` und `result.json` im gewählten Ordner.
`--screenshot` ergänzt auf macOS eine echte Aufnahme beider Fenster,
wenn der Bildschirm dafür breit genug ist.

Die Flotten und Aktionen sind geskriptet. Der Lauf belegt weder zwei
Personen noch fremde Rechner. Ohne `--output` wird ein eigener zeitgestempelter Ordner angelegt. Bereits
vorhandene Ausgabeordner werden vor jedem Dateizugriff abgelehnt. FAIL wird
auch nach einer durchgespielten Partie gespeichert, falls die abschliessende
Serverlogprüfung fehlschlägt. Für neue Läufe einen neuen Ausgabeordner
verwenden und alte Rohlogs erhalten.

## Paket

`python3 tools/build_submission.py --output "<neues_abgabearchiv.zip>"`
erzeugt eine technische Lieferform mit `.sha256`-Datei. Das innere
`SHA256SUMS.json` bildet ZIP-Pfade auf SHA256-Digests aller übrigen Dateien
ab. Projekt und `Dokumente` sind benachbarte Verzeichnisse, damit relative
Quellenlinks erhalten bleiben. `.git`, Umgebungen, Caches, Secrets,
Laufzeitlogs sowie lokale Entwicklungswerkzeuge unter `.agents/` und
`.specify/` bleiben draussen. Vorhandene Ausgaben werden abgelehnt.
Der Entpacktest muss aus einem frischen Ziel starten und darf nicht
versehentlich die ursprüngliche Arbeitskopie importieren.

## Änderungen durchführen

1. `AGENTS.md` und README lesen; Git-Status prüfen und vorhandene
   Änderungen erhalten.
2. Erwartetes Verhalten festhalten. Bei funktionalen Änderungen zuerst einen
   aussagekräftigen fehlschlagenden Test ergänzen.
3. Kleinste passende Änderung umsetzen. Protokolländerungen gemeinsam in
   Server, Clients, JSON-Katalog und lesbarem Katalog nachführen.
4. Betroffene Tests, dann die gemeinsame Suite ausführen. Für GUI und
   Netzwerk den tatsächlichen Bedienweg und Datenfluss prüfen.
5. Befehl, Umgebung und Grenzen dokumentieren; README aktualisieren.
6. Diff prüfen lassen, Mängel korrigieren und gezielt erneut testen.

Keine Commits/Pushes ohne neuen Auftrag. Keine erfundene Lizenz oder
Personenangaben ergänzen.
