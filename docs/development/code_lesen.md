# Code lesen: ein Weg durch das Spiel

Diese Reihenfolge beginnt beim einfachen Spiel ohne Netzwerk. Lies zuerst
`REGELN.md` und probiere danach `python3 tools/run_tests.py --core`.

## 1. Regeln und Zustand

`src/spiel.py` ist die wichtigste Datei. Die freien Funktionen prüfen
Koordinaten und Flotten; `BattleshipGame` hält Phase, Spieler, Schiffe und
Schüsse. `place_fleet()` und `shoot()` prüfen eine Anfrage, bevor sie den
Zustand ändern. `state(slot)` baut eine neue, gefilterte Sicht für genau
einen Spieler. Beginne mit den Tests in `tests/core/test_game.py`.
`src/board.py` ist nur ein alter Importname für denselben Kern.

## 2. Von der Nachricht zur Spielaktion

`src/netz.py` sendet und liest je eine JSON-Nachricht pro Zeile. Der Server
in `src/server.py` ordnet eine Verbindung dem Platz A oder B zu. Unter der
Spielsperre übersetzt `process()` eine Nachricht in eine Spielaktion;
`handle()` schickt die direkte Antwort und anschließend die erlaubten
Zustände. Beim Sieg folgt nach beiden Endzuständen `gameOver`. Die Tests in
`tests/network/` und `tests/gui/test_server_states.py`
zeigen diese Reihenfolge mit echten beziehungsweise kontrollierten Sockets.

## 3. Was die beiden Clients sehen

`src/client_gui.py` sendet Klicks als Anfragen. Empfangene Nachrichten
landen zunächst in einer Queue; Tk verarbeitet sie im Hauptthread.
`draw_state()` zeichnet das eigene und das Zielbrett erst nach einem
bestätigten `state` vollständig neu. `src/gui/client_view.py` berechnet die
Zeichen ohne Tk. `src/fleet_setup.py` erstellt einen gültigen Vorschlag für
die Platzierungsfelder; die Entscheidung über eine Platzierung trifft der
Server. Die Konsole in `src/play.py` ist ein zweiter Client für denselben
Server; `src/local_game.py` nutzt nur den Spielkern an einer Tastatur.

## 4. Bilder, Effekte und Nachweise

`src/gui/sea_cell.py` zeichnet ein Rasterfeld. `src/gui/ship_art.py` liest die fünf
SVG-Schiffe, `src/gui/ship_effects.py` zeichnet die kurze lokale Sprengung nach
einem bestätigten eigenen Schiffsverlust. `src/event_log.py` schreibt nur
Nachrichtenmetadaten; es speichert keine privaten Flotten. Die Werkzeuge in
`tools/` starten Tests, eine vollständige lokale GUI-Partie oder bauen ein
Abgabearchiv. Die Startprofile unter `varianten/` wählen lediglich die
passenden Adressen und Prozesse für ein oder zwei Geräte.

## 5. Eine Änderung prüfen

1. Nach Regeländerungen: `python3 tools/run_tests.py --core`.
2. Danach: `python3 tools/run_tests.py --group <name>` für den Bereich.
3. Vor der Übergabe: `python3 tools/run_tests.py --require-gui` in einer
   grafischen Sitzung mit lokalen TCP-Ports.
4. Nach GUI- oder Netzwerkänderungen zusätzlich eine neue vollständige
   lokale Partie gemäß `docs/development/testing.md` ausführen.

Ein lokaler Test belegt keinen echten Versuch mit zwei fremden Rechnern.
