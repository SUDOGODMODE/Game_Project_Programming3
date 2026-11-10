# Strukturmigration prüfen

Im Projektordner mit aktivierter `.venv`:

1. `python3 tools/run_tests.py --core` — 41 Kerntests ohne Tk, TCP oder
   fremde Prozesse.
2. Aus `src/`: `python3 -m unittest -v test_spiel.py` — Kursregeltest.
3. `python3 tools/run_tests.py --milestone 06 --require-gui` — echte
   Grafiktests in einer grafischen Sitzung.
4. `python3 tools/run_tests.py --require-gui --report-json
   <neuer_bericht.json>` — Gesamtlauf mit neuen, nicht überschriebenen
   Nachweisen.
5. `python3 tools/run_gui_demo.py --output <neuer_ordner>` — vollständige
   lokale Partie mit zwei echten Fenstern.
6. `git diff --check` und `git status --short` — Pfade und vorhandene
   Änderungen prüfen. Nur der Projektverantwortliche pusht.

Lokale Tests ersetzen keinen echten Fremdrechnernachweis.
