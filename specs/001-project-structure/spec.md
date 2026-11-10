# Feature Specification: Verständliche Projektstruktur

**Feature Branch**: `feature/testability-junior-clarity`
**Created**: 2026-11-10
**Status**: Abgeschlossen
**Input**: Benutzerauftrag: Verzeichnis sauber und professionell ordnen, alle Abhängigkeiten beachten und falsch bezeichnete Arbeiten bereinigen. Der aktuelle Kurs endet mit Meilenstein 6; daran wird später gearbeitet.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Projekt schnell verstehen (Priority: P1)

Als Junior finde ich Spielkern, GUI, Tests, Werkzeuge und Nachweise anhand
einer kurzen Projektübersicht und kann die wichtigsten Startbefehle weiter
verwenden.

**Why this priority**: Der Code muss für den Projektverantwortlichen erklärbar bleiben.

**Independent Test**: Ein neuer Leser findet für jede aktive Dateigruppe ihre Aufgabe und führt die dokumentierten Start- und Testbefehle aus.

**Acceptance Scenarios**:

1. **Given** das Repository, **When** ich README und Strukturübersicht lese, **Then** finde ich jede aktive Dateigruppe ohne historische Unterlagen mit aktuellem Kursumfang zu verwechseln.
2. **Given** die bestehenden Kursbefehle, **When** ich sie starte, **Then** funktionieren sie nach der Umordnung weiter.

---

### User Story 2 - Eindeutige Meilensteine (Priority: P1)

Als Projektverantwortlicher sehe ich nur Meilenstein 0 bis 6 als aktuelle
Kursfolge. Bereits vorhandene Logging- und Paketprüfungen bleiben als
Zusatzprüfungen erhalten, ohne als neue Kursmeilensteine zu erscheinen.

**Why this priority**: Falsche Meilensteinnummern führen zu falscher Planung und Abgabeaussagen.

**Independent Test**: Aktive Testauswahl und Einstiegstexte nennen nur M0–M6; die Zusatzprüfungen bleiben im Gesamtlauf sichtbar.

**Acceptance Scenarios**:

1. **Given** der Teststarter, **When** ich die Hilfe lese, **Then** gibt es keine Auswahl für M7 oder M8.
2. **Given** der Gesamtlauf, **When** er Tests sammelt, **Then** sind Logging- und Paketprüfungen weiterhin enthalten.

---

### User Story 3 - Bestehende Arbeit bewahren (Priority: P2)

Als Projektverantwortlicher bleiben Originalaufträge, alte Rohbelege und
lokale Änderungen erhalten. Die Strukturänderung erzeugt weder neue
GitHub-Aktionen noch eine stillschweigende M6-Umsetzung.

**Why this priority**: Der bisherige Nachweisstand darf nicht verfälscht werden.

**Independent Test**: Git-Status, alte Belegpfade und der aktuelle M6-Status werden vor und nach der Umordnung verglichen.

**Acceptance Scenarios**:

1. **Given** alte Rohbelege, **When** die Struktur bereinigt wird, **Then** bleiben diese Dateien und ihre historischen Aussagen unverändert.

---

### Edge Cases

- Eine verschobene GUI-Hilfsdatei lädt Bilder weiterhin relativ zum tatsächlichen Projektordner.
- Ein Test, der einen alten Modulnamen importiert, muss nach der Umordnung explizit angepasst werden.
- Ein Paket aus dem Repository enthält weiterhin die zum Spiel nötigen Dateien und keine lokalen Spec-Kit-Werkzeugdateien.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Die stabilen Kurspfade für Spielkern, Server, GUI-Start, Kursregeltest, Bilder und Varianten MÜSSEN erhalten bleiben.
- **FR-002**: GUI-interne Hilfsdateien MÜSSEN als zusammengehörige Gruppe erkennbar sein, ohne die Kurseinstiege zu verändern.
- **FR-003**: Aktive Testauswahl und Dokumentation DÜRFEN M7/M8 nicht als aktuelle Kursmeilensteine ausgeben.
- **FR-004**: Vorhandene Zusatzfunktionen und ihre Prüfungen MÜSSEN im Gesamtlauf erhalten bleiben.
- **FR-005**: Originalaufträge und Rohbelege MÜSSEN unverändert bleiben.
- **FR-006**: Es erfolgen keine Commits, Pushes oder Änderungen auf GitHub; nur der Projektverantwortliche pusht.
- **FR-007**: Die technische M6-Umsetzung beginnt erst mit dem gesonderten Auftrag des Projektverantwortlichen. **Einordnung vom 10.11.2026:** Dieser gesonderte Auftrag ist inzwischen erteilt und die M6-Umsetzung lokal abgeschlossen und geprüft, siehe [M6-Anforderungsabgleich](../../docs/status/06_requirements.md). FR-007 beschreibt weiterhin korrekt den Umfang dieses abgeschlossenen Features 001; es ist kein aktueller Status mehr.

### Key Entities *(include if feature involves data)*

- **Aktive Kursmeilensteine**: M0–M6, getrennt von alten Projektplänen.
- **Zusatzprüfungen**: vorhandene Logging- und Pakettests ohne offizielle Kursnummer.
- **Historische Belege**: unveränderte Originalaufträge und Rohdateien mit damaligen Pfaden.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Alle dokumentierten Kurseinstiege und die vollständige lokale GUI-Partie funktionieren nach der Umordnung.
- **SC-002**: Der strenge Gesamtlauf besteht ohne Fehler oder Skips und enthält alle bisherigen Prüfungen.
- **SC-003**: Aktive Einstiegstexte und Testhilfe nennen M0–M6 als aktuellen Kursumfang.
- **SC-004**: Originalaufträge und historische Rohbelege bleiben bytegleich.

## Assumptions

- Die heutige Nutzerangabe „M6 ist der Schluss“ ist für die aktuelle Kursplanung maßgeblich. Der ältere Projektablauf mit M7/M8 bleibt ein historisches Dokument.
- Öffentliche Kursbefehle und Dateinamen haben Vorrang vor einem installierbaren Paketlayout.
- Zusammengehörige GUI-Helfer werden gruppiert; ein Komplettumbau des Spielkerns wird vermieden.
