# Schulnetz-Nachweis für Kursmeilenstein 4

**Stand: vorbereitet, noch nicht durchgeführt.** Der Benutzer hat am
27.10.2026 die Vorbereitung für einen späteren Versuch beauftragt.
Lokale automatisierte Prüfungen ersetzen diesen Nachweis nicht.

## Vorbereitung

- [ ] Drei Rechner bereitstellen: ein Server, zwei andere Rechner als Clients.
- [ ] Auf allen Rechnern dieselben Projektdateien, Python >=3.12 und tkinter prüfen.
- [ ] Namen der tatsächlich beteiligten Personen erst beim Versuch eintragen:
  `<person_server>`, `<person_client_a>`, `<person_client_b>`.
- [ ] Server-IPv4 mit `ipconfig` (Windows), `ip addr` (Linux) oder
  `ifconfig` (macOS) bestimmen: `<server_ip>`.
- [ ] Zwei unterschiedliche fremde Clientadressen notieren:
  `<client_a_ip>`, `<client_b_ip>`; keine 127.0.0.1-Adressen.
- [ ] Vorab aufschreiben: Nach dem gewählten Schuss erwartet A
  `<sicht_a>`, B erwartet `<sicht_b>`, am Zug ist `<slot>`.

## Durchführen

Auf jedem Gerät und in jedem neuen Terminal zuerst die Projektumgebung
aktivieren: macOS/Linux `source .venv/bin/activate`, Windows PowerShell
`.venv\Scripts\Activate.ps1`. Das gilt auch für das Serverterminal.

Server im Projektordner starten und Ausgabe sichern. macOS/Linux:

```bash
python3 -u src/server.py --port 5100 2>&1 | tee docs/evidence/04_school_server.txt
```

Windows PowerShell:

```powershell
python -u src/server.py --port 5100 2>&1 | Tee-Object docs/evidence/04_school_server.txt
```

Auf den beiden anderen Rechnern die Projektumgebung aktivieren und starten,
Platzhalter vorher ersetzen. macOS/Linux verwenden `python3`, Windows in der
aktivierten Umgebung `python`:

```bash
python3 src/client_gui.py "<server_ip>" "<spieler_name>" --port 5100
```

- [ ] Erstes Fenster zeigt Warten; mit zweitem Beitritt beginnt die Platzierung.
- [ ] Zwei verschiedene Flotten setzen, eine vollständige Partie spielen.
- [ ] Beide sehen nach jedem Zug denselben Verlauf und nächsten Spieler
  aus ihrer jeweiligen erlaubten Sicht. Die eigene Flotte ist privat.
- [ ] Beide Fenster nach demselben Zug fotografieren oder aufnehmen.
  Rechner, Datum, Zug/Feld und aktueller Spieler müssen zuordenbar sein.
- [ ] Vor dem eigenen Zug nochmals klicken: `NOT_YOUR_TURN` nur beim Absender.
  Bild oder Ausgabe unter `04_school_out_of_turn.*` sichern.
- [ ] Nach einem regulären Gegenzug ein bereits beschossenes Feld klicken:
  `DUPLICATE_SHOT`, nur beim Absender; Bild/Ausgabe sichern.
- [ ] Genau ein Spieler ist am Zug; kein Zustandswechsel bei Ablehnung.
- [ ] Ein Fenster schliessen: Server bleibt ohne Thread-Traceback aktiv,
  Gegner sieht Abbruch und zurückgesetzte Runde.
- [ ] Ersatzclient startet eine neue Platzierungsrunde.

## Nachher prüfen und abgeben

- [ ] Serverlog zeigt zwei verschiedene, tatsächlich fremde Client-IPs.
- [ ] Log enthält keine `ships`, `ownShips`, Startfelder oder vollständigen
  privaten Zustände. Der Server protokolliert nur Metadaten.
- [ ] Ausgehende Zustände im isolierten lokalen Testmitschnitt mit dem
  Protokoll vergleichen: ein Client erhält keine unbeschossene Gegnerflotte.
  Falls für den Schulversuch zusätzlich Payloads aufgezeichnet werden,
  jede Aufnahme nur aus Sicht des jeweiligen Empfängers prüfen/weitergeben.
- [ ] Beobachtungen und Abweichungen eintragen: `<beobachtung>`.
- [ ] Ergebnis mit tatsächlichem Datum und Personen in
  `docs/status/04_requirements.md` und `journal.md` ergänzen.
- [ ] Quellen: `src/netz.py`, `src/server.py`, `src/client_gui.py`,
  `src/board.py` als notwendige Serverabhängigkeit, aktuelles Protokoll und
  README zusammen mit Bildern, Ablehnungen und Serverlog bereitstellen.

Keine fehlende Ausgabe durch erfundene IP-Adressen oder umbenannte
Loopback-Ausgaben ersetzen. Die alten Nachweise unverändert aufbewahren.
