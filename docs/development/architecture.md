# Architektur und Datenfluss

Python >=3.12, Standardbibliothek. `src/spiel.py` enthält den netzfreien
Spielkern und entscheidet über die Spielregeln. Der Server bindet Aktionen an
Verbindungen und verteilt ausschliesslich die vom Kern erzeugten Sichten.

```mermaid
flowchart LR
    A[GUI A] -->|Ausgangsqueue und Sendethread| S[Server mit Spielsperre]
    B[GUI B] -->|Ausgangsqueue und Sendethread| S
    Z[GUI Zuschauer, unverändert] -->|Anfragen über TCP| S
    S --> K[spiel.BattleshipGame]
    K --> S
    S -->|Sicht A über TCP, Empfangsqueue, after| A
    S -->|Sicht B über TCP, Empfangsqueue, after| B
    S -->|Öffentliche Sicht über TCP, Empfangsqueue, after| Z
```

| Datei | Aufgabe |
|---|---|
| `src/spiel.py` | Koordinaten, Flottenprüfung, Platzierung, Schüsse, Zugfolge, Sieg, gefilterte Kopien; keine Netz-, Tk- oder Threadimporte |
| `src/board.py` | Kompatibilitätseinstieg für ältere Importe; keine zweite Regelimplementierung |
| `src/netz.py` | UTF-8-JSON-Zeilen senden/lesen, ungültige Objekte markieren, Verbindungsende behandeln |
| `src/server.py` | Spieler und separate Zuschauer an Verbindungen binden, gemeinsame Sperre, private Antworten, Zustandsverteilung, Reset bei Spielerabgang |
| `src/event_log.py` | Exklusiv erzeugtes JSONL-Metadatenlog, Schreibsperre, Flush und geschütztes Schliessen |
| `src/client_gui.py` | Eingaben senden, bestätigte Zustände vollständig anzeigen, GUI-Lebenszyklus |
| `src/gui/client_view.py` | Brettzeichen und Schiffsausschnitte rein aus dem bestätigten Zustand berechnen; ohne Tk |
| `src/fleet_setup.py` | Gültige zufällige Platzierung ohne Tk erzeugen; ein gesetzter Zufallsgenerator macht Tests reproduzierbar |
| `src/gui/sea_cell.py` | Canvas-Rasterfelder, Schiffsausschnitte, Schussmarkierungen und Tastaturbedienung |
| `src/gui/ship_art.py` | Fünf SVG-Quellen laden, Grundformen skalieren und auf Canvas zeichnen |
| `src/gui/ship_effects.py` | Neue eigene Schiffsverluste erkennen und zeitlich begrenzte lokale Sprengungen zeichnen |
| `src/play.py` / `src/client.py` | Konsolenspiel bzw. Lobbydiagnose |
| `src/local_game.py` | Spielkern an einer Tastatur bedienen |
| `src/echo_*.py` | Separater einfacher TCP-Grundversuch |

`spiel.py`, `netz.py`, `test_spiel.py`, `test_netz.py` und
`tests/network/test_angriff.py` tragen Name und deutsche
Testbeschreibungen wörtlich aus der Aufgabenstellung; sie bleiben deshalb
bewusst unverändert. Alle eigenen Dateien und Bezeichner — auch die
Funktionen und Klassen innerhalb dieser Vorlagedateien selbst — sind
durchgehend Englisch benannt.

## Server

Ein Thread pro Verbindung liest Nachrichten. Eine gemeinsame Sperre umfasst
Prüfen, Ändern und Senden. So wird kein freier Platz doppelt vergeben und
jede Zustandsmeldung gehört zur unter derselben Sperre ausgeführten Aktion.
Helfer dokumentieren, dass die Sperre bereits gehalten sein muss.

Der erste freie Platz A/B wird serverseitig vergeben. Spätere Nachrichten
verwenden die Identität der Verbindung; zusätzliche Slotfelder wählen keinen
anderen Spieler. Direkte Antworten gehen vor den dazugehörigen Zuständen
hinaus. Nach join, place, shoot und Reset folgt die vollständige erlaubte
Sicht jedes verbundenen Spielers und die öffentliche Sicht an alle Zuschauer.
Beim siegreichen Schuss gehen nach `result` zuerst die gefilterten
Endzustände an Spieler und Zuschauer, danach `gameOver` an alle.
Fehler gehen nur an den Absender und verändern den Spielzustand nicht.

Meilenstein 7 ergänzt eine separate Zuschauerliste unter derselben
Spielsperre. Sind A und B belegt, erhält ein neuer Client `spectator` mit
`player` und aktueller `phase`, ohne `slot`, danach sofort den öffentlichen
`state`. Zuschauer stehen nie in der Spielerliste und werden auch nach
Spielerabgang nicht befördert. `place` und `shoot` lehnt der Server privat
mit `SPECTATOR_ONLY` ab; `getState` und `leave` bleiben erlaubt. Rundrufe
für `gameStart`, `gameOver` und `opponentLeft` umfassen Zuschauer.

## Geheimhaltung

`BattleshipGame.state(slot)` liefert eine unabhängige Kopie:

- `ownShips`: eigene Schiffsfelder und Treffer;
- `shotsAtOpponent`: eigene Schüsse mit Ergebnissen;
- `shotsAtSelf`: alle gegnerischen Schüsse auf das eigene Raster;
- `phase`, `turn`, `winner`: gemeinsamer Ablauf.

Die vollständige Gegnerflotte wird nicht übertragen. Die Spieler zeigen
denselben öffentlichen Verlauf und unterschiedliche private Flotten.
Die dritte Sicht nutzt dasselbe `state`-Format: `ownShips = []`,
`shotsAtSelf` = B auf A (links), `shotsAtOpponent` = A auf B (rechts).
Sie enthält auch nach Spielende keine Flotten. Unbeschossene Felder sind
unbekannt, nicht Wasser. Ein später Zuschauerbeitritt erhält diese Sicht
sofort; eine reine Kopie eines Spielerzustands wäre eine Datenfreigabe.
Serverlogs enthalten nur bekannte Typnamen, Adressen, Slots und eigene
Fehlercodes. Isolierte Testmitschnitte mit beiden Testsichten sind als
Testdaten gekennzeichnet.

Jedes `new_game()` besitzt ein `EventLog`; der Server erzeugt standardmässig
einen neuen UTC-Zeitstempelpfad mit Zufallssuffix unter projektlokalem `logs/`.
`--log-file` wählt eine ausdrücklich neue Datei. Empfangene Nachrichten
einschliesslich `broken` und jede erfolgreich gesendete Nachricht werden mit
ISO-Zeit, Richtung, Verbindung/Slot und erlaubten Metadaten geschrieben.
`EventLog` verwendet eine eigene Schreibsperre und flusht jede JSON-Zeile.
Der Logwriter greift nie auf die Spielsperre zu; dadurch entsteht keine
umgekehrte Sperrenreihenfolge. Beim regulären Serverende werden Sockets
beendet und Worker abgewartet, danach wird das Log geschlossen. Späte
Schreibversuche während des Shutdowns berühren keinen geschlossenen Handle.
Das Log ist eine Nachrichtenchronik, kein gespeicherter Spielzustand.

## Oberfläche und Abbruch

Ein Klick stellt eine Anfrage in die Ausgangsqueue; ein Sendethread führt
den Socketversand aus. Der Empfangsthread schreibt in die Eingangsqueue.
`after` ruft deren nicht blockierende Leerung im Tk-Hauptthread auf. Alle
Widgetzugriffe bleiben dort. `client_view.board_symbols` berechnet die
Zeichen ohne Widgetzugriff; `draw_state` zeichnet danach beide Raster
vollständig. `fleet_setup.random_placement` erzeugt nur den Vorschlag, und
die Tk-Klasse setzt ihn in die Eingabefelder.
Die Platzierungsfelder sind ein Entwurf, keine verbindliche Brettanzeige.

Die Meerblau-Oberfläche verwendet pro Feld einen `SeaCell`-Canvas. Eigene
Schiffe werden als zusammenhängende SVG-Grafik gezeichnet: Jede belegte
Zelle erhält das ganze Schiff mit passendem Versatz, und die Canvas-Grenze
schneidet ihren Ausschnitt aus. `ship_art.py` liest die fünf Quellen aus
`bilder/flotte/` mit `ElementTree` und zeichnet deren elementare SVG-Formen.
Die Quelldaten werden je Typ zwischengespeichert; Skalierung und eine
optionale Drehung um 90 Grad erfolgen ohne Zusatzpakete. Die Gegnerflotte
wird dadurch nicht sichtbar. Punkt, X und Doppelring bezeichnen Wasser,
Treffer und den versenkenden Treffer. Intern bleiben die Feldsymbole
`·`, `X` und `#` erhalten. Pfeiltasten verschieben den Zielrasterfokus;
Enter und Leertaste senden dieselbe Schussanfrage wie ein Klick.

`ShipEffects` vergleicht ausschliesslich die eigenen `ownShips` aufeinander
folgender bestätigter Zustände. Ein zuvor bekanntes, noch nicht vollständig
getroffenes Schiff löst beim ersten vollständigen Treffer eine lokale
Sprengung von rund 1,15 Sekunden aus. Der erste Zustand ist nur die
Ausgangslage; wiederholte Zustände spielen nichts erneut ab. Ein Schiff
wird durch Typ und seine Felder erkannt. Die Animation verwendet
`after`-Callbacks im Tk-Hauptthread und verändert keine Nachrichten oder
Spielregeln. Der Schalter „Sprengungseffekte“ stoppt laufende Bilder;
während der Abschaltung erkannte Verluste werden beim Einschalten nicht
nachgeholt. Reset, Verbindungsende und `close` entfernen Effektobjekte und
geplante Callbacks.

Das eigene PNG wird aus einem von `__file__` ausgehenden absoluten Pfad
geladen. Die 256×256-Pixel-Datei wird mit `subsample(4)` als 64×64-Pixel-
Dekoration angezeigt. `ship_image` hält die Referenz während der gesamten
Fensternutzung. `close` löst die Widgetzuordnung und gibt `PhotoImage` noch
im Tk-Hauptthread frei, bevor es das Root zerstört. Netzwerkworker erhalten
weiterhin keine Referenz auf das Fenster oder auf Tk-Objekte.

Der Client bleibt für Meilenstein 7 unverändert: Queue, `after`, Zeichnen
und Klickversand gelten auch für das Zuschauerfenster. Spielerbezogene
Raster-, Status- und Endtexte sind dort teilweise unpassend. Die angefragte
Anzeigeänderung ist nicht freigegeben; die Rolle wird nur serverseitig entschieden.

Das Fensterkreuz schliesst Socket und Fenster. Bei einem **Spieler** räumt
der Server den Platz einmalig auf und setzt die Partie zurück. Verbliebener
Spieler und Zuschauer erhalten `opponentLeft` und den leeren `waiting`-Zustand;
ein neuer Spieler startet eine frische Platzierung. Zuschauer bleiben in
ihrer Rolle. Ein **Zuschauerabgang** entfernt nur dessen Listeneintrag, ohne
Reset oder Nachricht an Spieler. Ein fehlgeschlagener Zuschauerversand darf
die Zustellung an Spieler nicht abbrechen. Kein Reconnect und keine
Wiederherstellung einer abgebrochenen Partie.

Vorgesehen ist ein Zweipersonenspiel mit Zuschauern im Unterrichtsnetz. Authentifizierung,
Verschlüsselung, mehrere Tische und persistente Partien sind nicht
Bestandteil des Projekts.
