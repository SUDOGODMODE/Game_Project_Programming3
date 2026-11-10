# Schiffe versenken auf einem Gerät

Diese Variante startet **Server und zwei Spielfenster auf demselben Gerät**.
Sie benutzt ausschliesslich `127.0.0.1`; nach der Python-Einrichtung ist
kein LAN oder Internet nötig. Die Regeln und das Protokoll sind dieselben
wie in der Zwei-Rechner-Variante. Im Profil-ZIP liegt diese Anleitung als
`START_HIER.md` im inneren Projektordner.

## 1. Einrichtung

Benötigt werden Python **3.12 oder neuer**, tkinter und eine grafische
Sitzung. Es sind keine zusätzlichen Python-Pakete nötig. Alle Befehle
werden im entpackten inneren Projektordner
`Schiffe_versenken_localhost/Game_Project_Programming3/` ausgeführt,
in dem `start.py`, `src/` und `bilder/` liegen. Im Repository steht der Einstieg stattdessen unter
`varianten/localhost/start.py`.

**macOS/Linux:** Eine vorhandene `.venv` weiterverwenden. Sonst einmal
anlegen und tkinter prüfen; das Testfenster danach schliessen:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m tkinter
```

**Windows PowerShell:** Eine vorhandene `.venv` weiterverwenden. Sonst
einmal anlegen und tkinter prüfen:

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m tkinter
```

Falls tkinter nicht startet, eine Python-Installation mit Tcl/Tk verwenden.

## 2. Drei Terminals starten

In **jedem** der drei Terminals zuerst in den Projektordner wechseln und
die `.venv` aktivieren. Den Server zuerst starten und laufen lassen, danach
den ersten Client, dann den zweiten. `<name_a>` und `<name_b>` durch zwei
selbst gewählte, unterschiedliche Spielernamen ersetzen; die Anführungszeichen
beibehalten. Der erste beigetretene Client erhält Slot A und beginnt nach
beiden Platzierungen.

**macOS/Linux, entpacktes Profil-ZIP:**

| Terminal | Befehle nach dem Wechsel in den Projektordner |
|---|---|
| 1, Server | `source .venv/bin/activate`<br>`python3 start.py server --port 5100` |
| 2, erster Client | `source .venv/bin/activate`<br>`python3 start.py alice --name "<name_a>" --port 5100` |
| 3, zweiter Client | `source .venv/bin/activate`<br>`python3 start.py bob --name "<name_b>" --port 5100` |

**Windows PowerShell, entpacktes Profil-ZIP:**

| Terminal | Befehle nach dem Wechsel in den Projektordner |
|---|---|
| 1, Server | `.venv\Scripts\Activate.ps1`<br>`python start.py server --port 5100` |
| 2, erster Client | `.venv\Scripts\Activate.ps1`<br>`python start.py alice --name "<name_a>" --port 5100` |
| 3, zweiter Client | `.venv\Scripts\Activate.ps1`<br>`python start.py bob --name "<name_b>" --port 5100` |

**Direkt im Quellrepository, macOS/Linux:** Im Projektordner je ein
Terminal pro Zeile öffnen; in jedem Terminal stehen Aktivierung und
Startbefehl zusammen:

```bash
# Terminal 1: Server
source .venv/bin/activate
python3 varianten/localhost/start.py server --port 5100
```

```bash
# Terminal 2: erster Client
source .venv/bin/activate
python3 varianten/localhost/start.py alice --name "<name_a>" --port 5100
```

```bash
# Terminal 3: zweiter Client
source .venv/bin/activate
python3 varianten/localhost/start.py bob --name "<name_b>" --port 5100
```

**Direkt im Quellrepository, Windows PowerShell:**

```powershell
# Terminal 1: Server
.venv\Scripts\Activate.ps1
python varianten/localhost/start.py server --port 5100
```

```powershell
# Terminal 2: erster Client
.venv\Scripts\Activate.ps1
python varianten/localhost/start.py alice --name "<name_a>" --port 5100
```

```powershell
# Terminal 3: zweiter Client
.venv\Scripts\Activate.ps1
python varianten/localhost/start.py bob --name "<name_b>" --port 5100
```

Der Server bindet in diesem Profil nur an `127.0.0.1:5100`;
beide Clients verbinden sich dorthin. Ein anderer Port muss bei allen drei
Prozessen gleich angegeben werden.

## 3. Spielen und beenden

Nach dem ersten Client zeigt dessen Fenster „Warte auf Gegner“. Sobald
beide verbunden sind, in **beiden** Fenstern die vorgeschlagene Flotte
anpassen oder „Flotte senden“ wählen. Danach schiesst Slot A zuerst. Ein
Klick auf ein Zielrasterfeld sendet eine Anfrage; die Anzeige übernimmt
erst den bestätigten Serverzustand. Ablehnungen erscheinen in der
Statuszeile. Das Benutzerhandbuch liegt unter `docs/guides/user_manual.md`.

Zum Beenden beide Fenster schliessen und im Serverterminal **Ctrl+C**
drücken. Eine abgebrochene Partie wird nicht fortgesetzt. Der Server
schreibt seinen neuen Metadatenlogpfad beim Start ins Terminal.

## Wenn der Start nicht klappt

| Beobachtung | Prüfen |
|---|---|
| Verbindung abgelehnt | Serverterminal läuft; alle drei Prozesse verwenden denselben Port. |
| Kein Fenster | `python3 -m tkinter` beziehungsweise `python -m tkinter` und grafische Sitzung prüfen. |
| „Warte auf Gegner“ | Zweiten Client starten; zuerst beigetretener Client ist A. |
| Port belegt | Einen anderen Port in **allen drei** Startbefehlen verwenden. |
