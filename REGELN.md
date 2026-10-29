# Schiffe versenken — Regelblatt

Stand: 27.10.2026. Spielwahl freigegeben, bestätigt im Gespräch. Die folgenden Regeln beschreiben den aktuellen Spielkern. Gegenlesen steht noch aus.

Zwei Spieler versuchen, die Flotte des Gegners zu versenken. Jeder setzt fünf Schiffe auf sein eigenes Raster, ohne dem Gegner die Positionen zu zeigen. Danach schiessen die Spieler abwechselnd auf ein gegnerisches Feld. Der Spielkern meldet Wasser, Treffer oder versenkt. Wer zuerst die gesamte gegnerische Flotte getroffen hat, gewinnt.

## Spieler und Material

Zwei Spieler, A und B, besitzen je ein Raster mit 10 × 10 Feldern. Die Spalten heissen A bis J, die Zeilen 1 bis 10. Das Feld C5 liegt in Spalte C, Zeile 5.

Jeder Spieler setzt genau ein Schiff jedes Typs:

| Schiff | Felder |
|---|---:|
| Carrier | 5 |
| Battleship | 4 |
| Cruiser | 3 |
| Submarine | 3 |
| Destroyer | 2 |

Eine Flotte belegt 17 Felder. Schiffe liegen gerade, entweder waagrecht nach rechts (`h`) oder senkrecht nach unten (`v`). Sie dürfen sich nicht überlappen oder über den Rand ragen. Berührungen zwischen Schiffen sind erlaubt.

## Zustand und Ablauf

Der Kern speichert die Phase, den Spieler am Zug, den Gewinner sowie für jeden Spieler seine gesetzten Schiffe, deren Treffer und seine Schüsse auf den Gegner.

1. **Warten (`waiting`):** Es fehlen noch Spieler. Spielaktionen sind gesperrt.
2. **Platzieren (`placing`):** Jeder Spieler reicht seine vollständige Flotte ein. Die Platzierungen müssen nicht abwechselnd erfolgen. Eine ungültige Flotte wird vollständig abgelehnt; es bleibt kein Teil davon gesetzt.
3. **Schiessen (`shooting`):** Sobald beide Flotten gültig stehen, beginnt A. Der Spieler am Zug nennt ein noch nicht beschossenes gegnerisches Feld. Der Kern entscheidet über Wasser (`miss`), Treffer (`hit`) oder versenkt (`sunk`).
4. **Beendet (`finished`):** Der letzte Treffer hat alle gegnerischen Schiffe versenkt. Der Schütze gewinnt.

Nach jedem gültigen Schuss wechselt der Spieler, auch bei einem Treffer oder einem versenkten Schiff. Ein Schiff ist versenkt, wenn alle seine Felder getroffen wurden. Ein abgelehnter Schuss verändert weder Treffer noch Zugfolge.

Die Ausgabe verwendet Koordinaten A1 bis J10. ASCII-Kleinbuchstaben und führende Nullen werden bei Eingaben vereinheitlicht: `a01` bezeichnet A1 und erlaubt keinen zweiten Schuss auf dasselbe Feld.

## Ungültige Aktionen

| Aktion / Grund | Prüfung im Kern |
|---|---|
| Platzieren ausserhalb der Platzierungsphase | `BattleshipGame.place_fleet`, `WRONG_PHASE` |
| Flotte des Spielers steht schon | `BattleshipGame.place_fleet`, `WRONG_PHASE` |
| Falsche Anzahl, fehlende/doppelte oder unbekannte Schiffstypen | `validate_placement`, `INVALID_PLACEMENT` |
| Ungültiger Start oder ungültige Richtung | `validate_placement` / `ship_cells`, `INVALID_PLACEMENT` |
| Überlappung oder Rasterüberstand | `validate_placement`, `INVALID_PLACEMENT` |
| Schiessen vor beiden Flotten oder nach Spielende | `BattleshipGame.check_shot`, `WRONG_PHASE` |
| Falscher Spieler am Zug | `BattleshipGame.check_shot`, `NOT_YOUR_TURN` |
| Fehlendes, falsch typisiertes oder ausserhalb liegendes Feld | `BattleshipGame.check_shot`, `CELL_OUT_OF_BOUNDS` |
| Bereits beschossenes Feld | `BattleshipGame.check_shot`, `DUPLICATE_SHOT` |

Unbekannte Spieler lehnt der Kern mit `INVALID_PLAYER` ab. Im Netzwerk vergibt der Server die Identität anhand der Verbindung; ein Client kann sie nicht durch ein zusätzliches Feld ändern. Ungültiges JSON, unbekannte Nachrichtentypen und Anfragen vor dem Beitritt sind Protokollfehler, beschrieben in [PROTOKOLL.md](PROTOKOLL.md).

## Verborgene Information

Ein Spieler sieht seine eigenen Schiffe und deren Treffer sowie die Ergebnisse seiner eigenen Schüsse und alle gegnerischen Schüsse auf sein Raster (auch Fehlschüsse). Die gegnerischen Schiffspositionen werden nicht ausgegeben. `BattleshipGame.state(slot)` liefert diese Sicht als Kopie; eine Änderung der zurückgegebenen Daten verändert die Partie nicht.

## Ende, Zugunfähigkeit und Abbruch

Es gibt kein Unentschieden. Bei einem gültigen Schuss wird immer zuerst genau eine gegnerische Flotte vollständig versenkt. Vor diesem letzten Treffer steht dem Spieler am Zug mindestens ein unbeschossenes Feld zur Verfügung: Wer alle 100 Felder beschossen hat, hat bereits die gesamte gegnerische Flotte getroffen. Ein Aussetzen ist deshalb nicht vorgesehen.

Geht im Netzwerk ein Spieler, wird sein Platz sofort frei. Beide Flotten, Treffer, Schüsse und das bisherige Ergebnis werden verworfen. Der verbleibende Spieler wartet auf einen neuen Gegner; der nächste Beitritt beginnt eine neue Partie. Ein Abbruch vergibt keinen Gewinner. Im lokalen Spiel beendet q oder EOF die laufende Partie ohne Gewinner.

**Änderung zum Vorschlag:** Das ursprüngliche Spielwahlformular nennt noch eine mögliche Wartefrist von 30 Sekunden mit anschliessender Aufgabe. Für den aktuellen Kursmeilenstein gilt stattdessen der sofortige Reset mit Ersatzbeitritt. Das entspricht den geforderten Abbruch- und Wiederbeitrittsfällen. Eine Wiederverbindung zur alten Partie ist nicht Teil dieses Stands.

## Bedienung und Prüfungen

Eine Partie ohne Server startet mit `python3 src/local_game.py`. Jeder Spieler setzt seine Flotte und schiesst danach abwechselnd. Für eine Netzwerkpartie wird der Server mit zwei Instanzen von `client_gui.py` gestartet; `play.py` bleibt als Konsolendiagnose erhalten; Startbefehle stehen im [README](README.md).

`tests/meilenstein_02/test_board.py` prüft Brett und Platzierung. `tests/meilenstein_02/test_game.py` prüft Phasen, Zugfolge, Sieg, ungültige Aktionen, Reset und den im Vorschlag benannten schwierigen Fall: getrennte Spielersichten, die keine gegnerischen Schiffe enthalten und keine internen Daten verändern können. `tests/meilenstein_03/test_network.py` prüft diese Zuordnung zusätzlich über echte TCP-Verbindungen.

## Oberflächenskizze für die Spielwahl

Ursprüngliche Skizze; seit Kursmeilenstein 4 ist die GUI umgesetzt.
Host und Name werden beim Start als Argumente übergeben; die Platzierung
erfolgt über einzelne Start-/Richtungsfelder, der Schuss durch Klick im Zielraster:

```text
Schiffe versenken
Server: <server_ip>   Name: <spieler_name>   [Verbinden]
Status: warte auf Gegner / platzieren / A oder B ist am Zug

Eigene Flotte                  Schüsse auf den Gegner
    A B C D E F G H I J             A B C D E F G H I J
 1  . . . . . . . . . .          1  . . . . . . . . . .
 2  . . . . . . . . . .          2  . . . . . . . . . .
 …                               …
10  . . . . . . . . . .         10  . . . . . . . . . .

Platzierung: <schiffstyp> <startfeld> <richtung> [Flotte senden]
Schuss: <feld> [Schiessen]        Letzte Antwort / Fehler
[Verlassen]
```

Die beiden Raster zeigen nur die erlaubte Sicht. Eine ungültige Aktion und ein Verbindungsabbruch erscheinen in der Statuszeile. Die Skizze ergänzt das ursprüngliche Formular; Der aktuelle GUI-Stand gehört zur einzelnen Kursaufgabe 4 (im alten Projektablauf M6). Start und Bedienung stehen in `docs/guides/`.
