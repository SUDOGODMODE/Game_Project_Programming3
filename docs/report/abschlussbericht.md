# Technischer Abschlussbericht

Dieser Bericht beschreibt den fertigen Stand des Projekts: Regeln,
Architektur, Protokoll und die wichtigsten Entwurfsentscheidungen. Die
[persönliche Reflexion](meine_reflexion.md) ergänzt der Projektverantwortliche
separat.

## Ziel und Regeln

Zwei Spieler spielen Schiffe versenken über einen zentralen Python-Server.
Das 10×10-Brett verwendet A1 bis J10; die fünf Schiffe haben die Längen
5/4/3/3/2. A beginnt nach zwei gültigen Platzierungen. Jeder gültige Schuss
wechselt den Spieler, auch bei einem Treffer. Alle gegnerischen Schiffe zu
versenken beendet die Partie. Die [Regeln](../../REGELN.md) behandeln
Überlappung, Randüberschreitung, wiederholte Schüsse und Abbruch ausdrücklich.
Beim Verbindungsende wird sofort zurückgesetzt; der verbleibende Spieler
wartet auf Ersatz. Ein Reconnect einer abgebrochenen Partie ist nicht
vorgesehen.

## Architektur und Verantwortung

`src/spiel.py` enthält den netz- und fensterunabhängigen `BattleshipGame`;
`src/board.py` stellt lediglich den älteren Importnamen bereit.
`src/netz.py` liest und schreibt UTF-8-JSON-Zeilen. `src/server.py` bindet
Verbindungen an A/B, ruft den Kern auf und verteilt Antworten und Sichten.
`src/client_gui.py` stellt Eingaben und bestätigte Zustände dar. Die
Konsolenprogramme bleiben zum Spielen und zur Diagnose erhalten.

Der Spielkern entscheidet verbindlich über Platzierung, Schuss, Treffer,
Zugrecht und Sieg. Der Server bindet die Anfrage an den Slot der Verbindung
und hält die Spielsperre. Ein zusätzlicher vom Client behaupteter Slot oder Treffer
wird nicht zur Autorität. Die GUI sendet bei einem Klick eine Anfrage; sie
zeichnet einen Zug erst nach `state`. `draw_state` zeichnet alle Felder neu,
damit ein Reset keine alten Markierungen stehen lässt. Die eigene Flotte ist
privat; beide Spieler teilen nur Schussverlauf, Phase, Zug und Gewinner.

Die [Architekturübersicht](../development/architecture.md) zeigt den Datenfluss.
Die Anwendung braucht Python ≥3.12 und tkinter, keine zusätzlichen
Python-Laufzeitpakete. Andere Python-/Betriebssystemkombinationen gelten erst
nach tatsächlicher Ausführung als geprüft.

## Protokollentwurf

Das [Protokoll](../../PROTOKOLL.md) und sein
[JSON-Katalog](../protocol/protocol.json) enthalten Richtung, Pflichtfelder,
Fehler, Beispiele und eine vollständige 33-Schuss-Partie. JSON Lines trennt
mehrere Nachrichten auf einer langlebigen TCP-Verbindung ohne Annahmen über
einzelne `recv`-Pakete. `shoot` enthält nur das Zielfeld. Die Identität ergibt
sich aus der Verbindung, das Ergebnis aus dem Kern.

Nach einem erfolgreichen Beitritt, einer Platzierung oder einem Schuss
sendet der Server zuerst die direkte Antwort und danach jedem belegten Slot
seine vollständige Sicht. Beim Sieg folgt nach dem `result` zuerst der
individuelle Endzustand an beide und anschliessend `gameOver` an beide.
Nach Abbruch folgen `opponentLeft` und die neue
Wartesicht. Ablehnungen bleiben privat und verändern keinen Spielzustand.
`ownShips` enthält eigene Schiffe, `shotsAtOpponent` eigene Schüsse und
`shotsAtSelf` eingehende Schüsse einschliesslich Wasser. Ein fehlendes
Zielfeld bedeutet unbekannt/unbeschossen, nicht automatisch Wasser.

Die Zustände sind gefilterte Kopien. Eine vollständige Gegnerflotte darf
weder im Zustand des anderen Clients noch in gemeinsamen Serverlogs stehen.
Prüfungen müssen dafür tatsächliche Clientnachrichten betrachten; ein
Metadatenlog allein beweist die Payload-Geheimhaltung nicht.

## Kritischer Abschnitt und Threads

Eine Verbindung hat einen Empfangsthread. `game["lock"]` umfasst in `handle`
Prüfen, Ändern und Senden. Deshalb können zwei gleichzeitige Beitritte keinen
Slot doppelt belegen, und ein `state` gehört zu dem unter derselben Sperre
ausgeführten Zug. Die gleiche Sperre schützt das Freigeben und Zurücksetzen
bei Abbruch. Helfer wie `send_states` setzen die gehaltene Sperre voraus.
Der einfache Aufbau serialisiert auch den Versand; ein langsamer Client
kann damit andere Aktionen verzögern. Für das Zwei-Spieler-Unterrichtsprojekt
bleibt diese vorhandene Entscheidung erhalten und muss erklärbar sein.

Die GUI trennt Versand und Empfang vom Tk-Hauptthread. Worker kennen nur
Socket, Queues und Stop-Ereignis. `after` verarbeitet eingehende Nachrichten
im Hauptthread. Tk-Variablen und das PNG werden dort erzeugt und beim
Fensterschliessen dort freigegeben; spätere Garbage Collection in einem
Worker darf keine Tcl-Objekte beseitigen müssen.

## Robustheit gegenüber fehlerhaften Anfragen

Der Server bleibt bei ungültigen oder unerwarteten Anfragen stabil und
antwortet mit einem passenden Fehlercode, ohne den Spielzustand zu ändern:

| Angriff | Erwartetes beobachtbares Verhalten |
|---|---|
| Ungültiges JSON | `INVALID_JSON`, Server bleibt verwendbar |
| Falsch typisiertes Feld | Regel-/Formatfehler, Zustand bleibt gleich |
| Feld ausserhalb A1–J10 | `CELL_OUT_OF_BOUNDS`, Zustand und Zug bleiben gleich |
| Pflichtfeld fehlt | Passender Fehler, keine Zustandsänderung |
| Unbekannter Nachrichtentyp | `UNKNOWN_TYPE`, kein Serverabsturz |
| Schuss ausser der Reihe | `NOT_YOUR_TURN`, Ablehnung nur beim Absender |
| Verbindung mitten im Zug trennen | Einmal freigeben, sofort Reset, Ersatz möglich |

Weitere Tests prüfen Doppelbeschuss, vollständige Partien, Filterung,
Sichtkopien, Nebenläufigkeit und Fensterschliessen. Der portable Testmodus
darf einen fehlenden Bildschirm als Skip melden. `--require-gui` verlangt
tatsächlich ausgeführte GUI-Tests und macht fehlende GUI-Abnahme sichtbar.
Ein automatisch gespeicherter JSON-Bericht beschreibt genau seinen Lauf.

## Bild und Nachrichtenaufzeichnung

Das eigene Schiffsbild liegt in `bilder/`; seine
[Herkunftsdokumentation](../../bilder/README.md) nennt Werkzeug, Prompt,
tatsächliche Grösse und Darstellung. Es dekoriert die Oberfläche und enthält
keine Spielinformationen. Als Zusatzfunktion schreibt der Server ein dauerhaftes
JSONL-Metadatenlog mit ISO-Zeit, Richtung, Verbindung/Slot, bekanntem Typ und
servereigenem Fehlercode. Ganze Payloads und freie Clienttexte werden nicht
geschrieben. Neue Logdateien werden exklusiv erzeugt und nicht überschrieben.

## Vorführung

Der [Vorführleitfaden](vorfuehrung.md) beschreibt die wiederholbaren Schritte,
mit denen sich das fertige Spiel vorführen lässt.
