# Tests finden

`meilenstein_00/` bis `meilenstein_06/` enthalten die vorhandenen technischen
Kursgruppen. Für M1 gibt es keinen eigenen Testordner. Die Gruppierung
beschreibt die technische Herkunft der Tests; sie behauptet nicht, dass die
später heute geplante Kursarbeit zu M6 bereits abgenommen wurde.

`additional/` enthält vorhandene Prüfungen für Nachrichtenlogs und
Abgabepakete. Diese Funktionen sind keine neuen Kursmeilensteine. Der
Gesamtlauf sammelt sie weiterhin ein.

`fixtures.py` enthält gemeinsame feste Testflotten. `gui_helpers.py`
stellt Tk-/Socket-Fixturen bereit, ohne selbst Testfälle zu erzeugen.
Die Befehle und Voraussetzungen stehen in
[docs/development/testing.md](../docs/development/testing.md).
