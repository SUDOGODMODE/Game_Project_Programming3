# Anforderungsabgleich – Kursmeilenstein 6 „Testen und abschliessen“

Stand: 10.11.2026. Quelle ist der unveränderte
[Originalauftrag](../../../Dokumente/Auftrag_Meilenstein6.docx). Der
Projektverantwortliche hat bestätigt, die Lehrschritte auf sein vorhandenes
**Schiffe versenken** zu übertragen. Es entsteht kein zweites Tic-Tac-Toe-Spiel.
Die [M6-Spezifikation](../../specs/002-milestone-6/spec.md) und der
[Arbeitsplan](../../specs/002-milestone-6/plan.md) halten diese Entscheidung fest.

## Übertragung des Unterrichtsbeispiels

| Lehrvorlage | Dieses Projekt |
|---|---|
| 3×3-Brett, X/O, `move`, `rejected` | 10×10-Brett, Flotten, `shoot`, `error` mit Code |
| Spieler 1/2 und fortlaufender Zählerfehler | Slots A/B; freie Plätze wurden bereits vor M6 wiederverwendet |
| Unentschieden | Fachlich nicht vorgesehen; Sieg durch Versenken der Flotte |
| 12 Regeltests + 19 Netztests = 31 | 19 vorhandene Regeltests + 21 neue Prozess-Netztests = **40 direkte Kurstests**; die grössere Projektsuite enthält weitere Regressionstests |

## Anforderungen und tatsächliche Nachweise

| Schritt | Forderung für Schiffe versenken | Stand |
|---|---|---|
| 1 | Blinden Fleck der Regeltests an einem fehlenden Zustands-Push zeigen und den Fehler entfernen. | Isolierte [Mutation A](../evidence/06_mutations_2026-11-10/result.md): 3 Netztests rot, 19/19 Regeltests grün; Original danach 21/21 grün. |
| 2 | Server mit eigenem Testport starten; Standard bleibt 5000. | `PORT` ergänzt, CLI-Option bleibt vorrangig. Ein Porttest war vor der Änderung rot, danach beide grün. |
| 3 | Fensterloser Client mit Queue, Zeitlimit und Nachrichtenchronik. | `src/testclient.py`, verwendet `netz.send`/`read_messages`; keine GUI und kein Serverimport. |
| 4 | Pro Test frischer Serverprozess und Aufräumen bei jedem Ende. | `src/test_netz.py`, `setUp`/Cleanups und zufälliger freier Loopback-Port; Einzeltest und Wiederholung bestanden. |
| 5 | Beitritt, unaufgeforderter Start/Zustand, voller Server, fehlender Name. | In 21 neuen Netztests enthalten; [Rohausgabe](../evidence/06_final_2026-11-10/test_netz_green.txt). |
| 6 | Gültiger Schuss an beide und ganze Partie bis zum Ende. | Vollständige 33-Schuss-Partie mit `result`, beiden gefilterten `state` und `gameOver` an beide; kein Unentschieden nach `REGELN.md`. |
| 7 | Protokollablehnungen, Privatheit und unveränderter Zustand. | Alle elf `PROTOKOLL.md`-Fehlercodes in echten Prozess-/Socketfällen; expliziter Privatheits- und Zustandsvergleich. |
| 8 | Harter Abbruch, freier Platz, Server läuft weiter. | Zwei Netztests; Bob geht, Carla erhält B. Der in der Lehrvorlage beschriebene Zählerfehler war bereits vor M6 vermieden. |
| 9 | Rote Tests bei gezielten Serverfehlern belegen. | [Drei vorhergesagte und gemessene Mutationen](../evidence/06_mutations_2026-11-10/result.md): 3, 1 und 1 rote Tests; unveränderter Server danach 21/21 grün. |
| 10 | Vollständige Tests und startbare, cachefreie Abgabe mit Anleitung und Fehlerabsatz. | [Original-`discover`-Ausgabe](../evidence/06_final_2026-11-10/discover_green.txt): 190/190. [Strenger Gesamtbericht](../evidence/06_final_2026-11-10/full_strict.json): 190/190, 29/29 echte GUI-Tests, 0 Skips. Frisch gebautes `dist/Schiffe_versenken_Meilenstein_6_2026-11-10.zip`, SHA256- und Manifestprüfung (336/336), in frischem fremdem Zielordner entpackt: `--help`-Einstiege und volle Suite bestanden dort erneut mit 190/190 Tests, 29/29 GUI-Prüfungen, 0 Skips; Beleg unter `dist/Schiffe_versenken_Meilenstein_6_2026-11-10.verification/`. |

Die elf Fehlercodes sind `GAME_FULL`, `ALREADY_JOINED`, `MISSING_PLAYER`,
`NOT_JOINED`, `NOT_YOUR_TURN`, `CELL_OUT_OF_BOUNDS`, `DUPLICATE_SHOT`,
`WRONG_PHASE`, `INVALID_PLACEMENT`, `INVALID_JSON` und `UNKNOWN_TYPE`.
`PROTOKOLL.md` bleibt für ihre Bedeutung verbindlich.

## Noch offen

Persönliche Reflexion, eigene Prüfung des Berichtstextes, menschliches
Gegenlesen, echte Fremdrechner- und Fremdclientversuche sowie Livevorführung
werden durch die lokalen M6-Tests nicht ersetzt. Ein echter Windows-/Linux-
und Python-3.12-Lauf ist hier ebenfalls nicht behauptet. Es gab keine
Commits, Pushes oder GitHub-Änderungen.
