# Ergänzte Prüfung bis Meilenstein 3

13.10.2026, macOS, vorhandene `.venv` mit Python 3.14.8. Grundlage: [vorher festgehaltene Erwartungen](03_expected_results.md).

## Ergebnisse

**57 Prüfungen bestanden:** 9 Bretttests, 12 Spielkern-Tests, 26 Netzwerk-/CLI-Tests, 5 Transporttests und 5 Tests für Echo und lokale Partie. Keine fehlgeschlagenen oder übersprungenen Tests. [Vollständige Testausgabe](03_followup/03_test_output.txt).

Der Spielserver wurde erneut als eigener Prozess gestartet, lokal auf Port 61885. Alice erhielt `welcome` und `waiting`; nach Bobs Beitritt kam `gameStart` bei beiden an. Carol erhielt `GAME_FULL`. Nach Bobs q bekam Alice einmal `opponentLeft`; Dave konnte Slot B übernehmen. Sein harter Prozessabbruch löste ebenfalls genau eine Abgangsmeldung aus.

| Nachweis | Datei |
|---|---|
| Server | [03_server_output.txt](03_followup/03_server_output.txt) |
| Alice, beide Spielstarts und beide Abgänge | [03_alice_output.txt](03_followup/03_alice_output.txt) |
| Bob, reguläres Ende mit q | [03_bob_output.txt](03_followup/03_bob_output.txt) |
| Carol, dritter Beitritt | [03_carol_output.txt](03_followup/03_carol_output.txt) |
| Dave, Ersatzbeitritt und hartes Ende | [03_dave_output.txt](03_followup/03_dave_output.txt) |
| Fehlerhafte Handshake-Nachrichten | [03_attack_output.txt](03_followup/03_attack_output.txt) |
| Echo-Server, zwei aufeinanderfolgende Clients | [03_echo_server_output.txt](03_followup/03_echo_server_output.txt) |
| Echo-Antworten HALLO NETZ und ZWEITER CLIENT | [03_echo_client_output.txt](03_followup/03_echo_client_output.txt) |
| Ganze geskriptete Partie ohne Netzwerk, 33 gültige Schüsse | [03_local_game_output.txt](03_followup/03_local_game_output.txt) |

Die Echo-Tests prüfen zusätzlich eine Antwort mit 7500 Bytes, die über mehrere Lesevorgänge zusammengesetzt wird. Die lokale Partie wird mit fehlerhaften Eingaben, ungültiger Flotte, Doppelbeschuss, q und EOF geprüft. Der Terminaltest stellt sicher, dass nach dem letzten Treffer direkt der Gewinner erscheint.

Die fünf Transporttests prüfen gemeinsame und zerstückelte JSON-Zeilen, eine Aufteilung mitten in einem UTF-8-Zeichen, maskierte Zeilenumbrüche in Zeichenketten, ungültige JSON-Werte, Leerzeilen und EOF. `netz.py` wurde dafür nicht geändert.

## Grenzen und weitere Prüfung

Alle Verbindungen liefen auf `127.0.0.1`. Die lokale Partie wurde durch vorbereitete Eingaben gespielt. Eine vollständige Partie durch zwei Personen und die fremden Rechner im Schulnetz sind weiterhin offen.

Unabhängiger Abgleich von Regeln, Programmen und Tests: keine wesentlichen Befunde. Entfernte Zusatzsperren im Server waren durch die gemeinsame Spielsperre bereits abgedeckt; Reihenfolge, Abbruch und gleichzeitige Zulassung bestehen weiterhin. Syntaxprüfung und `git diff --check` sind sauber. Ausgangsaufgaben, `netz.py` und historische Ausgaben bleiben unverändert; HEAD ist weiterhin `a23f73e`.

Alle Änderungen liegen lokal und uncommittet vor.
