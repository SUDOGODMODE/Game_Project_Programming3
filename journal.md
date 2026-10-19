# Journal

## 13.10.2026 — Kursmeilenstein 3, lokale Überarbeitung

**Umgesetzt:** Dauerhafter Lobbyclient, Servermeldungen `waiting`, `gameStart` und `opponentLeft`, Freigabe des Slots und Rundenreset bei Abgang. Der netzwerkfreie Kern `board.BattleshipGame` kapselt Spielzustand und Regeln; der Server verwaltet Verbindungen und die gemeinsame Sperre. Fachliche Durchsicht und Gegenlesen stehen aus.

**Dokumentation:** README und Nachrichtenkatalog Version 0.4 aktualisiert, `PROTOKOLL.md` mit Pflichtfeldern und Ablaufbeispiel ergänzt. Kursaufgabe und drei Kontextquellen unverändert kopiert. Unterschiedliche Nummerierung von Kursmeilenstein und Projektphasen erläutert, Schulnetz-Check vorbereitet und ältere Nachweise unverändert belassen.

**Prüfungen:** 47 Prüfungen bestanden (9 Brett-, 12 Spielkern-, 26 TCP-/CLI-Tests); die vier Lobbyfälle, q, harter Abbruch und Ersatzbeitritt sind aufgezeichnet. Ergebnisse, Angriffstabelle und Rohlogs stehen in `docs/evidence/03_local_output.md`. Lokale Umgebung: Python 3.15.0; Kursvorgabe: 3.12 oder neuer. Eine eigene Ausführung unter 3.12 ist noch nicht belegt.

**Offen:** Lesepartnerschaft mit Namen, fachliche Durchsicht, Regelblatt/Freigabe, manuelle Tischpartie und Schulnetzversuch mit zwei fremden Client-Rechnern. Für spätere Projektphasen: Zustands-Pushes nach Spielaktionen, GUI, zeitgestempelte Nachrichtendateien, Fremdclient-Test in beide Richtungen und Bericht/Vorführung. Reflexion und KI-Erklärung sind im Bericht noch zu ergänzen.

## 13.10.2026 — Abgleich beider Meilenstein-Nummerierungen

- Ursprünglichen Katalog und ausgefüllten Spielvorschlag gelesen; Spielwahl Schiffe versenken bestätigt. Kein vorhandener Fremdrechner- oder Gegenlese-Nachweis gefunden.
- Echo-Programme für M0 und eine Partie ohne Netz für M2 ergänzt. Regelblatt mit Flotte, ungültigen Aktionen, Abbruchregel und Oberflächenskizze angelegt. Der sofortige Reset ersetzt die ältere Idee einer Wartefrist mit Aufgabe.
- Transporttests für gemeinsame und zerstückelte Nachrichten ergänzt. Erwartungen vor dem erneuten Prüflauf festgehalten.
- Wiederholte Kommentare und Absätze gekürzt, Dokumentationssprache vereinheitlicht, ungenutzten Verbindungsstatus und überflüssige Zusatzsperren entfernt.
- In der Projektumgebung Python 3.14.8 bestehen 57 Prüfungen. Echo, Lobbyfälle und die vollständige geskriptete lokale Partie sind separat aufgezeichnet.
- Offen bis M3: Lesepartnerschaft und Gegenlesen, Zweipersonenpartie an einer Tastatur, Echo/Handschlag mit Rollenwechsel sowie Lobbyversuch mit zwei fremden Clients.

## 13.10.2026 — Platzhalter in der Dokumentation

Beispieladressen und offene Einträge auf `<beispiel_art>` vereinheitlicht, unter anderem `<server_ip>`, `<tcp_port>`, `<lesepartner_name>` und `<beobachtung>`. Platzhalter in Shell-Befehlen sind in Anführungszeichen gesetzt. Die Protokollvorlage verwendet `<feld>`; tatsächliche JSON-Beispiele und Testausgaben bleiben erhalten.

## 13.10.2026 — Paket für Kursmeilenstein 3

Meilenstein_3.zip auf dem Desktop gespeichert. Enthalten sind die drei verlangten Programme, board.py als Serverabhängigkeit, das aktuelle Protokoll, Regelblatt, Aufgabenstellung, lokale Ausgaben der vier Fälle und die Schulnetz-Checkliste. 16 Dateien; Archivintegrität, unveränderte Quellen und Ausgaben, Startparameter und Dokumentlinks geprüft. Der Nachweis mit zwei fremden Client-Rechnern bleibt offen und ist im Paket gekennzeichnet.
