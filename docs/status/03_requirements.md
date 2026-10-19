# Anforderungsabgleich bis Meilenstein 3

Stand: 13.10.2026. Grundlage sind die beiden Nummerierungen der Kursunterlagen. «Lokal geprüft» bezeichnet einen tatsächlich ausgeführten Versuch; «offen» bezeichnet noch fehlende Arbeit oder einen fremden Nachweis.

## Unterlagen

- [Projektablauf](../assignments/project_flow.txt): M0–M8, Architektur, Tests und Abgabe.
- [Der erste Handschlag](../assignments/02_first_handshake.txt): einzelne Kursaufgabe 2.
- [Zwei Spieler, ein Tisch](../assignments/03_two_players.txt): einzelne Kursaufgabe 3.
- [Alter Protokollentwurf](../assignments/protocol_example.txt): Beispiel, durch die späteren Vorgaben zu `type` und serverseitiger Identität ergänzt.
- `Projekt/Dokumente/Projektauftrag_Programming3_Game.docx`: Spielekatalog, insbesondere B1 Schiffe versenken.
- `Projekt/Dokumente/Auftrag1_Spielwahl_ausgefuellt.docx`: ausgefüllter Vorschlag; Schwierigkeit aus Frage 8 ist die verborgene Information, ergänzt um Platzierung und Trefferprüfung.
- `Projekt/Dokumente/Spielkatalog_Programming3.docx`: unbeschriebenes Spielwahlformular.

## Jetzt notwendig: Projektphasen M0–M3

| Anforderung | Umsetzung / Nachweis | Stand |
|---|---|---|
| M0 · Repository und erster Commit | Git-Historie seit `f156608`; aktueller HEAD unverändert `a23f73e` | vorhanden |
| M0 · Struktur und virtuelle Umgebung | `src/`, `docs/`, `.venv`; Python 3.14.8, Setup im README | vorhanden |
| M0 · Echo lokal | `echo_server.py` sendet empfangene Bytes gross zurück; `echo_client.py` liest bis EOF, auch bei langen Antworten | lokal geprüft |
| M0 · Echo über zwei Rechner und Rollenwechsel | Startprogramme vorhanden; fremde Adressen und Gegenversuch fehlen | offen, praktischer Versuch |
| M0 · Feste Lesepartnerschaft | Noch keine Person vereinbart; vorgesehener Eintrag: `<lesepartner_name>` | offen |
| M1 · Spielvorschlag und Freigabe | Formular vorhanden, Schiffe versenken laut Bestätigung für das Projekt erlaubt | vorhanden / bestätigt |
| M1 · Regeln: Zustand, Aktionen, ungültige Züge, Ende | [REGELN.md](../../REGELN.md), einschliesslich Flotte, kein Unentschieden, kein Aussetzen und Abbruch | dokumentiert |
| M1 · Oberflächenskizze | Zwei Raster und Bedienfelder im Regelblatt; ergänzt das Formular | vorbereitet |
| M1 · Regelblatt gegengelesen | Nach Auskunft hat bisher niemand das Blatt gelesen | offen |
| M2 · Netzunabhängige Klasse | `board.BattleshipGame`; keine Sockets oder GUI im Kern | geprüft |
| M2 · Prüfen, Ausführen, Zustand kopieren | `check_shot`, `shoot`, `place_fleet`, `state`; Fehler enthalten Grund und Code | geprüft |
| M2 · Mindestens fünf Tests, schwieriger Sonderfall | 9 Brett- und 12 Kerntests; getrennte Spielersichten, Kopien, Platzierung, Treffer und Sieg | geprüft |
| M2 · Jeder ungültige Zug im Code | Regelblatt ordnet die Fälle den Kernfunktionen und Fehlercodes zu | geprüft |
| M2 · Ohne Netz an einer Tastatur spielbar | `local_game.py`, individuelle Platzierung, Zugwechsel und Spielende; vollständige geskriptete Partie | lokal geprüft |
| M2 · Zwei Personen spielen eine ganze Partie | Das Programm steht bereit; ein geskripteter Lauf ist kein Nachweis zweier Personen | offen, manueller Versuch |
| M3 · Katalog mit Richtung, Feldern, Anlass | `PROTOKOLL.md` und `protocol.json`, 14 einzelne Typen | geprüft |
| M3 · Vollständige JSON-Beispiele und ganze Partie | Beispiele für alle Typen; vollständige Zugfolge von Beitritt bis Ende | geprüft |
| M3 · TCP-Rahmen und zwei Testprogramme | `netz.send` / `read_messages`; Server-/Clientprozesse und 5 Transporttests | lokal geprüft |
| M3 · Gefilterter vollständiger Zustand | `state(slot)` gibt die ganze erlaubte Sicht zurück; keine Gegnerflotte | geprüft |
| M3 · Fremde Person versteht den Katalog | Noch kein Gegenlesen oder unabhängiger Clientnachweis | offen |

Die spätere Serverphase M4 verlangt die automatische Verteilung der gefilterten Zustände nach Spielaktionen. Der Katalog beschreibt den aktuellen Stand: `state` kommt bislang als Antwort auf `getState`. Eine Umsetzung dieser Zustandsmeldungen ist noch offen und wird nicht als abgeschlossen geführt.

## Jetzt notwendig: einzelne Kursaufgaben 2 und 3

| Anforderung | Umsetzung / Nachweis | Stand |
|---|---|---|
| 2 · Nachrichten haben `type`, Beitritt ohne eigene ID | Client sendet `join/player`; Server vergibt Slot A oder B anhand der Verbindung | geprüft |
| 2 · Willkommen und Ablehnung mit Grund | `welcome` oder `error` mit Code und Nachricht; eigener Katalog stimmt mit Code überein | geprüft |
| 2 · Fehlende Felder, Doppelbeitritt, falsche Typen, kaputtes JSON | `test_angriff.py` prüft Antworten; tatsächliche Ausgabe gespeichert | lokal geprüft |
| 2 · Server läuft nach Ende und Angriffen weiter | Dauerhafte Accept-Schleife, Aufräumen in `finally`, Folgeverbindungen in Tests | geprüft |
| 2 · Handschlag über fremden Rechner, danach Rollenwechsel | Nur Loopback-Ausgaben gefunden; kein fremder Serverversuch | offen, praktischer Versuch |
| 3 · `netz.py` bleibt unverändert | Arbeitskopie stimmt mit Ausgangsstand überein | erfüllt |
| 3 · Threads, Spielerverzeichnis, Sperre | Ein Thread je Verbindung; Sperre umfasst Zulassung, Änderungen und Sendungen | geprüft |
| 3 · Empfang bleibt aktiv, während Nutzer nichts sendet | `client.py` hat Empfangsthread und Eingabeschleife | geprüft |
| 3 · Erster Spieler wartet | `welcome`, danach ungefragtes `waiting` | lokal geprüft |
| 3 · Zweiter startet bei beiden | `welcome` vor `gameStart`; identische Namen und serverseitige Slots bei beiden | lokal geprüft |
| 3 · Dritter wird abgewiesen | `error/GAME_FULL`, ohne die beiden Spieler zu verändern | lokal geprüft |
| 3 · q und harter Abbruch, danach Ersatzspieler | Einmal `opponentLeft`, Slot frei, Runde zurückgesetzt; erneuter Spielstart | lokal geprüft |
| 3 · Eigene Nachrichten dokumentiert | Richtung, Anlass, Beispiele und ungefragte Zustellung für die drei Lobbymeldungen | geprüft |
| 2/3 · Erwartungen vor Ausführung aufschreiben | [Erwartungen](../evidence/03_expected_results.md) vor der erneuten Prüfung angelegt | für neuen Prüflauf erfüllt |
| 3 · Server und zwei fremde Clients, Ausgaben abgeben | Lokale Ausgaben vorhanden; zwei echte fremde Adressen fehlen | offen, Schulnetzversuch |

Im eigenen Protokoll sind A/B wiederverwendbare Plätze. Eine dauerhaft hochzählende Nummer aus dem Kursbeispiel ist hier nicht das Identitätsmodell. Der Ausgangsserver hatte bereits Threads; die Blockierung des alten sequentiellen Beispiels wird deshalb nicht als beobachtetes Projektverhalten behauptet.

## Zukünftige Aufgaben

| Phase | Noch verlangte Arbeit | Bereits vorhandene Grundlage |
|---|---|---|
| M4 · Server | Gefilterte Zustandsmeldungen nach Platzierung/Schuss an beide; zwei Konsolenclients spielen eine komplette Partie; reproduzierbarer Testspieler | Spielkern, Server, `play.py`, vollständige Netzwerk-Spieltests, Abbruch und Sperre |
| M5 · Robustheit | Konsolenspiel abschliessen; sieben Angriffe und unveränderte Zustände prüfen; Testprotokoll mit Datum führen | Sieben Fälle bereits automatisiert geprüft und tabellarisch dokumentiert |
| M6 · Oberfläche | Zwei grafische Clients, Empfangsqueue, UI nur im Hauptthread, sichtbare Fehler/Zugfolge/Abbruch, eigenes Bild mit Herkunft | M1-Skizze und bestehendes Protokoll |
| M7 · Fremdtest | Vollständige Partie auf mindestens drei Rechnern; Zeitstempel und Mitschnitt; nur anhand des Protokolls gebauter Fremdclient, gegenseitiger Test | Konfigurierbare Adresse/Port, Wartezimmer, gewählte Abbruchregel |
| M8 · Abgabe | Vollständiger Bericht, Architektur und Protokoll begründen, Sperren erklären, Test-/Fremdtestergebnisse, KI-Erklärung und Reflexion | README, Regeln, Katalog, Journal und lokale Nachweise |
| M8 · Vorführung | Ganze Partie, sichtbare Ablehnung eines ungültigen Zugs, harter Abbruch; Fragen zum Code beantworten | Lokal geprüfte Abläufe, externe Vorführung noch offen |

## Ergebnis

Die lokal vorbereitbaren Anforderungen bis M3 sind umgesetzt und geprüft. **Bis M3 ist insgesamt noch nicht alles abgeschlossen:** Lesepartnerschaft, Gegenlesen, manuelle Zweipersonenpartie und Versuche mit fremden Rechnern fehlen. Die Suche in den Kursordnern fand dafür keine vorhandenen Textnachweise; alle tatsächlichen gespeicherten Client-Adressen sind Loopback-Adressen.

Ergebnisse der erneuten Prüfung stehen in [03_followup_output.md](../evidence/03_followup_output.md). Die [Schulnetz-Checkliste](../evidence/03_school_network_checklist.md) führt die noch zu sammelnden Dateien auf.
