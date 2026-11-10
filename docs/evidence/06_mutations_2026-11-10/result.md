# M6: Isolierte Fehlerläufe

Die [Vorhersage](predictions.md) wurde vor den drei Änderungen geschrieben.
Für jeden Fehler lag eine separate Kopie von `src/server.py` unter
`/private/tmp/m6_server_mutations_nyp7m99n/`. Die Projektdatei wurde für
diese Läufe nicht verändert. `SERVER=<Kopie>` wählte ausschliesslich den
Unterprozess der Netzsuite; die Tests liefen weiter über echte Sockets.

| Fehler | Vorhergesagt | Tatsächlich rot | Rohausgabe | Exakter Unterschied |
|---|---:|---:|---|---|
| A: kein Zustand nach Schuss | 3 | 3/21 | [A](a_no_state_red.txt) | [Diff](a_no_state.diff) |
| B: Regelablehnung an beide | 1 | 1/21 | [B](b_public_error_red.txt) | [Diff](b_public_error.diff) |
| C: fortlaufender Slotzähler | 1 | 1/21 | [C](c_counter_red.txt) | [Diff](c_counter.diff) |

Bei A scheiterten genau Einzelschuss, vollständige Partie und
Doppelbeschussvorbereitung. Dieselbe Serveränderung blieb für die
[19 reinen Regeltests](core_stays_green.txt) unsichtbar: **19/19 grün**.
Bei B meldete der Privatheitstest die fremde Fehlernachricht. Bei C scheiterte
der Ersatzbeitritt nach Bobs hartem Abbruch. Die [originale Netzsuite nach
den Mutationen](original_green_after_mutations.txt) bestand wieder mit
**21/21**.

**Einordnung zu Schritt 8:** Die aktuelle Slotvergabe sucht bereits A oder B.
Der Unterrichtsfehler mit einem fortlaufenden Zähler war im Projekt nicht
vorhanden. Fehler C ist daher eine gekennzeichnete Simulation zur Prüfung
des Regressionstests, kein neu entdeckter Produktionsfehler. Die
`KeyError`-Folge ist nur in der isolierten Kopie zu sehen.
