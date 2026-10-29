# Sieben Pflichtangriffe — frischer lokaler Lauf

Durchfuehrung: automatisierter Codex-Testlauf (Rolle 3). Reale TCP-Sockets, alle Adressen Loopback; kein Fremdrechner-/Personennachweis.

| Fall | Datum/Zeit | Beobachtung | Ergebnis |
|---|---|---|---|
| 1: ungueltiges JSON | 2026-10-27T18:00:33.115025+01:00 | INVALID_JSON; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 2: falsch typisiertes Feld | 2026-10-27T18:00:33.166728+01:00 | CELL_OUT_OF_BOUNDS; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 3: Feld ausserhalb | 2026-10-27T18:00:33.219022+01:00 | CELL_OUT_OF_BOUNDS; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 4: Pflichtfeld fehlt | 2026-10-27T18:00:33.272249+01:00 | CELL_OUT_OF_BOUNDS; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 5: unbekannter Typ | 2026-10-27T18:00:33.329358+01:00 | UNKNOWN_TYPE; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 6: ausser der Reihe | 2026-10-27T18:00:33.383123+01:00 | NOT_YOUR_TURN; nur Absender; beide Sichten und Zugrecht unveraendert; weitere Zustandsanfragen erfolgreich | PASS |
| 7: Verbindung mitten im Zug trennen | 2026-10-27T18:00:33.386834+01:00 | Unvollstaendiges shoot-JSON, TCP RST; Gegner informiert, leerer Reset, Ersatzbeitritt und naechster gueltiger Schuss erfolgreich | PASS |
