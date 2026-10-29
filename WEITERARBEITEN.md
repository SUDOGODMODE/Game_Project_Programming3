# Projektstand für die nächste Arbeitseinheit

Gesichert am 27.10.2026, Europe/Zurich. Projekt: Schiffe versenken, Programming 3, Max Rufener.

## Arbeitsweise und Quellen

- Repository: `/Users/max/Desktop/Shared_Folder_Desktop/Fachstudium/Programming3/Projekt/Game_Project_Programming3`.
- Branch `main`; Änderungen dieser Arbeitseinheit sind lokal und uncommittet. Keine Staging-, Commit-, Push-, PR- oder GitHub-Schritte durchgeführt. Vor weiterer Arbeit Status prüfen und vorhandene Änderungen erhalten.
- Zuerst `AGENTS.md`, README, `docs/status/04_rubric_requirements.md` und `docs/status/final_test_verdict.md` lesen. Der M4-Abgleich bleibt als Teilabgleich erhalten.
- Ursprüngliche Word-Unterlagen bleiben unter `../Dokumente/`; neue textgetreue Auszüge unter `docs/assignments/04_*.txt`.
- Zwei Nummerierungen: neue einzelne Kursaufgabe 4 verlangt die GUI; im alten Projektablauf gehören diese Teile zu M4/M6. Nur neu beauftragten Umfang bearbeiten.
- Aktuelle macOS-/Linux-Startbefehle verwenden `python3`; `.venv` in jedem Terminal aktivieren. In dieser Umgebung starten python und python3 beide Python 3.14.10. Windows-Abweichung im Setup dokumentiert. `.gitignore` schliesst Venv/Caches/lokale Konfigurationen aus, erhält aber Quellen/Vorlagen/Nachweise; geprüft. Benutzer testet den Stand anschliessend selbst.
- Der Benutzer will auf einem Gerät oder je nach Infrastruktur verteilt spielen. README und Setup erklären ein, zwei und drei Geräte. Ein-Gerät-Betrieb über 127.0.0.1 ist tatsächlich geprüft; keine separate Infrastruktur nötig.

## Jetzt umgesetzt

- Netzunabhängiger `BattleshipGame`-Kern, bestehende Regeln unverändert: 10×10, Flotte 5/4/3/3/2, A beginnt, jeder gültige Schuss wechselt den Spieler, kein Extrazug bei Treffer.
- Server sendet nach join/place/shoot/reset je eine vollständige gefilterte Sicht an alle belegten Slots. Direkte Antwort steht vor dem zugehörigen state. Ablehnungen bleiben privat und verändern nichts.
- `state` enthält phase, turn, ownShips, shotsAtOpponent, shotsAtSelf und winner. shotsAtSelf enthält auch gegnerische Fehlschüsse. Keine vollständige Gegnerflotte in einer Clientansicht.
- Server protokolliert ausschliesslich bekannte Metadaten; keine Flotten/Zustandspayloads oder freie Clienttexte. netz.read_messages beendet harte Socketabbrüche sauber und schliesst seinen Stream.
- `src/client_gui.py`: zwei Raster, individuelle bearbeitbare Zufallsflotte als Eingabevorschlag, Klick sendet nur Anfrage. Ein draw_state zeichnet ganze bestätigte Sicht; Queue/after verbindet Tk-Hauptthread und getrennte Sender-/Empfangsworker.
- Worker halten keine Tk-Objekte. Fensterkreuz beendet die Verbindung und gibt Tk-Variablen im Hauptthread frei. Server reset, Abbruchanzeige und Ersatzbeitritt geprüft.
- Konsolenclients, lokale Partie und Echo bleiben erhalten. Konsolen-Spielclient verwendet weiterhin seine bekannte Standardflotte als Diagnosehilfe.
- Protokoll Version 0.5 in Markdown und JSON; vollständiger 33-Schuss-Ablauf mit verschiedenen Beispiel-Flotten und automatisiertem Codeabgleich.

## Struktur und Prüfung

- Programme unter `src/`, Tests unter `tests/meilenstein_00/`, `02/`, `03/`, `04/`. M1 hat keine eigene technische Suite. Gemeinsame feste Testdaten: `tests/fixtures.py`.
- `tools/run_tests.py` startet alles oder `--milestone 04`; alle neun früheren Funktions-Bretttests sind jetzt in unittest eingebunden. Unterprozesspfade funktionieren auch nach dem Umzug.
- `tools/check_handshake.py` prüft einen separat gestarteten Server.
- `tools/run_gui_demo.py` lehnt vorhandene Ausgabeordner vor Schreibzugriff ab und speichert PASS erst nach dem letzten Logcheck. Ohne --output entsteht ein neuer zeitgestempelter Ordner. Es startet Server und zwei echte GUI/TCP-Clients und spielt eine vollständige Partie mit Ablehnungen, Reset und Ersatz durch. Für neue Läufe neuen Ausgabeordner wählen.
- Am 27.10.2026: **84 Tests bestanden, keine Fehler/Skips**, Python 3.14.10 / Tk 9.1 auf macOS. Vollständige echte lokale GUI/TCP-Partie nach abschliessender Werkzeugkorrektur: PASS, 33 Schüsse; separat unter `docs/evidence/04_final_run/`. Zusätzlich M2 aus fremdem Arbeitsverzeichnis: 26 bestanden.
- Nachweise: `docs/evidence/04_local_output.md`, Rohlogs/Bilder unter `docs/evidence/04_local/`. Zwei Originalbilder desselben Zuges; gemeinsame automatische Screenaufnahme war nicht verfügbar, fehlgeschlagener Teilversuch getrennt unter `04_diagnostics/` erhalten.
- Sandbox kann TCP-Bind/Tk blockieren. Echte Tests benötigten gezielte Freigabe. Solche Umgebungsfehler nicht als Spieldefekt oder bestandenen GUI-Test ausgeben.

```bash
.venv/bin/python3 tools/run_tests.py
.venv/bin/python3 -u src/server.py --host 127.0.0.1 --port 5100
.venv/bin/python3 src/client_gui.py 127.0.0.1 Alice --port 5100
.venv/bin/python3 src/client_gui.py 127.0.0.1 Bob --port 5100
```

## Offen / ausdrücklich später

- Benutzer verschiebt den echten Schulnetzversuch auf später. Checkliste: `docs/evidence/04_school_network_checklist.md`. Gefordert: Server und zwei andere Clientrechner, zwei verschiedene fremde IPs, ganze Partie, gemeinsames Bild beider Ansichten, private Ablehnungen und Server-Terminalausgabe.
- Menschliche Lesepartnerschaft, Regeln/Protokoll gegenlesen, echte Zweipersonenpartie an einer Tastatur und ältere Echo-/Handshake-Fremdrechnernachweise bleiben offen. KI-Review und Skripte ersetzen diese Aufgaben nicht.
- Python 3.12 / Windows / Linux noch nicht selbst geprüft; blanke Abgabefrist unbekannt. Keine Personen, Freigaben oder Tests erfinden.
- Neuer ausdrücklicher Benutzerauftrag: Verbesserungen anhand der gesamten Bewertung bis zur Endabgabe M8 sind freigegeben. Keine zusätzlichen Regelvarianten, kein Reconnect-Umbau.
- Das alte `Meilenstein_3.zip` auf dem Desktop bleibt ein unverändertes Zeitpunktpaket und enthält den neuen Stand nicht. Für M4 wurde kein neues Abgabearchiv behauptet.


## Ergänzter Gesamtprojektstand bis zur Endabgabe

Der Benutzer hat den Umfang nach dem M4-Abgleich auf die späteren Phasen bis
zur Endabgabe erweitert. Zuerst komplette ZIP-Sicherung erstellt und isoliert
wiederhergestellt: `docs/guides/rollback.md`; unveränderte Sicherung unter
`/Users/max/Desktop/Gaming_Backups/`. Danach Rolle 1 Anforderungen aus
Originalbewertung, Rolle 2 Umsetzung, Rolle 3 unabhängige Tests/Testbewertung.

- M6: ImageGen-Original und freigegeben skalierte transparente 256-Pixel-
  Ableitung in `bilder/`, Tk-Anzeige 64 Pixel. Herkunft und tatsächliche
  Werkzeuggrössen dokumentiert. Dekoration, keine Änderung der Spielregeln.
- M7: `src/event_log.py` protokolliert jede empfangene/erfolgreich gesendete
  Nachricht sofort in exklusive JSONL-Dateien mit UTC-Zeit, Richtung,
  Verbindung/Slot, bekanntem Typ und ggf. Fehlercode. Keine privaten Payloads.
  Server schreibt standardmässig nach `logs/`, `--log-file` wählt einen neuen
  Pfad. Lokale Laufzeitlogs sind ignoriert, Kursnachweise bleiben erhalten.
- `tools/run_tests.py --require-gui --report-json "<neuer_bericht.json>"` verlangt
  tatsächliche bestandene GUI-Prüfungen, erhält alte Reports und trennt
  ausgeführte Tests von Klassen-/Subtestereignissen. Neue Gruppen 06/07/08.
- `tools/build_submission.py` erstellt neue ZIPs samt SHA256-Manifest/Prüfsumme
  und offenem Abgabestatus, ohne Git/Venv/Caches/Secrets/Laufzeitlogs.
- Technische Materialsammlung: `docs/report/abschlussbericht.md`; Vorführung:
  `docs/report/vorfuehrung.md`. **Benutzer ergänzt seine eigene Reflexion in
  `docs/report/meine_reflexion.md` selbst.** README weist ausdrücklich darauf hin.
- Frische unabhängige Prüfung: 101 Tests, 16 echte GUI-Prüfungen, keine
  Fehler/Skips. Sieben Pflichtangriffe sowie komplette Konsolen-/GUI-Partien
  bestanden. Der entpackte Paketkandidat bestand dieselben 101 Prüfungen aus
  einer frischen Venv und einem fremden Arbeitsverzeichnis; Manifest und
  Originalquellenlinks geprüft. Massgebende Ergebnisse stehen im Testurteil
  und `docs/evidence/final_assessment_tests/`.
- Spielkern und sämtliche vor dieser Runde vorhandenen Rohbelege sind zum
  gesicherten Ausgangsstand bytegleich. Drahtprotokoll bleibt Version 0.5.

**Weiterhin offen:** alle oben genannten echten Personen-/Fremdrechneraufgaben,
wechselseitiger Fremdclienttest, Livevorführung, eigene Reflexion und die
persönlich geprüfte/erklärbare Berichtsendfassung. Keine volle Punktezahl oder
vollständig erfüllte Endabgabe behaupten. Keine neuen Git-Schreiboperationen.

## Auslieferung dieses technischen Stands

Endgültiger Archivpfad: `/Users/max/Desktop/Gaming_Abgabe/Schiffe_versenken_Abgabestand_2026-10-27_18-03-27.zip`.
Die eigene Prüfbestätigung dieses erst nach dem Dokumentationsabschluss
erstellten ZIP wird daneben unter `/Users/max/Desktop/Gaming_Abgabe/Schiffe_versenken_Abgabestand_2026-10-27_18-03-27.verification/result.json`
abgelegt. Sie prüft seinen eigenen Hash, Manifest, frische entpackte Venv,
strenge Tests und Laufzeitverhalten. Der Archivstand enthält deshalb nicht
seine erst nach Erstellung gemessene eigene Prüfung.

Abschliessender Kriterienreview: `docs/status/final_rubric_review.md`;
unabhängiges Testurteil: `docs/status/final_test_verdict.md`. Der Benutzer
prüft nun selbst, ergänzt seine Reflexion und verantwortet die ausstehenden
Personen-/Fremdrechnerleistungen.


## Neuester Stand: 29.10.2026 — SVG-Grafik und Sprengung

Zusätzlicher Benutzerauftrag lokal umgesetzt: maritime Oberfläche in Meerblau,
fünf gezeichnete SVG-Schiffe und kurze Sprengung beim Besitzer nach dem letzten
bestätigten Treffer. Neue Module `src/ship_art.py`, `src/sea_cell.py` und
`src/ship_effects.py`, Assets `bilder/flotte/`. Kein Zusatzpaket nötig;
das bestehende ImageGen-PNG und alle Spielregeln/Servernachrichten bleiben
bestehen. Canvas-Zielfelder mit Maus, Pfeilen, Eingabe und Leertaste bedienbar.

`ShipEffects.observe` erhält nur `ownShips`. Erst ein bekannter Übergang von
unversenkt zu vollständig getroffen startet die etwa 1,15 Sekunden lange
Animation; kein Effekt beim ersten bereits versenkten Snapshot oder dessen
Wiederholung. Der Effektschalter beendet nur Bilder und bewahrt die Historie;
Reset leert auch die Historie. Disconnect/Schliessen räumen Callbacks auf.

Letzte tatsächliche Prüfung: **114 Tests bestanden, darunter 28 echte
GUI-Prüfungen, keine Fehler/Skips**; komplette lokale 33-Schuss-Partie PASS.
Neue Tests unter `tests/meilenstein_06/`; unabhängiges Agentenreview, kein
menschliches Gegenlesen. Nachweise und Bildschirmvorschau unter
`docs/evidence/06_graphics_2026-10-29/`. Python 3.14.10 / Tk 9.1 auf macOS;
weitere Plattformen nicht neu geprüft.

Alle Änderungen weiterhin lokal, kein Staging/Commit/Push. Vorhandene
Abgabearchive enthalten diesen neueren Grafikstand nicht und wurden nicht
überschrieben. Sämtliche zuvor offenen Personen-/Fremdrechneraufgaben und
die eigene Reflexion bleiben unverändert offen.
