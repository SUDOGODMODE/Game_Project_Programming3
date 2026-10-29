# Schiffe versenken

Python-Projekt im Modul Programming 3 an der HFTM, Max Rufener. Zwei Spieler verbinden sich mit einem zentralen Server. Der Server entscheidet über jede Aktion und verteilt die vollständige erlaubte Sicht an beide Clients.

Kursmeilenstein 4 **„Das Brett auf dem Bildschirm“** ergänzt die tkinter-Oberfläche, automatische Zustandsmeldungen und lokale Nachweise. Der Versuch mit zwei fremden Clientrechnern ist für später vorbereitet und bleibt offen. Der [Anforderungsabgleich](docs/status/04_requirements.md) trennt Umsetzung, Prüfung und noch fehlende praktische Nachweise.

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

## Schnellstart

Du kannst **Server und beide Clients auf einem einzigen Gerät** laufen lassen.
Nach der Einrichtung brauchst du dafür weder Internet noch WLAN noch einen
separaten Serverrechner. Derselbe Spielcode funktioniert auch verteilt im LAN:

| Verfügbare Geräte | Startvariante |
|---|---|
| Ein Gerät | Server und zwei Spielfenster lokal über `127.0.0.1` |
| Zwei Geräte im LAN | Server + erster Client auf Gerät 1, zweiter Client auf Gerät 2 |
| Drei Geräte im LAN | Server auf Gerät 1, Clients auf Gerät 2 und 3; Schulnetz-Topologie |

Die folgenden Befehle zeigen den Ein-Gerät-Betrieb. Vollständige Alternativen
stehen in der [Startanleitung](docs/guides/setup.md).

Python **3.12 oder neuer** mit tkinter, keine weiteren Python-Pakete. Im Projektordner eine virtuelle Umgebung erstellen oder die vorhandene verwenden. Details für macOS, Linux und Windows in der [Installationsanleitung](docs/guides/setup.md). Die Bash-Beispiele verwenden `python3`; unter Windows nach Aktivierung der Umgebung `python` verwenden.

Falls `.venv` noch nicht existiert, einmal `python3 -m venv .venv` ausführen.
Mit `source .venv/bin/activate` und anschliessend `python3 -m tkinter` die
GUI-Unterstützung prüfen; das kleine Testfenster danach schliessen.

**Drei separate Terminals im Projektordner öffnen.** Den Server zuerst
starten und laufen lassen, danach die beiden Clients:

**Terminal 1 — Server:**

```bash
source .venv/bin/activate
python3 -u src/server.py --host 127.0.0.1 --port 5100
```

**Terminal 2 — erster Client:**

```bash
source .venv/bin/activate
python3 src/client_gui.py 127.0.0.1 Alice --port 5100
```

**Terminal 3 — zweiter Client:**

```bash
source .venv/bin/activate
python3 src/client_gui.py 127.0.0.1 Bob --port 5100
```

`127.0.0.1` ist localhost: Alle drei Programme laufen auf deinem Gerät.
Nach Alices Start ist „Warte auf Gegner“ normal; Bobs Start öffnet die
Flottenplanung in beiden Fenstern. In **beiden** Fenstern „Flotte senden“
klicken; danach beginnt Alice (Spieler A). Zum Beenden die zwei Fenster
schliessen und den Server in Terminal 1 mit **Ctrl+C** stoppen.

Jeder Spieler passt seine vorgeschlagene Flotte an und klickt „Flotte senden“. Nach beiden gültigen Platzierungen beginnt A. Zum Schiessen ein Feld im Zielraster anklicken oder mit den Pfeiltasten auswählen und mit Enter/Leertaste auslösen. Die Anzeige folgt ausschliesslich dem bestätigten Serverzustand. Das Fensterkreuz beendet die Verbindung. Das [Benutzerhandbuch](docs/guides/user_manual.md) erklärt Platzierung, Symbole, Zugfolge und Abbruch.

Standardport ist 5000; die Beispiele verwenden 5100 wegen möglicher Belegung auf macOS. Für fremde Clients den Server ohne `--host 127.0.0.1` starten und die tatsächliche Server-IP verwenden. Die [Schulnetz-Checkliste](docs/evidence/04_school_network_checklist.md) beschreibt den Versuch mit Server und zwei anderen Clientrechnern.

## Projektstruktur

```text
src/                          Spielprogramme und Netzwerk
tests/
  fixtures.py                 Gemeinsame feste Testdaten
  meilenstein_00/             Echo / Werkzeugbasis
  meilenstein_02/             Brett, Spielkern, lokale Partie
  meilenstein_03/             Transport, Lobby, TCP/CLI, Angriffstest
  meilenstein_04/             Zustandsverteilung und echte GUI-Tests
  meilenstein_06/             PNG, SVG-Flotte, Grafikeffekte und Tk-Lebensdauer
  meilenstein_07/             Persistentes privates Nachrichtenlog
  meilenstein_08/             Abgabepaket und Manifest
tools/                        Gemeinsamer Teststart und lokale Nachweise
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
PROTOKOLL.md                  Lesbarer Nachrichtenkatalog, Version 0.5
journal.md                    Tatsächliche Arbeitsschritte und Prüfungen
WEITERARBEITEN.md             Übergabe für die nächste Arbeitseinheit
```

M1 hat Dokumentations- und Freigabeaufgaben, keine eigene technische Testsuite. Bestehende Tests bleiben beim ursprünglichen Schwerpunkt; sie prüfen als Regression auch spätere Erweiterungen. Historische Rohlogs behalten ihre damaligen Dateipfade. Die originalen Word-Unterlagen liegen unverändert im benachbarten Ordner `../Dokumente/`.

## Tests

```bash
python3 tools/run_tests.py
python3 tools/run_tests.py --milestone 04
python3 tools/run_tests.py --require-gui --report-json "<neuer_testbericht.json>"
```

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
