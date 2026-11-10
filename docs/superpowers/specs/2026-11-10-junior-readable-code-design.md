# Junior-verständlicher Projektcode

Stand: 10.11.2026. Der Projektverantwortliche beauftragt eine Bereinigung des
gesamten Python-Projekts, damit er den Code als Junior nachvollziehen und
selbst erklären kann.

## Ziel und Grenzen

- Alle Produktionsmodule, Werkzeuge, Varianten und Tests auf Lesbarkeit
  prüfen. Dateien ohne konkretes Verständlichkeitsproblem bleiben bestehen.
- Lange Abläufe nach fachlichen Schritten strukturieren, unklare Namen und
  verdichtete Ausdrücke auflösen. Kommentare erklären Gründe und
  Zuständigkeiten, nicht jede offensichtliche Python-Zeile.
- Spielregeln, Drahtprotokoll, Reihenfolge der Serverantworten, GUI-Verhalten,
  Testauswahl und Nachweissemantik bleiben unverändert.
- Keine zusätzlichen Laufzeitabhängigkeiten. Python 3.12 oder neuer.
- Vorhandene lokale Änderungen und Rohbelege erhalten. Keine Commits,
  Pushes oder GitHub-Schreibvorgänge.

## Abnahme

Die betroffenen Tests und die strenge Gesamtsuite laufen grün, einschließlich
echter GUI-Prüfungen. Der Kernmodus startet weiterhin keine Fremdprozesse.
Ein unabhängiger Review sucht besonders nach Verhaltensänderungen durch
Extraktion, Testduplikaten und verlorenem Cleanup. Der Projektverantwortliche
erhält eine kurze Landkarte der wichtigsten Programmabläufe.
