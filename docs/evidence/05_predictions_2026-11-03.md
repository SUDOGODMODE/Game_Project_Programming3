# Meilenstein 5 — Vorhersagen vor den Hand- und Fehlerversuchen

Diese Erwartungen wurden **vor** den unten genannten Versuchen notiert.
Sie beziehen sich auf den eigenständigen Schiffe-versenken-Kern in
`src/spiel.py` und die 19 Tests in `src/test_spiel.py`. Die festen Flotten
und Schussfolgen sind Testdaten, keine Vorgaben für Nutzer.

## Handpartie

Nach `start()` und zwei gültigen Flotten ist A am Zug. `check_shot("B",
"A1")` soll `NOT_YOUR_TURN` mit lesbarem Grund liefern. Ein erfolgreicher
Schuss von A auf A1 soll `hit` ergeben und den Zug an B geben. Nach B auf
J10 (`miss`) soll ein weiterer Schuss von A auf A1 wegen `DUPLICATE_SHOT`
abgelehnt werden, ohne den Zustand zu ändern. Wenn A alle 17 gegnerischen
Schiffsfelder trifft und B dazwischen 16-mal Wasser, soll A nach dem 33.
Schuss gewinnen; `turn` soll `None` sein. Ein Schuss nach dem Ende soll
`WRONG_PHASE` auslösen und beide Ansichten unverändert lassen.

## Absichtlicher Fehler 1: Versenkungserkennung entfernen

In einer **isolierten Kopie** wird nur die Bedingung für den letzten Treffer
eines Schiffs in `apply_shot` auf `False` gesetzt. Erwartet: Von den 19
Kerntests scheitert genau **einer**,
`test_letztes_schiffsfeld_meldet_versenkt`, weil der letzte Treffer als
`hit` statt `sunk` gemeldet wird. Die Gesamtgewinnprüfung soll weiterhin
funktionieren, weil sie alle getroffenen Felder separat zählt.

## Absichtlicher Fehler 2: Spielerwechsel auslassen

In einer neuen **isolierten Kopie** wird die Zuweisung des gegnerischen Slots
nach einem nicht siegreichen Schuss durch die Zuweisung des bisherigen Slots
ersetzt. Erwartet: Genau **sieben** der 19 Kerntests werden rot oder mit
einer Regelablehnung abbrechen:

- `test_treffer_wechselt_den_spieler`
- `test_wasser_wechselt_den_spieler`
- `test_doppelter_schuss_verbraucht_keinen_zug`
- `test_letztes_schiffsfeld_meldet_versenkt`
- `test_gesamte_flotte_versenkt_beendet_ohne_spielerwechsel`
- `test_nach_dem_sieg_wird_auch_ein_freies_feld_abgelehnt`
- `test_geheime_flotte_bleibt_auch_im_endzustand_verborgen`

Danach müssen beide Kopien verworfen und der unveränderte Projektkern wieder
mit allen 19 Tests grün geprüft werden.
