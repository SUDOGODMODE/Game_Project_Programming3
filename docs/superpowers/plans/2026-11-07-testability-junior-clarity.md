# Testability and Junior Clarity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein schneller Kernlauf, ehrliche Berichte, isolierte Testlogs und kleine Tk-freie Helfer erleichtern Prüfung und Verständnis.

**Architecture:** Der bestehende Spielkern und das Protokoll bleiben unverändert. Der Teststarter erhält eine gezielte Auswahl; GUI-Berechnungen wandern in ein reines Modul, während `draw_state` weiterhin allein Widgets ändert.

**Tech Stack:** Python 3.12+, `unittest`, `tkinter`, Standardbibliothek.

**Spec:** `docs/superpowers/specs/2026-11-07-testability-junior-clarity-design.md`

## Global Constraints

- Keine zusätzlichen Laufzeitabhängigkeiten; keine Änderungen an Spielregeln oder Drahtprotokoll.
- Vorhandene Git-Änderungen erhalten; keine Commits oder Pushes.
- Keine Testläufe als Fremdrechner- oder menschlichen Nachweis bezeichnen.

## Review Focus

- `--core` darf weder `test_local_game.py` noch Tk-/TCP-Tests laden; Auswahl anhand tatsächlicher Test-IDs prüfen.
- `--core --require-gui` darf keinen falschen GUI-Erfolg melden.
- Ein übersprungener GUI-Subtest muss im Bericht `partial_skip` bleiben.
- Zufallsflotten müssen auch mit festem Zufallsgenerator gültig bleiben.
- GUI-Symbole für eigene Treffer, Wasser und versenkende Treffer müssen unverändert sein.

---

### Task 1: Kernprofil und ehrlicher Testbericht

**Files:** Modify `tools/run_tests.py`; test `tests/meilenstein_04/test_runner.py`.

**Interfaces:** `load_core_suite(loader)` liefert nur `tests.meilenstein_02.test_board`, `tests.meilenstein_02.test_game` und `tests.meilenstein_05.test_spiel`; `--core` schließt `--milestone` aus. `run_suite` meldet `selection="core"`.

- [ ] Test für die Kern-Auswahl und den `partial_skip`-Bericht ergänzen.
- [ ] Tests ausführen und das erwartete Scheitern prüfen.
- [ ] Minimalen Runner-Code ändern, ohne bestehende Auswahlen zu verändern.
- [ ] Betroffene Runner-Tests und Kernprofil ausführen; danach Gesamtsuite.

### Task 2: Temporäre Testlogs

**Files:** Modify `tests/meilenstein_03/test_network.py`, `tests/meilenstein_04/test_server_states.py`, `tests/meilenstein_04/test_protocol.py`.

**Interfaces:** Jeder Test nutzt einen neuen temporären JSONL-Pfad und schließt seinen `EventLog` bei der Bereinigung.

- [ ] Vorhandene Logerzeugung und Aufräumwege pro Testgruppe prüfen.
- [ ] Tests auf einen temporären Pfad und gesichertes Schließen umstellen.
- [ ] Betroffene Tests ausführen und prüfen, dass im Projekt keine neuen Logs entstehen.

### Task 3: Reine GUI-Berechnungen

**Files:** Create `src/client_view.py`, `src/fleet_setup.py`; modify `src/client_gui.py`; test `tests/meilenstein_02/test_client_view.py`, `tests/meilenstein_02/test_fleet_setup.py`.

**Interfaces:** `board_symbols(state)` liefert `(own_symbols, target_symbols, segments)`; `random_placement(rng)` liefert eine `validate_placement`-gültige Liste aus `type`, `start`, `direction`. Die GUI setzt nur Tk-Variablen und zeichnet die gelieferten Daten.

- [ ] Reine Verhaltenstests für Symbolpriorität, leere Sicht, gültige und reproduzierbare Flotten schreiben.
- [ ] Fehlschlag wegen fehlender Helfer prüfen.
- [ ] Helfer und schmale GUI-Anbindung implementieren.
- [ ] Reine Tests und betroffene echte GUI-Tests ausführen.

### Task 4: Lernweg und Endprüfung

**Files:** Modify `README.md`, `docs/development/testing.md`, `docs/development/architecture.md`, `WEITERARBEITEN.md`, `journal.md`.

- [ ] Vierstufige Testreihenfolge mit Befehlen und Voraussetzungen dokumentieren.
- [ ] Architektur um die zwei reinen GUI-Helfer ergänzen; historischen und aktuellen Teststand unterscheiden.
- [ ] `--core`, M5-Kursbefehl, `--require-gui` und vollständige lokale GUI-Demo frisch ausführen.
- [ ] Git-Diff, Testzahlen, verbleibende Grenzen und offene Aufgaben prüfen und dokumentieren.
