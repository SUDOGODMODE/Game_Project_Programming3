# Implementation Plan: Verständliche Projektstruktur

**Branch**: `feature/testability-junior-clarity` | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

**Input**: Der aktuelle Kurs endet laut Projektverantwortlichem mit M6. Feste Kursbefehle und historische Belege bleiben erhalten.

## Summary

GUI-interne Hilfsdateien werden unter `src/gui/` gruppiert. Die vorgegebenen
Kursprogramme bleiben unter `src/`. Vorhandene Tests für Nachrichtenlogs
und Pakete werden als Zusatzprüfungen statt M7/M8 geführt. Aktive Dokumente
zeigen die neue Struktur; Originalaufträge und Rohbelege bleiben unverändert.

## Technical Context

**Language/Version**: Python 3.12 oder neuer

**Primary Dependencies**: Python-Standardbibliothek, tkinter; Spec Kit nur für Entwicklung

**Storage**: Dateien für Dokumentation, Nachweise und lokale Metadatenlogs

**Testing**: unittest über `tools/run_tests.py`, echter Tk/TCP-Demolauf

**Target Platform**: macOS lokal geprüft; Anleitung für Windows/Linux vorhanden

**Project Type**: Desktop-/Netzwerk-Kursprojekt

**Performance Goals**: Keine Verhaltens- oder Geschwindigkeitsänderung

**Constraints**: Stabile Kursbefehle, Startprofile, 10×10-Regeln, Protokoll, Bildpfade, keine neuen Laufzeitpakete

**Scale/Scope**: Kleine Migration von vier GUI-Hilfsmodulen und zwei falsch benannten Testgruppen; keine Migration historischer Rohdaten

## Constitution Check

- Prinzip I: `REGELN.md` und `src/spiel.py` bleiben unverändert am Kurspfad.
- Prinzip II: Server-/Client-Nachrichtenfolge und gefilterte Sichten bleiben gleich.
- Prinzip III: Die GUI-Gruppe reduziert flache Modulnavigation ohne zusätzliche Framework-Schicht.
- Prinzip IV: Fokussierte Tests, strenge Gesamtsuite und echte lokale Demo prüfen die Migration.
- Prinzip V: Keine Commits/Pushes; alte Aufgaben und Rohbelege bleiben erhalten.

Alle Gates sind vor und nach dem Design erfüllt.

## Project Structure

### Documentation (this feature)

```text
specs/001-project-structure/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
└── quickstart.md
```

### Source Code (repository root)

```text
src/
├── spiel.py, board.py, test_spiel.py, netz.py, server.py
├── client_gui.py, fleet_setup.py, play.py, client.py, local_game.py
├── event_log.py, echo_client.py, echo_server.py
└── gui/
    ├── __init__.py
    ├── client_view.py
    ├── sea_cell.py
    ├── ship_art.py
    └── ship_effects.py
tests/
├── meilenstein_00/ ... meilenstein_06/
├── additional/
│   ├── test_event_log.py
│   └── test_packaging.py
└── gui_helpers.py, fixtures.py
tools/
varianten/
bilder/
docs/
specs/
.specify/
.agents/skills/
```

**Structure Decision**: Kurspfade und Startprofile sind öffentliche Schnittstellen.
Nur interne GUI-Helfer und falsch etikettierte Zusatztests werden verschoben.
Ein vollständiges installierbares Paket würde Adapter und mehr Komplexität
erfordern und ist hier nicht beauftragt.

## Complexity Tracking

Keine Verfassungsausnahme nötig.
