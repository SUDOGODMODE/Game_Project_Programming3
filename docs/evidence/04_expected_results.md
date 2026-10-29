# Erwartungen vor dem Prüflauf — Kursmeilenstein 4

Erstellt am 27.10.2026 vor dem neuen Integrationslauf.
Die historischen Nachweise zu M3 bleiben unverändert. Der folgende Versuch
läuft lokal; er ersetzt keinen Schulnetzversuch mit zwei fremden Clients.

1. Alice tritt als A bei: `welcome`, `waiting`, vollständiger leerer Zustand.
   Bob tritt als B bei: `welcome` für Bob, `gameStart` und `placing`-Zustand
   für beide. Kein Client muss dazu `getState` senden.
2. Die Demonstration verwendet absichtlich verschiedene Flotten:
   Alice waagrecht ab A1/A2/A3/A4/A5, Bob waagrecht ab A6/A7/A8/A9/A10.
   Nach jeder Platzierung bekommen beide ihre eigene vollständige Sicht;
   die unbeschossenen Bob-Felder fehlen in Alices Zustandsnachrichten.
3. Alices Klick auf B6 schickt `shoot/B6`. Bis zur Serverantwort bleibt das
   Raster unverändert. Danach zeigt Alice B6 als Treffer im Zielraster;
   Bob zeigt B6 als Treffer in seiner eigenen Flotte. Beide zeigen B am Zug.
4. Alices weiterer Klick auf J10 ausser der Reihe wird nur bei Alice mit
   `NOT_YOUR_TURN` angezeigt. Kein Raster und kein Spielzustand ändert sich.
5. Bob schiesst auf J10: beide zeigen Wasser an der entsprechenden Stelle
   und A am Zug. Alices erneuter Schuss auf B6 ergibt nur bei Alice
   `DUPLICATE_SHOT`; kein Zustand und keine Zugfolge ändert sich.
6. Falsche Koordinaten werden serverseitig begründet abgelehnt. Die GUI
   bleibt während einer ausbleibenden Netzwerkantwort bedienbar.
7. Eine vollständige geskriptete Partie endet nach 33 gültigen Schüssen
   mit A als Sieger; beide gefilterten Zustände enthalten `finished`,
   `turn: null`, `winner: A`. Weitere Schüsse werden abgelehnt.
8. Bob schliesst sein Fenster. Der Server erzeugt keinen Thread-Traceback;
   Alice erhält `opponentLeft` und anschliessend den leeren waiting-Zustand.
   Ein Ersatzspieler beginnt eine neue Platzierungsphase.
9. Netzwerkthreads greifen nicht auf Tk-Widgets zu. Die GUI verarbeitet
   Nachrichten in der Queue im Hauptthread und zeichnet immer beide Raster
   vollständig aus einem bestätigten Zustand.
10. Der Servermitschnitt enthält Verbindungsadressen, Richtung,
    Nachrichtentypen und Fehlercodes, aber keine Flotten-/Zustandspayloads.
    Ein zusätzlicher isolierter Testmitschnitt prüft die tatsächlichen
    personalisierten Zustandsnachrichten und wird ausdrücklich als Testdaten
    aus Sicht beider lokaler Testclients bezeichnet.

Nach dem Strukturumzug müssen dieselben Tests aus `tests/meilenstein_XX/`
ausführbar bleiben. Die gemeinsame Anleitung wird den vollständigen Lauf
und die Ausführung eines einzelnen Meilensteins beschreiben.
