# Erwartungen vor der erneuten lokalen Prüfung

Datum: 13.10.2026. Diese Erwartungen gelten für den folgenden Prüflauf der ergänzten Programme. Die erste lokale Prüfung ist in `03_local_output.md` dokumentiert.

| Versuch | Erwartete Ausgabe und Wirkung |
|---|---|
| Echo | Client sendet `hallo netz`, erhält `HALLO NETZ`; der Server nimmt danach einen weiteren Client an. |
| Alice verbindet sich | Alice erhält `welcome` mit Slot A, danach `waiting`. Der Client bleibt geöffnet. |
| Bob verbindet sich | Bob erhält zuerst `welcome` mit Slot B. Danach erscheint derselbe `gameStart` bei Bob und bei Alice, obwohl Alice nichts Neues sendet. |
| Carol verbindet sich | Nur Carol erhält `error/GAME_FULL`. Alice und Bob bleiben verbunden. |
| Bob beendet mit q | Alice erhält einmal `opponentLeft` für Bob. Der Server läuft weiter. |
| Ersatzspieler | Der freie Slot B wird wieder vergeben; beide Spieler erhalten einen neuen `gameStart`. |
| Ersatzspieler wird hart beendet | Alice erhält einmal `opponentLeft`; ein weiterer Beitritt bleibt möglich. |
| Angriffstest | Unbekannter oder fehlender Typ: `UNKNOWN_TYPE`; fehlender Name: `MISSING_PLAYER`; Doppelbeitritt: `ALREADY_JOINED`; kaputtes JSON und JSON-Liste: `INVALID_JSON`. Eine Lobbymeldung verschiebt die Antwortzuordnung nicht. |
| Transport | Zwei gemeinsam gesendete JSON-Zeilen werden getrennt gelesen. Eine zerstückelte Nachricht, auch mitten in einem UTF-8-Zeichen, wird erst nach vollständigem Zeilenende geliefert. |
| Lokale Partie ohne Netz | Beide Spieler können ihre Flotte setzen. Ungültige Aktionen werden erklärt und ändern den Spielstand nicht. Die vollständige vorbereitete Zugfolge endet mit Gewinner A. q/EOF beendet ohne erfundenen Gewinner. |

Der Server des bisherigen Repositories verwendet schon Threads. Das blockierende Verhalten des alten sequentiellen Kursbeispiels ist daher kein erwartetes Verhalten dieses Stands.
