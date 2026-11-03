# Abgleich der zwei Startvarianten

Stand: 03.11.2026, nach lokalem Paketbau und Prüfung. Die
[Spezifikation](../superpowers/specs/2026-11-03-two-versions-design.md)
beschreibt zwei Startprofile und zwei separat entpackbare ZIPs aus einer
gemeinsamen Codebasis. Eine ausdrückliche spätere Nutzerkorrektur geht vor.
Der Originalauftrag [Kursmeilenstein 5](../assignments/05_assignment.txt)
verlangt unter anderem die fünf Quelldateien und einen Server-Terminalbeleg
aus einem **echten** Lauf über zwei Rechner. Die bisherige lokale
[M5-Prüfung](05_requirements.md) ersetzt diesen praktischen Nachweis nicht.

| Anforderung | Vorgesehene Umsetzung | Prüfstatus |
|---|---|---|
| Zwei klar unterscheidbare Einstiege | `varianten/localhost/start.py` und `varianten/zwei_rechner/start.py`; je eigene `START.md`. | Beide CLI-Hilfen gelesen; die neue strenge Suite [155/155](../evidence/two_versions_2026-11-03/full_final.json) prüfte die Profile, darunter 29 echte GUI-Tests. |
| Eine Regelquelle | Beide Profile verwenden dieselben `src/`, `bilder/`, `REGELN.md` und Protokollversion 0.6. | Launcher und vorhandener Spielcode in der neuen Suite geprüft; ein realer Lauf über zwei Geräte bleibt offen. |
| localhost | Server bindet ausschliesslich `127.0.0.1`, beide Clients verbinden sich mit `127.0.0.1`; ein Gerät und drei Terminals. | [Vollständiger lokaler Tk/TCP-Lauf](../evidence/two_versions_2026-11-03/localhost_full_profile_game/result.json) PASS: Server über Profilwrapper, zwei echte Tk-Fenster, 33 Schüsse, Sieg/Niederlage, private Ablehnungen und Reset/Ersatzbeitritt. Die Clientwrapper wurden [separat bis `gameStart`](../evidence/two_versions_2026-11-03/localhost_startup_server.txt) mit zwei Tk-Prozessen geprüft; sie waren nicht Teil dieses Vollspieldurchlaufs. |
| zwei Rechner | Server und Alice auf Rechner 1, Bob auf Rechner 2; Server bindet `0.0.0.0`, Alice verbindet lokal, Bob braucht die tatsächliche Server-IPv4. | Ein [lokaler LAN-Server-Smoke](../evidence/two_versions_2026-11-03/lan_server_local_smoke_validated.txt) über den Profil-Wrapper bestand mit TCP-`join`/`welcome`; [drei ungültige Bob-IP-Aufrufe](../evidence/two_versions_2026-11-03/lan_invalid_ip.json) wurden vor einem Netzwerkversuch abgelehnt. Das war **ein Gerät**; echte Geräte/IPs und die vollständige Partie bleiben offen. |
| Persönliche Spielernamen | Beide Clientrollen verlangen `--name`; keine Namen werden fest im Code vorgegeben. | In Launcher-Tests geprüft. `<name_a>`/`<name_b>` in Anleitungen sind Platzhalter. |
| Je eine eigenständige Anleitung | [Ein Gerät](../../varianten/localhost/START.md) und [zwei Rechner](../../varianten/zwei_rechner/START.md) erklären Einrichtung, Repo-/ZIP-Pfade, Betriebssysteme, drei Terminals und Fehlerfälle. | Befehle gegen beide tatsächlichen `--help`-Ausgaben und Launcher-Tests abgeglichen; Windows nicht selbst ausgeführt. |
| Zwei eigenständig nutzbare Pakete | Eindeutige Profil-ZIPs mit jeweils `start.py`, `START_HIER.md`, gemeinsamem Programmcode, Assets, Pflichtdateien und Manifest/Prüfsumme. | Die endgültigen Archive `dist/Schiffe_versenken_localhost_2026-11-03_freigabe.zip` und `dist/Schiffe_versenken_zwei_rechner_2026-11-03_freigabe.zip` wurden separat entpackt. Die neben den ZIPs liegenden `.verification/`-Berichte melden jeweils PASS für SHA256, alle Manifestdateien, `start.py --help`, Kerntest und 155/155 Tests mit 29 echten GUI. Das Localhost-Paket bestand eine ganze lokale Partie; das Zwei-Rechner-Paket einen lokalen TCP-Beitritt. |
| Bestehende M5-Qualität | Kerntests, GUI- und Protokolltests bleiben nach Änderung grün. | Neuer strenger [Gesamtlauf: 155/155 Tests, 29 echte GUI, 0 Fehler/Skips](../evidence/two_versions_2026-11-03/full_final.json). Der erste Profil-Gesamtlauf [153/153](../evidence/two_versions_2026-11-03/full.json) und der Stand vor Profiländerung [139/139](../evidence/05_final_2026-11-03/full_release.json) bleiben historische Ergebnisse. |
| M5-Zweirechnernachweis | Tatsächliche ganze Partie über Rechner 1 und 2, Server-Terminalausgabe und reale Adressen. | **Offen, ausdrücklich auf später verschoben.** Lokale TCP-Tests und zwei erzeugte ZIPs zählen nicht. |

Die endgültigen Archive wurden separat entpackt geprüft. Der vollständige
Localhost-Lauf aus dem Paket liegt unter
`dist/Schiffe_versenken_localhost_2026-11-03_freigabe.verification/full_profile_game/result.json`;
der lokale LAN-Serverbeleg unter
`dist/Schiffe_versenken_zwei_rechner_2026-11-03_freigabe.verification/lan_local_smoke.json`.
Die Clientwrapper waren zuvor separat bis `gameStart` geprüft, nicht Teil
des vollständigen GUI-Demolaufs. `dist/` wird nicht in die Pakete
aufgenommen. Eine Partie über zwei echte Rechner ist nicht belegt.

Beim vorangehenden Archiv mit Suffix `_release` meldete ein erster
Gesamtlauf aus dem entpackten Localhost-Paket
`dist/Schiffe_versenken_localhost_2026-11-03_release.verification/full.json`
**154/155**: Ein echter Tk-Tastaturtest zählte drei statt zwei Aufrufe,
alle auf demselben Hauptthread. Der unveränderte isolierte Test und der
unveränderte Gesamtlauf
`dist/Schiffe_versenken_localhost_2026-11-03_release.verification/full_retry.json`
bestanden. Die Ursache des zusätzlichen Aufrufs ist nicht nachgewiesen;
beide Rohberichte bleiben erhalten. Die für diese Abgabe massgebenden
Berichte liegen in den Prüfverzeichnissen neben den endgültigen ZIPs.

Frühere Archive, Originalaufgaben und Rohbelege bleiben erhalten. Für
Paket- und GUI-Nachweise werden nur tatsächlich erstellte und geprüfte
Dateien mit ihrem eigenen Datum und Ergebnis eingetragen. Ein Test auf
Windows oder Python 3.12 wird erst nach eigener Ausführung behauptet.
Der erste [LAN-Smoke-Rohlog](../evidence/two_versions_2026-11-03/lan_server_local_smoke.txt)
zeigt ebenfalls eine gültige Serverantwort, doch ein zu strenger
Stringvergleich im Prüfskript meldete damals fälschlich einen Fehler.
Er zählt nicht als PASS; die korrigierte Prüfung wertete JSON aus.
