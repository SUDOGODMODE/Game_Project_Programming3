# SVG-Oberfläche und Sprengung — 29.10.2026

Benutzerauftrag: maritime Oberfläche in Meerblau, fünf SVG-Schiffe und eine
kleine Sprengung beim Besitzer, sobald alle Felder seines Schiffes getroffen
sind. Keine zusätzlichen Python-Pakete.

- `graphics-final-tests.json` / `.txt`: tatsächlicher abschliessender Lauf von
  `.venv/bin/python3 tools/run_tests.py --require-gui` unter macOS mit Python
  3.14.10 / Tk 9.1. **114 bestanden, 28 GUI-Prüfungen ausgeführt, keine Fehler
  oder Skips.** Der Bericht wurde zunächst unter `/private/tmp/` geschrieben
  und anschliessend unverändert hierher kopiert.
- `local_game/`: tatsächliche vollständige lokale TCP-Partie mit zwei echten
  Fenstern, 33 Schüssen, privaten Ablehnungen, Sieg/Niederlage, Reset und
  Ersatzbeitritt; Ergebnis PASS. Dieser Lauf wurde vor der abschliessenden
  Korrektur des Effektschalters ausgeführt; diese ist durch den neueren
  Gesamtlauf und dessen Integrationstest gedeckt.
- `graphics-preview.png`: echter Bildschirmabzug der neuen Oberfläche mit
  bewusst gesetzten Vorschau-Testdaten, kein TCP-Partienachweis. Horizontale
  und vertikale SVG-Schiffe sowie Treffer wurden visuell kontrolliert. Auch
  ein Bildschirmabzug während einer Sprengung wurde lokal betrachtet; wegen
  einer überlagernden Systemmeldung wird dieses Bild hier nicht ausgeliefert.

Der unveränderte ImageGen-PNG-Kopf bleibt erhalten. Die fünf neuen SVGs
wurden als Vektoren mit Code erstellt. Ihre Grundformen werden durch
`src/ship_art.py` in Tk-Canvas-Elemente übersetzt; dies ist kein allgemeiner
SVG-Renderer. `src/sea_cell.py` zeigt die passenden Ausschnitte ohne Rasterung.

Die Sprengung dauert etwa 1,15 Sekunden und verändert ausschliesslich die
Darstellung. Die Tests prüfen den letzten bestätigten eigenen Treffer,
keinen Effekt für gegnerische Verluste oder direkte Antwortnachrichten,
keine Wiederholung beim Zustandsabruf, den Effektschalter und Abbruch von
Callbacks bei Reset, Verbindungsende und Fensterschliessen. Ein unabhängiger
Agent prüfte den Code und ergänzte echte GUI-Integrationstests. Dieses
Agentenreview ersetzt keine menschliche Abnahme oder Fremdrechnerprüfung.

Kein neuer Windows-/Linux-/Fremdrechnernachweis; frühere Abgabearchive und
Rohbelege wurden nicht verändert. Keine Git-Schreiboperationen.
