# Meilenstein 6 Implementation Plan

> **For agentic workers:** Aufgaben getrennt umsetzen, fokussiert prüfen und unabhängig gegenlesen. Keine Commits oder Pushes; der Projektverantwortliche übernimmt Git.

**Goal:** Schiffe versenken mit prozessisolierten echten Netztests und einer nachvollziehbar startbaren M6-Abgabe abschliessen.

**Architecture:** `server.py` behält CLI-Optionen und liest zusätzlich `PORT`. `testclient.py` bildet einen kleinen fensterlosen TCP-Client. `test_netz.py` startet je Test einen Serverprozess, führt Protokollfälle aus und räumt auf. Isolierte Serverkopien dienen ausschliesslich dem Fehlernachweis.

**Tech Stack:** Python 3.12+, Standardbibliothek, `unittest`, TCP/JSON Lines, bestehendes tkinter-Spiel.

**Spec:** [spec.md](spec.md)

## Global Constraints

- Original `Auftrag_Meilenstein6.docx` und ältere Rohbelege unverändert erhalten.
- Tic-Tac-Toe-Lehrfälle fachlich auf `REGELN.md` und `PROTOKOLL.md` übertragen.
- Keine neue Laufzeitabhängigkeit, keine Commits oder Pushes.
- Jeder Nachweis benennt tatsächlichen Umfang und Umgebung.

## Review Focus

- Eigener Serverprozess pro Test; keine verdeckte Server-Importabkürzung.
- Kein starrer Portkonflikt, keine zurückbleibenden Prozesse.
- Keine alten `state`-Nachrichten als Reaktion auf einen neuen Zug auswerten.
- Private gegnerische Flotte und private Ablehnungen bleiben geschützt.
- `unittest discover` läuft im frisch entpackten Paket wirklich durch.

## Tasks

1. Test für `PORT`-Standard/Umgebung/CLI-Priorität schreiben, dann `server.py` ergänzen und gezielt prüfen.
2. `testclient.py` und `test_netz.py` mit 19 oder mehr fachlich passenden Fällen erstellen; alle elf Fehlercodes und komplette Partie prüfen.
3. Original-`discover`-Befehl aus Repository und entpackter Kopie ausführen; notwendige Pfade verständlich und stabil einrichten.
4. Gezielte Fehler in isolierten Serverkopien ausführen, Vorhersage und tatsächliche rote/grüne Rohausgaben sichern.
5. README, M6-Anforderungsabgleich und Übergabe aktualisieren; neue ZIP bauen und entpackt prüfen.
6. Strenge Gesamtsuite und echte lokale GUI/TCP-Demo ausführen; unabhängiger Review und Diffprüfung.
