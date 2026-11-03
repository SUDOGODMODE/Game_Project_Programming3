# Schiffe versenken

Python-Projekt im Modul Programming 3 an der HFTM, Max Rufener. Zwei Spieler verbinden sich mit einem zentralen Server. Der Server entscheidet über jede Aktion und verteilt die vollständige erlaubte Sicht an beide Clients.

Kursmeilenstein 4 **„Das Brett auf dem Bildschirm“** ergänzt die tkinter-Oberfläche, automatische Zustandsmeldungen und lokale Nachweise. Der Versuch mit zwei fremden Clientrechnern ist für später vorbereitet und bleibt offen. Der [Anforderungsabgleich](docs/status/04_requirements.md) trennt Umsetzung, Prüfung und noch fehlende praktische Nachweise.

Kursmeilenstein 5 **„Die Regeln“** überträgt die Lehrschritte auf das
bereits gewählte Schiffe versenken; das Tic-Tac-Toe-Beispiel der
Aufgabenstellung ist kein zweites Spiel dieses Projekts. Der
[M5-Anforderungsabgleich](docs/status/05_requirements.md) nennt die
tatsächlich ausgeführten lokalen Prüfungen und den weiterhin offenen
Zweirechnerbeleg. Dieser echte Versuch bleibt auf Wunsch des
Projektverantwortlichen verschoben.

Die [Vergleichsliste zu Meilenstein 5 und beiden Varianten](docs/status/05_coverage_comparison.md)
stellt jede Forderung, ihren Beleg und die offenen Verbesserungen gegenüber.

Der anschliessend freigegebene Umfang bis M8 ergänzt das eigene Bild,
dauerhafte Nachrichtenlogs, strenge Testabnahme und ein Abgabewerkzeug.
**Vor der Abgabe selbst ergänzen:** [meine persönliche Reflexion](docs/report/meine_reflexion.md).
Der Benutzer erledigt sie ausdrücklich selbst; die Datei enthält nur offene
Leitfragen. Der [technische Berichtsentwurf](docs/report/abschlussbericht.md)
ist mit KI erstelltes Material und muss vom Projektverantwortlichen selbst
geprüft, überarbeitet und erklärt werden. Menschliches Gegenlesen,
Fremdclienttest, reale Fremdrechner und Livevorführung bleiben offen.
Der [Bewertungsabgleich](docs/status/04_rubric_requirements.md) und das
[unabhängige Testurteil](docs/status/final_test_verdict.md) trennen diese
Aufgaben von tatsächlichen lokalen Ergebnissen.

## Variante wählen

Die beiden Startprofile verwenden **denselben Spielkern, Server, GUI-Client,
Bilder und dasselbe Protokoll**. Sie unterscheiden sich darin, wo die drei
Prozesse laufen und an welche Adresse sie sich binden beziehungsweise
verbinden. Python **3.12 oder neuer** mit tkinter ist erforderlich; weitere
Python-Pakete braucht das Spiel nicht.

| Variante | Geräte | Startanleitung |
|---|---|---|
| **localhost** | Server und zwei Spielfenster auf einem Gerät, auch ohne LAN | [Auf einem Gerät starten](varianten/localhost/START.md) |
| **zwei Rechner** | Server und erster Client auf Rechner 1, zweiter Client auf Rechner 2 | [Auf zwei Rechnern starten](varianten/zwei_rechner/START.md) |

Im Repository liegen die beiden Einstiege unter `varianten/localhost/` und
`varianten/zwei_rechner/`. Die beiden endgültigen Profil-ZIPs unter
`dist/Schiffe_versenken_localhost_2026-11-03_freigabe.zip` und
`dist/Schiffe_versenken_zwei_rechner_2026-11-03_freigabe.zip` enthalten
jeweils ein eigenes `start.py` und
`START_HIER.md` im inneren Projektordner; die
[gemeinsame Einrichtung](docs/guides/setup.md) erklärt Python, virtuelle
Umgebung und tkinter; die beiden Startanleitungen enthalten die
vollständigen Befehle für macOS/Linux und Windows.

Die separaten Prüfberichte liegen unter
`dist/Schiffe_versenken_localhost_2026-11-03_freigabe.verification/` und
`dist/Schiffe_versenken_zwei_rechner_2026-11-03_freigabe.verification/`
neben den ZIPs. Sie prüfen SHA256, Manifest, Start-Hilfe, Kerntest und die
strenge Gesamtsuite aus jedem entpackten Paket. Das Localhost-Paket wurde
zusätzlich mit einer vollständigen lokalen Tk/TCP-Partie geprüft; das
Zwei-Rechner-Paket mit einem lokalen TCP-Beitritt. `dist/` selbst gehört
nicht zum Inhalt der Pakete.

Ein [vollständiger lokaler Profil-Serverlauf](docs/evidence/two_versions_2026-11-03/localhost_full_profile_game/result.json)
bestand zusätzlich mit zwei echten Tk-Fenstern und 33 Schüssen. Dabei
startete der Server über `varianten/localhost/start.py`; die Clientwrapper
waren zuvor separat bis `gameStart` geprüft. Der neue strenge
[Gesamtlauf](docs/evidence/two_versions_2026-11-03/full_final.json) bestand
155/155 Tests, darunter 29 echte GUI-Prüfungen. Ältere ZIP-Kandidaten und
deren Prüfberichte bleiben als historische Zwischenstände erhalten.

Im localhost-Profil bindet der Server nur an `127.0.0.1`. Für zwei Rechner
bindet er auf Rechner 1 an `0.0.0.0`, während der zweite Client eine
**ausdrücklich eingegebene tatsächliche IPv4-Adresse von Rechner 1**
benötigt. Diese Adresse ist noch unbekannt. Der echte Zweirechnerlauf mit
Server-Terminalausgabe aus Kursmeilenstein 5 ist weiterhin offen und wird
nicht durch eine lokale Paket- oder Startprüfung ersetzt. Der
[M5-Anforderungsabgleich](docs/status/05_requirements.md) und der
[Abgleich der zwei Varianten](docs/status/two_versions.md) führen die
Nachweise getrennt.

## Projektstruktur

```text
src/                          Spielprogramme und Netzwerk; spiel.py ist der Regelkern,
                              board.py bietet den älteren Importnamen an
tests/
  fixtures.py                 Gemeinsame feste Testdaten
  meilenstein_00/             Echo / Werkzeugbasis
  meilenstein_02/             Brett, Spielkern, lokale Partie
  meilenstein_03/             Transport, Lobby, TCP/CLI, Angriffstest
  meilenstein_04/             Zustandsverteilung und echte GUI-Tests
  meilenstein_05/             Regelkern und Endfolge
  meilenstein_06/             PNG, SVG-Flotte, Grafikeffekte und Tk-Lebensdauer
  meilenstein_07/             Persistentes privates Nachrichtenlog
  meilenstein_08/             Abgabepaket und Manifest
tools/                        Gemeinsamer Teststart und lokale Nachweise
varianten/
  localhost/                 Startprofil und Anleitung für ein Gerät
  zwei_rechner/              Startprofil und Anleitung für zwei Geräte
bilder/                       ImageGen-PNG, Herkunft und SVG-Flotte
docs/
  assignments/                Unveränderte Aufgaben-Texte aus den Unterlagen
  guides/                     Einrichtung und Bedienung
  development/                Architektur, Tests und Weiterentwicklung
  protocol/                   Strukturierter Nachrichtenkatalog
  status/                     Anforderungsabgleiche je Meilenstein
  evidence/                   Erwartungen, Rohlogs, Bilder, Checklisten
  report/                     Technischer Entwurf, persönliche Reflexion, Vorführung
  superpowers/                Technische Spezifikation und Arbeitsplan
REGELN.md                     Verbindliche Spielregeln
PROTOKOLL.md                  Lesbarer Nachrichtenkatalog, Version 0.6
journal.md                    Tatsächliche Arbeitsschritte und Prüfungen
WEITERARBEITEN.md             Übergabe für die nächste Arbeitseinheit
```

M1 hat Dokumentations- und Freigabeaufgaben, keine eigene technische Testsuite. Bestehende Tests bleiben beim ursprünglichen Schwerpunkt; sie prüfen als Regression auch spätere Erweiterungen. Historische Rohlogs behalten ihre damaligen Dateipfade. Die originalen Word-Unterlagen liegen unverändert im benachbarten Ordner `../Dokumente/`.

## Tests

```bash
python3 tools/run_tests.py
python3 tools/run_tests.py --milestone 04
python3 tools/run_tests.py --milestone 05
python3 tools/run_tests.py --require-gui --report-json "<neuer_testbericht.json>"
```

Der Originalbefehl aus Kursmeilenstein 5 lautet im Ordner `src` mit
aktivierter Projektumgebung: `python3 -m unittest -v test_spiel.py`. Die
[grüne Rohausgabe mit 19 Tests](docs/evidence/05_final_2026-11-03/test_spiel_green.txt)
und die [roten Mutationsausgaben](docs/evidence/05_mutation_2026-11-03/result.json)
sind getrennt belegt; die absichtlichen Fehler liefen in isolierten Kopien
und wurden nicht in den Projektkern übernommen. Die [abschliessende vollständige Suite](docs/evidence/05_final_2026-11-03/full_release.json)
bestand mit 139/139 Tests, davon 29 echte GUI-Prüfungen, ohne Fehler oder Skips.

TCP-Tests benötigen lokale Portbindungen, GUI-Tests eine grafische Sitzung. Ein GUI-Skip ersetzt keine Funktionsprüfung. Befehle, Testzuordnung und Nachweisgrenzen stehen in der [Testanleitung](docs/development/testing.md).

`<neuer_testbericht.json>` zuerst durch einen neuen Dateipfad ersetzen.
`--require-gui` scheitert bei fehlenden oder übersprungenen GUI-Prüfungen,
auch bei übersprungenen Subtests und erwarteten Fehlern. Der normale Modus
bleibt portabel. Bestehende JSON-Berichte werden vor Testbeginn abgelehnt.

Reproduzierbare vollständige lokale TCP-Partie mit zwei echten Fenstern:

```bash
python3 tools/run_gui_demo.py --output docs/evidence/04_new_run
```

Unter macOS ergänzt `--screenshot` eine Aufnahme beider Fenster, wenn sie nebeneinander auf den Bildschirm passen. Ohne Ausgabeangabe entsteht ein neuer zeitgestempelter Ordner; vorhandene Ordner werden nicht überschrieben. Für benannte Läufe einen neuen Ausgabeordner verwenden. Die [lokalen M4-Ergebnisse](docs/evidence/04_local_output.md) beschreiben den tatsächlich durchgeführten Lauf; darin enthaltene feste Flotten sind ausschliesslich Testdaten.

## Bild, Nachrichtenlogs und Abgabepaket

Das dekorative [Schiffsbild](bilder/README.md) wurde mit ImageGen erzeugt,
mit ausdrücklich erlaubtem sips auf 256×256 Pixel skaliert und wird mit
64×64 Pixeln im Tk-Hauptthread angezeigt. Original, Prompt und Hashes sind
in `bilder/` enthalten. Es ist keine Flotten- oder Zuganzeige.

Die Oberfläche in Meerblau zeigt die eigene bestätigte Flotte mit fünf
SVG-Schiffstypen aus `bilder/flotte/`. Ein kleiner Canvas-Renderer zeichnet
deren Grundformen ohne zusätzliche Pakete. Wasser erscheint als Punkt,
Treffer als X und der versenkende Treffer mit einem Doppelring. Auf dem
Zielraster bleibt die Gegnerflotte verborgen.

Wird ein eigenes Schiff neu vollständig getroffen, läuft dort einmalig ein
rund 1,15 Sekunden langer Sprengungseffekt. Bereits versenkte Schiffe im
ersten Zustand und wiederholte Zustände lösen ihn nicht erneut aus.
„Sprengungseffekte“ schaltet die Animationen aus und ein; Reset,
Verbindungsende und Fensterschliessen räumen laufende Effekte auf.

Jeder Serverstart erzeugt eine neue JSONL-Datei unter `logs/` im Projekt.
Der ausgegebene Pfad ist vom Startverzeichnis unabhängig. Optional:

```bash
python3 -u src/server.py --host 127.0.0.1 --port 5100 --log-file "<neuer_logpfad.jsonl>"
python3 tools/build_submission.py --output "<neues_abgabearchiv.zip>"
```

Platzhalter durch neue Zielpfade ersetzen. Logs enthalten für jede
empfangene und erfolgreich gesendete Nachricht UTC-ISO-Zeit, Richtung,
Verbindung/Slot, bekannten Typ und bei Serverfehlern einen bekannten Code.
Keine Payloads, Namen oder freien Clienttexte. Vorhandene Logs werden nicht
überschrieben. Das GUI-Demowerkzeug legt seinen Mitschnitt zusätzlich als
`server_messages.jsonl` im neuen Nachweisordner ab.

Ohne `--output` erzeugt das Abgabewerkzeug einen Zeitstempelnamen in `dist/`.
ZIP und `.sha256` werden neu erstellt. Das Paket enthält Programmcode,
Bilder, Tests, Tools, Dokumentation, tatsächliche vorhandene Nachweise und
die benachbarten Originalunterlagen `Dokumente/`. Es schliesst `.git`,
virtuelle Umgebungen, Caches, lokale Geheimnisse und Laufzeitlogs aus;
bewusst abgelegte Nachweise unter `docs/evidence/` bleiben erhalten.
`SHA256SUMS.json` enthält die Hashes aller übrigen ZIP-Dateien,
`ABGABESTATUS.md` die offenen menschlichen Aufgaben. Das Paket ist eine
technische Lieferform und behauptet keine vollständig erfüllte Endabgabe.
Der [Vorführleitfaden](docs/report/vorfuehrung.md) beschreibt die Abnahme.

## Weitere Programme und Weiterentwicklung

`src/local_game.py` spielt ohne Netz an einer Tastatur. `src/play.py` ist der Konsolen-Spielclient mit Standardflotte; `src/client.py` bleibt als Lobby-/Nachrichtenclient erhalten. Echo-Server und -Client dienen dem Grundversuch aus M0. Startbefehle stehen in der Installationsanleitung.

[Architektur](docs/development/architecture.md), [Entwicklungs- und Testablauf](docs/development/testing.md), [Regeln](REGELN.md) und [Protokoll](PROTOKOLL.md) gehören zusammen. Änderungen nur lokal durchführen; Commits, Pushes und GitHub-Schritte übernimmt der Projektverantwortliche nach gesondertem Auftrag.

Die Unterlagen verwenden unterschiedliche Nummerierungen: Im älteren [Projektablauf](docs/assignments/project_flow.txt) gehört die GUI zu M6; die neuen Einzelunterlagen verlangen sie bereits in Kursmeilenstein 4. Ältere offene Personen-/Fremdrechnernachweise stehen weiterhin im [historischen M3-Abgleich](docs/status/03_requirements.md).
