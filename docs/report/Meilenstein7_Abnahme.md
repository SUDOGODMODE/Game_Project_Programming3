# Abnahme Meilenstein 7

Grundlage: `../../../Dokumente/Meilenstein7.txt` und
`../../../Dokumente/bewertungsraster_finale_abgabe.txt`.
Die Originalunterlagen bleiben unverändert. Umsetzung und Nachweise werden lokal erstellt.

## Kriterien und Nachweise

| Kriterium | Prüfung |
|---|---|
| AK1 Zuschaueraufnahme | Dritter und weitere Clients, sofortiger aktueller Zustand, keine Spielernummer |
| AK2 Server entscheidet | Platzierung und Schuss von Zuschauern werden privat abgelehnt |
| AK3 Gemeinsamer Spielstand | Öffentliche Schüsse, Phase, Zug und Gewinner stimmen nach jedem Zug überein; Ende und Spielerabbruch werden verteilt |
| AK4 Verborgene Information | Zuschauer erhalten keine Flotten; eigene Flotten bleiben nur beim jeweiligen Spieler |
| AK5 Robustheit | Zuschauerabbruch ohne Reset/Benachrichtigung; Sendefehler stoppen den Rundruf nicht; keine Beförderung |
| AK6 Dokumentation | Protokollbeispiele, Pflichtfelder, Nachrichtenrichtung und Startanleitung stimmen mit dem Code überein |
| AK7 Sichtbarer Nachweis | Drei echte Fenster nach demselben Zug, Zuschauerablehnung und Serverausgabe desselben Laufs |
| AK8 Tests | Gesamtsuite inklusive Regelkern, echter TCP-Verbindungen und GUI |

## Bezug zum Bewertungsraster

- Spielbar (20 %): Die automatisierte GUI-Partie prüft eine vollständige Partie mit Sieg und Niederlage. Schiffe versenken kennt nach den bestehenden Regeln kein Unentschieden. Ein automatisierter Lauf ersetzt keine persönliche Partie des Bewertenden.
- Server entscheidet (20 %): Serverseitige Rollenprüfung, Regelkern und öffentliche Sicht; ungültige Wünsche dürfen keinen Zustand verändern.
- Aufbau (20 %): Der Spielkern bleibt netz- und fensterfrei; Empfang über Queue, Zeichnen im Tk-Hauptthread; Prüfen und Ändern unter derselben Serversperre.
- Robustheit (15 %): Spieler- und Zuschauerabbruch, ungültiges JSON und unbekannte Nachrichtentypen.
- Tests (15 %): Entdeckung über `python3 -m unittest discover` in der vorhandenen Projektumgebung.
- Protokoll/README (10 %): Nachrichtenkatalog und ausführbare Startbefehle; Grenzen ausdrücklich dokumentiert.

## Ausführungsstand

Ausgangsstand vor den Änderungen: 189 Tests mit
`.venv/bin/python3 -m unittest discover` erfolgreich.

Stand 24.11.2026, lokal auf einem Rechner (macOS, Retina-Bildschirm):

| Kriterium | Ergebnis | Nachweis |
|---|---|---|
| AK1 | erfüllt | `test_third_client_is_spectator_without_changing_the_two_player_game`, `test_spectator_sees_only_public_shots_on_join_and_after_each_move`; GUI-Lauf: später Beitritt nach B6 zeigt sofort B6 |
| AK2 | erfüllt | `test_spectator_actions_are_private_and_cannot_spoof_a_player`; `server.txt` Zeilen 41/45 `SPECTATOR_ONLY` nur an den Zuschauer; `spectator_rejection.png` |
| AK3 | erfüllt | GUI-Lauf: 35 öffentliche Zuschauerzustände gleich den Spielersichten inkl. Spielende und Reset; `server.txt` Zeilen 201–207 und 220–221 (`gameOver`, `opponentLeft` an Zuschauer) |
| AK4 | erfüllt | `verify_private_states` im GUI-Lauf: alle 36 Zuschauerzustände mit `ownShips=[]`; `tests/core/test_game.py::test_public_state_hides_fleets_and_copies_shots_in_a_b_order` |
| AK5 | erfüllt | `test_spectator_leave_and_hard_disconnect_do_not_reset_or_notify_players`, `test_dead_spectator_during_broadcast_does_not_block_remaining_recipients`, `test_player_disconnect_resets_spectator_without_promotion_and_new_player_can_join` |
| AK6 | erfüllt | `tests/gui/test_protocol.py` vergleicht JSON-Katalog 0.7 und Markdown-Tabelle (15 Typen) |
| AK7 | erfüllt | `docs/evidence/meilenstein7_20261124_02/` (siehe unten) |
| AK8 | erfüllt | `.venv/bin/python3 -m unittest discover`: `Ran 203 tests` / `OK` |

### Bildnachweis

`docs/evidence/meilenstein7_20261124_02/` mit
`python3 tools/run_gui_demo.py --spectator --screenshot --final-screenshot`,
`result.json`: `PASS`.

- `three_windows.png`: **Montage echter Einzelaufnahmen** (`three_windows_Alice.png`,
  `_Bob.png`, `_Zuschauer.png`, je `screencapture`) nach demselben Zug; drei
  TCP-Verbindungen offen, während der Aufnahmen kein Spielzug.
- `spectator_rejection.png`: echte Einzelaufnahme nach dem Zuschauerklick mit
  `Fehler SPECTATOR_ONLY`.
- `three_windows_finished.png`: Montage echter Einzelaufnahmen nach Spielende.
- `server.txt`: Server-Terminalausgabe desselben Laufs.

Der unveränderte Client zeigt beim Zuschauer die Spielertexte (z. B.
„Verloren. Partie beendet.“); das ist keine Zuschauer-Rollenanzeige.

Ein früherer Lauf war FAIL, weil die Bilder verworfen wurden. Ursache: Die Bildprüfung tastete Bildschirmpunkte im
doppelt so grossen Retina-Bild ab und traf die Titelleiste. Korrigiert in
`tools/run_gui_demo.py` (`game_windows_visible(..., scale)`), Test
`test_screenshot_validation_scales_retina_pixels`.

### Nicht durchgeführt

- Persönliche Partie durch einen Menschen und Lauf auf einem Fremdrechner:
  nicht durchgeführt; der Nachweis ist ein automatisierter lokaler Lauf.
