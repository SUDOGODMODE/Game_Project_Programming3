# Gesicherter Ausgangsstand und Rollback

Vor den bewertungsbezogenen Verbesserungen am 27.10.2026 um 17:33 Uhr MEZ
wurde die unveränderte Arbeitskopie gesichert:

```text
/Users/max/Desktop/Gaming_Backups/Schiffe_versenken_vor_Bewertungsverbesserung_2026-10-27_17-33-09.zip
SHA256: bdcaf95c318fd800da0d82bf8cfa3847664030b2fc5cc342440df4c7084a2129
```

Die ZIP enthält 2’532 Einträge: Projekt einschliesslich Git-Metadaten,
uncommittierter Änderungen, lokaler Venv, Tests, Dokumentation und Nachweise
sowie den benachbarten Originalordner `Dokumente`. Die Sicherung liegt
ausserhalb des Repositorys und wird von weiteren Projektänderungen nicht
aktualisiert. Sie ist eine lokale Rollback-Kopie auf demselben Gerät.

**Tatsächlich geprüft:** ZIP-CRC, vollständiges Entpacken in einen separaten
temporären Ordner, SHA256 jeder Datei und jedes symbolischen Links,
identischer Git-Arbeitsstand und Import des wiederhergestellten Spielkerns.
Die Prüfbestätigung steht neben der ZIP in der Datei mit Endung
`.verification.json`, die Archivprüfsumme in `.zip.sha256`.

## Sicher wiederherstellen

Zuerst die Archivprüfsumme mit der obigen vergleichen:

```bash
shasum -a 256 /Users/max/Desktop/Gaming_Backups/Schiffe_versenken_vor_Bewertungsverbesserung_2026-10-27_17-33-09.zip
```

Dann ausschliesslich in einen **neuen, noch nicht existierenden Ordner**
wiederherstellen:

```bash
python3 /Users/max/Desktop/Gaming_Backups/restore_rollback.py /Users/max/Desktop/Gaming_Backups/Schiffe_versenken_vor_Bewertungsverbesserung_2026-10-27_17-33-09.zip /Users/max/Desktop/Schiffe_versenken_Restore_2026-10-27
```

Das mitgesicherte Wiederherstellungsprogramm verweigert bestehende Ziele
und prüft alle Dateiinhalte anhand des Manifests. Der Projektordner liegt
danach unter `Projekt/Game_Project_Programming3`, die Unterlagen unter
`Projekt/Dokumente`. Erst vergleichen; beim eigentlichen Rollback den
aktuellen Projektordner erhalten und umbenennen, statt blind darüber zu
entpacken. Der Rollback wurde hier nur im isolierten Ziel geprüft, nicht
auf die laufende Arbeitskopie angewendet.

Die gesicherte Venv verweist auf den installierten Python-Interpreter.
An einem anderen Pfad oder mit anderer Python-Installation eine neue Venv
mit Python >=3.12 und tkinter erstellen. Die systemweite Python-/Tk-
Installation selbst ist nicht in dieser ZIP enthalten.
