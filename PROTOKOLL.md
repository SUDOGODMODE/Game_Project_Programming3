# Schiffe versenken — Protokoll

Katalog des lokalen A/B-Protokolls mit Zuschauern und Revanche, Protokoll 0.8;
strukturierte Fassung: [protocol.json](docs/protocol/protocol.json).
Die Beispiele erläutern das vereinbarte Format für Meilenstein 8 und sind
keine Ausführungsnachweise. Version 0.7 ergänzte `spectator` und
`SPECTATOR_ONLY`; ein voller Tisch führt nicht mehr zu `GAME_FULL`.
Version 0.8 ergänzt `rematch`, `rematchRequested`, den Fehlercode
`DUPLICATE_REMATCH` und das Pflichtfeld `score` im `state`.

## Transport und Identität

TCP/IPv4, UTF-8, JSON Lines: Ein JSON-Objekt pro Zeile, abgeschlossen mit einem LF-Byte (`\n`). Ein `recv()` kann Teile einer Nachricht oder mehrere Nachrichten enthalten; `netz.read_messages` setzt Zeilen zusammen. Leere Zeilen werden ignoriert. Jedes Objekt enthält `type`. Ungültiges JSON und JSON-Werte, die keine Objekte sind, führen zu `error`/`INVALID_JSON`; `broken` ist nur der interne Transportmarker.

Standardport: 5100 (5000 belegt unter macOS der AirPlay-Empfänger); ist 5100 belegt und kein Port vorgegeben, nimmt der Server den nächsten freien und nennt ihn. Server: `0.0.0.0`, Clients lokal: `127.0.0.1`; Host und Port sind Startargumente. Für fremde Rechner ist die echte Serveradresse nötig. Der Server vergibt den ersten freien Slot `A`, dann `B`. Der Name aus `join` ist keine Zug-Identität: weitere Aktionen gehören zur bestehenden Verbindung, zusätzliche Slot-/Spielerfelder wählen keinen anderen Spieler.

Sind A und B belegt, wird jeder weitere beitretende Client Zuschauer.
Er bekommt `spectator` ohne `slot`, Spielernummer oder Symbol und direkt
danach den aktuellen öffentlichen `state`. Die Rolle ist an die Verbindung
gebunden; Zuschauer stehen separat und werden auch bei einem freien Platz
nie zu Spielern befördert. Ein erneutes `join` derselben Verbindung ergibt
`ALREADY_JOINED`.

Clients lesen dauerhaft in einem Empfangsthread und unterscheiden nach
`type`. Nach Spielerbeitritt, erfolgreicher Platzierung, erfolgreichem Schuss
und Reset erhalten Spieler und Zuschauer ungefragt ihren vollständigen
`state`. Ein neuer Zuschauer erhält sofort den aktuellen Stand, ohne den
nächsten Zug abzuwarten. `getState` antwortet nur dem Anfragenden. Clients
dürfen keine feste Eins-zu-eins-Zuordnung zwischen Anfrage und nächster
Nachricht annehmen.

`shoot` ist die Zuganforderung (`move` im Unterrichtsbeispiel); es gibt keine zusätzliche Nachricht `move`. Der grafische Client schickt Anfragen und zeichnet ausschliesslich empfangene Zustände. Sein Netzthread legt Nachrichten in eine Queue, der Tk-Hauptthread verarbeitet sie. Harte Socket-Abbrüche beenden den Nachrichtenleser wie EOF. Server-Terminalausgaben enthalten nur Metadaten (Richtung, Verbindung/Slot, Typ und gegebenenfalls Fehlercode), keine Flotten oder Zustands-Payloads. Für die Geheimhaltungsprüfung werden die tatsächlich am jeweiligen Client empfangenen Daten getrennt geprüft; eine Metadatenausgabe allein beweist die Filterung nicht.

## Nachrichtenaufzeichnung auf dem Server

Zusätzlich erzeugt jeder
Serverstart eine neue JSONL-Datei unter projektlokalem `logs/`; `--log-file`
wählt eine ausdrücklich neue Datei. Es gibt kein Anhängen an frühere Logs.
Pro empfangener und erfolgreich gesendeter Nachricht wird eine vollständige,
sofort geflushte JSON-Zeile geschrieben: `timestamp` (UTC-ISO-Zeit mit
Zeitzone), `direction` (`<-`/`->`), `peer` (Verbindung oder Slot), `slot`
(`A`/`B` oder `null` vor Anmeldung und bei Zuschauern) und `type` (bekannter Typ oder `unknown`).
Nur bei ausgehenden Serverfehlern kommt ein bekannter `code` hinzu.
Ungültiges JSON erscheint als interner Typ `broken`. Namen, Flotten,
Zustands-Payloads und freie Clienttexte werden nicht protokolliert.
Die Datei dokumentiert Nachrichtenmetadaten, keine wiederherstellbare Partie.
`spectator` und `SPECTATOR_ONLY` gehören zu den bekannten Metadaten.
Das Logfeld `slot: null` ist kein `slot` in der Nachricht `spectator`.

## Nachrichtenkatalog

Alle genannten Felder sind Pflichtfelder für den beschriebenen Nachrichtentyp; `null` ist ein vorhandener Wert, kein weggelassenes Feld. C = Client, S = Server. Zusätzliche Felder sind kein Mittel zur Wahl der Spieleridentität.

| Typ | Richtung | Pflichtfelder ausser `type` | Anlass / Empfänger | Ungefragt |
|---|---|---|---|---|
| `join` | C → S | `player` | Ein neuer Client meldet sich auf seiner TCP-Verbindung an. | nein |
| `welcome` | S → C | `slot`, `player`, `phase` | Direkte Antwort auf join auf einen freien Spielerplatz; nur an diesen Client. Beim Start einer Revanche erneut an jeden Spieler mit seinem neuen Slot. | nein, bei Revanche ja |
| `spectator` | S → C | `player`, `phase`; kein slot-Feld | Antwort auf join bei zwei belegten Spielerplätzen; nur an den neuen Zuschauer. | nein |
| `waiting` | S → C | `reason` | Nach welcome an den ersten/alleinigen beigetretenen Spieler. | ja |
| `gameStart` | S → C | `phase`, `players` | Nach welcome des zweiten Spielers und beim Start einer Revanche an Spieler und bereits verbundene Zuschauer. | ja |
| `place` | C → S | `ships` | Ein beigetretener Spieler platziert in phase placing einmal seine vollständige Flotte. | nein |
| `placeAck` | S → C | `phase` | Direkte Bestätigung einer erfolgreichen place-Anfrage; nur an den Absender. | nein |
| `shoot` | C → S | `field` | Der Spieler am Zug wählt in phase shooting ein noch nicht beschossenes Feld. | nein |
| `result` | S → C | `field`, `result`, `sunk`, `turn` | Direkte Antwort auf eine erfolgreiche shoot-Anfrage; nur an den Schützen. | nein |
| `getState` | C → S | keine | Ein bereits beigetretener Client fragt seinen aktuellen, gefilterten Zustand ab. | nein |
| `state` | S → C | `phase`, `turn`, `ownShips`, `shotsAtOpponent`, `shotsAtSelf`, `winner`, `score` | Nach Spielerbeitritt, Platzierung, Schuss, Reset oder Start einer Revanche an Spieler und Zuschauer; nach Zuschauerbeitritt sofort an diesen; auf getState nur an den Anfragenden. Nach Rolle gefiltert; der Punktestand ist für alle gleich. | ja, auch Antwort auf getState |
| `leave` | C → S | keine | Ein beigetretener Client verlässt die Runde bewusst. | nein |
| `opponentLeft` | S → C | `slot`, `player` | Ein Spieler geht; einmal an verbliebenen Spieler und alle Zuschauer. Nicht bei Zuschauerabgang. | ja |
| `gameOver` | S → C | `winner`, `reason` | Nach den gefilterten Endzuständen an Spieler und Zuschauer beim letzten erfolgreichen Schuss. | ja |
| `rematch` | C → S | keine | Ein Spieler wünscht nach dem Spielende eine neue Partie. | nein |
| `rematchRequested` | S → C | `slot`, `player` | Erster gültiger Revanchewunsch; an beide Spieler und alle Zuschauer. Der zweite Wunsch startet stattdessen die neue Partie. | ja |
| `error` | S → C | `code`, `message` | Eine Anfrage ist ungültig oder passt nicht zum aktuellen Zustand; nur an ihren Absender. | nein |

### join

```json
{"type":"join","player":"Alice"}
```

`type`: string, genau join; `player`: string, nicht leer und nicht nur Leerzeichen

Antwort: `welcome`, `spectator` oder `error`. Slotvergabe und Identität sind unter «Transport und Identität» beschrieben.

### welcome

```json
{"type":"welcome","slot":"A","player":"Alice","phase":"waiting"}
```

`type`: string, genau welcome; `slot`: A oder B; `player`: string, übernommener Name; `phase`: waiting oder placing

Ein alleiniger Spieler bekommt phase waiting. Der zweite bekommt phase placing. welcome steht auf seiner Verbindung vor waiting bzw. gameStart und dem anschliessenden state.

Beim Start einer Revanche erhält jeder Spieler ungefragt ein neues welcome mit phase placing und seinem **neuen** Slot, siehe «rematch». Der Client übernimmt den Slot aus jedem welcome.

### spectator

```json
{"type":"spectator","player":"Carla","phase":"shooting"}
```

Richtung S → C, nur an den neu beigetretenen Zuschauer. Pflichtfelder:
`type`: genau spectator; `player`: übernommener Name als string;
`phase`: aktuelle Spielphase, beim vollen Tisch placing, shooting oder
finished. **Kein `slot`-Feld.** Unmittelbar danach folgt der öffentliche
`state`. Ein später Beitritt startet die Partie nicht neu und löst kein
nachträgliches `gameStart` oder `gameOver` aus.

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

Auch wartende Spieler und bereits verbundene Zuschauer empfangen dies ungefragt.
Danach erhalten alle ihre erlaubte Sicht in phase placing. Nach einem
Ersatzbeitritt beginnt eine frische Runde; `players` enthält nur A und B.

### place

```json
{"type":"place","ships":[{"type":"Carrier","start":"A1","direction":"h"},{"type":"Battleship","start":"A2","direction":"h"},{"type":"Cruiser","start":"A3","direction":"h"},{"type":"Submarine","start":"A4","direction":"h"},{"type":"Destroyer","start":"A5","direction":"h"}]}
```

`type`: string, genau place; `ships`: Liste mit genau fünf Objekten; pro Objekt type (Schiffstyp), start (Feld), direction (h oder v)

Die Flotte muss den unten beschriebenen Spielregeln entsprechen. Antwort: `placeAck` oder `error`. Zuschauer erhalten privat `error` mit `SPECTATOR_ONLY`, ohne Zustandsänderung.

### placeAck

```json
{"type":"placeAck","phase":"placing"}
```

`type`: string, genau placeAck; `phase`: placing oder shooting

Nach der zweiten gültigen Platzierung ist phase shooting und A beginnt. Nur der Absender bekommt placeAck; danach erhalten Spieler und Zuschauer automatisch ihren vollständigen erlaubten state. Eine abgelehnte Platzierung erzeugt nur error an den Absender und keinen state-Push.

### shoot

```json
{"type":"shoot","field":"C5"}
```

`type`: string, genau shoot; `field`: string, ASCII-Feld A1–J10; Kleinbuchstaben und führende Nullen werden kanonisiert

Zuschauer erhalten privat `SPECTATOR_ONLY`. Für Spieler prüft der Server Phase, Zug, Feld und Doppelbeschuss. Antwort: `result` oder `error`. Nach einem erfolgreichen Schuss folgen die gefilterten Zustände für Spieler und Zuschauer; nach einer Ablehnung erhält ausschliesslich der Absender error, der Spielstand bleibt unverändert.

### result

```json
{"type":"result","field":"C5","result":"miss","sunk":null,"turn":"B"}
```

`type`: string, genau result; `field`: beschossenes Feld, kanonisch A1–J10; `result`: miss, hit oder sunk; `sunk`: Schiffstyp bei sunk, sonst null; `turn`: A/B als nächster Spieler; null bei Spielende

Beim letzten Treffer sind `result: "sunk"` und `turn: null` gesetzt. Danach folgen die vollständigen gefilterten `state`-Nachrichten und anschliessend `gameOver` an Spieler und Zuschauer. Der Schütze erhält somit `result`, `state` und `gameOver` in dieser Reihenfolge. Zuschauer erhalten kein `result`.

### getState

```json
{"type":"getState"}
```

`type`: string, genau getState

Für Spieler und Zuschauer erlaubt. Antwort: genau ein `state` in der erlaubten Sicht an den Anfragenden. Andere Verbindungen erhalten durch diese Abfrage keine Nachricht; die Abfrage ändert den Zustand nicht.

### state

```json
{"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
```

`type`: string, genau state; `phase`: waiting, placing, shooting oder finished; `turn`: A/B oder null; `ownShips`: Liste eigener Schiffe: {type, cells: Feldliste, hits: Feldliste}; `shotsAtOpponent`: Objekt Feld -> miss/hit/sunk für eigene Schüsse; `shotsAtSelf`: Objekt Feld -> miss/hit/sunk für **alle** gegnerischen Schüsse auf das eigene Raster, einschliesslich Fehlschüssen; `winner`: A/B oder null; `score`: Liste der belegten Slots, sortiert A dann B, je {slot: A/B, player: string, wins: ganze Zahl ab 0}.

`score` ist der Punktestand über alle Partien derselben zwei Spieler. Der Server zählt ihn, der Client zeigt ihn nur an (etwa «Alice 2 : 1 Bob»). Beim letzten Schuss bekommt der Sieger einen Punkt, bevor die Endzustände verschickt werden; ein Unentschieden gibt es nach den Regeln nicht, es gäbe niemandem einen Punkt. Die Siege gehören zum Spieler, nicht zum Slot: Nach dem Slottausch einer Revanche wandern sie mit. Geht ein Spieler, beginnt der Punktestand für die neue Paarung bei 0. Mit nur einem Spieler enthält `score` einen Eintrag.

Dies ist immer die vollständige erlaubte Sicht, keine Änderungsnachricht. Beide Raster haben 100 Felder A1–J10; es wird kein öffentliches board mit Gegnerflotte übertragen. Die folgende Feldbeschreibung gilt für Spieler; die Zuschauersicht steht danach.

- Ein fehlender Schlüssel in shotsAtOpponent bedeutet **noch nicht beschossen, Inhalt unbekannt**, nicht Wasser. Ein fehlender Schlüssel in shotsAtSelf bedeutet **noch nicht vom Gegner beschossen**.
- Nach eigener gültiger Platzierung ist ein Feld ausserhalb der eigenen ownShips Wasser. Leere ownShips bedeuten vor der eigenen gültigen Platzierung oder nach Reset, dass noch keine Flotte gesetzt ist.
- miss bedeutet Fehlschuss, hit bedeutet Treffer, sunk bedeutet, dass genau dieser Schuss ein Schiff versenkt hat. Frühere hit-Einträge werden beim Versenken nicht nachträglich zu sunk geändert. ownShips.hits enthält alle getroffenen Felder des jeweiligen eigenen Schiffs.
- Die eigene Flotte ist sichtbar; unbekannte gegnerische Positionen werden auch nach Partieende nicht übertragen. shotsAtSelf ist die Kopie der gegnerischen Schussliste und verrät keine gegnerischen Schiffe.

Für Zuschauer hat `state` dieselben Pflichtfelder, aber eine eigene öffentliche
Perspektive: `ownShips` ist **immer `[]`**, `shotsAtSelf` enthält **B auf A**
(linkes Raster), `shotsAtOpponent` enthält **A auf B** (rechtes Raster).
Es werden weder Flotte A noch Flotte B übertragen, auch nicht nach Spielende.
Ein unbeschossenes Feld bleibt unbekannt; aus `ownShips: []` darf ein
Zuschauer kein Wasser ableiten. Beispiel nach A auf A6 und B auf F1:

```json
{"type":"state","phase":"shooting","turn":"A","ownShips":[],"shotsAtOpponent":{"A6":"hit"},"shotsAtSelf":{"F1":"miss"},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
```

Nach opponentLeft folgt an verbliebenen Spieler und Zuschauer ein state mit phase waiting, leeren ownShips, shotsAtOpponent und shotsAtSelf sowie turn und winner jeweils null; `score` enthält nur noch den verbliebenen Spieler mit 0 Siegen. Ein Client zeichnet aus jeder Zustandsnachricht beide Raster vollständig neu.

### leave

```json
{"type":"leave"}
```

`type`: string, genau leave

Für Spieler und Zuschauer erlaubt, keine direkte Bestätigung. Die Verbindung wird wie bei EOF/Socket-Abbruch entfernt. Ein Zuschauerabgang verändert die Partie nicht und benachrichtigt keine anderen Clients. q im Lobbyclient beendet die Verbindung ebenfalls.

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

Spieler und Zuschauer erhalten zuerst ihren gefilterten Endzustand mit demselben `winner`, danach je eine `gameOver`-Nachricht. Der Gewinner kann das Ende bereits an `result` mit `turn: null` erkennen. Eine zusätzliche `getState`-Abfrage bleibt für alle möglich.

Nach `gameOver` bleibt der Server offen; die Verbindungen bleiben bestehen. Eine neue Partie beginnt nur über zwei Revanchewünsche.

### rematch

```json
{"type":"rematch"}
```

Richtung C → S. Pflichtfeld nur `type`: string, genau rematch. Zusätzliche
Felder werden ignoriert; der Wunsch gehört zur Verbindung.

Ein Klick auf «Revanche» ist ein Wunsch, kein Neustart. Der Server prüft in
dieser Reihenfolge: vor join `NOT_JOINED`, vom Zuschauer `SPECTATOR_ONLY`,
ausserhalb von phase finished `WRONG_PHASE`, derselbe Spieler ein zweites Mal
`DUPLICATE_REMATCH`. Jede Ablehnung geht nur an den Absender und ändert nichts.

Erster gültiger Wunsch: `rematchRequested` an beide Spieler und alle Zuschauer.
Zweiter gültiger Wunsch (vom anderen Spieler): Der Server legt ein **neues**
Spielkern-Objekt an und startet es, löscht die Wünsche und tauscht die Slots
der beiden Spieler. Der Spielkern lässt immer `A` beginnen; durch den Tausch
beginnt der Spieler, der in der letzten Partie nicht begonnen hat. Danach
folgen ungefragt je Spieler ein `welcome` mit seinem neuen Slot, `gameStart`
an alle und der gefilterte `state` an alle. Ein zusätzliches `rematchRequested`
für den zweiten Wunsch gibt es nicht. Geht ein Spieler, verfallen alle offenen
Wünsche.

Beispiel nach Alices Sieg in der ersten Partie, ohne Zuschauer. Die Pfeile
nennen hier Namen, weil sich die Slots ändern:

```text
Alice → S  {"type":"rematch"}
S → Alice  {"type":"rematchRequested","slot":"A","player":"Alice"}
S → Bob    {"type":"rematchRequested","slot":"A","player":"Alice"}
Alice → S  {"type":"rematch"}
S → Alice  {"type":"error","code":"DUPLICATE_REMATCH","message":"Revanche bereits verlangt"}
Bob → S    {"type":"rematch"}
S → Bob    {"type":"welcome","slot":"A","player":"Bob","phase":"placing"}
S → Alice  {"type":"welcome","slot":"B","player":"Alice","phase":"placing"}
S → Bob    {"type":"gameStart","phase":"placing","players":[{"slot":"A","player":"Bob"},{"slot":"B","player":"Alice"}]}
S → Alice  {"type":"gameStart","phase":"placing","players":[{"slot":"A","player":"Bob"},{"slot":"B","player":"Alice"}]}
S → Bob    {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Bob","wins":0},{"slot":"B","player":"Alice","wins":1}]}
S → Alice  {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Bob","wins":0},{"slot":"B","player":"Alice","wins":1}]}
```

Ein Zuschauer erhält dieselben `rematchRequested`- und `gameStart`-Nachrichten
und den öffentlichen `state` mit demselben `score`, aber kein `welcome`.

### rematchRequested

```json
{"type":"rematchRequested","slot":"A","player":"Alice"}
```

Richtung S → C, ungefragt an beide Spieler und alle Zuschauer. Pflichtfelder:
`type`: genau rematchRequested; `slot`: A oder B, Slot des Spielers, der die
Revanche verlangt; `player`: dessen Name als string. So erfährt der Gegner vom
Wunsch; der Absender sieht damit, dass sein Wunsch angenommen wurde. Der Stand
ändert sich dadurch nicht, deshalb folgt kein `state`.

### error

```json
{"type":"error","code":"UNKNOWN_TYPE","message":"unbekannter Typ: nonsense"}
```

`type`: string, genau error; `code`: einer der unten dokumentierten Fehlercodes; `message`: string, lesbarer Grund

Ungültige JSON-Zeilen und JSON-Werte ohne Objektstruktur werden mit `INVALID_JSON` abgelehnt.

Vollständige Ablehnung eines Zuschauer-`place` oder -`shoot`, Richtung S → C,
ausschliesslich an den anfragenden Zuschauer:

```json
{"type":"error","code":"SPECTATOR_ONLY","message":"Zuschauer duerfen nicht platzieren oder schiessen"}
```

Pflichtfelder sind `type`, `code` und `message`. Der Text ist ein lesbares
Formatbeispiel; ausgewertet wird `code`. Weder Spieler noch andere Zuschauer
erhalten diese Ablehnung oder einen dadurch ausgelösten `state`.

Ablehnungen eines `rematch`, Richtung S → C, jeweils ausschliesslich an den
Absender, ohne `state` und ohne Änderung der Partie oder der Wünsche:

```json
{"type":"error","code":"WRONG_PHASE","message":"aktuelle Phase ist shooting; Revanche erst nach Spielende"}
{"type":"error","code":"SPECTATOR_ONLY","message":"Zuschauer koennen keine Revanche verlangen"}
{"type":"error","code":"DUPLICATE_REMATCH","message":"Revanche bereits verlangt"}
```

Die erste Zeile gilt für eine laufende Partie (in phase placing steht dort
placing, nach einem Spielerabgang waiting), die zweite für einen Zuschauer, die
dritte für einen zweiten Wunsch desselben Spielers vor dem Start der Revanche.

## Flotte und Spielregeln

Raster 10×10, ausgegebene Koordinaten kanonisch `A1`–`J10`. Eingaben wie `a01` werden zu `A1` normalisiert; Kleinbuchstaben und führende ASCII-Nullen sind erlaubt, Unicode-Ziffern nicht. Doppelbeschuss wird nach Normalisierung geprüft. Platzierung: `h` nach rechts, `v` nach unten. Je ein Carrier (5), Battleship (4), Cruiser (3), Submarine (3) und Destroyer (2), insgesamt 17 Felder. Keine Überlappung oder Überschreitung des Rasters; angrenzende Schiffe sind erlaubt. Diese klassische Flotte ist im [Regelblatt](REGELN.md) festgelegt.

Phasen: `waiting` → `placing` → `shooting` → `finished`. Nach beiden gültigen Platzierungen beginnt `A`; jeder gültige Schuss wechselt den Spieler. Treffer erlauben keinen Extrazug. Doppelbeschuss ist ungültig. Sind alle gegnerischen Schiffe versenkt, gewinnt der Schütze; kein Unentschieden. Nach `finished` beginnt eine neue Partie nur, wenn beide Spieler `rematch` senden; dann beginnt der Spieler, der zuletzt nicht begonnen hat (Slottausch, siehe «rematch»). Spieler erhalten nur ihre eigene Flotte und beide Schusslisten; Zuschauer erhalten nur beide Schusslisten ohne Flotten.

## Reihenfolge und Abbruch

- Erster Beitritt: welcome, waiting, danach state an den beitretenden Client.
- Zweiter Spielerbeitritt: dessen welcome, danach gameStart und gefilterte states an Spieler und bereits verbundene Zuschauer.
- Zuschauerbeitritt: spectator ohne slot, unmittelbar danach aktueller öffentlicher state an diesen Zuschauer.
- Platzierung: placeAck nur an den Akteur; danach je ein gefilterter state an Spieler und Zuschauer.
- Schuss: `result` nur an den Akteur, danach je ein gefilterter `state` an Spieler und Zuschauer. Beim letzten Treffer folgt anschliessend `gameOver` an alle.
- Ablehnung: error mit Grund ausschliesslich an den Absender, kein state-Push und keine Zustandsänderung.
- getState: ein individueller state ausschliesslich an den Anfragenden.
- Spielerabgang: einmal opponentLeft an verbliebenen Spieler und jeden Zuschauer, danach deren zurückgesetzte states. Kein zusätzlicher waiting-Nachrichtentyp.
- Zuschauerabgang: nur aus der separaten Liste entfernen; kein Reset und keine Benachrichtigung anderer Clients. Ein fehlgeschlagener Versand an einen Zuschauer darf die Zustellung an Spieler nicht abbrechen.
- Spielende: Der Sieger bekommt einen Punkt, danach folgen die Endzustände mit `score` und `gameOver`. Der Server läuft weiter.
- Erster Revanchewunsch: rematchRequested an beide Spieler und alle Zuschauer, kein state.
- Zweiter Revanchewunsch: neues Spielkern-Objekt, Wünsche gelöscht, Slots getauscht; je Spieler welcome mit neuem Slot, danach gameStart und gefilterte states an Spieler und Zuschauer.
- Spielerabgang verwirft zusätzlich alle offenen Revanchewünsche und setzt den Punktestand zurück.

Prüfen, Ändern und Senden sowie Spieler- und Zuschauerliste liegen unter derselben Spielsperre. Zustände sind unabhängige Kopien der erlaubten Sicht. Die beschriebene Ereignisreihenfolge gilt je TCP-Verbindung. Eine Reihenfolge zwischen verschiedenen Clientverbindungen und eine zeitgleiche Anzeige auf verschiedenen Rechnern werden nicht zugesichert.

Bei `leave`, `q`, EOF oder erkanntem Socket-Abbruch eines **Spielers** wird sein Slot freigegeben und die gesamte Runde sofort zurückgesetzt: beide Flotten/Treffer und Schusslisten leer, `phase: "waiting"`, `turn: null`, `winner: null`. Verbliebener Spieler und Zuschauer erhalten diesen Zustand unmittelbar als Push. Beim nächsten neuen Beitritt wird der freie Slot vergeben, `gameStart` startet eine frische Platzierung. Bestehende Zuschauer bleiben Zuschauer. Keine Wiederverbindungsfrist, kein `forfeit`-Sieg, keine automatische Wiederaufnahme. Ein physischer Verbindungsverlust wird erst behandelt, wenn die Socket-Schicht ihn erkennt.

## Fehlercodes

| Code | Anlass |
|---|---|
| `SPECTATOR_ONLY` | Ein Zuschauer sendet place, shoot oder rematch; nur privat abgelehnt. |
| `ALREADY_JOINED` | Diese Verbindung ist bereits als Spieler oder Zuschauer angemeldet. |
| `MISSING_PLAYER` | join ohne gültigen nichtleeren Namen. |
| `NOT_JOINED` | place, shoot, getState, leave oder rematch vor join. |
| `NOT_YOUR_TURN` | shoot vom falschen Spieler. |
| `CELL_OUT_OF_BOUNDS` | shoot-Feld fehlt, hat ein ungültiges Format oder liegt ausserhalb A1-J10. |
| `DUPLICATE_SHOT` | Dieses Feld wurde vom Schützen bereits beschossen. |
| `WRONG_PHASE` | Aktion in der falschen Phase, erneute Platzierung desselben Spielers oder rematch vor dem Spielende. |
| `DUPLICATE_REMATCH` | Derselbe Spieler verlangt die Revanche ein zweites Mal, bevor sie startet. |
| `INVALID_PLACEMENT` | Flotte, Schiffstypen, Start/Richtung, Überlappung oder Rasterüberstand sind ungültig. |
| `INVALID_JSON` | Zeile ist kein gültiges JSON-Objekt (auch Listen/Skalare). |
| `UNKNOWN_TYPE` | type fehlt oder hat keinen bekannten Nachrichtennamen. |

`PLAYER_SPOOFING` ist kein ausgegebener Fehlercode: Die Zuordnung erfolgt über den Socket. Nachrichten zur falschen Zeit oder mit ungültigen Daten werden nur dem Absender abgelehnt; eine erfolgreiche regelkonforme Aktion ist die Voraussetzung für eine Spielzustandsänderung.

## Ablaufbeispiel einer vollständigen Partie

Dies ist ein nachvollziehbares Protokollbeispiel **ohne Zuschauer**, kein Ausführungsnachweis. Alice/A wählt die Katalogflotte in den Zeilen 1–5, Bob/B eine andere Flotte in den Zeilen 6–10. Die Anwendung schreibt diese Beispielpositionen nicht vor. Jede JSON-Darstellung ist eine vollständige Nachricht mit abschliessendem LF; A/B bei einer gemeinsamen Meldung bedeutet zwei Sendungen. Personalisierte state-Nachrichten stehen getrennt da. Der anschliessende Zuschauerablauf ergänzt die dritte Sicht.

### Beitritt und Platzierung

```text
A → S  {"type":"join","player":"Alice"}
S → A  {"type":"welcome","slot":"A","player":"Alice","phase":"waiting"}
S → A  {"type":"waiting","reason":"warte auf Gegner"}
S → A  {"type":"state","phase":"waiting","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0}]}
B → S  {"type":"join","player":"Bob"}
S → B  {"type":"welcome","slot":"B","player":"Bob","phase":"placing"}
S → A/B  {"type":"gameStart","phase":"placing","players":[{"slot":"A","player":"Alice"},{"slot":"B","player":"Bob"}]}
S → A  {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
S → B  {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
A → S  {"type":"place","ships":[{"type":"Carrier","start":"A1","direction":"h"},{"type":"Battleship","start":"A2","direction":"h"},{"type":"Cruiser","start":"A3","direction":"h"},{"type":"Submarine","start":"A4","direction":"h"},{"type":"Destroyer","start":"A5","direction":"h"}]}
S → A  {"type":"placeAck","phase":"placing"}
S → A  {"type":"state","phase":"placing","turn":null,"ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
S → B  {"type":"state","phase":"placing","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
B → S  {"type":"place","ships":[{"type":"Carrier","start":"A6","direction":"h"},{"type":"Battleship","start":"A7","direction":"h"},{"type":"Cruiser","start":"A8","direction":"h"},{"type":"Submarine","start":"A9","direction":"h"},{"type":"Destroyer","start":"A10","direction":"h"}]}
S → B  {"type":"placeAck","phase":"shooting"}
S → A  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
S → B  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A6","B6","C6","D6","E6"],"hits":[]},{"type":"Battleship","cells":["A7","B7","C7","D7"],"hits":[]},{"type":"Cruiser","cells":["A8","B8","C8"],"hits":[]},{"type":"Submarine","cells":["A9","B9","C9"],"hits":[]},{"type":"Destroyer","cells":["A10","B10"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
```

Nach jedem erfolgreichen Ereignis treffen die beiden state-Nachrichten ohne getState ein. Bereits nach Alices Platzierung sehen beide phase placing, aber nur Alice kennt ihre Schiffe. Nach Bobs Platzierung beginnt A. Die Namen/Slots stehen in gameStart; unbeschossene Schiffe des Gegners fehlen in jeder eigenen Ansicht.

### Alle Schüsse

Für jede Tabellenzeile sendet der genannte Spieler shoot mit dem angegebenen field; er erhält result mit den vier angegebenen Feldern. Nach **jeder** Tabellenzeile erhalten A und B den vollständigen eigenen state, auch wenn B nichts sendet. Bei Zug 33 folgt nach diesen beiden Endzuständen `gameOver` an A und B. Die Beispiele schreiben A vor B; diese Reihenfolge zwischen verschiedenen Clientverbindungen ist keine Protokollzusage.

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
S → A  {"type":"state","phase":"shooting","turn":"B","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{"A6":"hit"},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
S → B  {"type":"state","phase":"shooting","turn":"B","ownShips":[{"type":"Carrier","cells":["A6","B6","C6","D6","E6"],"hits":["A6"]},{"type":"Battleship","cells":["A7","B7","C7","D7"],"hits":[]},{"type":"Cruiser","cells":["A8","B8","C8"],"hits":[]},{"type":"Submarine","cells":["A9","B9","C9"],"hits":[]},{"type":"Destroyer","cells":["A10","B10"],"hits":[]}],"shotsAtOpponent":{},"shotsAtSelf":{"A6":"hit"},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
B → S  {"type":"shoot","field":"F1"}
S → B  {"type":"result","field":"F1","result":"miss","sunk":null,"turn":"A"}
S → A  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{"A6":"hit"},"shotsAtSelf":{"F1":"miss"},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
S → B  {"type":"state","phase":"shooting","turn":"A","ownShips":[{"type":"Carrier","cells":["A6","B6","C6","D6","E6"],"hits":["A6"]},{"type":"Battleship","cells":["A7","B7","C7","D7"],"hits":[]},{"type":"Cruiser","cells":["A8","B8","C8"],"hits":[]},{"type":"Submarine","cells":["A9","B9","C9"],"hits":[]},{"type":"Destroyer","cells":["A10","B10"],"hits":[]}],"shotsAtOpponent":{"F1":"miss"},"shotsAtSelf":{"A6":"hit"},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0},{"slot":"B","player":"Bob","wins":0}]}
```

Bob sieht Alices ersten Treffer auf A6 in shotsAtSelf und seiner eigenen Flotte. Alice kennt dadurch ausschliesslich das getroffene Feld, nicht Bobs übrige Schiffsfelder. Bobs Fehlschuss F1 erscheint danach bei Alice in shotsAtSelf und bei Bob in shotsAtOpponent.

### Letzter Schuss, Endzustände und Abgang

Nach den Tabellenzeilen 1–32 folgt ohne zusätzliche Zustandsabfrage:

```text
A → S  {"type":"shoot","field":"B10"}
S → A  {"type":"result","field":"B10","result":"sunk","sunk":"Destroyer","turn":null}
S → A  {"type":"state","phase":"finished","turn":null,"ownShips":[{"type":"Carrier","cells":["A1","B1","C1","D1","E1"],"hits":[]},{"type":"Battleship","cells":["A2","B2","C2","D2"],"hits":[]},{"type":"Cruiser","cells":["A3","B3","C3"],"hits":[]},{"type":"Submarine","cells":["A4","B4","C4"],"hits":[]},{"type":"Destroyer","cells":["A5","B5"],"hits":[]}],"shotsAtOpponent":{"A6":"hit","B6":"hit","C6":"hit","D6":"hit","E6":"sunk","A7":"hit","B7":"hit","C7":"hit","D7":"sunk","A8":"hit","B8":"hit","C8":"sunk","A9":"hit","B9":"hit","C9":"sunk","A10":"hit","B10":"sunk"},"shotsAtSelf":{"F1":"miss","G1":"miss","H1":"miss","I1":"miss","J1":"miss","F2":"miss","G2":"miss","H2":"miss","I2":"miss","J2":"miss","F3":"miss","G3":"miss","H3":"miss","I3":"miss","J3":"miss","F4":"miss"},"winner":"A","score":[{"slot":"A","player":"Alice","wins":1},{"slot":"B","player":"Bob","wins":0}]}
S → B  {"type":"state","phase":"finished","turn":null,"ownShips":[{"type":"Carrier","cells":["A6","B6","C6","D6","E6"],"hits":["A6","B6","C6","D6","E6"]},{"type":"Battleship","cells":["A7","B7","C7","D7"],"hits":["A7","B7","C7","D7"]},{"type":"Cruiser","cells":["A8","B8","C8"],"hits":["A8","B8","C8"]},{"type":"Submarine","cells":["A9","B9","C9"],"hits":["A9","B9","C9"]},{"type":"Destroyer","cells":["A10","B10"],"hits":["A10","B10"]}],"shotsAtOpponent":{"F1":"miss","G1":"miss","H1":"miss","I1":"miss","J1":"miss","F2":"miss","G2":"miss","H2":"miss","I2":"miss","J2":"miss","F3":"miss","G3":"miss","H3":"miss","I3":"miss","J3":"miss","F4":"miss"},"shotsAtSelf":{"A6":"hit","B6":"hit","C6":"hit","D6":"hit","E6":"sunk","A7":"hit","B7":"hit","C7":"hit","D7":"sunk","A8":"hit","B8":"hit","C8":"sunk","A9":"hit","B9":"hit","C9":"sunk","A10":"hit","B10":"sunk"},"winner":"A","score":[{"slot":"A","player":"Alice","wins":1},{"slot":"B","player":"Bob","wins":0}]}
S → A  {"type":"gameOver","winner":"A","reason":"sunk"}
S → B  {"type":"gameOver","winner":"A","reason":"sunk"}
B → S  {"type":"leave"}
S → A  {"type":"opponentLeft","slot":"B","player":"Bob"}
S → A  {"type":"state","phase":"waiting","turn":null,"ownShips":[],"shotsAtOpponent":{},"shotsAtSelf":{},"winner":null,"score":[{"slot":"A","player":"Alice","wins":0}]}
```

Bob bekommt keine direkte Antwort auf leave; seine Verbindung endet. Alice erhält opponentLeft und danach den leeren waiting-Zustand automatisch. Ein Ersatzspieler erhält den freien Slot B, beide bekommen gameStart und ihren neuen placing-Zustand. Auch nach Spielende enthält Alices state keine unbeschossene gegnerische Flotte.
