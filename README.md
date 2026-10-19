# Schiffe versenken

Projekt im Modul Programming 3 an der HFTM, Max Rufener. Zwei Spieler verbinden sich mit einem zentralen Server. Der Server prüft alle Aktionen; jeder Client erhält nur seine eigene Spielersicht.

## Stand

Schiffe versenken ist als Spielwahl freigegeben. Der aktuelle Kursmeilenstein **«Zwei Spieler, ein Tisch»** ist lokal umgesetzt und geprüft. Die Versuche mit fremden Rechnern und das Gegenlesen stehen noch aus.

Die Unterlagen verwenden zwei Nummerierungen: Im [Projektablauf](docs/assignments/project_flow.txt) bedeutet M3 «Das Protokoll». Die einzelne [Kursaufgabe 3](docs/assignments/03_two_players.txt) verlangt zwei gleichzeitig verbundene Spieler. Der [Anforderungsabgleich](docs/status/03_requirements.md) berücksichtigt beide.

| Projektphase | Stand |
|---|---|
| M0 · Werkzeuge / Echo | Repository, virtuelle Umgebung und lokal getestete Echo-Programme vorhanden; Netzwerkversuch mit Rollenwechsel offen |
| M1 · Spielwahl / Regeln | Spielwahl freigegeben, Formular vorhanden; [Regelblatt und Oberflächenskizze](REGELN.md) ergänzt, Gegenlesen offen |
| M2 · Kern ohne Netz | `BattleshipGame`, Tests und `local_game.py` vorhanden; vollständige Partie mit zwei Personen noch durchzuführen |
| M3 · Protokoll | 14 Nachrichtentypen mit Feldern, Beispielen und vollständigem Partieablauf; Gegenlesen offen |
| Kursaufgabe 2 · Handschlag | Eigene Beitrittsnachrichten und Angriffstest geprüft; Versuch mit fremdem Rechner und Rollenwechsel offen |
| Kursaufgabe 3 · Zwei Spieler | Warten, Spielstart, Ablehnung des dritten Spielers, Abbruch und Ersatzbeitritt lokal geprüft; Schulnetz-Nachweis offen |
| M4–M5 · Server / Robustheit | Spielserver, Konsolenclient und Angriffstests bereits vorhanden; Zustandsmeldungen nach jedem Spielzug fehlen noch |
| M6–M8 · Oberfläche / Fremdtest / Abgabe | offen; Einzelaufgaben im Anforderungsabgleich |

Bis M3 fehlen noch diese praktischen Nachweise:

- Eine feste Lesepartnerschaft vereinbaren (Eintrag: `<lesepartner_name>`); Regeln und Protokoll gegenlesen lassen und Ergebnis festhalten.
- Eine vollständige Partie mit zwei Personen an einer Tastatur spielen.
- Echo und Handschlag über zwei Rechner ausprobieren, danach die Rollen tauschen.
- Den Spielserver mit zwei fremden Client-Rechnern testen; die Ausgaben müssen zwei unterschiedliche Client-Adressen und den Spielstart bei beiden zeigen.

## Einrichtung

Python **3.12 oder neuer**, nur Standardbibliothek. Die vorhandene Projektumgebung läuft mit Python 3.14.8. Die erste Prüfung verwendete zusätzlich Python 3.15.0.

```bash
python3 -m venv .venv          # nur wenn noch keine Umgebung vorhanden ist
source .venv/bin/activate     # macOS / Linux
# Windows: .venv\Scripts\activate
python --version
```

Alle folgenden Befehle werden im Repository-Verzeichnis ausgeführt.

## Start und Bedienung

Für M0, in zwei Terminals:

```bash
python src/echo_server.py --port 5100
python src/echo_client.py 127.0.0.1 --port 5100
```

Der Client zeigt `Antwort: HALLO NETZ`. Für einen fremden Rechner die tatsächliche Server-IP einsetzen:

```bash
python src/echo_client.py "<server_ip>" --port "<tcp_port>"
```

`<server_ip>` und `<tcp_port>` vor dem Start ersetzen; danach die Rollen tauschen. Platzhalter haben in dieser Dokumentation die Form `<beispiel_art>`.

Für M2, ohne Server:

```bash
python src/local_game.py
```

A und B setzen nacheinander ihre Flotte, je Schiff beispielsweise `A1 h`. Danach werden Feldkoordinaten für die Schüsse eingegeben. q beendet die Partie. Bei der Tastaturübergabe verdeckt das Terminal die bisherige Anzeige; der andere Spieler sollte während der Platzierung nicht mitlesen.

Für die aktuelle Kursaufgabe, in drei Terminals:

```bash
python -u src/server.py --port 5100
python -u src/client.py 127.0.0.1 Alice --port 5100
python -u src/client.py 127.0.0.1 Bob --port 5100
```

Alice erhält `welcome` und `waiting`. Nach Bobs Beitritt erhalten beide `gameStart`. Ein dritter Spieler erhält `GAME_FULL`. Mit q wird der Platz frei und der Gegner erhält `opponentLeft`.

Für eine Netzwerkpartie `play.py` statt `client.py` starten. Die Standardflotte wird nach `gameStart` gesetzt. Eine Feldkoordinate schiesst, `state` fragt den aktuellen Zustand ab, `quit` oder q beendet. Zustände nach gewöhnlichen Spielzügen müssen derzeit abgefragt werden; automatische Zustandsmeldungen gehören zur weiteren Serverarbeit.

Alle Netzwerkprogramme verwenden standardmässig Port 5000. Die Beispiele nutzen 5100, falls 5000 auf macOS durch AirPlay belegt ist. Server und Clients müssen denselben Port verwenden. Der Server hört standardmässig auf `0.0.0.0`; für einen ausschliesslich lokalen Versuch ist `--host 127.0.0.1` möglich.

## Code und Unterlagen

- `board.py`: Spielkern, Regeln und gefilterte Kopien des Zustands; keine Netzabhängigkeit.
- `netz.py`: UTF-8-JSON-Zeilen über TCP; unverändert gegenüber dem Ausgangsstand.
- `server.py`: Verbindungen, Spielerzuordnung und Sendungen; eine gemeinsame Sperre umfasst Prüfen, Ändern und Senden.
- `client.py`: dauerhafter Lobbyclient mit Empfangsthread.
- `play.py`: vorhandener Netzwerkclient zum Spielen.
- `local_game.py`: Partie an einer Tastatur ohne Netz.
- `echo_server.py` / `echo_client.py`: Grundversuch aus M0, ohne Spielprotokoll.
- [REGELN.md](REGELN.md): Regeln, Abbruchentscheidung und Skizze.
- [PROTOKOLL.md](PROTOKOLL.md) / [protocol.json](docs/protocol/protocol.json): lesbarer und strukturierter Nachrichtenkatalog.
- `docs/assignments/`: unveränderte Kopien der Aufgabenstellungen; ursprüngliche Formulare liegen unter `Projekt/Dokumente/`.
- [journal.md](journal.md): Arbeitsschritte und offene Punkte.

Beim Netzwerkabbruch wird die gesamte Partie zurückgesetzt. Der nächste Gegner beginnt eine neue Partie. Diese aktuelle Regel ersetzt die Wartefrist mit Aufgabe aus dem ursprünglichen Vorschlag; Details stehen im Regelblatt.

## Tests und Nachweise

```bash
python src/test_board.py
python src/test_game.py
python src/test_transport.py
python src/test_tools.py
python src/test_network.py
```

Den Handshake-Angriffstest auf einem frischen, separat gestarteten Server ausführen:

```bash
python src/test_angriff.py 127.0.0.1 --port 5100
```

Die [erste lokale Prüfung](docs/evidence/03_local_output.md) enthält 47 bestandene Tests und Terminalausgaben. Der [ergänzte Prüflauf](docs/evidence/03_followup_output.md) enthält **57 bestandene Tests** und die Ergebnisse für Echo, lokale Partie und Transport sowie die erneute Gesamtprüfung. Historische Nachweise bleiben unverändert.

Die [Schulnetz-Checkliste](docs/evidence/03_school_network_checklist.md) beschreibt die noch durchzuführenden Versuche. Lokale Prüfungen sind kein Nachweis für einen Versuch mit fremden Rechnern.
