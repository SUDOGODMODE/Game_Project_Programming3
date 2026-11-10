# Junior-Readable Code Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Das gesamte Python-Projekt prüfen und konkrete Lesbarkeitshürden ohne Verhaltensänderung beseitigen.

**Architecture:** Drei unabhängige Bereiche: Spielkern/Netzwerk, GUI/Grafik sowie Werkzeuge/Tests. Bestehende Modulgrenzen und öffentliche Schnittstellen bleiben erhalten.

**Tech Stack:** Python 3.12+, unittest, tkinter, Standardbibliothek.

**Spec:** `docs/superpowers/specs/2026-11-10-junior-readable-code-design.md`

## Global Constraints

- Keine Änderungen an Spielregeln, Drahtprotokoll, Nachrichtenreihenfolge oder GUI-Verhalten.
- Keine zusätzlichen Laufzeitabhängigkeiten; Python 3.12 oder neuer.
- Vorhandene lokale Änderungen und Rohbelege erhalten; keine Commits oder Pushes.
- Bestehende öffentliche Schnittstellen, CLI-Optionen und JSON-Berichtsfelder erhalten.

## Review Focus

- `--core` startet auch bei Berichtsausgabe keine Fremdprozesse.
- GUI-Zielklicks erreichen nach Spielende weiter den Server; nur `state` zeichnet neu.
- Tk-Widgets werden nur im Hauptthread berührt; Cleanup-Reihenfolge bleibt erhalten.
- Testfixturen duplizieren keine GUI-Tests und verlieren keine Skip-Markierung.
- Paket- und Demo-Werkzeuge überschreiben keine vorhandenen Nachweise.

---

### Task 1: Spielkern und Netzwerk erklären

**Files:** `src/play.py`, `src/server.py`, `src/spiel.py`, `src/local_game.py`, `src/event_log.py`; übrige `src`-Kernmodule prüfen.

- [x] Reine Eingabe-/Textaufgaben aus `play.main` in benannte Helfer ziehen; Socket- und Thread-Lebensdauer bewahren.
- [x] Zuständigkeiten von Serverdaten und Spielkern, Vorbedingungen und Nachrichtenfolge knapp dokumentieren.
- [x] Unklare Kurzvariablen und verdichtete Ausdrücke ohne Verhaltensänderung auflösen.
- [x] Betroffene Kern-, CLI- und Netzwerktests ausführen; Diff selbst prüfen.

### Task 2: GUI und Grafik lesbarer machen

**Files:** `src/client_gui.py`, `src/ship_effects.py`, `src/ship_art.py`, `src/sea_cell.py`, `src/client_view.py`; `src/fleet_setup.py` prüfen.

- [x] Interfaceaufbau nach sichtbaren Bereichen aufteilen; Widget-Erzeugungsreihenfolge erhalten.
- [x] `draw_state` und `randomize_fleet` mit sprechenden Namen und normalen Bedingungen erklären.
- [x] Zeichenschritte der Sprengung und SVG-Transformation benennen; Formeln und Zeiten erhalten.
- [x] Betroffene GUI-/Grafiktests ausführen; Diff selbst prüfen.

### Task 3: Werkzeuge und Tests vereinfachen

**Files:** `tools/*.py`, `tests/**/*.py`, `varianten/*/start.py` prüfen; gezielte Änderungen an `run_gui_demo.py`, `build_submission.py`, `run_tests.py` und besonders schwer lesbaren Tests.

- [x] Lange Demo und Paketwerkzeuge in benannte Phasen/Helfer gliedern; exklusive Nachweispfade erhalten.
- [x] Teststarter-Namen und Auswertung verständlich machen; Berichtsfelder und Skip-Semantik erhalten.
- [x] Testwiederholungen und schwer lesbare Assertions gezielt vereinfachen; echte Tk-/TCP-Prüfungen bewahren.
- [x] Betroffene Werkzeug- und Testgruppen ausführen; Diff selbst prüfen.

### Task 4: Gesamtprüfung und Übergabe

**Files:** `README.md`, `docs/development/architecture.md`, `docs/development/testing.md`, `WEITERARBEITEN.md`, `journal.md` nur soweit für die neue Code-Landkarte und tatsächliche Ergebnisse nötig.

- [x] Drei Bereichsdiffs unabhängig auf Verhaltensgleichheit und Verständlichkeit prüfen; Befunde bearbeiten.
- [x] `--core`, strenge Gesamtsuite und vollständige lokale GUI-Demo frisch ausführen.
- [x] Ergebnisse, verbleibende Grenzen und eine kurze Lesereihenfolge für Junioren dokumentieren.
- [x] Git-Status und `git diff --check` prüfen; lokale Änderungen unveröffentlicht lassen.
