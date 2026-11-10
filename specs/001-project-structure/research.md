# Strukturentscheidungen

## Feste Kursdateien

**Decision:** `src/spiel.py`, `src/test_spiel.py`, `src/netz.py`,
`src/server.py`, `src/client_gui.py`, `bilder/` und die Startprofile bleiben.

**Rationale:** Die Kursunterlagen, Tests und Startskripte nennen diese Pfade;
der M5-Testbefehl muss aus `src/` eigenständig funktionieren.

**Alternatives considered:** Ein neues installierbares Paket würde zusätzliche
Adapter und Importwege schaffen, ohne den Junior-Einstieg zu verbessern.

## GUI-Hilfsmodule

**Decision:** Vier interne Module nach `src/gui/` gruppieren; GUI-Einstieg und
Tk-freie Flottenvorlage bleiben auf ihrem Kurspfad beziehungsweise in `src/`.

**Rationale:** Gemeinsame Aufgabe bei begrenztem Importumfang. Bildpfade und
Test-Patches werden beim Umzug ausdrücklich geprüft.

**Alternatives considered:** Komplettumzug des GUI-Einstiegs bricht bekannte
Startpfade; gar keine Gruppierung erfüllt den Strukturauftrag nur in Texten.

## Aktueller Meilensteinumfang

**Decision:** Aktive Tests für Logs und Pakete unter `tests/additional/`
führen und Auswahl `--milestone` auf 00–06 begrenzen.

**Rationale:** Der Projektverantwortliche hat M6 als letzten aktuellen
Kursmeilenstein festgelegt. Ältere Unterlagen mit M7/M8 bleiben historische
Originale, nicht aktuelle Planung.

**Alternatives considered:** Löschen vernichtet vorhandene Prüfungen;
unveränderte Benennung würde die falsche Kursnummerierung fortführen.
