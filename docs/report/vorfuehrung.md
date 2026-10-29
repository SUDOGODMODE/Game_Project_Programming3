# Vorführung und Abnahme

Die Schritte sind ein Leitfaden. Ihre Beschreibung ist kein Nachweis einer
bereits gehaltenen Vorführung. Alle Befehle mit aktivierter `.venv`; auf
Windows nach Aktivierung `python` statt `python3` verwenden.

1. README, Regeln und Protokoll zeigen. Den zentralen Server, private Sichten
   und den vollständigen Zustandsaufbau erklären.
2. `python3 tools/run_tests.py --require-gui --report-json "<neue_datei.json>"`
   ausführen. Skips und Fehler sichtbar besprechen; vorhandene Berichte erhalten.
3. Server mit `python3 -u src/server.py --port 5100` starten. Den tatsächlich
   ausgegebenen neuen JSONL-Pfad notieren. Für reine lokale Probe zusätzlich
   `--host 127.0.0.1` verwenden.
4. Auf zwei Clientgeräten `python3 src/client_gui.py "<server_ip>" "<name>" --port 5100`
   starten. Platzhalter vorher durch tatsächliche Werte ersetzen. Für eine lokale Probe zwei Fenster auf demselben
   Gerät öffnen. Gerätezahl und IPs ausdrücklich richtig benennen.
5. Verschiedene Flotten platzieren, ihre Geheimhaltung zeigen, A beginnen
   lassen. Einen Schuss ausser der Reihe und später einen Doppelbeschuss
   vorführen: nur der Absender erhält den Fehler; Bretter und Zug bleiben gleich.
6. Ganze Partie bis zum Sieg spielen. Nach demselben Zug beide Ansichten
   gemeinsam aufnehmen; tatsächliche fremde IPs im Serverterminal sichern.
7. Einen Client hart schliessen. Server und anderer Client laufen weiter,
   die Runde wird sofort zurückgesetzt. Ersatzclient verbinden und erneut
   platzieren. Das ist die dokumentierte Abbruchregel.
8. Den Metadatenmitschnitt öffnen: ISO-Zeit, Richtung, Typ und Slot zeigen;
   keine Flotteninhalte. Clientpayloads für Geheimhaltungsprüfung getrennt
   und nur mit bekannten Testdaten aufnehmen.

Für einen automatisierten **lokalen** Ablauf:

```bash
python3 tools/run_gui_demo.py --output "<neuer_nachweisordner>"
python3 tools/build_submission.py --output "<neues_abgabearchiv.zip>"
```

Das Werkzeugpaket enthält Manifest und offenen Abgabestatus. Frisch in einen
anderen Ordner entpacken, Manifest prüfen und von dort Tests/Start wiederholen.
Ein Paket allein erfüllt keine persönliche Reflexion oder Gerätevorführung.

Erklärfragen für die eigene Vorbereitung:

- Warum zeichnet der Klick nicht sofort einen Treffer?
- Weshalb brauchen Prüfen, Ändern und Zustandsversand dieselbe Sperre?
- Welche Felder darf der Gegner sehen? Wie prüft man tatsächliche Payloads?
- Wo trennen Queue/`after` Tk und Netzwerk? Wie werden Tk-Referenzen freigegeben?
- Wie erkennt der Transport vollständige Nachrichten trotz TCP-Paketgrenzen?
- Was bedeutet ein GUI-Skip, und welche praktischen Nachweise fehlen noch?

Für den gegenseitigen Fremdtest erhält die andere Person nur Protokoll und
Serveradresse. Tatsächliche Namen, Datum, selbst gebauten Client,
Rollenwechsel, Abweichungen und Rohbelege danach ergänzen. Bis dahin offen.
