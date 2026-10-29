# Unabhängiges Testurteil zur technischen Endabgabe

Stand: 27.10.2026, Europe/Zurich. Durchführung: **automatisierter
Codex-Testlauf, Rolle 3**; getrennt von Anforderungsableitung und
Produktionsumsetzung. Kein persönlicher Testlauf von Max Rufener und kein
Fremdrechner- oder menschlicher Fremdclientnachweis.

**Urteil:** Die lokal prüfbaren technischen Anforderungen bestehen im
geprüften Stand. Die vollständige Suite besteht mit **101 Tests, 0 Fehlern,
0 Fehlschlägen und 0 Skips**; alle **16 erforderlichen echten Tk-Prüfungen**
wurden ausgeführt. Sieben Pflichtangriffe, eine vollständige Partie mit
zwei tatsächlichen Konsolenclientprozessen und eine vollständige Partie mit
zwei echten Tk-Fenstern über TCP bestehen. Das separat entpackte
Kandidatenpaket besteht dieselbe technische Prüfung aus einer neuen
virtuellen Umgebung. Eine vollständige menschlich verantwortete Endabgabe
oder eine Note wird damit nicht bestätigt.

## Ausgangspunkt und Prüfverfahren

Massgebend ist der zuerst aus den Originalunterlagen abgeleitete
[Bewertungs- und Anforderungsabgleich](04_rubric_requirements.md), ergänzt
durch die freigegebene [Spezifikation](../superpowers/specs/2026-10-27-final-assessment-design.md)
und den [Arbeitsplan](../superpowers/plans/2026-10-27-final-assessment.md).
Die sechs aktuellen M4-Kriterien bleiben vom älteren Gesamtprojektraster
getrennt. Die Gewichte dort sind Quellenangaben, keine hier vergebenen Punkte.

Vor Produktionsänderungen führte Rolle 3 die bestehende Suite mit echtem
Tk/TCP aus: 84 Tests, alle bestanden, keine Skips (5,063 s; tatsächliche
Toolausgabe). Danach wurden die Schnittstellen mit Rolle 2 abgestimmt und
17 zusätzliche Verhaltenstests geschrieben: 10 Runner-, 1 Bild-, 4 Log-
und 2 Pakettests. Die 15 anfänglichen Tests scheiterten wegen der fehlenden
Funktionen; [RED-Rohausgabe](../evidence/final_assessment_tests/red.txt).
Zwei zusätzliche Runner-Grenzfälle scheiterten gegen die erste Umsetzung;
[RED-Grenzfälle](../evidence/final_assessment_tests/red_strict_boundaries.txt).
Auch ein danach entdeckter unzutreffender Endstatus eines übersprungenen
Subtests wurde vor seiner Korrektur reproduziert;
[RED-Endstatus](../evidence/final_assessment_tests/red_subtest_status.txt).

Rolle 3 änderte nur Tests und neue eigene Nachweis-/Urteilsdateien.
Rolle 2 änderte Produktion und Werkzeuge. Bestehende Quellen und Rohbelege
wurden nicht durch neue Resultate ersetzt. Zwischenstände mit Fehlern
bleiben erhalten und sind keine gültige Endabnahme.

## Tatsächliche Ausführungen

Alle folgenden Python-Befehle wurden direkt mit `.venv/bin/python3`,
dem Interpreter der Projekt-`.venv`, ausgeführt. Die Tabelle nennt die
gleichwertigen `python3`-Befehle nach Aktivierung dieser Umgebung. In dieser Umgebung: **Python 3.14.10,
Tk 9.1, macOS 27.0.1, ARM64**. Lokale Portbindungen und echte Tk-Fenster
benötigten die gezielte Ausführung ausserhalb der blockierenden Sandbox.
Ein Sandbox-Skip wurde nicht als GUI-Erfolg übernommen.

| Prüfung | Tatsächlicher Befehl / Auswahl | Ergebnis und Beleg |
|---|---|---|
| Abschliessende vollständige Suite | `python3 tools/run_tests.py --require-gui --report-json docs/evidence/final_assessment_tests/full_v3.json` | 101/101 bestanden; 16/16 GUI; keine Skips; [JSON](../evidence/final_assessment_tests/full_v3.json), [vollständige Rohausgabe](../evidence/final_assessment_tests/full_v3.txt) |
| M4 separat | `python3 tools/run_tests.py --milestone 04 --require-gui --report-json docs/evidence/final_assessment_tests/m04.json` | 35/35 bestanden, 15/15 GUI; [JSON](../evidence/final_assessment_tests/m04.json) |
| Neue Gruppen separat | `--milestone 06 --require-gui`, `--milestone 07`, `--milestone 08`, jeweils mit neuer JSON-Datei | 1/1 Bild, 4/4 Log, 2/2 Paket bestanden; [M6](../evidence/final_assessment_tests/m06.json), [M7](../evidence/final_assessment_tests/m07.json), [M8](../evidence/final_assessment_tests/m08.json) |
| Sieben Angriffe und zwei Konsolenprozesse | `python3 docs/evidence/final_assessment_tests/verify_local.py --output docs/evidence/final_assessment_tests/local_20261027_a` | 7/7 Angriffe und 33 gültige Konsolenschüsse; [Gesamtergebnis](../evidence/final_assessment_tests/local_20261027_a/result.json), [Angriffstabelle mit Zeit/Beobachtung](../evidence/final_assessment_tests/local_20261027_a/seven_attacks.md), [Konsolenergebnis](../evidence/final_assessment_tests/local_20261027_a/console_result.json) |
| Zwei echte GUI-/TCP-Clients | `python3 tools/run_gui_demo.py --output docs/evidence/final_assessment_tests/gui_20261027_a` | Vollständige 33-Schuss-Partie, private falsche Zugfolge und Doppelbeschuss, Fensterkreuz/Reset/Ersatz, individuelle private Flotten: PASS; [Ergebnis](../evidence/final_assessment_tests/gui_20261027_a/result.json), [tatsächlich empfangene Payloads](../evidence/final_assessment_tests/gui_20261027_a/client_messages.jsonl) |
| Kandidatenpaket unabhängig entpackt | `python3 docs/evidence/final_assessment_tests/verify_package.py --archive /private/tmp/Schiffe_versenken_candidate_20261027.zip --output docs/evidence/final_assessment_tests/candidate_verification --extract /private/tmp/Schiffe_versenken_candidate_extract_20261027` | 162 Manifestdateien, 7 Originalquellenlinks, neue `.venv`, fremdes Arbeitsverzeichnis, 101/101 strikt mit 16 GUI, anschliessend 7 Angriffe und echte 33-Schuss-Konsolenpartie: PASS; [Prüfbericht](../evidence/final_assessment_tests/candidate_verification/result.json), [Test-Rohausgabe](../evidence/final_assessment_tests/candidate_verification/tests.txt) |

Die vollständige Suite verteilt sich auf M0: 1, M2: 26, M3: 32, M4: 35,
M6: 1, M7: 4 und M8: 2 Tests. Der JSON-Bericht enthält 101 unterschiedliche
ausgeführte Test-IDs. Klassen-/Subtestereignisse werden getrennt erfasst;
ihre Ereigniszahlen sind keine erfundenen zusätzlichen Testmethoden.
Der letzte Gesamtlauf und die Kandidatenprüfung enthalten weder
ResourceWarnings noch unbehandelte Tracebacks.

Der erste Gesamtlauf mit den noch unbehobenen Runner-Grenzfällen ist unter
[first_full.json](../evidence/final_assessment_tests/first_full.json) und
[first_full.txt](../evidence/final_assessment_tests/first_full.txt) erhalten.
`full_v2` liegt vor der abschliessenden Endstatus-Korrektur; **`full_v3`
ist die abschliessende Prüfung der Arbeitskopie**.

## Bewertung der Tests und gefundene Defekte

Die neuen Tests prüfen Verhalten an echten Grenzen: kleine kontrollierte
`unittest`-Suiten statt rekursiver Gesamtstarts, tatsächliche PhotoImage-
Pixel und Widgets statt Widgetattrappen, reale Socketnachrichten,
JSONL-Dateien sowie ZIP-Inhalt und unabhängig berechnete SHA256-Werte.
Die Testfälle berechnen ihre Erwartungen nicht mit den produktiven
Hilfsfunktionen und prüfen keine Quelltextzeilen.

| Schutz | Konkret abgefangener Fehler / Befund |
|---|---|
| Strenger Runner | Fehlendes GUI, Klassen-/Test-/Subtest-Skip und `expectedFailure` dürfen keine bestandene GUI-Abnahme ergeben. Zwei echte Defekte der ersten Umsetzung wurden dabei gefunden und korrigiert. Ein dritter Befund betraf den dauerhaft falschen `running`-Status eines abgeschlossenen Tests mit Subtest-Skip; nun terminaler Status `partial_skip`. |
| Ergebnisbericht | Echte IDs, Dauer, Grund, Fehler und Fixture-Ereignisse; keine erfundenen Testausführungen bei `setUpClass`-Fehler. Vorhandene Berichte werden vor Ausführung geschützt. |
| Bild | Tatsächliches ausgeliefertes transparentes PNG entspricht den dargestellten Pixeln; zweierpotente Kantenlänge, sichtbare Gestaltung, fremdes Arbeitsverzeichnis, Referenz während Nutzung und Freigabe im Tk-Hauptthread. Alle 15 bisherigen GUI-Tests bleiben bestanden. |
| Dauerhafte Logs | Jede tatsächlich empfangene/gesendete Nachricht des kontrollierten Handlers besitzt Metadaten und Zeitzone; Sichtbarkeit vor `close`, 240 parallele Schreibvorgänge ohne zerrissene Zeilen, Schutz bestehender Datei, keine Flotte/freien Clienttexte. Ganze tatsächliche Partien ergänzen diese fokussierte Prüfung. |
| Paket | Echte Dateien statt Namensattrappen im Ergebnis: Kern/Netz/Server/GUI, Tests, Bild und Belege, benachbarte Originalquellen, Ausschlüsse, unabhängige Hashprüfung und Überschreibschutz. Der unabhängige Entpacklauf prüft die echten Programme zusätzlich in neuer Umgebung. |

Der GUI-Lauf protokolliert 40 ein- und 125 ausgehende Nachrichten; die
JSONL-Anzahl stimmt je Richtung exakt mit den separat ausgegebenen
Serverereignissen überein. Alle Zeilen sind parsebar, besitzen ISO-Zeit
mit Zeitzone und enthalten ausschliesslich die erlaubten Metadatenfelder.
Die Angriffs-/Konsolenläufe protokollieren 38/61 beziehungsweise 40/117
Nachrichten (ein/aus). Die Geheimhaltung der Gegnerflotte wird zusätzlich
an den tatsächlichen Client-Payloads mit verschiedenen Flotten geprüft.
Ein reines Metadatenlog wird dafür nicht als ausreichender Beweis verwendet.

Das eigene Bild wird mit 64×64 Pixeln angezeigt. Die angeforderte
Fenstergrösse beträgt jetzt **800×716**, zuvor 800×682 Pixel. Die 34 Pixel
zusätzliche Höhe stammen vom dekorativen Kopfbereich. Die getesteten
Bedienwege, Zeichenlogik, Payloads, Threadgrenzen und vollständige Partie
zeigen keine funktionale Regression. Ein neues gemeinsames Bildschirmfoto
wurde in diesem Lauf nicht aufgenommen; das ist kein Ersatz für das noch
ausstehende gemeinsame Originalbild aus dem Fremdrechnerversuch.

Die Prüfungen sind gezielte Regressions-/Verhaltensnachweise. Es wurde
keine Messung vollständiger Pfadabdeckung und keine umfassende automatische
Mutationskampagne ausgeführt; ein entsprechender Prozentwert wird nicht
behauptet. Den neuen Funktionen ging tatsächliches RED voraus, und die
beobachteten Runner-Fehler belegen praktische Fehlererkennung der Tests.

## Abgleich gegen die tatsächlichen Bewertungskriterien

| ID | Unabhängiges Urteil zum geprüften Stand |
|---|---|
| M4-B01 — Wer entscheidet | Lokal bestanden: Klick sendet nur Anfrage, keine spekulative Brettänderung; Kern entscheidet und Ablehnungen erhalten Zustand/Zug. |
| M4-B02 — Eine Anzeige, eine Wahrheit | Lokal bestanden: vollständiges Neuzeichnen beider Raster, auch Leeren/Reset und mehrere Zustände. |
| M4-B03 — Die Fäden | Lokal bestanden: echte Tk-Tests für Queue/Hauptthread, Idle, blockierten Versand und Ressourcenfreigabe. |
| M4-B04 — Wer was erfährt | Lokal bestanden: private Ablehnungen und verschiedene tatsächlich empfangene gefilterte Sichten; keine fremde Flotte. |
| M4-B05 — Nachweis | Lokale technische Partie belegt; **geforderte drei realen Rechner, zwei fremden IPs und gemeinsames Originalbild fehlen weiterhin**. |
| M4-B06 — Protokoll | Automatischer Abgleich beider Kataloge und dokumentierter Gesamtpartie bestanden; menschliches Gegenlesen bleibt offen. |
| M4-A01–A06 | Lokal bestanden: alle 100 Koordinaten, fünf GUI-Fälle, harter Abbruch/Ersatz, erhaltene Konsole, kritischer Abschnitt und benötigte Dateien. Die externen Teile der Nachweise bleiben offen. |
| G01 — Architektur | Technische Trennung und Zuständigkeiten durch Kern-/TCP-/GUI-Tests und Bericht gedeckt; persönliche Erklärung nicht abgenommen. |
| G02 — Protokoll | Version 0.5, Ablehnungen, Reihenfolge, vollständige individuell gefilterte Sichten und Gesamtpartie technisch geprüft. Echter gegenseitiger Fremdclienttest fehlt. |
| G03 — Nebenläufigkeit | Wettlauf-, Queue-, Tk-/Socket- und parallele Logtests bestanden. Die dokumentierte Entscheidung zum Versand unter der Spielsperre muss der Autor selbst begründen können. |
| G04 — Robustheit | Alle sieben Originalangriffe frisch mit Datum und tatsächlicher Beobachtung bestanden; nach TCP-RST leerer Reset, Ersatz und nächster gültiger Schuss erfolgreich. |
| G05 — Spiel/Oberfläche | Ganze Konsole-/GUI-Partie und eigene Bildintegration technisch bestanden (M6-01/M6-02). Eine reale Zweipersonenpartie an einer Tastatur wird dadurch nicht belegt. |
| G06 — Bericht/Vorführung | Technische Materialsammlung, KI-Kennzeichnung, Leitfaden und getrennte Reflexionsdatei vorhanden. Eigenverantwortliche Endfassung, persönliche Reflexion, echte Fremdtestergebnisse und Liveleistung bleiben offen. |
| M7-02 / END-01 | Dauerhafte Nachrichten-Dateilogs mit ISO-Zeit, vollständigen Zeilen, Privatheit und geschütztem Lebenszyklus technisch geprüft. |
| V01/V02 / END-02 | Strenger GUI-Nachweis und wahrheitsgemässe Einzelberichte geprüft; alte Ergebnisse erhalten. |
| V04 / M8-01 / END-03 | Kandidatenpaket mit Abhängigkeiten, Bildern, Tests, Dokumenten und Originalquellen unabhängig entpackt und ausführbar geprüft. |
| END-04 | Personen-/Fremdrechnerleistungen bleiben ausdrücklich ausstehend. |

## Paketstand und verbleibende Aufgaben

Das geprüfte Kandidatenarchiv liegt ausserhalb des Repositorys unter
`/private/tmp/Schiffe_versenken_candidate_20261027.zip`.
Sein SHA256 ist
`3ed836f3fadf3f4b686ad7c905498fa3f1a606183a314b16ca16fc325ed9a08f`.
Es ist eine technische Vorabprüfung des Paketstands vor Aufnahme dieses
Urteils. Das abschliessende Auslieferungsarchiv wird danach neu erzeugt und
nochmals unabhängig entpackt geprüft. Dessen eigene Prüfbestätigung wird
**neben dem Archiv** gespeichert: So behauptet das Archiv keine erst nach
seiner Erstellung erfolgte Prüfung und muss nach dieser Prüfung nicht
verändert werden. Der Kandidatenbericht gehört als tatsächlicher Beleg
ins Auslieferungspaket.

Der Benutzer ergänzt [meine_reflexion.md](../report/meine_reflexion.md)
selbst und prüft/überarbeitet die technische Materialsammlung zu seiner
eigenen erklärbaren Endfassung. Offen bleiben tatsächliche
Lesepartnerschaft, menschliches Regel-/Protokollreview, reale
Zweipersonenpartie, Echo/Handshake über fremde Rechner mit Rollenwechsel,
Dreirechnerpartie samt IP-/Bildnachweis, gegenseitiger Fremdclienttest und
Livevorführung. Diese Aufgaben sind ausdrücklich vertagt und werden hier
nicht nochmals angefordert oder als erledigt markiert. Python 3.12 sowie
Windows/Linux wurden in dieser Arbeitseinheit nicht ausgeführt.

Die Tests begründen keine erfundene Punktezahl und keine Garantie für die
Bewertung. Im abschliessend geprüften lokalen technischen Stand ist kein
reproduzierter offener Funktionsdefekt bekannt.
