# Tests finden

`core/`, `network/`, `gui/`, `integration/` und `graphics/` gliedern die
Tests nach Thema: netzfreie Spielregeln, Transport/Lobby/Protokoll über
TCP, die tkinter-Oberfläche und der Teststarter, Spielende/Startvarianten/
Abgabepakete sowie Grafik und Bildanzeige.

`additional/` enthält Prüfungen für Nachrichtenlogs und Abgabepakete. Der
Gesamtlauf sammelt sie mit ein.

`fixtures.py` enthält gemeinsame feste Testflotten. `gui_helpers.py`
stellt Tk-/Socket-Fixturen bereit, ohne selbst Testfälle zu erzeugen.
Die Befehle und Voraussetzungen stehen in
[docs/development/testing.md](../docs/development/testing.md).
