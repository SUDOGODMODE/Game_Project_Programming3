# Kursmeilenstein 3 — Nachweis im Schulnetz

**Status: ausstehend.** Aufgabenquelle: [`03_two_players.txt`](../assignments/03_two_players.txt), Schritte 4, 6 und 7. Der lokale Nachweis steht in [`03_local_output.md`](03_local_output.md).

## Vor dem Versuch

- [ ] Server-Rechner und **zwei physisch andere Client-Rechner** bereitstellen.
- [ ] Datum, Python-Version, Rechnerrollen und Testpersonen notieren.
- [ ] Alle drei Rechner im erreichbaren Schulnetz, passende Firewall-Freigabe für den gewählten TCP-Port.
- [ ] Auf dem Server die Schulnetz-IPv4-Adresse ermitteln: Windows `ipconfig`, Linux `ip addr`, macOS `ifconfig` oder Netzwerkeinstellungen. Keine `127.0.0.1` verwenden.
- [ ] Einen gemeinsamen Port wählen: standardmässig 5000; bei Belegung (z. B. macOS-AirPlay) überall 5100 einsetzen.
- [ ] Für jeden der vier Fälle **vor** der Ausführung aufschreiben, welche Zeile in welchem Terminal erwartet wird. Die Tabelle unten ist die Protokollreferenz; eigene Vorhersagen und Beobachtungen getrennt notieren.

| Metadatum | Tatsächlicher Eintrag nach Vorbereitung |
|---|---|
| Datum/Uhrzeit | `<datum>` / `<uhrzeit>` |
| Server-Rechner / Schulnetz-IP | `<server_rechner>` / `<server_ip>` |
| Port | `<tcp_port>` |
| Python-Version je Rechner | `<python_version_server>` / `<python_version_client_1>` / `<python_version_client_2>` |
| Alice-Rechner / fremde Client-IP | `<client_1_rechner>` / `<client_1_ip>` |
| Bob-Rechner / andere fremde Client-IP | `<client_2_rechner>` / `<client_2_ip>` |
| Testende Person(en) / Lesepartnerschaft | `<testperson_name>` / `<lesepartner_name>` |

## Terminals starten und rohe Ausgaben sammeln

Die Befehle werden auf dem jeweils genannten Rechner **aus dessen Repository-Verzeichnis** gestartet. Alle Platzhalter im Format `<beispiel_art>` vor dem Start ersetzen: `<server_ip>` durch die Schulnetz-IP des Servers, `<tcp_port>` durch denselben gewählten Port auf allen Rechnern (standardmässig 5000, bei Belegung beispielsweise 5100). `<spieler_1_name>`, `<spieler_2_name>` und `<spieler_3_name>` sind die tatsächlichen Spielernamen; Alice, Bob und Carol bezeichnen unten diese drei Rollen. Die Anführungszeichen in den Befehlen verhindern, dass die Platzhalterzeichen als Shell-Umleitung interpretiert werden.

Server-Rechner:

```bash
python3 --version
python3 -u src/server.py --host 0.0.0.0 --port "<tcp_port>" | tee docs/evidence/03_school_server.txt
```

Fremder Client-Rechner 1 (Alice), offen lassen:

```bash
python3 --version
python3 -u src/client.py "<server_ip>" "<spieler_1_name>" --port "<tcp_port>" | tee docs/evidence/03_school_alice.txt
```

Fremder Client-Rechner 2 (Bob):

```bash
python3 --version
python3 -u src/client.py "<server_ip>" "<spieler_2_name>" --port "<tcp_port>" | tee docs/evidence/03_school_bob.txt
```

`-u` verhindert gepufferte Python-Ausgabe. `tee` ist optional und verfügbar auf macOS/Linux; unter Windows kann stattdessen der Terminalmitschnitt gespeichert werden. Die Dateien liegen zunächst auf dem jeweiligen Rechner und müssen für die Abgabe zusammengetragen werden. Vor einer Wiederholung vorherige Logs unter einem neuen Namen sichern, damit keine Ergebnisse überschrieben werden.

## Die vier verlangten Fälle

**Erwartungen — noch keine Beobachtungen:**

| Fall | Aktion | Erwartete Ausgabe | Beobachtet |
|---|---|---|---|
| 1 · erster Spieler | Alice verbinden, Fenster offen lassen | Alice: `welcome`, `slot: A`, `phase: waiting`; danach `waiting`, `reason: warte auf Gegner` | `<beobachtung>` |
| 2 · zweiter Spieler | Bob verbinden, Alice tippt nichts | Bob: `welcome`, `slot: B`, `phase: placing`; **Alice und Bob**: `gameStart`, `phase: placing`, Namen/Slots A und B | `<beobachtung>` |
| 3 · Spiel voll | Carol in zusätzlichem Terminal verbinden, A/B bleiben offen | Carol: `error`, `code: GAME_FULL`, `message: es sind bereits zwei Spieler verbunden`; Alice/Bob bleiben verbunden | `<beobachtung>` |
| 4a · q | Carol beenden, in Bob-Terminal `q` und Enter | Alice: genau ein `opponentLeft`, `slot: B`, `player: <spieler_2_name>`; Server läuft weiter | `<beobachtung>` |
| 4b · hartes Ende | Bob erneut verbinden, dann dessen Fenster/Prozess hart beenden | Alice: wieder genau ein `opponentLeft` für diesen neuen Bob-Beitritt; Server läuft weiter | `<beobachtung>` |
| Ergänzung · EOF | Bob erneut verbinden, dessen Standardeingabe beenden (macOS/Linux Ctrl-D; Windows Ctrl-Z, Enter) | Alice: genau ein `opponentLeft`; Server läuft weiter | `<beobachtung>` |
| Ergänzung · Ersatz | Nach jedem Abgang Bob oder einen neuen Namen erneut verbinden | neuer Client bekommt freien Slot B; beide bekommen `gameStart` für eine frische Platzierungsrunde | `<beobachtung>` |

Carol kann in einem weiteren Terminal auf einem der Client-Rechner gestartet werden; der geforderte Nachweis zweier verschiedener fremder Adressen bezieht sich auf Alice und Bob:

```bash
python3 -u src/client.py "<server_ip>" "<spieler_3_name>" --port "<tcp_port>" | tee docs/evidence/03_school_carol.txt
```

Für einen echten harten Prozessabbruch den Bob-Prozess im Taskmanager beenden oder in einem separaten Terminal zuerst seine PID eindeutig ermitteln. Unter macOS/Linux kann dann `kill -KILL "<client_pid>"` verwendet werden, wobei `<client_pid>` durch **genau die PID des Bob-Clients** ersetzt wird. Diese PID nicht mit der des Servers oder des `tee`-Prozesses verwechseln. Den verbliebenen Alice-Client und das Serverlog beobachten und speichern; der Bob-Mitschnitt endet beim Abbruch.

Beim Ersatzbeitritt verwenden:

```bash
python3 -u src/client.py "<server_ip>" "<spieler_2_name>" --port "<tcp_port>" | tee docs/evidence/03_school_bob_replacement.txt
```

Nach einem Abgang erhält Alice `opponentLeft`. Der Server setzt die Runde zurück; ein Ersatzbeitritt startet eine neue Platzierungsrunde. Details stehen im [Protokoll](../../PROTOKOLL.md#reihenfolge-und-abbruch). Ein physischer Netzverlust wird erst behandelt, wenn TCP ihn erkennt; der harte Prozessabbruch ist separat zu prüfen.

## Vor Abgabe prüfen

- [ ] Serverlog zeigt für die **gleichzeitig verbundenen** Alice- und Bob-Clients zwei unterschiedliche fremde IPv4-Adressen; keine ist `127.0.0.1` oder die Serveradresse.
- [ ] Beide Clientlogs enthalten denselben `gameStart` mit beiden Namen/Slots.
- [ ] Der erste Client erhielt den Push ohne weitere eigene Nachricht.
- [ ] Carol-Log enthält `GAME_FULL`; danach laufen Server und A/B weiter.
- [ ] q und hartes Ende sind je separat dokumentiert; Alice erhält pro Abgang genau einmal `opponentLeft`.
- [ ] Ein Ersatzbeitritt gelingt, derselbe freie Slot wird verwendet und `gameStart` kommt bei beiden an.
- [ ] Eigene Vorhersagen, tatsächliche Beobachtungen und Abweichungen getrennt notiert; mit Datum und echten Tester-Namen.
- [ ] Tatsächliche Rohlogs aller Rechner zusammengetragen: Server, Alice, Bob, Carol, Abgänge/Ersatz.
- [ ] `src/netz.py`, `src/server.py`, `src/client.py`, [`PROTOKOLL.md`](../../PROTOKOLL.md) und [`protocol.json`](../protocol/protocol.json) sind im Abgabeumfang.
- [ ] Historische Belege (`01_client_server_output.md` usw.) unverändert lassen; neue Logs separat einordnen.

Die spätere Projektphase M7 verlangt zusätzlich eine **vollständige Partie** über mindestens drei Rechner, zeitgestempelte Nachrichtendateien sowie den gegenseitigen Fremdtest mit einem nur anhand von `PROTOKOLL.md` geschriebenen Client. Der obige Lobby-Nachweis markiert M7 nicht als erledigt.

Ausgangsstand und lokale Ergebnisse sind in [03_local_output.md](03_local_output.md) dokumentiert; der weitere Projektstand steht im [README](../../README.md).
