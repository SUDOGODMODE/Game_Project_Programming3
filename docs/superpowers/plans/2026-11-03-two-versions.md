# Zwei Betriebsarten Implementation Plan

> **For agentic workers:** Test first, then implement and review. This repository forbids staging, commits, pushes and GitHub changes without a new order.

**Goal:** Eine localhost-Version und eine für zwei Rechner vorbereitete Version mit zwei Anleitungen und zwei separat nutzbaren Paketen liefern.

**Architecture:** `src/`, Bilder, Regeln und Protokoll bleiben einmalig. Zwei dünne Starteinstiege unter `varianten/` übergeben das ausgewählte Profil an einen gemeinsamen Launcher; der bestehende Paketbauer erzeugt je ein Profil-ZIP mit eigenem Einstieg und eigener Startanleitung.

**Tech Stack:** Python 3.12+, tkinter, TCP, unittest, Standardbibliothek.

**Spec:** `docs/superpowers/specs/2026-11-03-two-versions-design.md`

## Global Constraints

- localhost bindet den Server nur an `127.0.0.1:5100`; beide Clients verbinden sich dorthin.
- Zwei Rechner: Server und Alice auf Gerät 1; Server bindet `0.0.0.0:5100`, Alice nutzt `127.0.0.1`, Bob braucht eine ausdrücklich eingegebene echte Server-IPv4.
- Keine reale fremde IP, kein echter Zweirechnerlauf und keine Personenleistung werden erfunden.
- Jede Variante nutzt dieselbe Regelquelle `src/spiel.py` und dieselben Assets.
- Alte Archive und Rohbelege bleiben unverändert; neue Dateien nur lokal.

## Review Focus

- `127.0.0.1` darf im Zweirechnerprofil für Bob nicht akzeptiert werden.
- `0.0.0.0` darf in keinem Client-Aufruf als Ziel landen.
- Das localhost-Profil darf den Server nicht unbeabsichtigt im LAN öffnen.
- Beide Pakete müssen unabhängig voneinander und von der ursprünglichen Arbeitskopie starten.
- Die zwei Pakete dürfen keine lokalen Logs, Venvs oder ungültigen Desktopbilder enthalten.

---

### Task 1: Profilstart und Tests

**Files:** Create `tools/variant_start.py`, `varianten/localhost/start.py`, `varianten/zwei_rechner/start.py`, `tests/meilenstein_05/test_variant_start.py`.

**Interfaces:** `command_for(profile: str, role: str, *, server_ip: str | None, port: int, name: str | None, root: Path, python: str) -> list[str]`; `main(profile: str, argv: list[str] | None = None) -> int`.

- [ ] Erst Tests für Server-Bind, Zieladressen, fehlende/falsche IPv4, Port und fremdes Arbeitsverzeichnis schreiben; RED beobachten.
- [ ] Gemeinsamen Launcher und dünne Profil-Einstiege implementieren. Drei separate Terminals bleiben möglich; kein Shell-Aufruf.
- [ ] Fokussierte Tests grün ausführen.

### Task 2: Zwei Paketprofile

**Files:** Modify `tools/build_submission.py`, `tests/meilenstein_05/test_variant_packages.py`; create `varianten/localhost/START.md`, `varianten/zwei_rechner/START.md` before final package build.

**Interfaces:** `build_submission(repo_root, output, *, variant: str | None = None) -> Path` bewahrt das alte Verhalten ohne Profil; `--variant localhost|zwei_rechner` ergänzt CLI. Profil-ZIP enthält `START_HIER.md`, `start.py` und einen Profilmarker sowie alle benötigten gemeinsamen Quellen. Unterschiedliche äussere ZIP-Ordner erlauben paralleles Entpacken.

- [ ] ZIP-Tests für ausgewählten Einstieg, Quellen, Bilder, M5-Belege, Manifest, Hash und Ausschlüsse schreiben; RED beobachten.
- [ ] Profilpaket-Option implementieren; alte M8-Pakettests weiter bestehen lassen.
- [ ] Beide Profilpaket-Tests grün ausführen.

### Task 3: Anleitungen und Struktur

**Files:** Modify `README.md`, `docs/guides/setup.md`, `WEITERARBEITEN.md`, `journal.md`; create/update `varianten/*/START.md` and `docs/status/two_versions.md`.

- [ ] Wurzel-README als Auswahl und technische Übersicht klar strukturieren.
- [ ] Zwei eigenständige Schritt-für-Schritt-Anleitungen für macOS/Linux und Windows schreiben, mit Einrichtung, drei Terminals, Geräteverteilung, Beenden und Fehlersuche.
- [ ] Zwei-Rechner-Anleitung trennt technische Vorbereitung vom weiterhin offenen echten Versuch.
- [ ] Dokumente und Startbefehle gegen die tatsächliche Launcher-Schnittstelle lesen.

### Task 4: Ganze Abnahme und Auslieferung

**Files:** New unique ZIPs and adjacent verification reports under `dist/`; no overwrite of earlier packages.

- [ ] Gesamtsuite mit erforderlichen echten GUI-Tests ausführen.
- [ ] Beide ZIPs bauen, Manifest/Prüfsumme und Pflichtdateien unabhängig prüfen.
- [ ] Beide ZIPs separat entpacken, Start-CLI und Kerntest aus fremdem Arbeitsverzeichnis prüfen; localhost-Profil mit echter lokaler TCP/Tk-Partie prüfen.
- [ ] Unabhängiger Review und finaler Git-/Dokumentationsabgleich; Fremdrechnerbeleg bleibt offen.
