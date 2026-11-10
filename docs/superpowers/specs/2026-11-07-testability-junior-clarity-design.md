# Testbarkeit und Verständlichkeit des Spielprojekts

Stand: 07.11.2026. Der Projektverantwortliche möchte das bestehende Spiel in
einem lokalen Feature-Branch leichter prüfen und als Junior besser verstehen.
Dieser Entwurf konkretisiert die Umsetzung; die Spielregeln und das
Netzwerkprotokoll bleiben verbindlich.

## Ziel

Ein kurzer Testbefehl prüft den netz- und GUI-freien Spielkern. Die vollständige
Suite behält ihre strenge GUI-Abnahme. Testläufe hinterlassen keine unnötigen
Serverlogs im Projekt. Berechnungen für die GUI lassen sich ohne Tk prüfen,
während das Fenster weiterhin allein die Widgets zeichnet. Eine kurze
Lernanleitung erklärt, wo ein Junior beginnt und wann welcher Test sinnvoll ist.

## Änderungen

1. `tools/run_tests.py --core` lädt nur Brett-, Spielkern- und die eigenständig
   lauffähigen Kurstests aus `src/test_spiel.py`. Der JSON-Bericht kennzeichnet
   diese Auswahl als `core`. Die bestehenden Meilenstein- und Gesamtbefehle
   behalten ihre Bedeutung.
2. Ein übersprungener GUI-Subtest darf den zugehörigen Test im JSON-Bericht
   nicht als `passed` erscheinen lassen. Die strenge GUI-Abnahme lehnt ihn
   weiterhin ab.
3. Server-Integrationstests erzeugen Logs in temporären Verzeichnissen und
   schließen den Logwriter bei der Bereinigung. Produktionslogs und
   absichtlich abgelegte Kursnachweise bleiben unverändert.
4. Reine Funktionen berechnen die Symbolbelegung beider Bretter sowie eine
   gültige zufällige Flottenvorlage. Die Tk-Klasse überträgt die Ergebnisse in
   Widgets; für die Zufallsauswahl ist ein Generator injizierbar. Die GUI
   zeichnet ein Brett weiterhin ausschließlich nach einer `state`-Nachricht.
5. README und Testanleitung zeigen einen Lern- und Testweg: Kern, betroffener
   Teil, vollständige Suite, echte GUI-Partie. Sie erklären Port-/Tk-Bedarf,
   Skips und die Grenze eines lokalen Tests zum echten Zweirechnernachweis.

## Grenzen und Abnahme

- Python 3.12 oder neuer; keine zusätzlichen Laufzeitabhängigkeiten.
- Flotte, Zugfolge, Fehlercodes, gefilterte Sichten und Drahtprotokoll bleiben
  unverändert. Nach dem letzten Schuss gilt weiter `result`, beide `state`,
  beide `gameOver`. Ein Zielklick nach Spielende erreicht weiterhin den Server.
- Bestehende 155 Tests bestehen erneut mit `--require-gui`. Der neue Kernmodus
  läuft ohne Socketbindung, Tk-Fenster und fremde Prozesse.
- Neue reine Funktionen erhalten Verhaltenstests, die vor ihrer Implementierung
  fehlschlagen. Die GUI-Integration wird mit bestehenden echten Tk-Tests und
  einer vollständigen lokalen Demo geprüft.
- Keine Commits, Pushes oder Änderungen auf GitHub. Persönliche Reflexion,
  menschliches Gegenlesen und echter Zweirechnerlauf werden nicht als erledigt
  ausgegeben.

## Umsetzungsermessen

Die genauen Namen der reinen Helfer und ihre Rückgabetypen dürfen im Plan
festgelegt werden. Kleine Dokumentationskorrekturen, die den tatsächlichen
Teststand präzisieren, gehören dazu. Ein breiter Umbau des Servers oder der
Protokolldaten gehört nicht dazu.
