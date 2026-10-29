# Kursmeilenstein 3 — lokale Prüfung

Datum: 13.10.2026. Umgebung: macOS, Python 3.15.0, Standardbibliothek.
Ausgangsstand: `a23f73e43964d106fd2289ac27a863be666d2f34`, identisch mit dem bei Arbeitsbeginn gelesenen [GitHub-Stand](https://github.com/SUDOGODMODE/Game_Project_Programming3/commit/a23f73e43964d106fd2289ac27a863be666d2f34).

## Umfang

Geprüft wurden die vier Fälle aus [«Zwei Spieler, ein Tisch»](../assignments/03_two_players.txt), Abgänge per `q` und Prozessabbruch, Ersatzbeitritt, gleichzeitige Beitritte sowie Regressionen für Spielkern und vorhandene Spielaktionen. Alle Verbindungen dieses Nachweises liefen auf `127.0.0.1`. Der geforderte Versuch mit zwei fremden Client-Rechnern im Schulnetz steht noch aus; die Vorbereitung liegt in [03_school_network_checklist.md](03_school_network_checklist.md).

Im bisherigen Repository gab es bereits Threads pro Verbindung. Das sequentielle Serverproblem aus Schritt 1 der Kursvorlage trifft daher auf diesen Ausgangsstand nicht zu. Der vorher ausgeführte Beitrittstest zeigte stattdessen: `welcome` kam an, die anschliessende `waiting`-Meldung fehlte. Auch `gameStart` an den untätigen ersten Spieler war im Ausgangsstand nicht vorhanden.

## Echte Terminalausgaben

Server und Clients wurden als eigene Prozesse gestartet. Der lokale Versuch verwendete den freien Port **59659**, ohne den Standardport 5000 im Code zu ändern.

| Datei | Aufgezeichneter Ablauf |
|---|---|
| [Server](03_server_output.txt) | Annahme aller Verbindungen, eingehende Nachrichten mit Adresse, ausgehende Meldungen mit Slot, Abgänge und Weiterbetrieb |
| [Alice](03_alice_output.txt) | `welcome`, `waiting`, beide Spielstarts und beide Abgangsmeldungen; Alice sendet nach `join` keine weitere Anfrage |
| [Bob](03_bob_output.txt) | Zweiter Beitritt, `welcome`, `gameStart`; anschliessend `q` |
| [Carol](03_carol_output.txt) | Dritter Beitritt mit `GAME_FULL`; danach `q` |
| [Dave](03_dave_output.txt) | Ersatzbeitritt auf Slot B; danach harter Prozessabbruch |
| [Handshake-Angriffe](03_attack_output.txt) | Fehlerhafte Typen, fehlender Name, Doppelbeitritt, ungültiges JSON und JSON-Liste |
| [Testsuite](03_test_output.txt) | Unveränderte Ausgabe der drei dokumentierten Testbefehle |

Die Eingabe von `q` wurde über die Standardeingabe des jeweiligen Prozesses geschickt. Dave wurde mit einem harten Prozessabbruch beendet. Sein Log endet daher ohne die abschliessende Zeile «Verbindung beendet»; Alices Log und das Serverlog zeigen die erkannte Trennung.

| Fall | Erwartet | Beobachtet |
|---|---|---|
| 1 · Alice allein | `welcome` mit A, danach `waiting` | beide Meldungen in Alices Log |
| 2 · Bob tritt bei | Bob erhält `welcome`; beide erhalten denselben `gameStart` | identische Namen/Slots A und B in beiden Logs |
| 3 · Carol tritt bei | Ablehnung, bestehende Spieler bleiben verbunden | `error/GAME_FULL`; Alice und Bob erhalten keine Abgangsmeldung für Carol |
| 4a · Bob beendet mit q | genau einmal `opponentLeft` an Alice | Slot B, Name Bob; Server nimmt danach Dave an |
| 4b · Dave wird hart beendet | genau einmal `opponentLeft` an Alice | Slot B, Name Dave; Server läuft bis zum kontrollierten Ende weiter |
| Ersatzbeitritt | freier Slot B, neuer Spielstart an beide | Dave erhält B; Alice und Dave erhalten `gameStart` mit dem neuen Namen |

## Automatisierte Prüfungen

```bash
python3 src/test_board.py
python3 src/test_game.py
python3 src/test_network.py
```

Ergebnis: **47 Prüfungen bestanden** — 9 Bretttests, 12 Spielkern-Tests und 26 TCP-/CLI-Tests. Die vollständige Ausgabe steht in [03_test_output.txt](03_test_output.txt).

Zusätzlich geprüft: Übersetzen aller Python-Dateien mit `python3 -m compileall -q src`, `git diff --check`, unverändertes `netz.py` und unveränderte historische Nachweise. Die Beispiele im lesbaren und im strukturierten Protokoll stimmen mit dem lokalen Code überein.

Die Netzwerkprüfungen umfassen auch die Freigabe von Slot A, sechs gleichzeitige Beitritte mit genau zwei zugelassenen Spielern, eine komplette Partie, Privatsphäre bei `getState`, einen Abbruch gleichzeitig mit einem Schuss und eine neue Partie nach einem bereits beendeten Spiel. Die Konsolenskripte können ohne Netzwerkzugriff oder Tastatureingabe importiert werden. `play.py` platziert nach `gameStart` und erneut nach einem Ersatzbeitritt; der Angriffstest ordnet ungefragte Lobbymeldungen korrekt ein.

## Sieben Pflichtangriffe aus dem Projektablauf

Die Tabelle bezieht sich auf die ausgeführten Fälle in [test_network.py](../../tests/meilenstein_03/test_network.py). Je Fall werden auch weitere Anfragen beziehungsweise der Zustand geprüft, damit eine Ablehnung allein keinen unbeachteten Verbindungsabbruch verdeckt.

| Nr. | Angriff | Erwartet | Beobachtet | Ergebnis |
|---|---|---|---|---|
| 1 | ungültige JSON-Zeile bei angemeldetem Spieler | Ablehnung; Server und Verbindung bleiben verwendbar | `INVALID_JSON`, unveränderter Zustand, nächster gültiger Schuss erfolgreich | bestanden |
| 2 | `shoot.field` als Zahl, null, Liste, Objekt oder bool | Ablehnung ohne Zustandsänderung | `CELL_OUT_OF_BOUNDS`, Zug und Schüsse unverändert | bestanden |
| 3 | Feld K1, A0, A11 oder leer | Ablehnung ausserhalb des Rasters | `CELL_OUT_OF_BOUNDS`, Zug und Schüsse unverändert | bestanden |
| 4 | `shoot` ohne `field` | Ablehnung; nächste korrekte Anfrage funktioniert | `CELL_OUT_OF_BOUNDS`, danach gültiger Treffer | bestanden |
| 5 | unbekannter Typ `grantVictory` | Ablehnung; kein erfundener Gewinner | `UNKNOWN_TYPE`, Gewinner und Zustand unverändert | bestanden |
| 6 | Bob schiesst, während A am Zug ist | Ablehnung; keine Beschädigung der Flotte | `NOT_YOUR_TURN`, Trefferlisten bleiben leer | bestanden |
| 7 | Gegner trennt Verbindung gleichzeitig mit einem Schuss | einmalige Meldung, kein Absturz, sauberer Zustand | `opponentLeft`, danach per `getState` die Phase `waiting` mit leeren Flotten/Schüssen | bestanden |

Bei Fall 7 hängt die Antwort auf den gleichzeitig gesendeten Schuss von der Reihenfolge der beiden Threads ab: Entweder war der Schuss vor der Trennung gültig, oder er wird nach dem Reset mit `WRONG_PHASE` abgelehnt. In beiden Fällen endet der verbleibende Client im selben leeren Wartezustand.

## Übergabe

Der lokale Funktionsnachweis ist abgeschlossen. Für die Abgabe dieses Kursmeilensteins fehlen noch die Server- und Clientausgaben von zwei fremden Rechnern im Schulnetz. Fachliche Durchsicht, reale Lesepartnerschaft und die weiteren Projektphasen bleiben im [README](../../README.md) aufgeführt. Alle Änderungen liegen lokal und uncommittet vor.


Hinweis zum Strukturumzug vom 27.10.2026: Der Link auf den Testcode folgt
jetzt dem Ordner `tests/meilenstein_03/`. Die damaligen Ergebnisse und
zugehörigen Rohlogs wurden nicht verändert.
