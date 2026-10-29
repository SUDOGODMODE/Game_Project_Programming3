# Bewertungsbezogene Endabgabe — Implementation Plan

> **For agentic workers:** superpowers:subagent-driven-development; Benutzer verlangt getrennte Anforderungen, Umsetzung und Tests. Keine Commits.

**Goal:** Die lokal erfüllbaren Anforderungen bis zur Endabgabe vollständig belegen und echte verbleibende Lücken sichtbar machen.

**Architecture:** Spielkern und Drahtprotokoll bleiben erhalten. Neue Tools liefern ehrliche Test-/Abgabenachweise; Serverlog und GUI-Bild erfüllen die neu freigegebenen M7-/M6-Pflichten.

**Tech Stack:** Python >=3.12, Standardbibliothek/tkinter, ImageGen nur zur Asset-Erzeugung.

**Spec:** `docs/superpowers/specs/2026-10-27-final-assessment-design.md`

## Global Constraints

- ZIP-Rollback vor Änderungen verifiziert; siehe docs/guides/rollback.md.
- Keine Staging-/Commit-/Push-/GitHub-Operationen, ursprüngliche Quellen und Rohlogs erhalten.
- Aktivierte .venv, aktuelle macOS-Beispiele python3; Windows-Abweichung erklären.
- Keine erfundenen Punkte, Fremdtests, Personen, Reflexionen oder Freigaben.
- Benutzer ergänzt Reflexion selbst; Datei und README-Hinweis sind beauftragt.

## Review Focus

- Ein GUI-Skip darf im strengen Prüfmodus keinen Erfolg erzeugen.
- Zeitstempellogs dürfen weder Flotten offenlegen noch bei parallelem Schreiben beschädigt werden.
- Bildreferenzen dürfen nicht aus Arbeitsthreads freigegeben werden oder von cwd abhängen.
- Tests/Manifeste/ZIP dürfen alte Nachweise nicht überschreiben oder .venv/Secrets aufnehmen.
- Technischer Bericht und Abgabestatus dürfen menschliche Pflichten nicht als erfüllt führen.

### Task 1: Unabhängige rote Abnahmetests

**Owner:** Rolle 3. **Files:** neue fokussierte Tests in tests/meilenstein_04, 06, 07, 08; nur notwendige Markierung/Erweiterung vorhandener GUI-Tests.

- [x] V01/V02: echtes unittest-Verhalten für Erfolg/Fehler/Skip/fehlende GUI und JSON-Konsistenz prüfen; vorhandenen Bericht erhalten.
- [x] END-01/M6-02: reales Tk-Bild laden, Referenz, cwd-Unabhängigkeit und Freigabe prüfen.
- [x] END-01/M7-02: tatsächliche Ein-/Ausgangslogs mit Zeit, vollständige JSON-Zeilen, Privatheit, parallelem Schreiben und vorhandener Zieldatei prüfen.
- [x] V04/END-03/M8-01: Paketvollständigkeit, Ausschlüsse, SHA256 und Überschreibschutz über Dateisystem-/ZIP-Verhalten prüfen.
- [x] Rote Fälle mit Ursache melden, dann Rolle 2 freigeben. Keine Produktionsänderungen in der Testrolle.

### Task 2: Umsetzung nach Kriterien

**Owner:** Rolle 2. **Files:** tools/run_tests.py, tools/build_submission.py, src/event_log.py, src/server.py, src/client_gui.py, bilder/, aktuelle Anleitungen/Bericht/Status.

- [x] Schnittstellen mit Rolle 3 vor Tests abgleichen, getrennte Dateizuständigkeiten erhalten.
- [x] Strenge Abnahme und geschützte JSON-Berichte implementieren.
- [x] ImageGen-PNG erzeugen und mit dokumentierter Herkunft in GUI integrieren.
- [x] Persistente private Metadatenlogs mit ISO-Zeitstempel standardmässig ergänzen.
- [x] Technischen Bericht, eigene Reflexionsdatei als offener Benutzerteil, Demo-/Abnahmeleitfaden und Abgabewerkzeug erstellen.
- [x] README/Setup/Architektur/Protokollbeschreibung des Logverhaltens zusammen aktualisieren; keine Drahtänderung erfinden.

### Task 3: Unabhängige Endprüfung und Abgleich

**Owner:** Rolle 3; Deckungsreview Rolle 1; Controller Integration.

- [x] Neue Tests und komplette Suite im strengen GUI-Modus mit frischem JSON-/Rohbericht ausführen.
- [x] Sieben Pflichtangriffe, ganze Konsolenpartie und echte GUI-/TCP-Partie frisch belegen; Zeitstempellog prüfen.
- [x] Neues Abgabepaket erstellen, in frischem Ziel entpacken, Tests und Starts daraus prüfen.
- [x] Testqualität anhand realer Fehlerfälle/Mutation beurteilen; schriftliches Urteil je Bewertungsbereich mit Grenzen.
- [x] Anforderungen zeilenweise abschliessend prüfen, Dokumentlinks/Quellenkompilierung/ungeänderten Git-Index bestätigen.

## Fortschritt / Entscheidungen

- Anforderungen aus Originalbewertung durch Rolle 1 vor Umsetzung erstellt.
- Benutzer erweitert Umfang ausdrücklich bis Endabgabe; externe Versuche bleiben auf später verschoben.
- Benutzerantwort: Reflexion selbst erledigen; separate Datei und README-Hinweis vorbereiten.
- Referenzstand bleibt im vollständigen ZIP ausserhalb des Repositorys erhalten. Alle Rollen arbeiten in der beauftragten bestehenden Arbeitskopie, ohne Git-Änderungsoperationen.

## Vorabprüfung der Rollen / Schnittstellen

| Schnittstelle | Prüfung / Zuständigkeit |
|---|---|
| Bewertung → Umsetzung/Tests | Rollen 2 und 3 verwenden denselben Bericht von Rolle 1; Originalquellen bleiben unverändert. |
| Neue Tools ↔ unabhängige Tests | Rolle 3 schreibt tests/** zuerst; Rolle 2 ändert nur Produktion/Tools/Anleitungen. APIs werden direkt abgestimmt. |
| Bild ↔ GUI-Lebenszyklus | Generierung darf parallel zur roten Testvorbereitung laufen; Einbindung erst nach entsprechendem Abnahmetest. |
| Logger ↔ TCP-Server | Neue Klassen bleiben rückwärtskompatibel zu new_game(); gemeinsamer Zustand und Drahtprotokoll bleiben geschützt. |
| Paket ↔ ursprüngliche Unterlagen | Paketstruktur enthält Repository und benötigten Schwesterordner Dokumente; keine Git-/Venv-/Secret-Dateien. |
| Testergebnis ↔ Abschlussbericht | Nur tatsächlich ausgeführte Ergebnisse; Angriffe nennen Datum und automatisierte ausführende Instanz. |
| Persönlicher Berichtsteil | Benutzer bearbeitet eigene Reflexion; README und Abgabestatus benennen diese offene Arbeit. |


## Lokaler Abschlussstand vor dem finalen Archiv

Alle lokalen Planaufgaben einschliesslich unabhängiger Kandidaten-Entpackprüfung
und Kriterienreview sind erledigt. 101/101 Tests, 16 echte GUI-Prüfungen,
sieben Angriffe und ganze Konsolen-/GUI-Partien bestanden. Der abschliessende
Hash-/Entpacknachweis für das erst danach gebaute Auslieferungsarchiv liegt
bewusst ausserhalb des Archivs neben dessen ZIP; damit wird kein zukünftiger
Test im Archiv als schon erledigt behauptet. Menschen-/Fremdrechnerleistungen
und eigene Reflexion bleiben offen, ohne die lokale Technik als fehlerhaft
oder vollständig benotet darzustellen.
