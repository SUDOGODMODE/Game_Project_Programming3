# Schiffe versenken — Protokoll 0.4

Katalog des lokalen A/B-Protokolls, Version 0.4; strukturierte Fassung: [protocol.json](docs/protocol/protocol.json). Das Gegenlesen steht aus. Die Beispiele erläutern das Format; Ausführungsnachweise stehen unter `docs/evidence/`.

## Transport und Identität

TCP/IPv4, UTF-8, JSON Lines: Ein JSON-Objekt pro Zeile, abgeschlossen mit einem LF-Byte (`\n`). Ein `recv()` kann Teile einer Nachricht oder mehrere Nachrichten enthalten; `netz.read_messages` setzt Zeilen zusammen. Leere Zeilen werden ignoriert. Jedes Objekt enthält `type`. Ungültiges JSON und JSON-Werte, die keine Objekte sind, führen zu `error`/`INVALID_JSON`; `broken` ist nur der interne Transportmarker.

Standardport: 5000. Server: `0.0.0.0`, Clients lokal: `127.0.0.1`; Host und Port sind Startargumente. Für fremde Rechner ist die echte Serveradresse nötig. Der Server vergibt den ersten freien Slot `A`, dann `B`. Der Name aus `join` ist keine Zug-Identität: weitere Aktionen gehören zur bestehenden Verbindung, zusätzliche Slot-/Spielerfelder wählen keinen anderen Spieler.

Clients lesen dauerhaft in einem Empfangsthread und unterscheiden die Nachrichten anhand von `type`. Ungefragte Servermeldungen können auch während der Tastatureingabe eintreffen. `state` wird derzeit nur auf `getState` geschickt; allgemeine Zustands-Pushes nach Spielaktionen sind für die spätere Projektphase M4 noch offen.

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
| `state` | S → C | `phase`, `turn`, `ownShips`, `shotsAtOpponent`, `winner` | Direkte Antwort auf getState; nur an den anfragenden beigetretenen Client. | nein |
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

Ein alleiniger Spieler bekommt phase waiting. Der zweite bekommt phase placing. welcome steht auf seiner Verbindung vor waiting bzw. gameStart.

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

Auch der zuvor wartende Client empfängt dies, ohne etwas zu senden. Nach einem Ersatzbeitritt beginnt eine frische Runde.

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

Nach der zweiten gültigen Platzierung ist phase shooting und A beginnt. Nur der Absender bekommt placeAck; der andere Client fragt die Phase bei Bedarf mit getState ab.

### shoot

```json
{"type":"shoot","field":"C5"}
```

`type`: string, genau shoot; `field`: string, ASCII-Feld A1–J10; Kleinbuchstaben und führende Nullen werden kanonisiert

Der Server prüft Phase, Zug, Feld und Doppelbeschuss. Antwort: `result` oder `error`.

### result

```json
{"type":"result","field":"C5","result":"miss","sunk":null,"turn":"B"}
```

`type`: string, genau result; `field`: beschossenes Feld, kanonisch A1–J10; `result`: miss, hit oder sunk; `sunk`: Schiffstyp bei sunk, sonst null; `turn`: A/B als nächster Spieler; null bei Spielende

Beim letzten Treffer sind `result: "sunk"` und `turn: null` gesetzt. Der Gewinner erhält kein zusätzliches `gameOver`.

### getState

```json
{"type":"getState"}
```

`type`: string, genau getState

Antwort: `state`.

### state

```json
{"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"winner":null}
```

`type`: string, genau state; `phase`: waiting, placing, shooting oder finished; `turn`: A/B oder null; `ownShips`: Liste eigener Schiffe: {type, cells: Feldliste, hits: Feldliste}; `shotsAtOpponent`: Objekt Feld -> miss/hit/sunk für eigene Schüsse; `winner`: A/B oder null

Die Antwort enthält nur die eigene Ansicht. Nach `opponentLeft` zeigt sie `waiting`, leere `ownShips` und `shotsAtOpponent` sowie `turn: null` und `winner: null`.

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

Der Gewinner erkennt das Spielende an `result` mit `turn: null`. Beide können den Endzustand mit `getState` abfragen.

### error

```json
{"type":"error","code":"UNKNOWN_TYPE","message":"unbekannter Typ: nonsense"}
```

`type`: string, genau error; `code`: einer der unten dokumentierten Fehlercodes; `message`: string, lesbarer Grund

Ungültige JSON-Zeilen und JSON-Werte ohne Objektstruktur werden mit `INVALID_JSON` abgelehnt.

## Flotte und Spielregeln

Raster 10×10, ausgegebene Koordinaten kanonisch `A1`–`J10`. Eingaben wie `a01` werden zu `A1` normalisiert; Kleinbuchstaben und führende ASCII-Nullen sind erlaubt, Unicode-Ziffern nicht. Doppelbeschuss wird nach Normalisierung geprüft. Platzierung: `h` nach rechts, `v` nach unten. Je ein Carrier (5), Battleship (4), Cruiser (3), Submarine (3) und Destroyer (2), insgesamt 17 Felder. Keine Überlappung oder Überschreitung des Rasters; angrenzende Schiffe sind erlaubt. Diese klassische Flotte ist im [Regelblatt](REGELN.md) festgelegt.

Phasen: `waiting` → `placing` → `shooting` → `finished`. Nach beiden gültigen Platzierungen beginnt `A`; jeder gültige Schuss wechselt den Spieler. Treffer erlauben keinen Extrazug. Doppelbeschuss ist ungültig. Sind alle gegnerischen Schiffe versenkt, gewinnt der Schütze; kein Unentschieden. Jeder `state` enthält ausschliesslich eigene Schiffe/Treffer und eigene Schüsse, keine Gegnerflotte.

## Reihenfolge und Abbruch

- Erster Beitritt: `welcome`, dann `waiting` an den beitretenden Client.
- Zweiter Beitritt: dessen `welcome`, danach `gameStart` an beide.
- Platzierung: `placeAck` nur an den Akteur; den Zustand fragt jeder Client mit `getState` ab.
- Schuss: `result` nur an den Akteur. Beim letzten Treffer `gameOver` nur an den Gegner. Kein Zustands-Push nach normalen Schüssen; Zug/Zustand bei Bedarf mit `getState` abfragen.
- Abgang: einmal `opponentLeft` an den Verbliebenen. Kein zusätzlicher `waiting`- oder `state`-Push.

Bei `leave`, `q`, EOF oder erkanntem Socket-Abbruch wird der Slot freigegeben und die gesamte Runde sofort zurückgesetzt: beide Flotten/Treffer und Schusslisten leer, `phase: "waiting"`, `turn: null`, `winner: null`. Der Verbliebene bleibt verbunden und kann diesen Zustand mit `getState` abfragen. Beim nächsten Beitritt wird der freie Slot vergeben, `gameStart` startet eine frische Platzierung. Keine Wiederverbindungsfrist, kein `forfeit`-Sieg, keine automatische Wiederaufnahme. Ein physischer Verbindungsverlust wird erst behandelt, wenn die Socket-Schicht ihn erkennt.

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

Dieses Ablaufbeispiel verwendet das dokumentierte Protokoll. Alice/A und Bob/B verwenden beide die gültige `place`-Flotte aus dem Katalog (Zeilen 1–5, ab Spalte A). Jede folgende Darstellung steht für eine vollständige JSON-Zeile mit LF am Ende. Die Tabellen legen die Zugliste vollständig fest.

```text
A → S  {"type":"join","player":"Alice"}
S → A  {"type":"welcome","slot":"A","player":"Alice","phase":"waiting"}
S → A  {"type":"waiting","reason":"warte auf Gegner"}
B → S  {"type":"join","player":"Bob"}
S → B  {"type":"welcome","slot":"B","player":"Bob","phase":"placing"}
S → A/B  {"type":"gameStart","phase":"placing","players":[{"slot":"A","player":"Alice"},{"slot":"B","player":"Bob"}]}
A → S  {"type":"place","ships":[{"type":"Carrier","start":"A1","direction":"h"},{"type":"Battleship","start":"A2","direction":"h"},{"type":"Cruiser","start":"A3","direction":"h"},{"type":"Submarine","start":"A4","direction":"h"},{"type":"Destroyer","start":"A5","direction":"h"}]}
S → A  {"type":"placeAck","phase":"placing"}
A → S  {"type":"getState"}
S → A  {"type":"state","phase":"placing","turn":null,"ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"winner":null}
B → S  {"type":"getState"}
S → B  {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"winner":null}
B → S  {"type":"place","ships":[{"type":"Carrier","start":"A1","direction":"h"},{"type":"Battleship","start":"A2","direction":"h"},{"type":"Cruiser","start":"A3","direction":"h"},{"type":"Submarine","start":"A4","direction":"h"},{"type":"Destroyer","start":"A5","direction":"h"}]}
S → B  {"type":"placeAck","phase":"shooting"}
A → S  {"type":"getState"}
S → A  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"winner":null}
B → S  {"type":"getState"}
S → B  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"winner":null}
```

Die `gameStart`-Zeile `S → A/B` steht für zwei getrennte Sendungen. Die folgenden `state`-Antworten wurden jeweils mit `getState` angefragt. Nach beiden Platzierungen sind die privaten Ansichten noch gleich, weil beide dieselbe Flotte ohne Treffer gewählt haben; nach Schüssen unterscheiden sie sich.

Für jede Tabellenzeile schickt der angegebene Spieler `{"type":"shoot","field":"<feld>"}`. `<feld>` wird vor dem Senden durch die Koordinate der Tabellenzeile ersetzt. Die Antwort hat den Typ `result` und die dort angegebenen Werte für `field`, `result`, `sunk` und `turn`; `null` bleibt dabei ein JSON-Wert. Normale Schüsse erzeugen keine Nachricht an den Gegner. Dieser kann mit `getState` seinen aktuellen Zustand und den nächsten Zug abfragen. Die Tabelle verwendet eine festgelegte abwechselnde Zugliste; ihr Ablauf braucht keinen automatischen Zustands-Push.

| Zug | Spieler | field | result | sunk | turn |
|---|---|---|---|---|---|
| 1 | A | `A1` | hit | null | "B" |
| 2 | B | `F1` | miss | null | "A" |
| 3 | A | `B1` | hit | null | "B" |
| 4 | B | `G1` | miss | null | "A" |
| 5 | A | `C1` | hit | null | "B" |
| 6 | B | `H1` | miss | null | "A" |
| 7 | A | `D1` | hit | null | "B" |
| 8 | B | `I1` | miss | null | "A" |
| 9 | A | `E1` | sunk | "Carrier" | "B" |
| 10 | B | `J1` | miss | null | "A" |
| 11 | A | `A2` | hit | null | "B" |
| 12 | B | `F2` | miss | null | "A" |
| 13 | A | `B2` | hit | null | "B" |
| 14 | B | `G2` | miss | null | "A" |
| 15 | A | `C2` | hit | null | "B" |
| 16 | B | `H2` | miss | null | "A" |
| 17 | A | `D2` | sunk | "Battleship" | "B" |
| 18 | B | `I2` | miss | null | "A" |
| 19 | A | `A3` | hit | null | "B" |
| 20 | B | `J2` | miss | null | "A" |
| 21 | A | `B3` | hit | null | "B" |
| 22 | B | `F3` | miss | null | "A" |
| 23 | A | `C3` | sunk | "Cruiser" | "B" |
| 24 | B | `G3` | miss | null | "A" |
| 25 | A | `A4` | hit | null | "B" |
| 26 | B | `H3` | miss | null | "A" |
| 27 | A | `B4` | hit | null | "B" |
| 28 | B | `I3` | miss | null | "A" |
| 29 | A | `C4` | sunk | "Submarine" | "B" |
| 30 | B | `J3` | miss | null | "A" |
| 31 | A | `A5` | hit | null | "B" |
| 32 | B | `F4` | miss | null | "A" |
| 33 | A | `B5` | sunk | "Destroyer" | null |

Der letzte Schuss und das Ende vollständig ausgeschrieben:

```text
A → S  {"type":"shoot","field":"B5"}
S → A  {"type":"result","field":"B5","result":"sunk","sunk":"Destroyer","turn":null}
S → B  {"type":"gameOver","winner":"A","reason":"sunk"}
A → S  {"type":"getState"}
S → A  {"type":"state","phase":"finished","turn":null,"ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{"A1":"hit","B1":"hit","C1":"hit","D1":"hit","E1":"sunk","A2":"hit","B2":"hit","C2":"hit","D2":"sunk","A3":"hit","B3":"hit","C3":"sunk","A4":"hit","B4":"hit","C4":"sunk","A5":"hit","B5":"sunk"},"winner":"A"}
B → S  {"type":"getState"}
S → B  {"type":"state","phase":"finished","turn":null,"ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":["A1","B1","C1","D1","E1"]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":["A2","B2","C2","D2"]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":["A3","B3","C3"]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":["A4","B4","C4"]},{"type":"Destroyer","cells":["A5","B5"],"hits":["A5","B5"]}],"shotsAtOpponent":{"F1":"miss","G1":"miss","H1":"miss","I1":"miss","J1":"miss","F2":"miss","G2":"miss","H2":"miss","I2":"miss","J2":"miss","F3":"miss","G3":"miss","H3":"miss","I3":"miss","J3":"miss","F4":"miss"},"winner":"A"}
A → S  {"type":"getState"}
S → A  {"type":"state","phase":"finished","turn":null,"ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{"A1":"hit","B1":"hit","C1":"hit","D1":"hit","E1":"sunk","A2":"hit","B2":"hit","C2":"hit","D2":"sunk","A3":"hit","B3":"hit","C3":"sunk","A4":"hit","B4":"hit","C4":"sunk","A5":"hit","B5":"sunk"},"winner":"A"}
B → S  {"type":"leave"}
S → A  {"type":"opponentLeft","slot":"B","player":"Bob"}
A → S  {"type":"getState"}
S → A  {"type":"state","phase":"waiting","turn":null,"ownShips":[],"shotsAtOpponent":{},"winner":null}
```

Bob bekommt keine direkte Antwort auf `leave`; seine Verbindung endet. Ein Ersatzspieler erhält den nun freien Slot B und löst eine neue Platzierungsrunde mit `gameStart` an beide aus.
