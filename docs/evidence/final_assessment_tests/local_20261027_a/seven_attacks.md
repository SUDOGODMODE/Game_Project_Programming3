# Sieben Pflichtangriffe — frischer lokaler Lauf

Durchfuehrung: automatisierter Codex-Testlauf (Rolle 3). Reale TCP-Sockets, alle Adressen Loopback; kein Fremdrechner-/Personennachweis.

| Fall | Datum/Zeit | Beobachtung | Ergebnis |
|---|---|---|---|
| 1: ungueltiges JSON | 2026-10-27T17:50:40.743187+01:00 | INVALID_JSON; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 2: falsch typisiertes Feld | 2026-10-27T17:50:40.798776+01:00 | CELL_OUT_OF_BOUNDS; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 3: Feld ausserhalb | 2026-10-27T17:50:40.854912+01:00 | CELL_OUT_OF_BOUNDS; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 4: Pflichtfeld fehlt | 2026-10-27T17:50:40.911743+01:00 | CELL_OUT_OF_BOUNDS; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 5: unbekannter Typ | 2026-10-27T17:50:40.966401+01:00 | UNKNOWN_TYPE; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 6: ausser der Reihe | 2026-10-27T17:50:41.019952+01:00 | NOT_YOUR_TURN; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 7: Verbindung mitten im Zug trennen | 2026-10-27T17:50:41.023963+01:00 | Unvollstaendiges shoot-JSON, TCP RST; Gegner informiert, leerer Reset, Ersatzbeitritt und naechster gueltiger Schuss erfolgreich | PASS |
