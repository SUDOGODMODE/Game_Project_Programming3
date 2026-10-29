# Installation und Start

Benötigt werden Python **3.12 oder neuer** mit tkinter und eine grafische
Sitzung. Es werden keine zusätzlichen Python-Pakete benötigt. Die lokale
Prüfung vom 29.10.2026 verwendet macOS, Python 3.14.10 und Tk 9.1.
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

Danach tkinter prüfen:

```bash
python3 -m tkinter
```

Es öffnet sich ein kleines Testfenster. Fehlt tkinter, eine Python-Installation
mit Tcl/Tk verwenden. Unter Linux stellt die Distribution dafür häufig das
Paket `python3-tk` bereit. `pip install tkinter` ist kein Installationsweg.
In einer Sitzung ohne Bildschirm lassen sich die Kerntests durchführen;
GUI-Tests benötigen einen echten oder virtuellen Bildschirm.

## Startvariante wählen

Ein Spielserver ist hier ein Python-Prozess, der neben den Clients laufen
kann. Ein separater Serverrechner ist nicht nötig. Nach der Python-/Tk-
Einrichtung braucht die lokale Variante kein Internet und kein WLAN.

| Infrastruktur | Server | Alice | Bob |
|---|---|---|---|
| Ein Gerät, auch offline | Gerät 1 | Gerät 1, `127.0.0.1` | Gerät 1, `127.0.0.1` |
| Zwei Geräte im selben LAN | Gerät 1 | Gerät 1, `127.0.0.1` | Gerät 2, Server-LAN-IP |
| Drei Geräte im selben LAN | Gerät 1 | Gerät 2, Server-LAN-IP | Gerät 3, Server-LAN-IP |

Regeln, GUI und Protokoll bleiben gleich. Nur Startort und Adressen ändern
sich. Die Kursabgabe verlangt zusätzlich den Versuch mit zwei fremden
Clientrechnern; zum Spielen bist du an diese Topologie nicht gebunden.

## Variante A: Server und zwei Clients auf deinem Gerät

Drei Terminals im Projektordner öffnen. In **jedem** Terminal zuerst die
Umgebung aktivieren und dann genau das zugehörige Programm starten:

**Terminal 1: Server zuerst starten und laufen lassen.**

```bash
source .venv/bin/activate
python3 -u src/server.py --host 127.0.0.1 --port 5100
```

**Terminal 2: Ersten Client starten.**

```bash
source .venv/bin/activate
python3 src/client_gui.py 127.0.0.1 Alice --port 5100
```

**Terminal 3: Zweiten Client starten.**

```bash
source .venv/bin/activate
python3 src/client_gui.py 127.0.0.1 Bob --port 5100
```

`127.0.0.1` bedeutet localhost, also dieses Gerät. Nach dem ersten Client
ist „Warte auf Gegner“ normal. Sobald Bob verbunden ist, in **beiden**
Fenstern die vorgeschlagene Flotte anpassen oder direkt „Flotte senden“
klicken. Nach beiden Bestätigungen beginnt Alice (Spieler A).

Port 5100 vermeidet mögliche Belegung von 5000; ohne Argument verwenden alle
Programme Port 5000. Server und Clients müssen denselben Port verwenden.
Die Bedienung ist im [Benutzerhandbuch](user_manual.md) beschrieben.

Lass das Serverterminal während der Partie offen und bediene die beiden
Fenster abwechselnd. A beginnt nach beiden Platzierungen. Mit zwei Personen
an demselben Bildschirm die private Flottenansicht des anderen nicht
mitlesen. Für getrennte Bildschirme die LAN-Variante nutzen.

Zum Beenden beide Clientfenster schliessen und den Server im Terminal mit
Ctrl+C stoppen. Später dieselben drei Befehle erneut ausführen; eine
abgebrochene Partie wird nicht gespeichert. Für diesen Startweg musst du
keine LAN-IP heraussuchen und keinen Router konfigurieren.

Der Server nennt beim Start seinen neuen Nachrichtenlogpfad. Standard ist
`logs/<utc_zeitstempel>_<zufall>.jsonl` im Projekt, unabhängig vom aktuellen
Arbeitsverzeichnis. Für einen gezielten Nachweis einen neuen Zielpfad wählen:

```bash
python3 -u src/server.py --host 127.0.0.1 --port 5100 --log-file "<neuer_logpfad.jsonl>"
```

Platzhalter zuerst ersetzen. Vorhandene Dateien werden abgelehnt, auch
wenn sie leer sind. Das Log enthält nur Zeitstempel und erlaubte Metadaten
der ein-/ausgehenden Nachrichten; es speichert keine Flotten oder Partien.
Für einen späteren Lauf einen neuen Namen verwenden.

Das GUI benötigt zusätzlich zum Quellcode `bilder/schiff.png` und die fünf
SVG-Dateien unter `bilder/flotte/`; `bilder/` und `src/` deshalb gemeinsam
belassen. PNG-Decoder und Canvas gehören zu Tk; es ist kein Pillow oder
anderes Laufzeitpaket erforderlich. Die vollständige lokale Partie mit der
neuen Oberfläche ist unter [Grafikprüfung vom 29.10.2026](../evidence/06_graphics_2026-10-29/README.md)
dokumentiert.

## Variante B: Über mehrere Geräte im lokalen Netzwerk

Auf jedem Gerät in **jedem neuen Terminal** zuerst die Projektumgebung wie
oben aktivieren: macOS/Linux `source .venv/bin/activate`, Windows PowerShell
`.venv\Scripts\Activate.ps1`. Das gilt für Server und beide Clients.

Den Server ohne `--host 127.0.0.1` starten; Standard ist `0.0.0.0`:

```bash
python3 -u src/server.py --port 5100
python3 src/client_gui.py "<server_ip>" "<spieler_name>" --port 5100
```

Auf beiden Clientrechnern `<server_ip>` durch die tatsächliche IPv4-Adresse
des Serverrechners und `<spieler_name>` durch den eigenen Namen ersetzen.
`0.0.0.0` ist eine Bindeadresse, keine Zieladresse für Clients. Bei fehlender
Verbindung Adresse, Port, gemeinsames Netz und eingehende lokale
Firewallfreigabe des Servers prüfen. Die Verbindung nutzt TCP ohne
Verschlüsselung und Anmeldung; vorgesehen ist das Unterrichtsnetz.

Für den geforderten Nachweis die [Schulnetz-Checkliste](../evidence/04_school_network_checklist.md)
verwenden. Dazu sind Server und zwei andere Clientrechner erforderlich.

**Mit nur zwei Geräten:** Server und Alice auf Gerät 1, Bob auf Gerät 2:

```bash
# Gerät 1, Terminal 1
python3 -u src/server.py --port 5100
# Gerät 1, Terminal 2
python3 src/client_gui.py 127.0.0.1 Alice --port 5100
# Gerät 2
python3 src/client_gui.py "<server_ip>" Bob --port 5100
```

**Mit drei Geräten:** Server auf Gerät 1 starten; auf Gerät 2 und 3 jeweils
einen Client mit `<server_ip>` und unterschiedlichem Namen starten. Der
Server hat genau zwei Spielerplätze. Ein dritter Client wird abgewiesen.

Der Ein-Gerät-Betrieb wurde mit einer vollständigen TCP-Partie und zwei
echten Fenstern geprüft. Die LAN-Varianten nutzen dieselben Programme;
der tatsächliche Fremdrechnernachweis ist noch offen.

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
