# Kursmeilenstein 4: Das Brett auf dem Bildschirm

## Auftrag und Grenzen

Massgebend sind die drei neuen Word-Unterlagen, textgetreu ausgelesen unter
`docs/assignments/04_*.txt`. Kursaufgabe 4 entspricht in Teilen M4 und M6
des älteren Projektablaufs. Bestehende Regeln und Konsolenprogramme bleiben
erhalten. Beauftragt sind lokale Implementierung, Tests, Dokumentation und
Anforderungsabgleich; keine Commits, Pushes oder GitHub-Änderungen.

## Verhalten

- Der Server entscheidet über Platzierung, Zugfolge, Feldgrenzen und
  Doppelbeschuss. Ablehnungen erhalten nur die jeweiligen Absender.
- Nach Beitritt, gültiger Platzierung, gültigem Schuss und Partierücksetzung
  erhalten alle verbundenen Spieler ihre vollständige erlaubte Sicht.
- `shoot` und `state` sind die bereits bestehenden Entsprechungen von
  `move` und `state` aus dem Unterrichtsbeispiel. Keine zweite Zugnachricht.
- Der Zustand enthält `phase`, `turn`, `ownShips`, `shotsAtOpponent`,
  zusätzlich `shotsAtSelf` (alle gegnerischen Schüsse auf das eigene Raster),
  sowie `winner`. Keine unbeschossene Gegnerposition verlässt dessen Sicht.
- Serverlogs enthalten Nachrichtentyp, Verbindung/Slot und Fehlercode,
  keine Flotten oder vollständigen personalisierten Zustände.
- `client_gui.py` zeigt eigene Flotte und Zielraster mit Koordinaten A–J,
  1–10, Statuszeile, verständlicher Legende und Platzierungsbedienung.
- Eine schlichte Flottenvorlage kann vor dem Senden verschoben/gedreht
  werden; die verbindliche Flotte erscheint erst nach Serverbestätigung.
  Der Gegner darf die Vorlage nicht aus einem festen Automatismus kennen.
- Klicks schicken ausschliesslich Anfragen. Eine Zeichenfunktion setzt bei
  jeder Zustandsnachricht alle Rasterfelder vollständig. Empfangs- und
  Sendearbeit laufen ausserhalb des Tk-Threads; Queues und `after` verbinden
  Netzwerk und Oberfläche. Keine Widgetzugriffe aus Arbeitsthreads.
- Fensterkreuz beendet Verbindung und Prozess; Gegner sieht Abbruch und
  leeres Raster. Ersatzbeitritt startet eine neue Platzierungsphase.
- `netz.py` behandelt harte Verbindungsabbrüche als Ende des Lesers.

## Technische Entscheidungen

Python >=3.12, Standardbibliothek und tkinter; keine neuen Laufzeitpakete.
CLI wie bestehende Clients: Host, Name und `--port` (Standard 5000).
Kein neuer Regelkern und keine Löschung vorhandener Funktionen.
GUI-Bedienung und Integration werden mit echtem Tk geprüft, nicht nur mit
Widgetattrappen. Fehlende Tk-Installation wird im Setup erklärt.

Die Raster zweier Spieler zeigen denselben öffentlichen Verlauf und
Zugstatus, aber absichtlich unterschiedliche geheime eigene Flotten.
Die Originalunterlagen und historischen Nachweise bleiben unverändert.

## Nachweise

Neue, getrennte Rohlogs für Tests, vollständige lokale TCP-Partie,
Ablehnungen und Prüfung der geheimen Information; echter Screenshot mit
zwei GUI-Fenstern nach demselben Zug. Automatisierte lokale Versuche werden
als solche bezeichnet. Die geforderte Schulnetz-Topologie besteht aus
Server und zwei anderen Clientrechnern; zwei verschiedene fremde IPs und
Mitspieler können hier nicht durch Loopback ersetzt werden. Dieser Nachweis
bleibt bis zum tatsächlichen Versuch offen. Die separat erwähnte Vorbereitung
«Das Brett in den Server» ist inhaltlich durch Schritt 1 und 2 der vorhandenen
Anleitung abgedeckt; nach Benutzerantwort und Quellenabgleich keine
blockierende Unterlagenlücke.

## Ergänzter Benutzerauftrag

Tests nach `tests/meilenstein_XX/` verlagern, gemischte Werkzeugtests sinnvoll
aufteilen, gemeinsame Testausführung anbieten und alle aktuellen Pfade
sowie README, Bedienungs-, Architektur- und Testanleitungen aktualisieren.
Die Spielwahl Schiffe versenken bestimmt Darstellung und Bedienung.
