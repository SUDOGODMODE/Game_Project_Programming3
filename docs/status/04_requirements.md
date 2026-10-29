# Anforderungsabgleich — Kursmeilenstein 4

Stand: 27.10.2026. Die abschliessenden tatsächlichen Prüfergebnisse stehen
in [04_local_output.md](../evidence/04_local_output.md). Fremdrechner- und
Personenversuche werden nur nach Durchführung als erfüllt geführt.

Nach dem M4-Stand hat der Benutzer Verbesserungen **bis zur Endabgabe**
freigegeben. Dafür gelten zusätzlich der [Bewertungsabgleich M0–M8](04_rubric_requirements.md),
das unabhängige [Endtesturteil](final_test_verdict.md) und die
[technische Berichtsmaterialsammlung](../report/abschlussbericht.md).
Dieser M4-Abgleich bleibt ein Teilabgleich und ersetzt das Gesamturteil nicht.

## Verbindliche Grundlagen und Umfang

Aus `../Dokumente/aufträge meilenstein 4/` wurden drei Word-Dateien gelesen.
Die Originale bleiben unverändert; die textgetreuen Auszüge stehen unter:

- [Auftrag Meilenstein 4](../assignments/04_assignment.txt)
- [Brett auf dem Bildschirm](../assignments/04_board_on_screen.txt)
- [Oberflächen mit tkinter](../assignments/04_tkinter_guide.txt)

Die separat erwähnte Vorbereitung „Das Brett in den Server“ ist inhaltlich
in Schritt 1 und 2 von „Brett auf dem Bildschirm“ enthalten. Die Unterlagen
lassen dafür keine erkennbare Umsetzungslücke. Der Benutzer hat ausdrücklich
den inhaltlichen Abgleich statt einer weiteren Dateisuche beauftragt.
Der Schulnetzversuch soll laut Benutzer später stattfinden.

Die einzelne Kursaufgabe 4 verlangt bereits die GUI. Im älteren
[Projektablauf](../assignments/project_flow.txt) entspricht das Teilen von
M4 (Server), M6 (GUI) und dem verteilten Versuch. Die vorhandenen Regeln
bleiben erhalten; „Regeln kommen später“ beschreibt den Ausgangspunkt des
Unterrichtsbeispiels und ist kein Auftrag, vorhandene Funktionen zu entfernen.
Eine zusätzliche Bildgenerierung oder neue Regelvariante wird von diesen
drei Unterlagen nicht verlangt.

## Anforderungen aus den Unterlagen

| Anforderung | Umsetzung / Prüfung | Stand |
|---|---|---|
| Eigenes Schiffe-versenken-Brett statt 3×3-Beispiel | Eigene Flotte und Zielraster je 10×10, Koordinaten A–J/1–10 | umgesetzt |
| Server prüft Absender am Zug, gültiges Feld, noch nicht beschossen | Bestehender Kern, private `NOT_YOUR_TURN`, `CELL_OUT_OF_BOUNDS`, `DUPLICATE_SHOT`; TCP-/GUI-Prüfung | umgesetzt |
| Prüfen, Ändern und Senden gemeinsam gesperrt | `server.handle`, dokumentierte Helfer, Wettlauftests | umgesetzt |
| Vollständiger Zustand nach Aktionen an beide | `send_states` nach join/place/shoot/reset, je eigener Snapshot | umgesetzt |
| Ablehnung nur an Absender, keine Zustandsänderung | Vorher-/Nachher-Vergleich beider Sichten und private Fehlerzustellung | umgesetzt |
| Verborgene Information nicht senden | Nur eigene Flotte; eigene/ankommende Schüsse; Payload- und Logprüfung mit verschiedenen Flotten | umgesetzt |
| Konsolenclient behalten | `src/client.py`, `src/play.py`, lokale Partie und Echo weiter vorhanden | erfüllt |
| `client_gui.py` mit Knöpfen und Status | Individuelle Platzierung, Schussklicks, Warten/Zug/Fehler/Ende | umgesetzt |
| Ein Klick schickt nur eine Anfrage | Kein spekulativer Brettwechsel; Regressionstest vor Zustandsantwort | umgesetzt |
| Eine Zeichenfunktion, ganzer bestätigter Zustand | `draw_state`, beide Raster vollständig, auch unveränderte/leere Felder | umgesetzt |
| Keine Widgets aus Netzwerkthreads | Queues; `after` im Hauptthread; Empfang und Versand getrennt | umgesetzt |
| Fenster bleibt bedienbar | Idle-/blockierter-Versand-Tests mit echtem Tk | umgesetzt |
| Fensterkreuz beendet, Server bleibt aktiv | Socket-Shutdown, `opponentLeft`, Reset, Ersatzbeitritt; Transport behandelt OSError | umgesetzt |
| Schleifenklicks melden eigene Koordinaten | Alle 100 Zielknöpfe auf eigene Nachricht geprüft | umgesetzt |
| Erwartung vor Versuch | [04_expected_results.md](../evidence/04_expected_results.md) | vorhanden |
| Fünf Fälle der Anleitung | Ungefragte Aktualisierung, falscher Zug, Doppelbeschuss, Zuganzeige, Fensterschliessen | lokal geprüft, siehe Ergebnis |
| Bild beider Fenster nach demselben Zug | Zwei unveränderte Originalaufnahmen derselben lokalen Partie; gemeinsame Aufnahme im Schulnetz noch erforderlich | lokales Bildpaar vorhanden; Fremdversuch offen |
| Nachweise beider Ablehnungen | Ausgaben und tatsächliche Zustellung im lokalen Integrationslauf | lokal geprüft, siehe Ergebnisnachweis |
| Ganze Partie über andere Rechner | Drei reale Rechner, zwei unterschiedliche fremde Client-IPs und zwei Mitspieler | offen, vom Benutzer auf später verschoben |
| Server-Terminalausgabe dieses Fremdversuchs | Vorbereitete [Checkliste](../evidence/04_school_network_checklist.md); lokale IPs zählen nicht | offen |
| Abzugebender Code und Abhängigkeiten | `src/netz.py`, `server.py`, `client_gui.py`, notwendiges `board.py` und README | vorhanden |
| Zug-/Zustandsprotokoll mit Richtung, Pflichtfeldern, vollständigen Beispielen | Version 0.5: bestehendes `shoot` entspricht dem Beispiel-`move`; `state` inkl. `shotsAtSelf`, Leerfeld-/Geheimhaltungsbedeutung | dokumentiert und automatisiert abgeglichen |

Bei Schiffe versenken bedeutet „beide sehen dasselbe“ den konsistenten
öffentlichen Verlauf und gleichen Zugstatus. Private eigene Flotten dürfen
und müssen verschieden sein. `#` bezeichnet das Feld des versenkenden
Treffers; frühere Treffer dieses Schiffes bleiben `X`.

## Zusätzliche Benutzeranforderungen

| Vorgabe | Nachweis / Umsetzung | Stand |
|---|---|---|
| Vorhandenes Python-Gamingprojekt fortsetzen | Bestehender Kern und Programme weiterverwendet | erfüllt |
| Passend aufteilen und Subagenten einsetzen | Getrennte Anforderungs-/Codeprüfung, Server, GUI, Protokoll und unabhängiges Review | durchgeführt |
| Fragen sofort klären | Schulnetz auf später verschoben; Servervorbereitung inhaltlich abgeglichen, keine offene blockierende Fachfrage | geklärt |
| Skills verwenden | DOCX-Auslesen, Planung, TDD, systematische Fehleranalyse, Delegation, Review und abschliessende Verifikation | angewendet |
| Keine GitHub-Pushes | Keine Commits, Staging-, Push-, PR- oder GitHub-Änderungsoperationen | eingehalten |
| Funktionen tatsächlich testen | Gemeinsame Suite, echte TCP-/Tk-Prüfung und vollständige lokale Partie | Ergebnisse separat aufgezeichnet |
| Tests nach Meilenstein ordnen | `tests/meilenstein_00`, `02`, `03`, `04`; gemischte Werkzeugtests aufgeteilt; gemeinsamer Starter | umgesetzt |
| Saubere Projektstruktur und Anleitungen | `src`, `tests`, `tools`, gegliederte `docs`; README, Setup, Bedienung, Architektur und Tests | umgesetzt |
| Auf Spielwahl optimieren | Geheime individuelle Flotten, eigene/gegnerische Schüsse, Treffer/Wasser/versenkender Treffer, Sieg/Reset | umgesetzt |
| Auf einem Gerät oder verteilt spielen | Gleichberechtigte Startvarianten für ein, zwei oder drei Geräte, offline lokal über 127.0.0.1 und LAN | dokumentiert; Ein-Gerät-Betrieb tatsächlich geprüft |
| Eindeutige Python-3-Startbefehle | Aktuelle macOS-/Linux-Beispiele mit `python3`, Aktivierung der `.venv` je Terminal, Windows-Abweichung erklärt | geprüft |
| Virtuelle Umgebung und lokale Artefakte ausschliessen | `.gitignore` für Venv, Caches, Coverage, Build, lokale Konfiguration und OS-Dateien; Quellen, Vorlagen und Nachweise bleiben versionierbar | 18 Ausschlüsse und 7 Ausnahmen geprüft; keine Venv-Dateien getrackt |
| Zum Schluss Benutzer- und Unterlagenvorgaben abgleichen | Diese beiden Tabellen und Ergebnisnachweis | vorhanden |

## Weiterhin offene ältere praktische Nachweise

Der [historische M3-Abgleich](03_requirements.md) bleibt gültig für offene
Personenaufgaben: Lesepartnerschaft und Gegenlesen von Regeln/Protokoll,
vollständige Partie mit zwei Personen an einer Tastatur, Echo/Handschlag
mit Rollenwechsel über fremde Rechner sowie zwei fremde Lobby-Clients.
Ein automatisierter Test und ein KI-Review werden dafür nicht als
menschlicher Nachweis ausgegeben. Auch eine eigene Prüfung unter Python
3.12, auf Windows/Linux und die leere Abgabefrist aus dem Auftrag sind
noch nicht nachgewiesen bzw. bekannt.
