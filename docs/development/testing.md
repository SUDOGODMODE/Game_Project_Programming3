# Tests und Weiterentwicklung

## Gemeinsamer Teststart

Im Projektordner mit aktivierter Umgebung. Die Bash-Beispiele verwenden
`python3`; unter Windows nach Aktivierung der `.venv` stattdessen `python`
verwenden (siehe [Setup](../guides/setup.md)):

```bash
python3 tools/run_tests.py
python3 tools/run_tests.py --milestone 00
python3 tools/run_tests.py --milestone 02
python3 tools/run_tests.py --milestone 03
python3 tools/run_tests.py --milestone 04
python3 tools/run_tests.py --milestone 06 --require-gui
python3 tools/run_tests.py --milestone 07
python3 tools/run_tests.py --milestone 08
python3 tools/run_tests.py --require-gui --report-json "<neuer_testbericht.json>"
```

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
| `tests/meilenstein_00/` | Echo-Server/-Client als eigene Prozesse, lange Nachrichten |
| `tests/meilenstein_02/` | Brett, Kernphasen, ganze Partie, geheime Kopien, lokale CLI |
| `tests/meilenstein_03/` | Transport über Socketpaare; echte TCP-/CLI-Prozesse, Lobby, Angriffe, Partie, Wettläufe, Abbruch und Ersatz |
| `tests/meilenstein_04/` | Serverzustände/Privatheit/Logs; echte Tk-Widgets mit Socketpaaren, Eingaben, Zeichnen, Threadgrenzen und Lebenszyklus |
| `tests/meilenstein_06/` | PNG-Pixel und PhotoImage-Lebensdauer; SVG-Flotte, Canvas-Drehung, eigene Sprengungseffekte und Tastaturbedienung |
| `tests/meilenstein_07/` | Sofort persistente Nachrichtenmetadaten, parallele Schreiber, Privatheit, Überschreibschutz, tatsächlicher Handler |
| `tests/meilenstein_08/` | Echte ZIP-Dateien, Laufzeitabhängigkeiten, Originalquellen, Ausschlüsse, unabhängige SHA256-Prüfung |

Feste Testflotten stehen in `tests/fixtures.py`. Sie sind keine Vorgabe für
GUI-Flotten. Tests bleiben bei ihrem ursprünglichen Schwerpunkt, auch wenn
sie spätere Erweiterungen mitprüfen. M1 hat Dokumentations-/Freigabeaufgaben;
deshalb gibt es dafür keinen leeren Testordner.

TCP-Tests brauchen freie lokale Ports. Tk-Tests prüfen zuerst in einem
Unterprozess, ob tkinter und ein Display funktionieren; andernfalls melden
sie einen begründeten Skip. **Ein Skip ist kein GUI-Nachweis.** Unter Windows
ist ein POSIX-Terminaltest nicht verfügbar. Die tatsächlich geprüfte
Umgebung steht in den Ergebnissen.

Die Grafikprüfungen in M6 sind nach Verhalten getrennt:

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

Diese Liste beschreibt den Prüfumfang. Frühere Ergebniszahlen belegen
ihren jeweiligen Stand; die grafische Überarbeitung benötigt einen neuen
Gesamtlauf mit `--require-gui` und einem neuen Berichts- oder Nachweisziel.

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
python3 tools/run_gui_demo.py --output docs/evidence/04_new_run
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
verwenden und alte Rohlogs erhalten. Der Klassenversuch steht in der
[Schulnetz-Checkliste](../evidence/04_school_network_checklist.md).

## Endprüfung und Paket

Die unabhängige Testrolle hält frische Prüfungen unter
`docs/evidence/final_assessment_tests/` fest. Sieben Angriffe und eine ganze
Partie mit zwei tatsächlichen Konsolenclientprozessen sind eigenständige
Nachweise; sie werden nicht aus dem GUI-Lauf abgeleitet. Massgebend für
aktuelle Zahlen und Grenzen ist das [Testurteil](../status/final_test_verdict.md).
Ausführende Rolle ist bei den automatischen Läufen Codex, keine erfundene
persönliche Bedienung durch den Projektverantwortlichen.

`python3 tools/build_submission.py --output "<neues_abgabearchiv.zip>"`
erzeugt eine neue technische Lieferform mit `.sha256`-Datei. Das innere
`SHA256SUMS.json` bildet ZIP-Pfade auf SHA256-Digests aller übrigen Dateien
ab. Projekt und `Dokumente` sind benachbarte Verzeichnisse, damit relative
Quellenlinks erhalten bleiben. `.git`, Umgebungen, Caches, Secrets und
Laufzeitlogs bleiben draussen; absichtlich gespeicherte Rohbelege unter
`docs/evidence` werden mitgeliefert. Vorhandene Ausgaben werden abgelehnt.
Der Entpacktest muss aus einem frischen Ziel starten und darf nicht
versehentlich die ursprüngliche Arbeitskopie importieren. Persönliche und
externe Aufgaben stehen weiter im Paketstatus; ein grüner lokaler Testlauf
erfüllt sie nicht.

## Änderungen durchführen

1. `AGENTS.md`, Übergabe, README und aktuellen Abgleich lesen; Git-Status
   prüfen und vorhandene Änderungen erhalten.
2. Erwartetes Verhalten festhalten. Bei funktionalen Änderungen zuerst einen
   aussagekräftigen fehlschlagenden Test ergänzen.
3. Kleinste passende Änderung umsetzen. Protokolländerungen gemeinsam in
   Server, Clients, JSON-Katalog und lesbarem Katalog nachführen.
4. Betroffene Tests, dann die gemeinsame Suite ausführen. Für GUI und
   Netzwerk den tatsächlichen Bedienweg und Datenfluss prüfen.
5. Befehl, Umgebung, Datum und Grenzen dokumentieren; README, Journal,
   Übergabe und Anforderungsabgleich aktualisieren.
6. Diff unabhängig prüfen lassen, Fehler korrigieren und gezielt erneut testen.

Keine Commits/Pushes ohne neuen Auftrag. Keine erfundene Lizenz oder
Personenangaben ergänzen. Eine KI-Codeprüfung ersetzt nicht das im Kurs
geforderte Gegenlesen durch eine andere Person.
