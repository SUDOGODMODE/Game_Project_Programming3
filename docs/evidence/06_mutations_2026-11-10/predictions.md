# Vorhersagen vor den M6-Fehlerläufen

Datum: 10.11.2026. Alle Änderungen werden nur in temporären Kopien von
`src/server.py` ausgeführt. Die Projektdatei bleibt unverändert.

| Isolierter Fehler | Vorhersage für 21 M6-Netztests | Grund |
|---|---:|---|
| A: Nach einem erfolgreichen `shoot` gehen keine `state`-Nachrichten heraus | 3 rote Tests | Der Einzelschuss, die ganze Partie und der Doppelbeschussfall warten auf den bestätigten Stand. Die 19 Regeltests sollten grün bleiben. |
| B: Eine Regelablehnung geht an alle verbundenen Spieler | 1 roter Test | Der Privatheitstest sieht eine fremde `error`-Nachricht bei Alice. |
| C: Ein fortlaufender Slotzähler ersetzt die Suche nach A/B | 1 roter Test | Nach Bobs Abbruch erhält Carla den ungültigen Slot C; der Ersatzbeitritt schlägt fehl. Dieser Fehler existiert im aktuellen Projekt **nicht**. |

Erst nach dieser Vorhersage werden die Kopien gebaut und die tatsächlichen
Rohausgaben aufgezeichnet. Der Originalauftrag verwendet andere
Tic-Tac-Toe-Namen; hier gelten `shoot`, `state`, `error` und A/B aus
`PROTOKOLL.md`.
