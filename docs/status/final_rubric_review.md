# Unabhängiger Bewertungsabgleich des Endstands

27.10.2026. Rolle 1 prüfte den eingefrorenen Stand nach der Umsetzung erneut
gegen die zuerst gelesenen Originalquellen, die
[Anforderungs-IDs](04_rubric_requirements.md) und die
[freigegebene Spezifikation](../superpowers/specs/2026-10-27-final-assessment-design.md).
Dies ist ein lesender Deckungs- und Qualitätsreview. Dafür wurden keine
Produktions-/Testdateien verändert und keine Tests oder Tk-Instanzen erneut
gestartet. Die folgenden tatsächlichen Ausführungsbelege stammen von der
unabhängigen Testrolle 3.

**Urteil:** Der lokal erfüllbare vereinbarte Verbesserungsumfang ist
quellengerecht umgesetzt und durch frische lokale Nachweise gedeckt.
Es wurden keine zusätzlich zu behebenden konkreten Codefehler oder
Spezifikationsabweichungen gefunden. Die vollständige Kurs-Endabgabe bleibt
wegen der ausdrücklich offenen Personen-, Fremdrechner- und Autorenleistungen
unvollständig. Dieser Review vergibt keine Note und keine Punkte.

## Gelesene aktuelle Belege

- [Strenger Gesamtlauf nach letzter Reporter-Korrektur](../evidence/final_assessment_tests/full_v3.json):
  101 ausgeführte und bestandene Tests, 16 gefundene/ausgeführte GUI-Tests,
  keine Fehler und keine Skips; macOS, Python 3.14.10, Tk 9.1.
- [Sieben Pflichtangriffe](../evidence/final_assessment_tests/local_20261027_a/seven_attacks.md):
  alle sieben mit tatsächlicher Zeit, Beobachtung und Ausführung durch
  automatisierten Codex-Lauf bezeichnet. Ungültige Anfragen bleiben privat
  und verändern keine Sicht; TCP-RST während eines unvollständigen Zuges
  führt zu Benachrichtigung, Reset und verwendbarem Ersatzbeitritt.
- [Ganze Konsolenpartie](../evidence/final_assessment_tests/local_20261027_a/console_result.json):
  eigener Server und zwei tatsächliche `play.py`-Prozesse, 33 gültige
  Schüsse, Sieg/Niederlage und sauberes Ende. Kein umbenannter GUI-Nachweis.
- [Echte GUI-/TCP-Partie](../evidence/final_assessment_tests/gui_20261027_a/result.json):
  PASS, 33 Schüsse, individuelle Sichten, beide privaten Ablehnungen,
  Fensterkreuz, Reset und Ersatz; Fenstergrösse 800×716.
- [Entpackter Abgabekandidat](../evidence/final_assessment_tests/candidate_verification/result.json):
  PASS, 162 Manifestdateien und sieben Originalquellenlinks geprüft;
  neue virtuelle Umgebung im entpackten Projekt, wiederum 101/101 Tests
  einschliesslich 16 GUI-Tests sowie sieben Angriffe und vollständige
  Konsolenpartie. SHA256 des geprüften Kandidaten:
  `3ed836f3fadf3f4b686ad7c905498fa3f1a606183a314b16ca16fc325ed9a08f`.

Der Kandidat ist ein bestimmtes früher gebautes Archiv. Diese Prüfung
bescheinigt keinem erst danach erstellten endgültigen ZIP rückwirkend einen
erfolgreichen Entpacktest. Dessen externer Nachweis muss sich auf dessen
eigenen Hash beziehen. Die finalen Berichtsdateien können später in diesem
endgültigen Paket enthalten sein; ein Archiv muss seinen eigenen zukünftigen
Testbericht nicht schon enthalten.

## Sechs aktuelle M4-Kriterien

| ID | Endstand / Urteil |
|---|---|
| M4-B01 — Wer entscheidet | Erfüllt im geprüften lokalen Verhalten: `shoot` reiht nur eine Anfrage ein; serverseitiger Kern prüft Phase, Zugrecht, Feld und Doppelbeschuss. Kein spekulativer Rasterwechsel und kein Vertrauen in behauptete Spieleridentität. |
| M4-B02 — Eine Anzeige, eine Wahrheit | Erfüllt: `draw_state` bleibt die einzige vollständige Zeichenfunktion für beide Raster. Bilddekoration ergänzt keine zweite Stelle für Spielzustände. Reset und Lobby-Ereignisse erhalten die bestätigte Wahrheit. |
| M4-B03 — Die Fäden | Erfüllt: Netzwerkworker erhalten nur Sockets, Queues und Stop-Ereignis. `after`, Zeichenfunktion, Tk-Variablen und `PhotoImage` bleiben im Hauptthread; echte Tests prüfen Last, Bildpixel und Freigabe. |
| M4-B04 — Wer was erfährt | Lokal erfüllt: private Fehler, vollständige individuell gefilterte Zustände und keine Gegnerflotte in einer Clientansicht. Neue gemeinsame Logs enthalten nur erlaubte Metadaten; tatsächliche Clientpayloads werden separat geprüft. |
| M4-B05 — Nachweis | **Externer Teil offen:** lokale GUI-/TCP-Partie, Bildpaar und Ablehnungen sind belegt. Server mit zwei anderen Clientrechnern, zwei fremde IPs und gemeinsames Bild aus dieser Partie fehlen weiterhin ausdrücklich. |
| M4-B06 — Protokoll | Erfüllt im lokalen Code-/Vertragsabgleich: Katalog 0.5 mit `shoot`/`state`, Richtung/Feldern/Anlass, Leerfeldbedeutung und vollständiger Partie. Neue Dateilogbeschreibung ändert den Drahtvertrag nicht. Menschliches Gegenlesen bleibt offen. |

M4-A01–A07 sind lokal weiterhin gedeckt: 10×10-Koordinaten, fünf
spielgerechte Fälle, harter Abbruch, erhaltene Konsole, gemeinsame Sperre,
notwendige Quelldateien und vorher dokumentierte Erwartungen. Für
Schiffe versenken sind verschiedene eigene Flotten die verlangte private
Sicht und kein Synchronisationsfehler.

## Gesamtprojekt M0–M8 und originales Bewertungsraster

Die Originalgewichte 20/20/20/15/15/10 werden ausschliesslich zur Zuordnung
genannt. Sie sind keine hier zugesprochenen Punkte.

| Bereich / IDs | Technischer Endstand und noch erforderliche Leistung |
|---|---|
| Architektur, 20 — G01 / M2-01 | Kern, Vertrag, Transport/Server und Anzeige bleiben getrennt; keine neue Regelvariante und kein unbegründeter Kernumbau. Sichere Sichtkopien und der benannte schwierige Fall sind getestet. Technische Begründungen sind im Berichtsmaterial enthalten; Autor muss sie selbst vertreten. |
| Protokoll, 20 — G02 / M3-01 | Vollständige Beispiele werden durch den Servereingang nachgespielt, TCP-Rahmung und individuelle Sichten geprüft. Menschliche Lesung sowie gegenseitiger nur aus dem Vertrag entwickelter Fremdclienttest bleiben offen. |
| Nebenläufigkeit, 20 — G03 / M4-01 / M6-01 | Spielsperre schützt Prüfen/Ändern/Senden und Reset. Der Preis des Sendens unter der Sperre wird sachlich erklärt. Queues und Tk-Lebensdauer sind tatsächlich geprüft. Keine zusätzliche Server-Sendequeue ist für diesen kleinen Kursserver erforderlich. |
| Robustheit, 15 — G04 / M5-01 | Alle sieben Pflichtfälle sind frisch über echte TCP-Verbindungen geprüft und datiert tabellarisch dokumentiert. Danach sind Anfragen und Ersatzspiel weiter möglich. Der ausführende Akteur wird richtig als Codex-Testrolle genannt. |
| Spiel/Oberfläche, 15 — G05 / M6-02 | Bestehende Regeln und Bedienung erhalten. Eigenes transparentes 256×256-PNG vorhanden und als 64×64-Dekoration sichtbar, Herkunft/Original/Skalierung dokumentiert. Die reale Zweipersonenpartie an einer Tastatur bleibt offen. |
| Bericht/Vorführung, 10 — G06 / M8-02–03 | Technische Materialsammlung erklärt Architektur, Protokoll, Sperre, Angriffe, Bild und Logging; Vorführleitfaden vorhanden. Sie ersetzt keine persönlich geprüfte Endfassung, Reflexion, Fremdtestergebnisse oder tatsächliche Livevorführung. |
| M0-01–02 | Repository, Umgebung, Echo und Struktur vorhanden. Fremdrechner-Echo mit Rollenwechsel und feste echte Lesepartnerschaft bleiben offen. Keine neuen Commits werden aus der alten Aufgabenformulierung abgeleitet. |
| M1-01 | Später bestätigte Schiffe-versenken-Wahl, Regeln und Skizze bleiben massgeblich. Originalformular wird nicht umgeschrieben; tatsächliches Gegenlesen fehlt weiter. Die spätere dokumentierte Resetregel erfordert keinen 30-Sekunden-Reconnect. |
| M2-02 | Lokale Partie technisch vorhanden und geskriptet belegt; zwei echte Personen wurden dadurch nicht nachgewiesen. |
| M4-01 | Zusätzlich jetzt komplette Partie über zwei tatsächliche Konsolenclientprozesse belegt. |
| M7-01–03 | Konfigurierbarer Server, Wartezimmer und dokumentierter Abbruch vorhanden. M7-02 ist neu geschlossen: jede empfangene und erfolgreich gesendete Nachricht wird dauerhaft mit UTC-ISO-Zeit und erlaubten Metadaten protokolliert. Dreirechnerpartie und gegenseitiger menschlicher Fremdtest bleiben offen. |
| M8-01 | Builder liefert notwendige Programme/Assets/Tests/Anleitungen, Quellen und vorhandene Belege mit Manifest und offenem Abgabestatus. Kandidat erfolgreich unabhängig entpackt/geprüft. Abschliessendes Archiv benötigt seinen eigenen externen Prüfbeleg. |
| M8-04 | Neue Arbeit, aktuelle Zahlen und noch offene Pflichten müssen im Journal/Übergabestand nach der Endprüfung sachlich fortgeführt werden. Frühere Rohlogs bleiben historische Originalbelege. |

## Prüfung der neuen Hilfsmittel und Qualität

`tools/run_tests.py` unterscheidet ausgeführte Testmethoden von Klassen-
und Subtestereignissen. Strenge Abnahme scheitert auch bei fehlender
GUI-Auswahl, Klassen-/Test-/Subtest-Skips und erwarteten GUI-Fehlern.
Die letzte korrigierte Reporterfassung ist im grünen `full_v3` enthalten.
Vorhandene Berichtsdateien werden vor Testbeginn abgelehnt. Neue
Meilensteingruppen 06/07/08 sind auswählbar und dokumentiert.

`EventLog` erzeugt Dateien exklusiv, serialisiert parallele Schreiber,
flusht vollständige JSON-Zeilen und schützt Schliessen gegen weitere
Schreibzugriffe. Bekannte Typen/Fehlercodes verhindern, dass freie
Clienttexte oder Flotten in den gemeinsamen Nachweis geraten.
Die Chronik ist bewusst kein rekonstruierbarer Speicher beider Flotten.
Die eigene Spielsperre und die Logschreibsperre erzeugen keine umgekehrte
Sperrenreihenfolge.

Das ausgelieferte Bild wurde auch visuell als Schiffsillustration
betrachtet. Sein Dateipfad hängt nicht vom Arbeitsverzeichnis ab. Die
tatsächlichen Tk-Pixel, Transparenz, Referenzhaltung und Freigabe sind in
der unabhängigen Suite geprüft. Das erhaltene generierte Original und die
ausdrücklich erlaubte Skalierung auf Zweierpotenzgrösse sind transparent
dokumentiert; die bestehende GUI-Partie bleibt erfolgreich.

`build_submission.py` schliesst Git-/Umgebungsdaten, Caches, übliche lokale
Geheimnisse und Laufzeitlogs aus, erhält absichtliche Kursbelege und
benachbarte Originalquellen. Exklusive neue Archive und SHA256-Dateien
verhindern das Überschreiben früherer Pakete. Der tatsächliche
Entpacknachweis prüft die archivierten Hashes und startet Tests/Programme
aus dem entpackten Projekt mit neuer Umgebung.

## Noch offen, ohne neue technische Rückfrage

Der Benutzer ergänzt ausdrücklich die
[eigene Reflexion](../report/meine_reflexion.md) selbst; README markiert
dies gut sichtbar. Auch die
[technische Materialsammlung](../report/abschlussbericht.md) bezeichnet
ihre KI-Unterstützung und die notwendige eigene Prüfung/Überarbeitung.
Eine persönliche Erfahrung, Reflexion oder Erklärungsgarantie wurde nicht
erfunden.

Offen bleiben tatsächliche Lesepartnerschaft, menschliche Regel-/Protokoll-
Reviews, Zweipersonen-Lokalpartie, Echo-/Handshake-Fremdversuche mit
Rollenwechsel, Dreirechnerpartie mit fremden IPs/gemeinsamem Bild,
gegenseitiger Fremdclienttest und Livevorführung. Ein späterer Nachweis
muss diese Tatsachen selbst belegen. Die bereits vertagte praktische
Durchführung wird hier nicht erneut beim Benutzer angefragt.
