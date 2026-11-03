# Kursmeilenstein 5: Die Regeln — Entwurf

Quelle: `../../../Dokumente/auftrag_Meilenstein5` (Original bleibt unverändert).
Der Projektverantwortliche hat am 03.11.2026 bestätigt, die Lehrschritte
1–7 auf das bestehende **Schiffe versenken** zu übertragen. Ein separates
Tic-Tac-Toe-Spiel ist nicht Teil des Auftrags. Der echte Zweirechnerlauf
bleibt auf seinen Wunsch verschoben und wird nicht als durchgeführt bezeichnet.

## Ziel und Grenzen

Der vorhandene netzfreie Spielkern wird als `src/spiel.py` zur eindeutigen
Regelquelle. `src/board.py` bleibt als Kompatibilitätseinstieg für ältere
Tests erhalten und enthält keine zweite Regelimplementierung. Die Regeln,
Flotte, Zugfolge und das unmögliche Unentschieden bleiben wie in `REGELN.md`.
Der Server verwaltet Verbindungen, Identität und Sperre. Seine Endfolge wird
für den neuen Auftrag zu `result` an den Schützen, dann `state` an beide,
dann `gameOver` an beide. Das Protokoll wird entsprechend aktualisiert.

Die geforderten Kerntests stehen in `src/test_spiel.py`, sodass im Ordner
`src` der Originalbefehl `python3 -m unittest -v test_spiel.py` funktioniert.
Der gemeinsame Teststarter findet sie zusätzlich unter Meilenstein 05.
Die Tests decken jede Regelablehnung, Platzierungsgrenzen, Zugwechsel,
Schiffversenkung, Sieg, Nach-Ende-Ablehnung, Zustandskopie und geheime
Gegnerflotte ab. Zwei absichtliche, danach rückgängig gemachte Fehler
belegen, dass passende Tests rot werden.

Ein lokaler Lauf mit zwei echten Tk-Fenstern belegt die vorangehende
Funktionsfähigkeit und die fertige Partie; ein Endbild beider Fenster wird
zusätzlich erstellt, falls die Umgebung es tatsächlich erlaubt. Der
Zweirechner-Terminalbeleg bleibt offen. Vorhersagen, tatsächliche Ausgaben,
Grenzen und offene persönliche Aufgaben werden sachlich dokumentiert.

## Abnahme

- `src/spiel.py` importiert weder `socket`, `threading` noch `tkinter`; ein
  Import zieht diese Module auch nicht nach.
- Der Originalbefehl für `test_spiel.py` und die komplette Projektsuite
  bestehen; der neue Nachrichtenreihenfolge-Test ist vor der Änderung rot.
- Beide Mutationen erzeugen die vorher prognostizierten roten Kerntests;
  danach ist der unveränderte Kern wieder grün.
- Ein echter lokaler Tk/TCP-Gesamtlauf endet mit Sieg/Niederlage, sichtbarer
  Ablehnung nach Spielende und weiterhin laufendem Server.
- Protokoll, README, Status und Journal unterscheiden lokale Belege vom
  noch ausstehenden Zweirechnerbeleg.
