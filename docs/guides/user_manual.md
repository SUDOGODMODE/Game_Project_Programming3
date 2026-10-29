# Schiffe versenken bedienen

Server und zwei Fenster wie in der [Startanleitung](setup.md) öffnen. Der
Server vergibt die Plätze A und B; der Name ist eine Anzeige, kein eigener
Spielzugschlüssel. Der erste Spieler wartet auf den zweiten.

Beide Fenster dürfen auf demselben Gerät oder auf getrennten Geräten laufen.
Lokal startest du Server und zwei Clients in drei Terminals mit `127.0.0.1`;
dafür brauchst du nach der Einrichtung keine weitere Infrastruktur. Beim
Ausprobieren wechselst du zwischen beiden Fenstern. Zwei Personen an einem
gemeinsamen Bildschirm müssen die private Flottenansicht des anderen
respektieren; getrennte Geräte vermeiden dieses Mitlesen am selben Bildschirm.

## Flotte setzen

Jeder Spieler hat fünf Schiffe mit Längen 5, 4, 3, 3 und 2. In den
Platzierungsfeldern pro Schiff ein Startfeld und die Richtung wählen:
`h` legt nach rechts, `v` nach unten. A1 liegt links oben, J10 rechts unten.
Alle Schiffe müssen vollständig im 10×10-Raster liegen und dürfen sich
nicht überlappen. Berührungen sind erlaubt.

Die vorgeschlagenen Koordinaten sind ein veränderbarer Entwurf. Erst
„Flotte senden“ reicht sie beim Server ein. Vor der Bestätigung wird kein
Schiff auf dem Spielfeld als gesetzt dargestellt. Bei Ablehnung den
angezeigten Grund lesen, den Entwurf korrigieren und erneut senden.
Eine angenommene Flotte kann in derselben Partie nicht erneut gesetzt werden.

## Spielen

Die Oberfläche ist in Meerblau gehalten. Links steht die eigene bestätigte
Flotte als Schiffsgrafiken mit den gegnerischen Schüssen; rechts die eigenen
Schüsse auf den Gegner. Die Gegnerflotte bleibt verdeckt. Die
Koordinatenbeschriftung gehört jeweils zum eigenen Raster.

| Markierung | Bedeutung |
|---|---|
| Leeres Zielfeld | Noch unbekannt |
| Schiffsgrafik links | Eigenes bestätigtes Schiff |
| Punkt | Wasser / Fehlschuss |
| X im Treffersymbol | Treffer |
| Doppelring um den Treffer | Dieser Schuss hat das Schiff versenkt |

Frühere Treffer desselben Schiffs behalten ihr X. Der Doppelring markiert
das Feld des letzten Treffers.

Sobald beide Flotten gesetzt sind, beginnt A. Im Zielraster das gewünschte
Feld anklicken. Alternativ mit Tab ein Zielfeld fokussieren, mit den
Pfeiltasten im Zielraster wechseln und mit Enter oder Leertaste schiessen.
Die türkise Umrandung zeigt das fokussierte oder mit der Maus angewählte
Zielfeld. Beide Bedienwege senden eine Anfrage; erst die Serverantwort
ändert beide erlaubten Ansichten. Jeder gültige Schuss wechselt den
Spieler, auch ein Treffer. Die Statuszeile zeigt, wer am Zug ist.

Schüsse ausser der Reihe, ausserhalb des Rasters oder auf ein bereits
beschossenes Feld lehnt der Server mit einem Grund ab. Die Fehlermeldung
erscheint nur beim Absender; Brett und Zugfolge bleiben unverändert.
Wer zuerst alle 17 gegnerischen Schiffsfelder trifft, gewinnt.

Wird eines deiner Schiffe durch einen bestätigten neuen Treffer vollständig
versenkt, erscheint nur in deiner eigenen Flottenansicht einmalig eine rund
1,15 Sekunden lange Sprengung mit Funken, Druckring und Rauch. Sie verändert
keine Spielregeln. Bereits versenkte Schiffe beim ersten empfangenen Zustand
und wiederholte Zustandsmeldungen spielen die Animation nicht nochmals ab.
Mit „Sprengungseffekte“ kannst du sie ausschalten und laufende Bilder sofort
beenden. Beim erneuten Einschalten werden vergangene Verluste nicht nachgeholt.

## Beenden und neu beginnen

Das Fenster mit dem Fensterkreuz schliessen. Der Gegner wird informiert,
und die bisherige Partie wird zurückgesetzt. Er bleibt mit dem Server
verbunden. Ein neu gestarteter Ersatzclient belegt den freien Platz;
beide Spieler setzen ihre Flotten für eine neue Partie.

Bei einem erkannten Serverabbruch zeigt die GUI das Verbindungsende.
Für eine neue Verbindung das Fenster schliessen und den Client erneut
starten. Eine alte Partie wird nach einem Abbruch nicht wiederhergestellt.

Reset, Verbindungsende und Fensterschliessen beenden laufende
Sprengungseffekte und entfernen ihre Bilder.

Die verbindlichen Regeln stehen in [REGELN.md](../../REGELN.md), die
Nachrichten in [PROTOKOLL.md](../../PROTOKOLL.md).
