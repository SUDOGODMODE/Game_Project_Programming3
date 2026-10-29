# Schiffe versenken — Protokoll 0.5

Katalog des lokalen A/B-Protokolls für Kursmeilenstein 4, Version 0.5; strukturierte Fassung: [protocol.json](docs/protocol/protocol.json). Das Gegenlesen steht aus. Die Beispiele erläutern das Format; Ausführungsnachweise stehen unter `docs/evidence/`.

## Transport und Identität

TCP/IPv4, UTF-8, JSON Lines: Ein JSON-Objekt pro Zeile, abgeschlossen mit einem LF-Byte (`\n`). Ein `recv()` kann Teile einer Nachricht oder mehrere Nachrichten enthalten; `netz.read_messages` setzt Zeilen zusammen. Leere Zeilen werden ignoriert. Jedes Objekt enthält `type`. Ungültiges JSON und JSON-Werte, die keine Objekte sind, führen zu `error`/`INVALID_JSON`; `broken` ist nur der interne Transportmarker.

Standardport: 5000. Server: `0.0.0.0`, Clients lokal: `127.0.0.1`; Host und Port sind Startargumente. Für fremde Rechner ist die echte Serveradresse nötig. Der Server vergibt den ersten freien Slot `A`, dann `B`. Der Name aus `join` ist keine Zug-Identität: weitere Aktionen gehören zur bestehenden Verbindung, zusätzliche Slot-/Spielerfelder wählen keinen anderen Spieler.

Clients lesen dauerhaft in einem Empfangsthread und unterscheiden die Nachrichten anhand von `type`. Nach Beitritt, erfolgreicher Platzierung, erfolgreichem Schuss und Partierücksetzung sendet der Server ungefragt einen vollständigen `state` an jeden verbundenen Spieler, jeweils mit dessen erlaubter Sicht. `getState` bleibt als zusätzliche Abfrage erhalten und antwortet nur dem Anfragenden. Clients dürfen deshalb keine feste Eins-zu-eins-Zuordnung zwischen Anfrage und nächster Nachricht annehmen.

`shoot` ist die Zuganforderung (`move` im Unterrichtsbeispiel); es gibt keine zusätzliche Nachricht `move`. Der grafische Client schickt Anfragen und zeichnet ausschliesslich empfangene Zustände. Sein Netzthread legt Nachrichten in eine Queue, der Tk-Hauptthread verarbeitet sie. Harte Socket-Abbrüche beenden den Nachrichtenleser wie EOF. Server-Terminalausgaben enthalten nur Metadaten (Richtung, Verbindung/Slot, Typ und gegebenenfalls Fehlercode), keine Flotten oder Zustands-Payloads. Für die Geheimhaltungsprüfung werden die tatsächlich am jeweiligen Client empfangenen Daten getrennt geprüft; eine Metadatenausgabe allein beweist die Filterung nicht.

## Nachrichtenaufzeichnung auf dem Server

Die Drahtnachrichten bleiben Version 0.5. Zusätzlich erzeugt jeder
Serverstart eine neue JSONL-Datei unter projektlokalem `logs/`; `--log-file`
wählt eine ausdrücklich neue Datei. Es gibt kein Anhängen an frühere Logs.
Pro empfangener und erfolgreich gesendeter Nachricht wird eine vollständige,
sofort geflushte JSON-Zeile geschrieben: `timestamp` (UTC-ISO-Zeit mit
Zeitzone), `direction` (`<-`/`->`), `peer` (Verbindung oder Slot), `slot`
(`A`/`B` oder `null` vor Anmeldung) und `type` (bekannter Typ oder `unknown`).
Nur bei ausgehenden Serverfehlern kommt ein bekannter `code` hinzu.
Ungültiges JSON erscheint als interner Typ `broken`. Namen, Flotten,
Zustands-Payloads und freie Clienttexte werden nicht protokolliert.
Die Datei dokumentiert Nachrichtenmetadaten, keine wiederherstellbare Partie.

## Nachrichtenkatalog

Alle genannten Felder sind Pflichtfelder für den beschriebenen Nachrichtentyp; `null` ist ein vorhandener Wert, kein weggelassenes Feld. C = Client, S = Server. Zusätzliche Felder sind kein Mittel zur Wahl der Spieleridentität.

| Typ | Richtung | Pflichtfelder ausser `type` | Anlass / Empfänger | Ungefragt |
|---|---|---|---|---|
| `join` | C → S | `player` | Ein neuer Client meldet sich auf seiner TCP-Verbindung an. | nein |
| `welcome` | S → C | `slot`, `player`, `phase` | Direkte Antwort auf einen erfolgreichen join; nur an den beitretenden Client. | nein |
| `waiting` | S → C | `reason` | Nach welcome an den ersten/alleinigen beigetretenen Spieler. | ja |
| `gameStart` | S → C | `phase`, `players` | Der zweite Spieler hat erfolgreich join abgeschlossen. Nach dessen welcome an beide verbundenen Spieler. | ja |
| `place` | C → S | `ships` | Ein beigetretener Spieler platziert in phase placing einmal seine vollständige Flotte. | nein |
| `placeAck` | S → C | `phase` | Direkte Bestätigung einer erfolgreichen place-Anfrage; nur an den Absender. | nein |
| `shoot` | C → S | `field` | Der Spieler am Zug wählt in phase shooting ein noch nicht beschossenes Feld. | nein |
| `result` | S → C | `field`, `result`, `sunk`, `turn` | Direkte Antwort auf eine erfolgreiche shoot-Anfrage; nur an den Schützen. | nein |
| `getState` | C → S | keine | Ein bereits beigetretener Client fragt seinen aktuellen, gefilterten Zustand ab. | nein |
| `state` | S → C | `phase`, `turn`, `ownShips`, `shotsAtOpponent`, `shotsAtSelf`, `winner` | Nach Beitritt, erfolgreicher Platzierung, erfolgreichem Schuss oder Reset an jeden verbundenen Spieler; auf getState nur an den Anfragenden. Immer individuell gefiltert. | ja, auch Antwort auf getState |
| `leave` | C → S | keine | Ein beigetretener Client verlässt die Runde bewusst. | nein |
| `opponentLeft` | S → C | `slot`, `player` | Ein beigetretener Spieler geht per leave, q, EOF oder erkanntem Socket-Abbruch; einmal an den verbliebenen Spieler. | ja |
| `gameOver` | S → C | `winner`, `reason` | Sobald der letzte erfolgreiche Schuss die gesamte gegnerische Flotte versenkt; nur an den unterlegenen Gegner. | ja |
| `error` | S → C | `code`, `message` | Eine Anfrage ist ungültig oder passt nicht zum aktuellen Zustand; nur an ihren Absender. | nein |

### join

```json
{"type":"join","player":"Alice"}
```

`type`: string, genau join; `player`: string, nicht leer und nicht nur Leerzeichen

Antwort: `welcome` oder `error`. Slotvergabe und Identität sind unter «Transport und Identität» beschrieben.

### welcome

```json
{"type":"welcome","slot":"A","player":"Alice","phase":"waiting"}
```

`type`: string, genau welcome; `slot`: A oder B; `player`: string, übernommener Name; `phase`: waiting oder placing

Ein alleiniger Spieler bekommt phase waiting. Der zweite bekommt phase placing. welcome steht auf seiner Verbindung vor waiting bzw. gameStart und dem anschliessenden state.

### waiting

```json
{"type":"waiting","reason":"warte auf Gegner"}
```

`type`: string, genau waiting; `reason`: string, warte auf Gegner

Eigene Servermeldung ohne waiting-Anfrage. Nach einem Abgang informiert opponentLeft; es wird dann kein zusätzliches waiting gesendet.

### gameStart

```json
{"type":"gameStart","phase":"placing","players":[{"slot":"A","player":"Alice"},{"slot":"B","player":"Bob"}]}
```

`type`: string, genau gameStart; `phase`: placing; `players`: Liste der beiden Objekte {slot: A/B, player: string}, sortiert A dann B

Auch der zuvor wartende Client empfängt dies, ohne etwas zu senden. Danach erhalten beide je ihren state in phase placing. Nach einem Ersatzbeitritt beginnt eine frische Runde.

### place

```json
{"type":"place","ships":[{"type":"Carrier","start":"A1","direction":"h"},{"type":"Battleship","start":"A2","direction":"h"},{"type":"Cruiser","start":"A3","direction":"h"},{"type":"Submarine","start":"A4","direction":"h"},{"type":"Destroyer","start":"A5","direction":"h"}]}
```

`type`: string, genau place; `ships`: Liste mit genau fünf Objekten; pro Objekt type (Schiffstyp), start (Feld), direction (h oder v)

Die Flotte muss den unten beschriebenen Spielregeln entsprechen. Antwort: `placeAck` oder `error`.

### placeAck

```json
{"type":"placeAck","phase":"placing"}
```

`type`: string, genau placeAck; `phase`: placing oder shooting

Nach der zweiten gültigen Platzierung ist phase shooting und A beginnt. Nur der Absender bekommt placeAck; danach erhalten beide automatisch ihren vollständigen state. Eine abgelehnte Platzierung erzeugt nur error an den Absender und keinen state-Push.

### shoot

```json
{"type":"shoot","field":"C5"}
```

`type`: string, genau shoot; `field`: string, ASCII-Feld A1–J10; Kleinbuchstaben und führende Nullen werden kanonisiert

Der Server prüft Phase, Zug, Feld und Doppelbeschuss. Antwort: `result` oder `error`. Nach einem erfolgreichen Schuss folgen die gefilterten Zustände für beide; nach einer Ablehnung erhält ausschliesslich der Absender error, der Spielstand bleibt unverändert.

### result

```json
{"type":"result","field":"C5","result":"miss","sunk":null,"turn":"B"}
```

`type`: string, genau result; `field`: beschossenes Feld, kanonisch A1–J10; `result`: miss, hit oder sunk; `sunk`: Schiffstyp bei sunk, sonst null; `turn`: A/B als nächster Spieler; null bei Spielende

Beim letzten Treffer sind `result: "sunk"` und `turn: null` gesetzt. Der Gewinner erhält kein zusätzliches `gameOver`. Nach result und gegebenenfalls gameOver folgen die vollständigen state-Nachrichten an beide Spieler.

### getState

```json
{"type":"getState"}
```

`type`: string, genau getState

Antwort: genau ein `state` an den anfragenden Spieler. Andere Spieler erhalten durch diese Abfrage keine Nachricht; die Abfrage ändert den Zustand nicht.

### state

```json
{"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
```

`type`: string, genau state; `phase`: waiting, placing, shooting oder finished; `turn`: A/B oder null; `ownShips`: Liste eigener Schiffe: {type, cells: Feldliste, hits: Feldliste}; `shotsAtOpponent`: Objekt Feld -> miss/hit/sunk für eigene Schüsse; `shotsAtSelf`: Objekt Feld -> miss/hit/sunk für **alle** gegnerischen Schüsse auf das eigene Raster, einschliesslich Fehlschüssen; `winner`: A/B oder null.

Dies ist immer die vollständige erlaubte Sicht, keine Änderungsnachricht. Beide Raster haben 100 Felder A1–J10; es wird kein öffentliches board mit Gegnerflotte übertragen.

- Ein fehlender Schlüssel in shotsAtOpponent bedeutet **noch nicht beschossen, Inhalt unbekannt**, nicht Wasser. Ein fehlender Schlüssel in shotsAtSelf bedeutet **noch nicht vom Gegner beschossen**.
- Nach eigener gültiger Platzierung ist ein Feld ausserhalb der eigenen ownShips Wasser. Leere ownShips bedeuten vor der eigenen gültigen Platzierung oder nach Reset, dass noch keine Flotte gesetzt ist.
- miss bedeutet Fehlschuss, hit bedeutet Treffer, sunk bedeutet, dass genau dieser Schuss ein Schiff versenkt hat. Frühere hit-Einträge werden beim Versenken nicht nachträglich zu sunk geändert. ownShips.hits enthält alle getroffenen Felder des jeweiligen eigenen Schiffs.
- Die eigene Flotte ist sichtbar; unbekannte gegnerische Positionen werden auch nach Partieende nicht übertragen. shotsAtSelf ist die Kopie der gegnerischen Schussliste und verrät keine gegnerischen Schiffe.

Nach opponentLeft folgt ein state mit phase waiting, leeren ownShips, shotsAtOpponent und shotsAtSelf sowie turn und winner jeweils null. Ein Client zeichnet aus jeder Zustandsnachricht beide Raster vollständig neu.

### leave

```json
{"type":"leave"}
```

`type`: string, genau leave

Keine direkte Bestätigung. Die Verbindung wird geschlossen und derselbe Aufräumablauf wie bei EOF/Socket-Abbruch ausgeführt. q im Lobbyclient beendet die Verbindung ebenfalls.

### opponentLeft

```json
{"type":"opponentLeft","slot":"B","player":"Bob"}
```

`type`: string, genau opponentLeft; `slot`: A oder B, der abgegangene Slot; `player`: string, Name des abgegangenen Spielers

Der Server gibt den Slot frei und setzt die Runde zurück; siehe «Reihenfolge und Abbruch».

### gameOver

```json
{"type":"gameOver","winner":"A","reason":"sunk"}
```

`type`: string, genau gameOver; `winner`: A oder B; `reason`: sunk

Der Gewinner erkennt das Spielende an `result` mit `turn: null`. Danach erhalten beide automatisch ihren gefilterten Endzustand; winner im state benennt denselben Gewinner. Eine zusätzliche getState-Abfrage bleibt möglich.

### error

```json
{"type":"error","code":"UNKNOWN_TYPE","message":"unbekannter Typ: nonsense"}
```

`type`: string, genau error; `code`: einer der unten dokumentierten Fehlercodes; `message`: string, lesbarer Grund

Ungültige JSON-Zeilen und JSON-Werte ohne Objektstruktur werden mit `INVALID_JSON` abgelehnt.

## Flotte und Spielregeln

Raster 10×10, ausgegebene Koordinaten kanonisch `A1`–`J10`. Eingaben wie `a01` werden zu `A1` normalisiert; Kleinbuchstaben und führende ASCII-Nullen sind erlaubt, Unicode-Ziffern nicht. Doppelbeschuss wird nach Normalisierung geprüft. Platzierung: `h` nach rechts, `v` nach unten. Je ein Carrier (5), Battleship (4), Cruiser (3), Submarine (3) und Destroyer (2), insgesamt 17 Felder. Keine Überlappung oder Überschreitung des Rasters; angrenzende Schiffe sind erlaubt. Diese klassische Flotte ist im [Regelblatt](REGELN.md) festgelegt.

Phasen: `waiting` → `placing` → `shooting` → `finished`. Nach beiden gültigen Platzierungen beginnt `A`; jeder gültige Schuss wechselt den Spieler. Treffer erlauben keinen Extrazug. Doppelbeschuss ist ungültig. Sind alle gegnerischen Schiffe versenkt, gewinnt der Schütze; kein Unentschieden. Jeder `state` enthält ausschliesslich eigene Schiffe/Treffer, eigene Schüsse und alle eingegangenen Schüsse, keine Gegnerflotte.

## Reihenfolge und Abbruch

- Erster Beitritt: welcome, waiting, danach state an den beitretenden Client.
- Zweiter Beitritt: dessen welcome, danach gameStart an beide, danach je ein individueller state an beide.
- Platzierung: placeAck nur an den Akteur; danach je ein individueller state an beide.
- Schuss: result nur an den Akteur. Beim letzten Treffer danach gameOver nur an den Gegner. Anschliessend je ein individueller state an beide.
- Ablehnung: error mit Grund ausschliesslich an den Absender, kein state-Push und keine Zustandsänderung.
- getState: ein individueller state ausschliesslich an den Anfragenden.
- Abgang: einmal opponentLeft an den Verbliebenen, danach dessen zurückgesetzter state. Kein zusätzlicher waiting-Nachrichtentyp.

Prüfen, Ändern und Senden liegen zusammen unter derselben Spielsperre. Zustände werden für jeden verbundenen Slot aus unabhängigen Kopien der erlaubten Sicht erzeugt. Die beschriebene Ereignisreihenfolge gilt je TCP-Verbindung. Eine Reihenfolge zwischen verschiedenen Clientverbindungen und eine zeitgleiche Anzeige auf verschiedenen Rechnern werden nicht zugesichert.

Bei `leave`, `q`, EOF oder erkanntem Socket-Abbruch wird der Slot freigegeben und die gesamte Runde sofort zurückgesetzt: beide Flotten/Treffer und Schusslisten leer, `phase: "waiting"`, `turn: null`, `winner: null`. Der Verbliebene bleibt verbunden und erhält diesen Zustand unmittelbar als Push. Beim nächsten Beitritt wird der freie Slot vergeben, `gameStart` startet eine frische Platzierung. Keine Wiederverbindungsfrist, kein `forfeit`-Sieg, keine automatische Wiederaufnahme. Ein physischer Verbindungsverlust wird erst behandelt, wenn die Socket-Schicht ihn erkennt.

## Fehlercodes

| Code | Anlass |
|---|---|
| `GAME_FULL` | Ein dritter Spieler versucht beizutreten. |
| `ALREADY_JOINED` | Diese Verbindung hat bereits einen Slot. |
| `MISSING_PLAYER` | join ohne gültigen nichtleeren Namen. |
| `NOT_JOINED` | place, shoot, getState oder leave vor join. |
| `NOT_YOUR_TURN` | shoot vom falschen Spieler. |
| `CELL_OUT_OF_BOUNDS` | shoot-Feld fehlt, hat ein ungültiges Format oder liegt ausserhalb A1-J10. |
| `DUPLICATE_SHOT` | Dieses Feld wurde vom Schützen bereits beschossen. |
| `WRONG_PHASE` | Aktion in der falschen Phase oder erneute Platzierung desselben Spielers. |
| `INVALID_PLACEMENT` | Flotte, Schiffstypen, Start/Richtung, Überlappung oder Rasterüberstand sind ungültig. |
| `INVALID_JSON` | Zeile ist kein gültiges JSON-Objekt (auch Listen/Skalare). |
| `UNKNOWN_TYPE` | type fehlt oder hat keinen bekannten Nachrichtennamen. |

`PLAYER_SPOOFING` ist kein ausgegebener Fehlercode: Die Zuordnung erfolgt über den Socket. Nachrichten zur falschen Zeit oder mit ungültigen Daten werden nur dem Absender abgelehnt; eine erfolgreiche regelkonforme Aktion ist die Voraussetzung für eine Spielzustandsänderung.

## Ablaufbeispiel einer vollständigen Partie

Dies ist ein nachvollziehbares Protokollbeispiel, kein Ausführungsnachweis. Alice/A wählt die Katalogflotte in den Zeilen 1–5, Bob/B eine andere Flotte in den Zeilen 6–10. Die Anwendung schreibt diese Beispielpositionen nicht vor. Jede JSON-Darstellung ist eine vollständige Nachricht mit abschliessendem LF; A/B bei einer gemeinsamen Meldung bedeutet zwei Sendungen. Personalisierte state-Nachrichten stehen getrennt da.

### Beitritt und Platzierung

```text
A → S  {"type":"join","player":"Alice"}
S → A  {"type":"welcome","slot":"A","player":"Alice","phase":"waiting"}
S → A  {"type":"waiting","reason":"warte auf Gegner"}
S → A  {"type":"state","phase":"waiting","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
B → S  {"type":"join","player":"Bob"}
S → B  {"type":"welcome","slot":"B","player":"Bob","phase":"placing"}
S → A/B  {"type":"gameStart","phase":"placing","players":[{"slot":"A","player":"Alice"},{"slot":"B","player":"Bob"}]}
S → A  {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
S → B  {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
A → S  {"type":"place","ships":[{"type":"Carrier","start":"A1","direction":"h"},{"type":"Battleship","start":"A2","direction":"h"},{"type":"Cruiser","start":"A3","direction":"h"},{"type":"Submarine","start":"A4","direction":"h"},{"type":"Destroyer","start":"A5","direction":"h"}]}
S → A  {"type":"placeAck","phase":"placing"}
S → A  {"type":"state","phase":"placing","turn":null,"ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
S → B  {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
B → S  {"type":"place","ships":[{"type":"Carrier","start":"A6","direction":"h"},{"type":"Battleship","start":"A7","direction":"h"},{"type":"Cruiser","start":"A8","direction":"h"},{"type":"Submarine","start":"A9","direction":"h"},{"type":"Destroyer","start":"A10","direction":"h"}]}
S → B  {"type":"placeAck","phase":"shooting"}
S → A  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
S → B  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A6","B6","C6","D6","E6"],"hits":[]},{"type":"Battleship","cells":["A7","B7","C7","D7"],"hits":[]},{"type":"Cruiser","cells":["A8","B8","C8"],"hits":[]},{"type":"Submarine","cells":["A9","B9","C9"],"hits":[]},{"type":"Destroyer","cells":["A10","B10"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
```

Nach jedem erfolgreichen Ereignis treffen die beiden state-Nachrichten ohne getState ein. Bereits nach Alices Platzierung sehen beide phase placing, aber nur Alice kennt ihre Schiffe. Nach Bobs Platzierung beginnt A. Die Namen/Slots stehen in gameStart; unbeschossene Schiffe des Gegners fehlen in jeder eigenen Ansicht.

### Alle Schüsse

Für jede Tabellenzeile sendet der genannte Spieler shoot mit dem angegebenen field; er erhält result mit den vier angegebenen Feldern. Bei Zug 33 erhält anschliessend B gameOver. Nach **jeder** Tabellenzeile erhalten A und B den vollständigen eigenen state, auch wenn B nichts sendet. Die Beispiele schreiben A vor B; diese Reihenfolge zwischen verschiedenen Clientverbindungen ist keine Protokollzusage.

Der state nach Zeile n ist vollständig festgelegt: phase ist shooting und turn der Tabellenwert (nach Zeile 33: finished, turn null, winner A). shotsAtOpponent enthält alle bisherigen Schüsse des Empfängers aus Zeile 1 bis n; shotsAtSelf enthält alle bisherigen Schüsse des anderen Spielers, jeweils mit dem Tabellenwert result. ownShips entspricht der eigenen Platzierung, ergänzt um alle bisherigen Treffer auf diese Schiffe in hits. Alle vorherigen Schusseinträge bleiben erhalten; vor Spielende ist winner null. Die ersten zwei und die letzte Zeile sind unten mit vollständigen Zuständen ausgeschrieben.

| Zug | Spieler | field | result | sunk | turn |
|---|---|---|---|---|---|
| 1 | A | `A6` | hit | null | "B" |
| 2 | B | `F1` | miss | null | "A" |
| 3 | A | `B6` | hit | null | "B" |
| 4 | B | `G1` | miss | null | "A" |
| 5 | A | `C6` | hit | null | "B" |
| 6 | B | `H1` | miss | null | "A" |
| 7 | A | `D6` | hit | null | "B" |
| 8 | B | `I1` | miss | null | "A" |
| 9 | A | `E6` | sunk | "Carrier" | "B" |
| 10 | B | `J1` | miss | null | "A" |
| 11 | A | `A7` | hit | null | "B" |
| 12 | B | `F2` | miss | null | "A" |
| 13 | A | `B7` | hit | null | "B" |
| 14 | B | `G2` | miss | null | "A" |
| 15 | A | `C7` | hit | null | "B" |
| 16 | B | `H2` | miss | null | "A" |
| 17 | A | `D7` | sunk | "Battleship" | "B" |
| 18 | B | `I2` | miss | null | "A" |
| 19 | A | `A8` | hit | null | "B" |
| 20 | B | `J2` | miss | null | "A" |
| 21 | A | `B8` | hit | null | "B" |
| 22 | B | `F3` | miss | null | "A" |
| 23 | A | `C8` | sunk | "Cruiser" | "B" |
| 24 | B | `G3` | miss | null | "A" |
| 25 | A | `A9` | hit | null | "B" |
| 26 | B | `H3` | miss | null | "A" |
| 27 | A | `B9` | hit | null | "B" |
| 28 | B | `I3` | miss | null | "A" |
| 29 | A | `C9` | sunk | "Submarine" | "B" |
| 30 | B | `J3` | miss | null | "A" |
| 31 | A | `A10` | hit | null | "B" |
| 32 | B | `F4` | miss | null | "A" |
| 33 | A | `B10` | sunk | "Destroyer" | null |

### Erste zwei Schüsse mit beiden Ansichten

```text
A → S  {"type":"shoot","field":"A6"}
S → A  {"type":"result","field":"A6","result":"hit","sunk":null,"turn":"B"}
S → A  {"type":"state","phase":"shooting","turn":"B","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{"A6":"hit"},"shotsAtSelf":{},"winner":null}
S → B  {"type":"state","phase":"shooting","turn":"B","ownShips":[{"type":"Carrier","cells":["A6","B6","C6","D6","E6"],"hits":["A6"]},{"type":"Battleship","cells":["A7","B7","C7","D7"],"hits":[]},{"type":"Cruiser","cells":["A8","B8","C8"],"hits":[]},{"type":"Submarine","cells":["A9","B9","C9"],"hits":[]},{"type":"Destroyer","cells":["A10","B10"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{"A6":"hit"},"winner":null}
B → S  {"type":"shoot","field":"F1"}
S → B  {"type":"result","field":"F1","result":"miss","sunk":null,"turn":"A"}
S → A  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{"A6":"hit"},"shotsAtSelf":{"F1":"miss"},"winner":null}
S → B  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A6","B6","C6","D6","E6"],"hits":["A6"]},{"type":"Battleship","cells":["A7","B7","C7","D7"],"hits":[]},{"type":"Cruiser","cells":["A8","B8","C8"],"hits":[]},{"type":"Submarine","cells":["A9","B9","C9"],"hits":[]},{"type":"Destroyer","cells":["A10","B10"],"hits":[]}],"shotsAtOpponent":{"F1":"miss"},"shotsAtSelf":{"A6":"hit"},"winner":null}
```

Bob sieht Alices ersten Treffer auf A6 in shotsAtSelf und seiner eigenen Flotte. Alice kennt dadurch ausschliesslich das getroffene Feld, nicht Bobs übrige Schiffsfelder. Bobs Fehlschuss F1 erscheint danach bei Alice in shotsAtSelf und bei Bob in shotsAtOpponent.

### Letzter Schuss, Endzustände und Abgang

Nach den Tabellenzeilen 1–32 folgt ohne zusätzliche Zustandsabfrage:

```text
A → S  {"type":"shoot","field":"B10"}
S → A  {"type":"result","field":"B10","result":"sunk","sunk":"Destroyer","turn":null}
S → B  {"type":"gameOver","winner":"A","reason":"sunk"}
S → A  {"type":"state","phase":"finished","turn":null,"ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{"A6":"hit","B6":"hit","C6":"hit","D6":"hit","E6":"sunk","A7":"hit","B7":"hit","C7":"hit","D7":"sunk","A8":"hit","B8":"hit","C8":"sunk","A9":"hit","B9":"hit","C9":"sunk","A10":"hit","B10":"sunk"},"shotsAtSelf":{"F1":"miss","G1":"miss","H1":"miss","I1":"miss","J1":"miss","F2":"miss","G2":"miss","H2":"miss","I2":"miss","J2":"miss","F3":"miss","G3":"miss","H3":"miss","I3":"miss","J3":"miss","F4":"miss"},"winner":"A"}
S → B  {"type":"state","phase":"finished","turn":null,"ownShips":[{"type":"Carrier","cells":["A6","B6","C6","D6","E6"],"hits":["A6","B6","C6","D6","E6"]},{"type":"Battleship","cells":["A7","B7","C7","D7"],"hits":["A7","B7","C7","D7"]},{"type":"Cruiser","cells":["A8","B8","C8"],"hits":["A8","B8","C8"]},{"type":"Submarine","cells":["A9","B9","C9"],"hits":["A9","B9","C9"]},{"type":"Destroyer","cells":["A10","B10"],"hits":["A10","B10"]}],"shotsAtOpponent":{"F1":"miss","G1":"miss","H1":"miss","I1":"miss","J1":"miss","F2":"miss","G2":"miss","H2":"miss","I2":"miss","J2":"miss","F3":"miss","G3":"miss","H3":"miss","I3":"miss","J3":"miss","F4":"miss"},"shotsAtSelf":{"A6":"hit","B6":"hit","C6":"hit","D6":"hit","E6":"sunk","A7":"hit","B7":"hit","C7":"hit","D7":"sunk","A8":"hit","B8":"hit","C8":"sunk","A9":"hit","B9":"hit","C9":"sunk","A10":"hit","B10":"sunk"},"winner":"A"}
B → S  {"type":"leave"}
S → A  {"type":"opponentLeft","slot":"B","player":"Bob"}
S → A  {"type":"state","phase":"waiting","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null}
```

Bob bekommt keine direkte Antwort auf leave; seine Verbindung endet. Alice erhält opponentLeft und danach den leeren waiting-Zustand automatisch. Ein Ersatzspieler erhält den freien Slot B, beide bekommen gameStart und ihren neuen placing-Zustand. Auch nach Spielende enthält Alices state keine unbeschossene gegnerische Flotte.
