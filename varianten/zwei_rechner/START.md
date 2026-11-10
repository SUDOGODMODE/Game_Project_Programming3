# Schiffe versenken auf zwei Rechnern

In dieser Variante laufen **Server und erster Client auf Rechner 1**,
**zweiter Client auf Rechner 2**. Beide Rechner müssen sich im selben
erreichbaren LAN befinden. Rechner 2 benötigt die echte IPv4-Adresse von
Rechner 1. Das Spiel verwendet weiterhin denselben Regelkern und dasselbe
Protokoll wie die localhost-Variante. Im Profil-ZIP liegt diese Anleitung
als `START_HIER.md` im inneren Projektordner.

## 1. Projekt und Python auf beide Rechner bringen

Das **gleiche** Zwei-Rechner-ZIP auf beiden Geräten entpacken. Es erzeugt
einen äusseren Ordner `Schiffe_versenken_zwei_rechner/` und darin den
Projektordner `Game_Project_Programming3/`. Auf **beiden** Geräten in den
inneren Projektordner wechseln, in dem `start.py`, `src/` und `bilder/`
liegen. `Dokumente/` liegt daneben und ist für den Spielstart nicht nötig.
Im Repository statt des `start.py` im Projektordner den Einstieg
`varianten/zwei_rechner/start.py` verwenden.

Auf beiden Rechnern sind Python **3.12 oder neuer**, tkinter und eine
grafische Sitzung erforderlich; zusätzliche Python-Pakete sind nicht
nötig. Eine vorhandene `.venv` weiterverwenden, sonst auf **jedem Gerät**
eine eigene Umgebung anlegen. Eine `.venv` nicht vom anderen Gerät
herüberkopieren.

**macOS/Linux, je Gerät:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m tkinter
```

**Windows PowerShell, je Gerät:**

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m tkinter
```

Das tkinter-Testfenster danach schliessen. macOS/Linux verwendet in den
folgenden Befehlen `python3`; Windows nach Aktivierung `python`.

## 2. Server-IP von Rechner 1 bestimmen

Auf Rechner 1 die tatsächliche IPv4-Adresse der Netzwerkkarte im
gemeinsamen LAN ermitteln, etwa in den Netzwerkeinstellungen oder unter
Windows mit `ipconfig`. Diese Adresse als `<server_ipv4>` in Bobs Befehl
einsetzen. Keine Adresse raten oder aus Beispielen übernehmen.

`0.0.0.0` ist nur die Bindeadresse des Servers und **keine** Zieladresse
für Bob. `127.0.0.1` zeigt auf den jeweils eigenen Rechner: Bei Bob
würde es also fälschlich auf Rechner 2 zeigen. Der Start lehnt eine
fehlende oder ungültige Server-IP für Bob ab. Alle Prozesse müssen
denselben Port verwenden; unten ist es 5100.

## 3. In drei Terminals starten

In **jedem** Terminal im inneren Projektordner beginnen und die dortige
`.venv` aktivieren. Reihenfolge: Server auf Rechner 1, dann Alice auf
Rechner 1, zuletzt Bob auf Rechner 2. Der Server vergibt Slot A an die
erste beigetretene Verbindung. Für Alice als A muss sie vor Bob starten.
`<name_a>` und `<name_b>` durch zwei selbst gewählte, unterschiedliche
Namen ersetzen; die Anführungszeichen beibehalten.

**macOS/Linux, entpacktes Profil-ZIP:**

| Ort | Befehle nach dem Wechsel in den inneren Projektordner |
|---|---|
| Rechner 1, Terminal 1, Server | `source .venv/bin/activate`<br>`python3 start.py server --port 5100` |
| Rechner 1, Terminal 2, Alice | `source .venv/bin/activate`<br>`python3 start.py alice --name "<name_a>" --port 5100` |
| Rechner 2, Terminal 1, Bob | `source .venv/bin/activate`<br>`python3 start.py bob --name "<name_b>" --server-ip "<server_ipv4>" --port 5100` |

**Windows PowerShell, entpacktes Profil-ZIP:**

| Ort | Befehle nach dem Wechsel in den inneren Projektordner |
|---|---|
| Rechner 1, Terminal 1, Server | `.venv\Scripts\Activate.ps1`<br>`python start.py server --port 5100` |
| Rechner 1, Terminal 2, Alice | `.venv\Scripts\Activate.ps1`<br>`python start.py alice --name "<name_a>" --port 5100` |
| Rechner 2, Terminal 1, Bob | `.venv\Scripts\Activate.ps1`<br>`python start.py bob --name "<name_b>" --server-ip "<server_ipv4>" --port 5100` |

**Direkt im Quellrepository, macOS/Linux:** Auf jedem Rechner im
Projektordner beginnen, jedes Terminal einzeln aktivieren und in dieser
Reihenfolge starten:

```bash
# Rechner 1, Terminal 1: Server
source .venv/bin/activate
python3 varianten/zwei_rechner/start.py server --port 5100
```

```bash
# Rechner 1, Terminal 2: erster Client
source .venv/bin/activate
python3 varianten/zwei_rechner/start.py alice --name "<name_a>" --port 5100
```

```bash
# Rechner 2, Terminal 1: zweiter Client
source .venv/bin/activate
python3 varianten/zwei_rechner/start.py bob --name "<name_b>" --server-ip "<server_ipv4>" --port 5100
```

**Direkt im Quellrepository, Windows PowerShell:**

```powershell
# Rechner 1, Terminal 1: Server
.venv\Scripts\Activate.ps1
python varianten/zwei_rechner/start.py server --port 5100
```

```powershell
# Rechner 1, Terminal 2: erster Client
.venv\Scripts\Activate.ps1
python varianten/zwei_rechner/start.py alice --name "<name_a>" --port 5100
```

```powershell
# Rechner 2, Terminal 1: zweiter Client
.venv\Scripts\Activate.ps1
python varianten/zwei_rechner/start.py bob --name "<name_b>" --server-ip "<server_ipv4>" --port 5100
```

Der Server bindet an `0.0.0.0:5100`, Alice verbindet sich lokal
über `127.0.0.1:5100`, Bob über `<server_ipv4>:5100`.

## 4. Spielen, beenden und Nachweis aufheben

Nach Alices Beitritt ist „Warte auf Gegner“ normal. Sobald Bob verbunden
ist, in beiden Fenstern die eigene Flotte bearbeiten oder „Flotte senden“
wählen. Nach beiden Bestätigungen beginnt Slot A. Treffer, Wasser,
Versenkung und Ablehnungen erscheinen in den jeweiligen Fenstern. Die
Bedienung steht auch unter `docs/guides/user_manual.md`.

Zum Beenden beide Clientfenster schliessen und im Serverterminal auf
Rechner 1 **Ctrl+C** drücken. Bei Verbindungsabbruch wird die Runde
zurückgesetzt; der verbleibende Spieler wartet auf Ersatz.

Keine privaten Flotten aus Clientfenstern in das Serverlog übertragen.

## Wenn die Verbindung nicht klappt

| Beobachtung | Prüfen |
|---|---|
| Bob: Verbindung abgelehnt | Server läuft auf Rechner 1, richtige `<server_ipv4>`, gleicher Port und gemeinsames LAN? |
| Bob: Zeitüberschreitung | Firewall auf Rechner 1 für den gewählten Port und Erreichbarkeit im LAN prüfen. |
| Alice: Verbindung abgelehnt | Server zuerst starten; Alice verwendet lokal `127.0.0.1`. |
| Kein Fenster | tkinter und grafische Sitzung auf **dem betroffenen Rechner** prüfen. |
| Bob erscheint als A | Alice war nicht zuerst beigetreten; Runde neu starten und Startreihenfolge einhalten. |

Die Netzwerkverbindung verwendet TCP ohne Anmeldung oder Verschlüsselung;
vorgesehen ist ein vertrauenswürdiges Unterrichtsnetz.
