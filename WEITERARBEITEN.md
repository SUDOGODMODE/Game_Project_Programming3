# Projektstand für die nächste Arbeitseinheit

## Pause während Kursmeilenstein 6, 10.11.2026

Der Projektverantwortliche hat M6 begonnen und bestätigt, die Tic-Tac-Toe-
Lehrschritte auf das bestehende Schiffe versenken zu übertragen. Auf Wunsch
bei 14 % verbleibender Ladung wird nach diesem geprüften Arbeitsblock
pausiert. Die unten stehenden älteren Abschnitte beschreiben frühere Stände;
damalige Aussagen „M6 beginnt später“ sind inzwischen überholt.

**Abgeschlossen und lokal geprüft:** Originalauftrag
`../Dokumente/Auftrag_Meilenstein6.docx` gelesen; Spec-Kit-Plan unter
`specs/002-milestone-6/`; `PORT`-Umgebungsvariable in `src/server.py`
ergänzt (CLI-`--port` hat Vorrang), zuerst roter, danach 2/2 grüner Porttest.
Fensterloser `src/testclient.py` und `src/test_netz.py` mit **21 echten
Prozess-/TCP-Tests**: alle elf Protokoll-Fehlercodes, private Antworten,
gefilterte Zustände, 33-Schuss-Partie, harter Abbruch und Ersatzbeitritt.
Der Kurslauf steht in
`docs/evidence/06_final_2026-11-10/test_netz_green.txt` (21/21).
`python3 -m unittest discover` aus dem Projektordner bestand **190/190**;
Rohausgabe `docs/evidence/06_final_2026-11-10/discover_green.txt`.
Der strenge Gesamtlauf bestand **190/190, 29/29 echte GUI-Prüfungen,
0 Skips**; `full_strict.json` und `full_strict.txt` liegen daneben.

Vorhergesagte isolierte Servermutationen A/B/C lieferten genau **3/1/1
rote Netztests**; die 19 Kernregeltests blieben bei A grün und die originale
Netzsuite danach wieder 21/21. Diffs, Rohlogs und Erklärung stehen unter
`docs/evidence/06_mutations_2026-11-10/`. Der Zählerfehler der Lehrvorlage
war im echten Server bereits behoben; C ist ausdrücklich Simulation. Der
tatsächlich vor M6 vorhandene Portfehler wurde korrigiert.

**Nach der Pause erledigt, 10.11.2026:**

1. ✓ Fünf Statusdokumente, die noch „M6 beginnt später/noch nicht begonnen“
   sagten, auf den tatsächlichen Abschluss korrigiert (siehe Journal
   10.11.2026 „M6-Übergabe abgeschlossen“). `--core` dabei unverändert 41/41.
2. ✓ Die bereits vorhandene vollständige lokale GUI/TCP-Demo für M6
   (`docs/evidence/06_final_2026-11-10/gui_demo_m6/result.json`, PASS) war
   unverlinkt und ist jetzt im README und M6-Abgleich referenziert. Keine
   zusätzliche Demo nötig.
3. ✓ Neues `dist/Schiffe_versenken_Meilenstein_6_2026-11-10.zip` gebaut;
   SHA256- und innere Manifestprüfung (336/336), in frischem fremdem
   Zielordner entpackt, dort `--require-gui`-Gesamtlauf **190/190 Tests,
   29/29 echte GUI-Prüfungen, 0 Skips** unter frischer Venv mit Python
   3.14.10. Beleg unter
   `dist/Schiffe_versenken_Meilenstein_6_2026-11-10.verification/`.
4. ✓ README und `docs/status/06_requirements.md` mit den tatsächlichen
   Endergebnissen ergänzt; Journal fortgeschrieben.

**Noch offen:**

- Unabhängigen Diff-Review und `git diff --check` über den gesamten
  aktuellen Arbeitsstand ausführen; abschliessenden Git-Status prüfen.
- Persönliche Reflexion, menschliches Gegenlesen, echte Fremdrechner- und
  Fremdclientversuche sowie Livevorführung bleiben offen und sind durch
  keinen der obigen Schritte ersetzt.

**Grenze:** Persönliche Reflexion, menschliche Gegenlesung, Fremdrechner-
und Fremdclientversuche sowie Livevorführung bleiben offen. Nur der
Projektverantwortliche committet und pusht; bisher keine Commits/Pushes.

## Verzeichnisordnung und aktueller Nachweis, 10.11.2026

Die festen Kurseinstiege unter `src/`, die Startprofile und `bilder/` bleiben
an ihren bisherigen Pfaden. Vier interne GUI-Helfer liegen nun unter
`src/gui/`. Vorhandene Log- und Pakettests wurden ohne Verlust nach
`tests/additional/` verschoben; `--milestone` bietet nur technische Gruppen
bis 06. Die [Spec-Kit-Spezifikation](specs/001-project-structure/spec.md)
und [Dokumentübersicht](docs/README.md) erklären die Entscheidung.

Nach der Umordnung bestanden der Kernlauf **41/41**, der eigenständige
Kurstest **19/19** und die [strenge Gesamtsuite](docs/evidence/refactor_2026-11-07/full_suite_structure_2026-11-10.json)
**167/167 Tests mit 29/29 echten GUI-Prüfungen**, ohne Fehler oder Skips.
Die [lokale vollständige Tk/TCP-Partie](docs/evidence/refactor_2026-11-07/gui_demo_structure_2026-11-10/result.json)
bestand. Ein neu gebautes temporäres Spiel-ZIP enthielt die verschobenen
Module und Zusatztests, schloss `.specify/` und `.agents/` aus und bestand
Manifest-/Hashprüfung, den entpackten Kernlauf und die Client-Starthilfe
aus fremdem Arbeitsverzeichnis. Der unabhängige Review meldete einen
veralteten Pfad in `bilder/README.md`; er wurde korrigiert. Dies belegt
keinen echten Fremdrechnerlauf und keine Umsetzung des späteren M6-Auftrags.
Nur der Projektverantwortliche pusht; es wurden keine Commits oder Pushes
ausgeführt.

## Aktueller Kursumfang und Testordnung, 10.11.2026

Der Projektverantwortliche hat klargestellt: Der aktuelle Kurs endet mit
Meilenstein 6, dessen Umsetzung erst mit einem späteren Auftrag beginnt.
Vorhandene Nachrichtenlogs und Paketwerkzeuge sind Zusatzfunktionen.
Ihre Tests liegen unter `tests/additional/`; `tools/run_tests.py` sammelt sie
im Gesamtlauf und bietet als Meilensteinauswahl nur die vorhandenen Gruppen
00, 02, 03, 04, 05 und 06 an. Der ältere Grafik-Testordner
`tests/meilenstein_06/` bleibt als technische Gruppierung erhalten und
belegt keine Umsetzung des späteren Kursauftrags.

Die untenstehenden datierten Arbeitsstände und Originalunterlagen bleiben
historische Belege. Ihre früheren M7/M8-Bezeichnungen sind keine aktuelle
Kursplanung. Lokale Entwicklungswerkzeuge unter `.agents/` und `.specify/`
werden aus neu erstellten Spiel-ZIPs ausgeschlossen.

## Fortsetzung am 10.11.2026

Der am 07.11. pausierte Testbarkeitsstand wurde weiter geprüft. Der erste
Gesamtlauf in der eingeschränkten Sandbox scheiterte an gesperrten lokalen
TCP-Portbindungen; sein Bericht ist
`docs/evidence/refactor_2026-11-07/full_suite_resume_2026-11-10.json` und
kein Code- oder GUI-Nachweis. Mit TCP-/Tk-Zugriff bestanden zunächst 162/162
Tests und 29/29 GUI-Prüfungen. Ein unabhängiger Review fand danach, dass
`platform.platform()` im Teststarter selbst für `--core` fremde Prozesse
starten konnte. Ein zuerst fehlschlagender Regressionstest sichert den
CLI-Einstieg mit und ohne JSON-Bericht ab; die Plattformangabe nutzt jetzt
prozessfreie Systemdaten. Nach dem Fix bestanden
`docs/evidence/refactor_2026-11-07/full_suite_after_fix_2026-11-10.json`
mit **163/163 Tests, 29/29 GUI-Prüfungen, ohne Fehler oder Skips**. Der
fokussierte Re-Review meldete keine weiteren Befunde.

Die lesende [Spec-Kit-Recherche](docs/development/spec_kit_research.md) ist
abgeschlossen. Danach wurde Spec Kit 1.3.3 auf ausdrücklichen Auftrag des
Projektverantwortlichen lokal installiert und im bestehenden Repository für
Codex initialisiert. Die Projektgrundsätze stehen in
`.specify/memory/constitution.md`; die Skills unter `.agents/skills/`.
Alle Änderungen bleiben lokal und uncommittet.

## Projektweite Lesbarkeitsbereinigung, 10.11.2026

Alle Python-Bereiche wurden auf Verständlichkeit geprüft. Konkrete lange
Abläufe in Konsolenclient, GUI, Grafik und Werkzeugen wurden in benannte
Schritte gegliedert; Server- und Spielkernzuständigkeiten sind erklärt.
Gemeinsame GUI-Testfixturen liegen nun in `tests/gui_helpers.py`.
Die [Lesereihenfolge](docs/development/code_lesen.md) führt vom Spielkern
über Server und Clients zu Tests und Nachweisen. Spezifikation und Plan
liegen unter `docs/superpowers/`.

Ein sporadischer Tastaturtest-Ausreißer wurde auf zusätzliche wartende
Tastaturereignisse während dreier unnötiger `root.update()`-Aufrufe im Test
eingegrenzt. Die Aufrufe wurden entfernt; ein kontrolliert eingereihtes
Return reproduzierte vorher den Fehler und bestand danach. Die genaue
Herkunft des ursprünglich eingereihten Return bleibt unbekannt.

Die abschließende [strenge Gesamtsuite](docs/evidence/refactor_2026-11-07/full_suite_readability_final_2026-11-10.json)
bestand mit **166/166 Tests, 29/29 echten GUI-Prüfungen, ohne Fehler oder
Skips**. Die [vollständige lokale Tk/TCP-Demo](docs/evidence/refactor_2026-11-07/gui_demo_readability_2026-11-10/result.json)
bestand mit 33 Schüssen, privaten Ablehnungen, Sieg/Niederlage und
Ersatzbeitritt. Ein unabhängiger Gesamtreview meldete keine weiteren
konkreten Regressionsbefunde. Dies ist kein echter Zweirechnernachweis.

## Pause auf Wunsch des Projektverantwortlichen, 07.11.2026

Arbeit auf `feature/testability-junior-clarity` angehalten. Sämtliche
Änderungen sind lokal und uncommittet; nichts zurücksetzen oder überschreiben.
Die unten genannte strenge Suite mit 162/162 und die GUI-Demo bestanden vor
einer letzten kleinen Vereinfachung der Imports in zwei neuen Testdateien.
Danach bestanden diese fünf gezielten Tests erneut; die volle Suite wurde
seit dieser letzten Änderung noch nicht wiederholt. Der unabhängige
Gesamtreview und die lesende Spec-Kit-Recherche wurden wegen der gewünschten
Pause unterbrochen. Es gibt noch keinen Reviewabschluss.

Beim Fortsetzen: zuerst Git-Status prüfen, den strengen Gesamtlauf erneut
ausführen, dann den gesamten Diff unabhängig reviewen und Befunde bearbeiten.
Die früher bestätigten Entscheidungen gelten weiterhin: Der Projektpfad ist
dieses Repository und Spezifikationen sollen dauerhaft darin bleiben. Offen
ist nur, ob die eigentliche Spec-Kit-Installation Teil dieses Feature-Branches
oder eine getrennte Arbeit sein soll; die Rückfrage wurde gestellt, aber bis
zur Pause nicht beantwortet. Keine Commits, Pushes oder GitHub-Änderungen.

## Aktuelle Ergänzung: Testbarkeit und Junior-Einstieg, 07.11.2026

Lokaler Branch: `feature/testability-junior-clarity`; keine Commits oder
Pushes. Die [Spezifikation](docs/superpowers/specs/2026-11-07-testability-junior-clarity-design.md)
und der [Arbeitsplan](docs/superpowers/plans/2026-11-07-testability-junior-clarity.md)
bleiben wie vom Projektverantwortlichen gewünscht im Repository.

`python3 tools/run_tests.py --core` prüft 41 Spielkern- und Kurstests ohne
Netzwerk oder Tk. Tk-freie Helfer berechnen Brettzeichen und eine gültige
Zufallsflotte; `client_gui.py` bleibt für die Widgetdarstellung zuständig.
Server-Integrationstests nutzen temporäre Logpfade und schließen ihren
Logwriter. README und Testanleitung erklären einen Lern- und Testweg.
Regeln und Drahtprotokoll wurden nicht geändert.

Frische Prüfungen: [strenge Gesamtsuite](docs/evidence/refactor_2026-11-07/full_suite.json)
mit **162/162 Tests, 29/29 echten GUI-Prüfungen, ohne Fehler oder Skips**;
eigenständiger Kursbefehl in `src/` mit 19/19 Tests; [vollständige lokale
Tk/TCP-Demo](docs/evidence/refactor_2026-11-07/gui_demo/result.json) mit
33 Schüssen, privaten Ablehnungen, Sieg/Niederlage und Ersatzbeitritt: PASS.
Bei einem gezielten GUI-Teillauf trat einmal der bereits historisch
dokumentierte Tastaturtest-Ausreißer mit drei statt zwei Aufrufen auf. Der
einzelne Test und der frische strenge Gesamtlauf bestanden danach; seine
Ursache bleibt offen. Dies ist kein Fremdrechnernachweis. Persönliche und
reale Zweirechner-Aufgaben bleiben offen.

## Aktuelle Ergänzung: zwei Startvarianten, 03.11.2026

Der neue Auftrag ergänzt getrennte Einstiege und Anleitungen für
[localhost](varianten/localhost/START.md) und
[zwei Rechner](varianten/zwei_rechner/START.md) aus derselben Codebasis.
Die [Statusmatrix](docs/status/two_versions.md) trennt technische Prüfung
vom weiterhin offenen echten Zweirechnerlauf. Der
[Vergleich der Soll- und Ist-Abdeckung](docs/status/05_coverage_comparison.md)
steht als eigene Liste bereit. Der neue strenge
[Gesamtlauf](docs/evidence/two_versions_2026-11-03/full_final.json) bestand
155/155 Tests, darunter 29 echte GUI-Prüfungen, ohne Fehler oder Skips.
Ein [echter lokaler Profilstart](docs/evidence/two_versions_2026-11-03/localhost_startup_server.txt)
startete Server und zwei Tk-Clientprozesse über den localhost-Einstieg;
zwei Joins und `gameStart` sind im Servermitschnitt sichtbar. Eine ganze
Partie über beide Clientwrapper ist dadurch noch nicht belegt.
Ein [lokaler LAN-Server-Smoke](docs/evidence/two_versions_2026-11-03/lan_server_local_smoke_validated.txt)
über den Zwei-Rechner-Einstieg bestand mit TCP-`join`/`welcome` auf demselben
Gerät; [ungültige Bob-IP-Aufrufe](docs/evidence/two_versions_2026-11-03/lan_invalid_ip.json)
wurden vor einem Verbindungsversuch abgelehnt. Dies ist kein Fremdrechnerbeleg.
Zwei endgültige Profil-ZIPs liegen unter
`dist/Schiffe_versenken_localhost_2026-11-03_freigabe.zip` und
`dist/Schiffe_versenken_zwei_rechner_2026-11-03_freigabe.zip`.
Die zugehörigen Prüfverzeichnisse mit demselben Namen und dem Suffix
`.verification/` liegen daneben. Aus jedem entpackten Paket bestanden
Manifest-/Hashprüfung, Start-Hilfe, Kerntest sowie 155/155 Tests mit
29 echten GUI-Prüfungen. Das Localhost-Paket durchlief zusätzlich eine
ganze Partie, das Zwei-Rechner-Paket einen lokalen TCP-Beitritt.
Ein weiterer [vollständiger lokaler Tk/TCP-Lauf](docs/evidence/two_versions_2026-11-03/localhost_full_profile_game/result.json)
bestand mit Serverstart über den localhost-Profilwrapper, zwei echten
Tk-Fenstern und 33 Schüssen bis Sieg/Niederlage. Die Clientwrapper wurden
separat nur bis `gameStart` geprüft. Ältere Kandidaten und Zwischenberichte
bleiben erhalten; der echte Zweirechnerlauf bleibt offen.
Die älteren M5-Ergebnisse und die historische Übergabe unten behalten ihren
damaligen Stand.

## Aktuelle Arbeitseinheit: 03.11.2026 — Kursmeilenstein 5

Der Originalauftrag liegt unverändert unter `../Dokumente/auftrag_Meilenstein5`;
`docs/assignments/05_assignment.txt` ist eine bytegleiche Kopie.
Der Projektverantwortliche hat die Übertragung der Tic-Tac-Toe-Lehrschritte
auf Schiffe versenken bestätigt; ein zweites Spiel wird nicht gebaut. Der
echte Zweirechnerlauf bleibt ausdrücklich auf später verschoben. Die
Abgabefrist im Auftrag ist leer. [M5-Anforderungsabgleich](docs/status/05_requirements.md)
und [M5-Spezifikation](docs/superpowers/specs/2026-11-03-milestone-5-design.md)
trennen den beauftragten Umfang vom älteren Projektablauf.

Ein neuer lokaler M5-Paketkandidat liegt unter
`dist/Schiffe_versenken_Meilenstein_5_2026-11-03.zip`; seine unabhängige
Prüfung steht daneben unter
`dist/Schiffe_versenken_Meilenstein_5_2026-11-03.verification/result.json`.
Die entpackte Suite bestand 139/139 Tests mit 29 echten GUI-Prüfungen.
Dieser Kandidat enthält die vorliegende spätere Ergänzung zur Paketprüfung
noch nicht. Der echte Zweirechnerlauf bleibt offen.

Ein tatsächlicher lokaler Vorlauf mit zwei Tk/TCP-Fenstern bestand vor
Änderungen: [Ergebnis](docs/evidence/05_preflight_2026-11-03/result.json).
Die für M5 vereinbarte Endfolge lautet `result` an den Schützen, dann
individuelle `state` an beide, dann `gameOver` an beide. Der
Nachrichtenkatalog beschreibt sie als Version 0.6. Die früheren Belege
zu Version 0.5 bleiben historische Ergebnisse. Tatsächlich durchgeführt:
[interaktive Kernpartie](docs/evidence/05_final_2026-11-03/interactive_core.txt)
mit 33 Zügen und Ablehnungen ohne Zustandsänderung; [zwei absichtliche rote
Mutationen](docs/evidence/05_mutation_2026-11-03/result.json) in isolierten
Kopien (1 bzw. 7 vorhergesagte rote Tests); anschliessend [19/19 grüne
Kerntests](docs/evidence/05_final_2026-11-03/test_spiel_green.txt) und
[139/139 Tests](docs/evidence/05_final_2026-11-03/full_release.json), darunter
29 echte GUI-Prüfungen, keine Fehler oder Skips. Der [verifizierte lokale
Tk/TCP-Lauf](docs/evidence/05_gui_verified_2026-11-03/result.json) belegt
33 Schüsse, Sieg/Niederlage, einen echten Zielbutton-Klick nach Spielende
mit privater `WRONG_PHASE`-Ablehnung und den weiterlaufenden Server. Das
[gemeinsame Endbild](docs/evidence/05_gui_verified_2026-11-03/two_windows_finished.png)
zeigt beide Tk-Fenster eng nebeneinander. Ein früherer kompakter Bildversuch
war ungültig; seine unveränderte Ergebnisdatei meldete den Screenshot
fälschlich PASS. Einzelheiten im [M5-Abgleich](docs/status/05_requirements.md).
Der echte Zweirechner-Terminalbeleg bleibt offen.
Nach der letzten M5-Paketstatuskorrektur ist
`docs/evidence/05_final_2026-11-03/full_release.json` der massgebende
strenge Gesamtlauf. Das Abgabewerkzeug nennt den offenen Zweirechnerlauf
und verlinkt den M5-Abgleich; beide M8-Pakettests sind grün. Ältere
M5-Reports bleiben als Zwischenstände erhalten. Kein neues M5-Abgabearchiv
oder Fremdrechnerergebnis wird behauptet.

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
