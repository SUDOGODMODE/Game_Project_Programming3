# Gemeinsame Einrichtung

Benötigt werden Python **3.12 oder neuer** mit tkinter und eine grafische
Sitzung. Es werden keine zusätzlichen Python-Pakete benötigt. Die letzte lokale M5-Releaseprüfung vom 03.11.2026 verwendete macOS,
Python 3.14.10 und Tk 9.1. Die neuen Startprofile haben eigene, noch
getrennt zu prüfende Nachweise.
Eine eigene Ausführung unter Python 3.12 oder auf Windows ist damit nicht belegt.

Alle Befehle im Projektordner ausführen. Die Bash-Beispiele verwenden
unter macOS/Linux durchgehend `python3`. Nach Aktivierung der `.venv` zeigen
`python` und `python3` hier beide auf Python 3.14.10 aus dieser Umgebung.
Ohne aktivierte Umgebung ist auf diesem Mac nur `python3` verfügbar.

Unter Windows PowerShell verwenden die entsprechenden Spiel-/Testbefehle
nach Aktivierung der `.venv` normalerweise `python` statt `python3`.
Die Umgebung dort mit dem Python-3-Launcher erstellen (nur falls noch keine
vorhanden ist):

```powershell
py -3 --version
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Unter macOS/Linux:

```bash
python3 --version
python3 -m venv .venv
```

Eine vorhandene `.venv` weiterverwenden. Aktivierung unter macOS/Linux:

```bash
source .venv/bin/activate
```

Unter Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Danach tkinter prüfen; unter macOS/Linux:

```bash
python3 -m tkinter
```

Unter Windows PowerShell:

```powershell
python -m tkinter
```

Es öffnet sich ein kleines Testfenster. Fehlt tkinter, eine Python-Installation
mit Tcl/Tk verwenden. Unter Linux stellt die Distribution dafür häufig das
Paket `python3-tk` bereit. `pip install tkinter` ist kein Installationsweg.
In einer Sitzung ohne Bildschirm lassen sich die Kerntests durchführen;
GUI-Tests benötigen einen echten oder virtuellen Bildschirm.

## Startprofil wählen

Die beiden Profile verwenden dieselben Quellen und Bilder, aber
unterschiedliche Adressen und Geräteverteilung:

| Profil | Geräte | Anleitung |
|---|---|---|
| localhost | Server und zwei Clients auf einem Gerät | [Start auf einem Gerät](../../varianten/localhost/START.md) |
| zwei Rechner | Server und erster Client auf Rechner 1; zweiter Client auf Rechner 2 | [Start auf zwei Rechnern](../../varianten/zwei_rechner/START.md) |

Jede Startanleitung enthält die vollständigen Befehle für das Quellrepo
und das entpackte Profil-ZIP, getrennt nach macOS/Linux und Windows.
Für beide Profile gilt: In jedem neuen Terminal die `.venv` aktivieren,
Server vor den Clients starten, und denselben Port auf allen Prozessen
verwenden. Der erste beigetretene Client bekommt Slot A. Das
[Benutzerhandbuch](user_manual.md) beschreibt Platzierung, Schüsse und
Abbruch.

`src/` und `bilder/` zusammenlassen; der grafische Client braucht das
PNG `bilder/schiff.png` und die fünf SVG-Dateien unter `bilder/flotte/`.
Der Server nennt bei jedem Start einen neuen JSONL-Metadatenlogpfad unter
`logs/`. Das Log enthält keine Flotten oder vollständigen Zustände.

Der localhost-Betrieb braucht nach der Einrichtung kein LAN. Für zwei
Rechner muss der zweite Client die tatsächliche IPv4-Adresse von Rechner 1
bekommen; `0.0.0.0` ist nur eine Server-Bindeadresse. Startanleitungen und
lokale Tests belegen noch keinen echten Zweirechnerlauf. Der geforderte
M5-Terminalbeleg und der getrennte ältere Dreirechnernachweis bleiben offen.

## Terminalwerkzeuge

```bash
python3 src/local_game.py
python3 src/play.py 127.0.0.1 Alice --port 5100
python3 src/client.py 127.0.0.1 Alice --port 5100
```

`local_game.py` spielt ohne Netzwerk an einer Tastatur. `play.py` ist der
Konsolen-Spielclient mit bekannter Standardflotte; für einen Diagnoseversuch
beide Spieler damit starten. Die GUI erlaubt individuelle Flotten.
`client.py` ist der einfache Lobby-/Nachrichtenclient. Die Programme bleiben
für die Fehlersuche erhalten. q beendet den jeweiligen Konsolenclient.

## Häufige Probleme

| Beobachtung | Prüfen |
|---|---|
| Verbindung abgelehnt | Server läuft, richtige Adresse und gleicher Port? |
| Server kann Port nicht belegen | Anderer Prozess belegt Port; auf beiden Seiten z.B. 5100 wählen. |
| Kein Tk-Fenster / TclError | tkinter und grafische Sitzung mit `python3 -m tkinter` prüfen. |
| Warten auf Gegner | Zweiten Client starten; ein dritter Spieler wird abgewiesen. |
| Flotte abgelehnt | Fünf verschiedene Typen, gültige Startfelder/Richtungen, keine Überlappung oder Randüberschreitung. |
| Schuss abgelehnt | Platzierung abgeschlossen, eigener Zug und noch nicht beschossenes Feld? |
| Gegner hat verlassen | Partie wurde zurückgesetzt; Ersatzspieler beginnt eine neue Partie. |

Fehler bei der Prüfung mit Befehl, Python-Version und vollständiger Ausgabe
festhalten. Eine Sandbox kann lokale Portbindungen oder Fenster blockieren;
das ist separat von einem Programmfehler zu behandeln.
