# Verbesserungen anhand der Gesamtbewertung

## Verbindlicher Umfang

Der Benutzer hat nach der M4-Arbeit ausdrücklich die späteren Phasen bis zur
Endabgabe einbezogen. Ausgangspunkt ist die von Rolle 1 zuerst gelesene
Bewertung: [Anforderungsbericht](../../status/04_rubric_requirements.md).
Die sechs M4-Kriterien bleiben getrennt vom originalen 100-Punkte-Raster.
Keine neue Regelvariante, kein Reconnect-Umbau und keine erfundenen Nachweise.

Vor jeder Änderung wurde ein vollständiges ZIP einschliesslich .git/.venv
und Originalunterlagen erstellt und isoliert wiederhergestellt; siehe
[Rollback](../../guides/rollback.md). Nur lokale Arbeit, keine Git-Operationen
zum Staging/Commit/Push. Frühere Rohlogs und Quellen bleiben erhalten.

## Neue lokale Leistungen

1. **Nachvollziehbare Testabnahme:** `tools/run_tests.py` erhält
   `--require-gui` und `--report-json <neue_datei>`. Der strenge Modus darf
   fehlende/übersprungene GUI-Tests nicht als Erfolg ausgeben. Testklassen
   markieren echte GUI-Prüfungen mit `requires_gui = True`. JSON enthält
   tatsächliche Umgebung, Auswahl, Zeiten, Test-IDs, Ergebnisse, Gründe und
   Gesamtstatus. Klassen-/Subtestereignisse korrekt von ausgeführten Tests
   unterscheiden; keine falschen Summen. Vorhandene Berichte nicht überschreiben.
   Der normale Modus bleibt auch ohne Display benutzbar und benennt Skips.
2. **M6-Bild:** Mindestens ein mit ImageGen erzeugtes transparentes PNG in
   `bilder/` ins Fenster einbinden. Bildreferenz im Tk-Hauptthread halten
   und dort freigeben. Feste Kantenlänge als Zweierpotenz, Darstellung 64/128
   Pixel, Quelle und tatsächliche Erzeugung dokumentieren. Pfade sind vom
   aktuellen Arbeitsverzeichnis unabhängig. Keine Gegnerinformation im Bild.
3. **M7-Nachrichtenlog:** Jede ein-/ausgehende Nachricht mit eindeutigem
   ISO-Zeitstempel persistent protokollieren. JSON-Zeilen mit Richtung,
   Verbindung/Slot, bekanntem Typ und servereigenem Fehlercode genügen;
   keine unbeschossenen Flotten, freien Clienttexte oder ganzen Zustände in
   gemeinsame Logs. Der Server legt standardmässig eine neue Zeitstempeldatei
   unter `logs/` an, `--log-file` erlaubt einen neuen Zielpfad. Getrennte
   Schreibsperre und geschützter Dateilebenszyklus, kein Überschreiben.
   Tests dürfen einen expliziten temporären Logpfad verwenden. Protokoll 0.5
   auf dem Draht bleibt unverändert, Meldungen an Clients bleiben gefiltert.
4. **Abgabebereitschaft:** Technischen Abschlussbericht aus belegbaren Fakten,
   Begründungen, sieben Angriffen und echten Ergebnissen zusammenführen.
   Der Benutzer ergänzt die eigene Reflexion selbst: separate Datei mit
   Leitfragen und klarem README-Hinweis. KI-Einsatz ehrlich offenlegen;
   Eigenverantwortung/Erklärbarkeit, Fremdtest, reale Fremdrechner und
   Gegenlesen bleiben als ausstehende menschliche Leistungen erkennbar.
5. **Prüfbares Abgabepaket:** `tools/build_submission.py --output <neues_zip>`
   erstellt ein lokales Paket mit Code, Bildern, Tests, Anleitungen,
   Protokoll und tatsächlichen Nachweisen, sowie benötigten Originalquellen.
   Keine .git/.venv/Caches/Secrets/lokalen Laufzeitlogs. Quellenlinks zu
   `../Dokumente` bleiben durch passende Paketstruktur auflösbar.
   SHA256-Manifest und offener Abgabestatus enthalten; keine alte Ausgabe
   überschreiben. Entpacktes Paket unabhängig starten und prüfen. Das Paket
   behauptet keine fertige menschliche Endabgabe.

## Rollen und Abnahme

Rolle 1 hat Bewertung und Anforderungen erstellt und prüft abschliessend die
Deckung. Rolle 2 setzt Produktion, Tools, Bild und Anleitungen um. Rolle 3
schreibt neue Verhaltenstests unabhängig, beobachtet die erwarteten roten
Fälle vor Umsetzung, prüft dann neue Funktionen und bestehende Regression
mit echtem Tk/TCP und bewertet die Ergebnisse schriftlich gegen die IDs.
Der Controller koordiniert, sichert und integriert Nachweise; er ersetzt
weder die unabhängige Testrolle noch persönliche Benutzerangaben.

Die sieben Angriffe aus der Quelle werden spielgerecht als neue tatsächliche
Tabelle belegt, ebenso eine Konsolenpartie und eine GUI-Partie mit Logs.
Ein lokaler Erfolg ersetzt keine reale Verteilung oder unabhängigen Fremdclient.
