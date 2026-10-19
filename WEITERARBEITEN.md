# Projektstand für die nächste Arbeitseinheit

Gesichert am 13.10.2026, Europe/Zurich.

## Projekt und Arbeitsweise

- Projekt: Schiffe versenken, Programming 3 an der HFTM, Max Rufener.
- Repository: `/Users/max/Desktop/Shared_Folder_Desktop/Fachstudium/Programming3/Projekt/Game_Project_Programming3`.
- Origin: `https://github.com/SUDOGODMODE/Game_Project_Programming3.git`.
- Letzter geprüfter HEAD: `a23f73e43964d106fd2289ac27a863be666d2f34`. Zu Beginn der Arbeit stimmte er mit GitHub überein.
- Die Änderungen sind noch nicht committet. Beim Sichern waren die bisherigen Projektänderungen bereits gestagt. Vor weiteren Änderungen den aktuellen Status neu lesen und den Index erhalten.
- Nur lokale Änderungen; abschliessende Git-Schritte übernimmt der Projektverantwortliche.
- Spielwahl Schiffe versenken ausdrücklich bestätigt. Bisher hat niemand Regeln oder Protokoll gegengelesen.

## Zwei Nummerierungen

1. `docs/assignments/project_flow.txt`: M0 Werkzeuge/Echo, M1 Spielwahl/Regeln, M2 Spielkern ohne Netz, M3 Protokoll, danach M4–M8.
2. Einzelaufgaben: `02_first_handshake.txt` ist «Der erste Handschlag»; `03_two_players.txt` ist «Zwei Spieler, ein Tisch».

Der letzte Auftrag umfasste beide Nummerierungen bis einschliesslich M3. Eine neue Meilenstein-Datei ist vor weiterer Umsetzung gegen den Projektablauf abzugleichen.

## Umgesetzt

- `board.BattleshipGame`: netzunabhängige Regeln, Phasen, Flottenprüfung, Zugfolge, Treffer, Sieg und gefilterte Zustandskopien.
- `server.py`: ein Thread pro Verbindung; gemeinsame Sperre um Prüfen, Ändern und Senden. Zwei Plätze A/B, `waiting`, `gameStart`, Ablehnung eines dritten Spielers und `opponentLeft`.
- `client.py`: dauerhafter Empfangsthread, Eingabeschleife, q beendet; Host, Name und Port konfigurierbar.
- `play.py`: vorhandener Netzwerk-Spielclient, setzt Standardflotte nach `gameStart` und nach Ersatzbeitritt erneut. `state` fragt den Zustand ab.
- `test_angriff.py`: begründete Fehler geprüft; ungefragte Lobbymeldungen verschieben die Antwortzuordnung nicht.
- `echo_server.py` / `echo_client.py`: M0-Grundversuch mit vollständigem Lesen langer Antworten.
- `local_game.py`: vollständige Zweipersonenpartie an einer Tastatur ohne Netzwerk, Platzierung und Schüsse über den Kern.
- `REGELN.md`: Regeln, ungültige Aktionen, Ende, Zugunfähigkeit, Abbruch und Oberflächenskizze.
- `PROTOKOLL.md` / `docs/protocol/protocol.json`: Version 0.4, 14 einzelne Typen und vollständiger Partieablauf.
- README, Journal, Anforderungsabgleich, Erwartungen vor dem erneuten Prüflauf und echte lokale Rohlogs vorhanden.
- `netz.py`, ursprüngliche Aufgabenstellungen und historische Nachweise unverändert.

## Festgelegte Entscheidungen

- Raster 10 × 10, fünf Schiffe mit Grössen 5/4/3/3/2; je ein Carrier, Battleship, Cruiser, Submarine und Destroyer.
- A beginnt nach beiden gültigen Platzierungen. Jeder gültige Schuss wechselt den Spieler; Treffer geben keinen Extrazug.
- Koordinaten werden vereinheitlicht; beispielsweise bezeichnet `a01` dasselbe Feld wie A1 und erlaubt keinen Doppelbeschuss.
- Abgang: Platz sofort freigeben, beide Flotten/Schüsse/Ergebnis zurücksetzen. Ersatzspieler beginnt eine neue Partie. Diese Regel ersetzt die ältere Idee von 30 Sekunden Wartefrist und Aufgabe aus dem Vorschlag.
- `state` ist derzeit eine Antwort auf `getState`. Automatische gefilterte Zustände nach Spielaktionen fehlen noch und gehören zur weiteren Serverphase M4.
- `gameOver` wird bei versenkter Flotte an den Verlierer gesendet; der Gewinner erkennt das Ende an `result.turn == null`.
- Standardport 5000, Ersatzport 5100 bei Belegung; Server und Clients verwenden denselben Port.

## Verifikation und Start

Vorhandene `.venv`: Python 3.14.8, nur Standardbibliothek. Letzter vollständiger Prüflauf: **57 bestanden**, keine Fehler oder übersprungenen Tests — 9 Brett-, 12 Kern-, 26 Netzwerk-/CLI-, 5 Transport- und 5 Werkzeugtests. Erste Prüfung zusätzlich unter Python 3.15.0.

```bash
.venv/bin/python src/test_board.py
.venv/bin/python src/test_game.py
.venv/bin/python src/test_transport.py
.venv/bin/python src/test_tools.py
.venv/bin/python src/test_network.py
```

Netzwerktests öffnen lokale TCP-Ports. In der bisherigen Sandbox war dafür eine gezielte Freigabe nötig; ein Bind-Verbot ist nicht mit einem Programmfehler gleichzusetzen.

```bash
# Drei Terminals für den Lobbyversuch
.venv/bin/python -u src/server.py --port 5100
.venv/bin/python -u src/client.py 127.0.0.1 Alice --port 5100
.venv/bin/python -u src/client.py 127.0.0.1 Bob --port 5100
```

Aktuelle Nachweise: `docs/evidence/03_followup_output.md` und Rohdateien unter `docs/evidence/03_followup/`. Ergebnisse nicht mit einem neuen Prüflauf überschreiben; neue Ausgaben separat ablegen.

## Noch notwendig bis M3

- Lesepartnerschaft vereinbaren und Regeln sowie Protokoll gegenlesen lassen; tatsächliche Person und Ergebnis eintragen.
- Vollständige Partie mit zwei Personen an einer Tastatur durchführen.
- Echo und Handschlag über fremde Rechner ausprobieren, danach die Rollen tauschen.
- Server auf einem Rechner, zwei Clients auf zwei anderen Rechnern: zwei unterschiedliche fremde Adressen und Spielstart-Ausgaben beider Clients sammeln.

Die Suche in den vorhandenen Kursordnern fand keine entsprechenden alten Nachweise. Alle gespeicherten tatsächlichen Client-Adressen sind `127.0.0.1`. Die lokale Technik ist vorbereitet; die gesamten Anforderungen bis M3 sind deshalb noch nicht abgeschlossen.

## Abgabepaket

`/Users/max/Desktop/Meilenstein_3.zip`, geprüft, 16 Dateien. Enthalten sind die drei verlangten Programme plus `board.py`, Protokoll, Regelblatt, Aufgabenstellung, lokale Lobby-Ausgaben, eine paketbezogene README und Schulnetz-Checkliste. Der fehlende Fremdrechner-Nachweis ist ausdrücklich gekennzeichnet.

SHA256: `7623a94f6d5edb0affdf4bf9d1fa0a8b297a802de09f00dfce9cfe7b3cdb52a0`.

Eine identische Arbeitskopie liegt unter `/Users/max/Desktop/Shared_Folder_Desktop/Meilenstein_3.zip`. Das ZIP ist ein Zeitpunktpaket; spätere Projektänderungen aktualisieren es nicht automatisch.

## Nächste technische Schritte nach neuem Auftrag

M4: gefilterte Zustandsmeldungen nach Platzierung und Schuss an beide Clients, vollständige Konsolenpartie und reproduzierbare Testspieler. Danach M5 Robustheit, M6 GUI, M7 Fremdtest und zeitgestempelte Logs, M8 Bericht und Demo. Keine dieser späteren Aufgaben ist allein durch diesen Projektstand beauftragt.

Detailabgleich: `docs/status/03_requirements.md`. Weitere Entscheidungen und Arbeitseinheiten stehen in `journal.md`.
