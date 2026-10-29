# Bewertungsabgleich — Kursmeilenstein 4 und Gesamtprojekt bis Endabgabe

Stand: 27.10.2026. Rolle 1: Anforderungen aus der Bewertung ableiten.
Dieser Abgleich wurde **vor einer neuen Umsetzung** erstellt. Er trennt
nachprüfbaren vorhandenen Code, frühere tatsächliche Testnachweise und
weiterhin fehlende praktische Nachweise. Er behauptet keinen neuen Testlauf.
Der Benutzer hat den Arbeitsumfang anschliessend ausdrücklich auf die
späteren Meilensteine bis zur Endabgabe erweitert. Der erste Teil hält das
aktuelle M4-Raster getrennt fest; der letzte Teil ist die verbindliche
Ergänzung für den erweiterten Auftrag.

**Ergebnis:** Für die sechs aktuellen M4-Bewertungskriterien ist keine
konkrete zusätzliche Produktionscode-Lücke belegt. Die vorhandene Lösung
deckt die lokal prüfbaren Kriterien ab. Eine konkrete Nachweisverbesserung
ist dagegen möglich: Der Teststarter kann derzeit auch dann mit Exitcode 0
enden, wenn die GUI-Prüfung wegen fehlendem Tk/Display übersprungen wurde.
Das ist normales unittest-Verhalten und wird bereits richtig dokumentiert;
ein ausdrücklicher strenger GUI-Prüfmodus kann Fehlinterpretationen bei
einer erneuten Abnahme verhindern. Der geforderte Fremdrechnernachweis
bleibt offen und ist vom Benutzer ausdrücklich auf später verschoben.
Eine Note oder Punkteerreichung lässt sich daraus nicht zusichern.

## Quellen und Geltung

Zuerst gelesen wurde **Teil 4 „Beurteilung“** des Originals
[Auftrag meilenstein 4.docx](<../../../Dokumente/aufträge meilenstein 4/Auftrag meilenstein 4.docx>).
Danach wurden die übrigen Auftragsabschnitte, die beiden mitgeltenden
Original-DOCX und erst anschliessend Code, Tests und bestehende
Statusdokumentation geprüft.

| Kürzel | Primärquelle | Präzise Fundstellen |
|---|---|---|
| A | [Auftrag meilenstein 4.docx](<../../../Dokumente/aufträge meilenstein 4/Auftrag meilenstein 4.docx>) | Teil 4: P069–P083; Teil 2: P014–P048; Teil 3: P049–P068 |
| B | [Brett auf dem Bildschirm Meilenstein 4.docx](<../../../Dokumente/aufträge meilenstein 4/Brett auf dem Bildschirm Meilenstein 4.docx>) | Fünf Fälle: P310–P339; eigenes Spiel/Protokoll: P340–P379; Fremdrechner/Nachweis: P380–P392 |
| G | [Gui entwickeln meilenstein 4.docx](<../../../Dokumente/aufträge meilenstein 4/Gui entwickeln meilenstein 4.docx>) | Nicht blockieren: P030–P061; Klick: P136–P146; vollständig zeichnen: P147–P162; Fäden/Queue: P163–P207 |
| H | [Alter Projektablauf](../../../Dokumente/Projektablauf.txt) | Gesamtprojekt-Bewertung: Zeilen 719–728; KI/Erklärbarkeit: Zeilen 707–718 |

P001 usw. zählen alle `w:p`-Elemente in `word/document.xml` in
Dokumentreihenfolge, einschliesslich leerer Absätze und Tabellenabsätze.
So bleiben die Fundstellen auch ohne Word-Seitenumbruch eindeutig.

Die drei bestehenden [M4-Textauszüge](../assignments/04_assignment.txt),
[Brett-Anleitung](../assignments/04_board_on_screen.txt) und
[Tkinter-Unterlagen](../assignments/04_tkinter_guide.txt) wurden mit den
Originalen abgeglichen: Alle nichtleeren Absätze entsprechen exakt den
nichtleeren Textzeilen (81 / 366 / 220). Originale und Auszüge wurden nicht
verändert. Auch `docs/assignments/project_flow.txt` entspricht exakt dem
ursprünglichen `../Dokumente/Projektablauf.txt`.

Die aktuelle M4-Bewertung nennt **sechs Kriterien ohne Punktegewichte**.
Die vorhandenen Spielregeln werden beibehalten. Die Aussage „Regeln kommen
später“ (A P020–P021) beschreibt das Unterrichtsbeispiel; sie verlangt keine
Entfernung des bestehenden Schiffe-versenken-Kerns. Das alte M6/M7/M8-Raster
wird nicht zu zusätzlichen M4-Funktionen umgedeutet; es gilt nun zusätzlich
für den vom Benutzer freigegebenen Gesamtprojektumfang.

## Verbindliches aktuelles M4-Raster

| ID / Kriterium | Quelle | Beobachtbare Abnahmebedingung | Vorhandene Deckung und verbleibende Lücke |
|---|---|---|---|
| M4-B01 — Wer entscheidet | A P072–P073; P016–P019; G P136–P146 | Ein Schussklick sendet eine Anfrage und ändert kein Spielfeld. Der Server prüft jeden Schuss auf Zugrecht, gültiges Feld und Doppelbeschuss. Ablehnung verändert weder Zustand noch Zugrecht. | `BattleshipWindow.shoot` stellt nur `shoot` in die Ausgangsqueue; auch direkte `result`-/`placeAck`-Antworten zeichnen nicht. `server.handle` ruft den Kern unter der Spielsperre auf; `BattleshipGame.check_shot` prüft die drei Fälle. Vorhandene GUI-, Zustands- und TCP-Tests prüfen spekulatives Zeichnen, ungültige Felder und private Ablehnungen. **Keine belegte lokale Code-Lücke.** |
| M4-B02 — Eine Anzeige, eine Wahrheit | A P074–P075; G P147–P162 | Eine einzige Zeichenfunktion setzt bei jedem bestätigten Zustand alle Felder beider Raster, einschliesslich leerer/unveränderter Felder. Reset entfernt alle alten Markierungen. | `draw_state` ist die einzige Stelle für Spielfeld-`configure`; sie durchläuft beide Raster und speichert eine Kopie des bestätigten Zustands. Lobby-Ereignisse ändern nur Statusmeldungen. Vorhandene Tests prüfen volle Darstellung, Leeren, mehrere Zustände und das Warten auf `state`. **Keine belegte lokale Code-Lücke.** |
| M4-B03 — Die Fäden | A P076–P077; G P163–P207 | Empfangs-/Sendeworker berühren keine Tk-Widgets oder Tk-Variablen. Nachrichten gelangen über eine Queue und `after` zum Tk-Hauptthread. Idle und langsamer Versand blockieren die Oberfläche nicht. | Statische `_receive`-/`_send`-Worker erhalten nur Socket, Queues und Stop-Ereignis. `_poll_messages` leert die Queue im Hauptthread. `close` gibt Tk-Variablen dort frei. Vorhandene echte Tk-Tests prüfen Hauptthread, Rückstau, Idle, blockierten Versand, Fensterkreuz und Worker-Lebensdauer. **Keine belegte lokale Code-Lücke.** |
| M4-B04 — Wer was erfährt | A P078–P079; P046–P048; B P370–P373 | Nur der Absender erhält seinen Ablehnungsgrund; nach erfolgreicher Aktion erhalten beide ihre vollständige erlaubte Sicht. Eine tatsächlich empfangene Clientnachricht enthält keine unbeschossene Gegnerflotte. | `send_to` adressiert private Antworten; `send_states` erzeugt je Slot `core.state(slot)`. Diese enthält eigene Schiffe, eigene Schüsse und eingehende Schüsse, keine Gegnerflotte. Tests und vorhandener lokaler Clientmitschnitt verwenden verschiedene Flotten und prüfen die Empfänger. Serverlogs enthalten nur Metadaten und ersetzen die Payload-Prüfung nicht. **Keine belegte lokale Code-Lücke; Prüfung im späteren Fremdversuch bleibt offen.** |
| M4-B05 — Nachweis | A P080–P081; P054–P061; B P380–P390 | Eine ganze Partie läuft mit Server und zwei anderen Clientrechnern. Serverausgabe zeigt zwei verschiedene fremde Client-IPs; ein gemeinsames Bild zeigt beide Ansichten nach demselben Zug. Ablehnung ausser der Reihe und Doppelbeschuss sind sichtbar belegt. | Lokale echte GUI-/TCP-Partie und Bildpaar vorhanden; alle IPs sind Loopback. Der Nachweis auf drei realen Rechnern und das gemeinsame Bild aus diesem Versuch fehlen. [Checkliste](../evidence/04_school_network_checklist.md) vorhanden. **Offen, ausdrücklich vertagt; nicht lokal erfüllbar und nicht als erfüllt zu führen.** |
| M4-B06 — Protokoll | A P082–P083; P066–P068; B P368–P369 | Zuganforderung und Zustand nennen Richtung, Pflichtfelder, vollständige Beispiele und Leerfeldbedeutung. Dokumentierte Payloads, Empfänger und Reihenfolge stimmen mit dem Code überein. | [PROTOKOLL.md](../../PROTOKOLL.md) und [JSON-Katalog](../protocol/protocol.json), Version 0.5, beschreiben `shoot` als spielgerechtes `move` sowie vollständige gefilterte `state`-Sichten. Fehlendes Zielfeld bedeutet unbekannt/unbeschossen. Die beiden vorhandenen Protokolltests vergleichen beide Kataloge und spielen die dokumentierte 33-Schuss-Partie durch den Servereingang nach. **Keine belegte lokale Code-/Dokumentationslücke; menschliches Gegenlesen bleibt separat offen.** |

Für M4-B04/B05 bedeutet „beide sehen dasselbe“ bei Schiffe versenken
konsistente Schussergebnisse, Phase und Zugrecht. Die eigenen privaten
Flotten sind verschieden. Das ist ausdrücklich durch A P046–P048 und
B P370–P372 verlangt; identische ungefilterte Bretter wären hier falsch.

Die Zufallsflotte im Client ist ein bearbeitbarer Eingabevorschlag. Sie
entscheidet keinen Spielzug, zeichnet keine Schiffe auf dem Brett und
ersetzt die serverseitige Platzierungsprüfung nicht. Daraus ist kein
Verstoss gegen M4-B01 abzuleiten.

## Mitgeltende praktische Anforderungen

| ID | Quelle | Abnahmebedingung und tatsächlicher Stand |
|---|---|---|
| M4-A01 — Eigenes Brett | B P345–P357; P374–P378 | Zwei 10×10-Raster, alle 100 Zielknöpfe senden ihre eigene A1–J10-Koordinate. Implementiert; eigener GUI-Test für alle Knöpfe vorhanden. |
| M4-A02 — Fünf Fälle | B P310–P339 | Ungefragte Aktualisierung beim Gegner, private falsche Zugfolge, private Doppelbelegung, genau ein Spieler am Zug, Fensterschliessen ohne Servertraceback. Vorhandener lokaler Lauf belegt die spielgerechten Fälle. Kein Fremdrechnernachweis daraus. |
| M4-A03 — Harter Abbruch | B P170–P200; P339 | `netz.read_messages` beendet harte Socketfehler wie EOF; Fensterkreuz informiert Gegner und Server bleibt für Ersatzbeitritt verwendbar. Implementiert, Transport-/GUI-/TCP-Prüfungen und lokaler Lauf vorhanden. |
| M4-A04 — Konsole erhalten | A P024–P026; B P201–P202 | Diagnose im Terminal bleibt möglich. `src/client.py` und `src/play.py` vorhanden; bestehende CLI-Integrationstests bleiben bestehen. |
| M4-A05 — Geschützter Zug | B P163–P169 | Prüfen, Ändern und Senden erfolgen unter derselben Spielsperre, Helfer dokumentieren diese Voraussetzung. In `server.handle` und `remove_player` vorhanden, Wettlauftests vorhanden. |
| M4-A06 — Abzugebende Dateien | A P063–P068 | `src/netz.py`, `src/server.py`, `src/client_gui.py` und ihr benötigter Kern `src/board.py`, Protokoll und Startanleitung sind vorhanden. Die zusätzliche Datei `board.py` ist eine notwendige Abhängigkeit, keine neue Funktion. |
| M4-A07 — Erwartung vorher | B P315–P316 | Vorher-Erwartungen für beide Ansichten stehen in [04_expected_results.md](../evidence/04_expected_results.md); tatsächliche Ergebnisse separat in [04_local_output.md](../evidence/04_local_output.md). Die vorliegenden Dateien werden nicht nachträglich zu einem neuen Versuch umgeschrieben. |

## Einordnung der älteren Gesamtprojektbewertung

Es gibt zusätzlich ein echtes Punkteraster im alten Projektablauf
(H Zeilen 719–726): Architektur 20, Protokoll 20, Nebenläufigkeit 20,
Robustheit 15, Spiel/Oberfläche 15, Bericht/Vorführung 10. Das ist ein
Gesamtprojektraster mit späteren Aufgaben wie Fremdtest und Abschlussbericht,
keine Gewichtung der sechs aktuellen M4-Zeilen. Für die ausdrücklich
beauftragte Endabgabe wird es im letzten Teil dieses Dokuments separat
konkretisiert.

Der folgende Originalsatz (H Zeile 728) nennt für die ersten drei Bereiche
55 Punkte; die drei Tabellenwerte ergeben 60. Die Quelle wird unverändert
gelassen, und aus dieser Unstimmigkeit wird weder eine neue Gewichtung noch
eine blockierende Rückfrage für die aktuelle M4-Arbeit abgeleitet.

Das unter `Projektauftrag_Programming3_Game.docx` abgelegte Dokument enthält
Spielkatalog und Vorschlagsprüfung, kein zusätzliches M4-Punkteraster.
Die dortige Vorschlagsprüfung erklärt ausdrücklich, dass der Vorschlag
nicht benotet wird (XML-P293–P301).

## Priorisierte Verbesserungsliste für Rolle 2 und Rolle 3

Die Prioritäten bezeichnen Arbeitsreihenfolge, keine erfundenen Notengewichte.

| Priorität / ID | Konkrete nächste Arbeit | Erledigt, wenn |
|---|---|---|
| P1 / V01 — Strengen GUI-Nachweis ermöglichen | Rolle 2 kann `tools/run_tests.py` um einen ausdrücklichen Modus wie `--require-gui` ergänzen. Bezug: M4-B02/B03 verlangen tatsächliches GUI-Verhalten; `GuiTests.setUpClass` meldet bei fehlendem Tk/Display bisher Skip, `result.wasSuccessful()` bleibt dabei wahr. Der normale portable Testlauf darf Skips weiter ehrlich anzeigen. Der strenge Modus ist eine empfohlene Nachweishilfe, keine wortwörtliche Auftragsforderung. | Der strenge M4-/Gesamtlauf liefert nur Erfolg, wenn die erforderlichen echten GUI-Tests tatsächlich ausgeführt wurden und bestanden haben; fehlende oder übersprungene GUI-Prüfung führt zu einem klaren Misserfolg. Normales Portabilitätsverhalten bleibt verständlich dokumentiert. |
| P1 / V02 — Frische Ergebnisse nachvollziehbar speichern | Als Ergänzung kann Rolle 2 eine maschinenlesbare Testausgabe mit tatsächlichen Test-IDs, Ergebnis, Dauer, Fehler-/Skipgrund und Umgebung anbieten. Bezug: M4-B05 und ehrliche lokale Nachweise. JSON-Format und Einzelzeiten sind **keine** Pflicht des Auftrags; sie helfen der reproduzierbaren Prüfung. | Gesamtzahlen stimmen mit ausgeführten Einzelergebnissen überein; Fehler und Skips bleiben sichtbar; vorhandene Nachweise werden nicht überschrieben; Umgebungsfelder berichten tatsächliche Messwerte statt ungetesteter Plattformbehauptungen. |
| P2 / V03 — Bewertungsweg sichtbar machen | Rolle 2 verlinkt diesen Quellen-/Bewertungsabgleich aus README und bestehendem M4-Status. Optional ein kurzer Abnahmeleitfaden mit Start, sechs Kriterien, Belegpfaden und offenem LAN-Status. Keine zweite abweichende Anforderungsliste einführen. | Vom Einstieg führen klickbare Links zu den sechs Kriterien, tatsächlichen lokalen Ergebnissen und dem ausdrücklich offenen Fremdversuch; Befehle verwenden aktivierte `.venv` und `python3`. |
| P2 / V04 — Abgabepaket reproduzierbar vorbereiten | Ein lokales M4-Abgabe-ZIP kann A P063–P068 praktisch unterstützen: notwendige `src`-Abhängigkeiten, Regeln, Protokoll, Start-/Prüfanleitung und echte Nachweise aufnehmen, `.git`/`.venv`/Caches ausschliessen. Das ZIP ist **keine zusätzliche explizite M4-Abgabeform** und ersetzt das bereits erstellte vollständige Sicherungs-ZIP nicht. | Entpacktes Paket startet und kann mit eigenen temporären Umgebungen geprüft werden. Manifest/Prüfung belegt Vollständigkeit; offener LAN-Versuch ist im Paket klar markiert; vorhandene Pakete bleiben erhalten. |
| P2 / V05 — KI-Einsatz sachlich nachweisen | Nur bekannte tatsächliche KI-Arbeiten aus Journal, Umsetzung und unabhängiger Prüfung benennen. Bezug: ältere Gesamtprojektquelle H Zeilen 707–718, besonders Erklärungspflicht. Eine solche Dokumentation unterstützt Transparenz, ist aber kein Ersatz für den späteren persönlich verantworteten Bericht. | Keine erfundene persönliche Reflexion, kein behauptetes menschliches Gegenlesen und keine Erklärungsgarantie. Offene persönliche Ergänzungen sind klar als solche kenntlich; die technischen Entscheidungen bleiben anhand des Codes nachvollziehbar. |
| P1 / V06 — Unabhängig neu prüfen | Rolle 3 prüft den finalen lokalen Stand gegen M4-B01–B06 und M4-A01–A06; technische Tests mit aktivierter `.venv` und `python3`, M4 separat sowie relevante Regression. Eine echte GUI-/TCP-Partie bekommt einen neuen Ausgabeordner. Testurteil nennt tatsächliche Befehle, Ergebnisse, Skips und Grenzen. | Frisches schriftliches Testurteil liegt vor; weder ein Skip noch vorhandene Rohlogs werden als neu bestandener Versuch ausgegeben. Erst dabei konkret reproduzierte Defekte erzeugen weitere Codeaufträge für Rolle 2. |
| Höchste fachliche Nachweislücke, jetzt vertagt / V07 | Später die vorhandene Schulnetz-Checkliste mit realem Server und zwei fremden Clientrechnern ausführen; gemeinsames Originalbild, fremde IPs und private Ablehnungen sichern. | Die echten Fremdrechnernachweise liegen vor. **In dieser Arbeitseinheit nicht als erledigt markieren und den Benutzer nicht erneut um denselben bereits vertagten Versuch bitten.** |

**Kein vorsorglicher Produktionsumbau empfohlen:** Für weitere Features,
neue Regelvarianten, Bildgenerierung, Protokoll-Neuerfindung oder eine neue
Abstraktionsschicht liefert die aktuelle M4-Bewertung allein keinen Auftrag.
Die tatsächlich geforderte Bildintegration und weitere Gesamtprojektlücken
stehen nach der Umfangserweiterung gesondert unten.
Rolle 2 soll keinen vermeintlichen Notengewinn durch unbelegte Änderungen
erzwingen. Falls die unabhängige Prüfung einen tatsächlichen Defekt findet,
ist er mit verletzter Kriterien-ID, Reproduktion und gezielter Korrektur
einzutragen.

## Fragen und Grenzen

Es gibt derzeit keine blockierende fachliche Rückfrage für die lokale
M4-Arbeit. Der externe Versuch und menschliche Reviews wurden bereits
ausdrücklich verschoben und werden nicht nochmals erfragt. Die Abgabefrist
im Original ist leer (A P087); sie wird nicht erfunden und ist für diese
lokalen Verbesserungen nicht erforderlich. Eine Bestätigung menschlicher
Reviews, persönliche Erklärfähigkeit oder Prüfung auf anderen Systemen
kann ein KI-Abgleich nicht erbringen.

Rolle 1 hat nur diese Datei erstellt: keine Produktions-/Testdateien,
Originalunterlagen, Rohlogs, Staging-Einträge, Commits oder entfernten
Repositories verändert. Der unabhängige neue Testlauf gehört zu Rolle 3.

## Ergänzung nach Freigabe: Gesamtprojekt M0–M8

Diese Ergänzung gilt für die ausdrücklich gewünschte Verbesserung bis zur
Endabgabe. Sie erweitert den Umfang, ohne externe Versuche oder persönliche
Leistungen als bereits durchgeführt zu behaupten. Die Zustandsangaben
beschreiben den vor der neuen Umsetzung inspizierten Stand.

Zusätzliche Originalquellen:

- **S:** [Ausgefüllte Spielwahl](../../../Dokumente/Auftrag1_Spielwahl_ausgefuellt.docx),
  besonders P058–P095 (Spielentscheid, Zustand, Züge, Fehler, Abbruch,
  verborgene Information und schwierigster Sonderfall), P097–P118
  (Freigabe und Abgabecheckliste).
- **K:** [Projektauftrag / Spielekatalog](../../../Dokumente/Projektauftrag_Programming3_Game.docx),
  P015–P032 (Eignung und Architektur), P112–P127 (Schiffe versenken),
  P260–P305 (Vorschlag und Abnahme).
- **H:** ursprünglicher Projektablauf, vollständig gelesen; unten werden
  dessen tatsächliche Zeilennummern verwendet, nicht nachträglich erfundene
  Meilensteinpflichten.

### Das tatsächliche 100-Punkte-Raster

Die Punktzahlen sind Gewichte der Originalquelle, keine hier vergebenen
Punkte. Ohne fremde Nachweise und persönliche Vorführung kann dieser
Abgleich keine vollständige Punkteerreichung bestätigen.

| ID / Bereich / Punkte | Quelle | Beobachtbare Anforderung | Aktuelle Deckung / echte Lücke |
|---|---|---|---|
| G01 — Architektur / 20 | H L721; L15–L33 | Vier getrennte Verantwortungen: netzunabhängiger Kern, Nachrichtenvertrag, Transport/Server, Anzeige. Kern entscheidet Spielregeln; Server bindet Identität an Verbindung und orchestriert; Client sendet Wünsche und zeigt bestätigte Sicht. | Technisch vorhanden (`board.py`, `PROTOKOLL.md`, `netz.py`/`server.py`, `client_gui.py`). Eine neue Aufteilung ist nicht begründet. Technische Entscheidungen für den Abschlussbericht zusammenführen; persönliche Erklärfähigkeit bleibt vorzuführen. |
| G02 — Protokoll / 20 | H L722; L267–L338; L671–L688 | Alle Nachrichten eindeutig mit Richtung, Pflichtfeldern, Anlass, vollständigen Beispielen und Gesamtpartie. Unbekannte Typen werden abgelehnt, Zustände vollständig und individuell gefiltert. Fremde Person baut ohne Quellcode einen Client; Abweichungen werden dokumentiert. | Version 0.5 und automatische Beispielprüfung vorhanden. Echte menschliche Lesung und gegenseitiger Fremdclienttest fehlen. Ein eigener weiterer Testclient zählt nicht als solcher Fremdtest. |
| G03 — Nebenläufigkeit / 20 | H L723; L340–L449; L530–L632 | Geteilte Daten unter korrekt bemessenem kritischem Abschnitt; Prüfen/Ändern/Senden zusammen; keine Tk-Zugriffe aus fremden Fäden; Begründung der Sperrgrenze. | Implementierung und lokale Wettlauf-/Tk-Tests vorhanden. Bericht muss auch den bekannten Preis des Sendens unter der Sperre erläutern (H L431–L435). Persönliches Begründen kann nicht automatisiert abgenommen werden. |
| G04 — Robustheit / 15 | H L724; L498–L527; L775–L784 | Alle sieben Pflichtangriffe überstanden; Server bleibt verwendbar, ungültige Anfragen ändern keinen Zustand; Abbruch benachrichtigt Gegner. Testtabelle mit Datum und tatsächlichen Beobachtungen. | Tests, historische Angriffsausgaben und Tabellen vorhanden. Frische Gesamtprüfung und eindeutiger Zugriff auf sieben einzelne Ergebnisse sind sinnvoll; keinen zusätzlichen Angriff als vermeintliche Originalpflicht erfinden. |
| G05 — Spiel und Oberfläche / 15 | H L725; L138–L265; L654–L660 | Schriftlich festgelegte Regeln vollständig, Spiel bedienbar, Zug/Zustand/Fehler/Abbruch erkennbar; vollständige GUI-Partie; mindestens ein selbst erzeugtes eingebundenes Bild mit dokumentierter Herkunft. | Regeln, Kern, lokale/GUI-Partie und Zustandsanzeigen vorhanden. **Pflichtbild fehlt:** derzeit weder Bildasset noch `PhotoImage`-Einbindung im GUI. Zwei-Personen-Partie am Tisch fehlt als menschlicher Nachweis. |
| G06 — Bericht und Vorführung / 10 | H L726; L690–L718 | Bericht begründet Architektur, Protokoll und geteilten Zustand, enthält sieben Angriffe, echtes Fremdtestergebnis, KI-Erklärung und Reflexion. Live: ganze Partie, sichtbare Ablehnung, harter Abbruch; jede Person beantwortet Codefragen. | Technische Dokumente und Rohbelege sind vorhanden, **vollständiger Abschlussbericht und Vorführleitfaden fehlen**. Persönliche Reflexion, eigenverantwortliche Endfassung, fremdes Testergebnis und tatsächliche Livevorführung sind nicht durch KI ersetzbar. |

### Vollständige Abnahmeübersicht nach ursprünglichem Meilenstein

| ID | Quelle | Akzeptanz und vorhandene Grundlage | Fehlend / Behandlung |
|---|---|---|---|
| M0-01 — Werkzeuge/Git | H L60–L94; L131–L136 | Repository mit Anfangshistorie, funktionsfähige Struktur, virtuelle Umgebung, Python ≥3.12, lokales Echo. Vorhanden; Historie/Setup sind im bisherigen Status dokumentiert. | Neue Git-Schritte bleiben ausdrücklich untersagt; der Benutzer übernimmt Staging/Commits/Pushes. Original-Beispielpfade sind keine Pflicht, Quellen aus `src/` zurück in die Wurzel zu verschieben. |
| M0-02 — Echo und Lesepartner | H L65–L69; L131–L136 | Echo über zwei reale Rechner, danach Rollenwechsel, tatsächliche IP notiert. Feste Lesepartnerschaft im README. | Fremdversuch und reale Partnerperson fehlen. Nicht erfinden und nicht aus Loopback-/KI-Prüfung ableiten. |
| M1-01 — Wahl und Regeln | H L138–L148; S P057–P095; K P112–P127 | Freigegebene Wahl; Regelblatt mit Zustand, allen Zugarten/Fehlern, Ende, Unentschieden/Zugunfähigkeit/Abbruch, Skizze. | Schiffe versenken laut bestehendem Status im Gespräch freigegeben; `REGELN.md` beantwortet die Punkte und enthält Skizze. Tatsächliches menschliches Gegenlesen bleibt offen. Original-Skizzenrückseite/Formular nicht nachträglich als abgezeichnet behaupten. |
| M2-01 — Kern und Tests | H L150–L265; S P095 | Klasse ohne Socket/Tk, Prüfen/Ausführen/Zustandskopie; mindestens fünf Tests; expliziter Test für schwierigsten benannten Fall. | Vorhanden: Tests prüfen u.a. individuelle Sichten/Kopien, Platzierung und Treffer. S P095 benennt genau diese Fälle. Frischen Lauf durchführen, keine zusätzliche Regelvariante nötig. |
| M2-02 — Zwei Personen am Tisch | H L264 | Zwei reale Personen spielen eine ganze Partie an einer Tastatur. | `local_game.py` und geskripteter 33-Schuss-Lauf vorhanden; reale Zweipersonenpartie fehlt. |
| M3-01 — Vertrag und Transport | H L267–L338 | Vollständiger Katalog, alle Beispiele, ganze Partie, dauerhafte JSON-Lines-Lesung; zwei Testprogramme für Transport. | Vorhanden in Protokoll 0.5, Transport-/TCP-Tests und CLI. Echte Person muss zusätzlich bestätigen können, daraus einen Client zu bauen. |
| M4-01 — Konsolenserver | H L340–L449 | Zwei Konsolenclients spielen ganze Partie, Ablehnung privat, Kern entscheidet Regeln, Abbruch behandelt, kommentierter/begründbarer kritischer Abschnitt; reproduzierbare Zugliste. | `play.py` und echte TCP-Spieltests vorhanden. Für klare Endabgabebelege möglichst komplette Partie über zwei tatsächliche Konsolenclient-Prozesse mit frischen Ausgaben sichern; nicht bloss GUI-Lauf zu Konsolennachweis umbenennen. Persönliche Begründung bleibt beim Autor. |
| M5-01 — Sieben Angriffe | H L498–L527; L775–L784 | 1 ungültiges JSON; 2 falsch typisiertes Feld; 3 ausserhalb; 4 Pflichtfeld fehlt; 5 unbekannter Typ; 6 ausser der Reihe; 7 Verbindung mitten im Zug trennen. Danach Server verwendbar; ungültige Anfragen ohne Zustandsänderung. Tabelle mit Datum und Beobachtung. | Technische Fälle sind in bestehenden Transport-/TCP-/Angriffstests und historischen Tabellen enthalten. Endabgabe soll die sieben spielgerechten Fälle in einem leicht auffindbaren frischen Ergebnis zusammenführen. Nicht nur die kürzere Handshake-Prüfung als alle sieben Spielangriffe bezeichnen. |
| M6-01 — Bedienbare GUI | H L530–L632; L654–L659; aktuelles M4-Raster | Ganze Partie, nachgewiesene Hauptthread-Grenze, Zug/Fehler/Abbruch sichtbar. | Bereits technisch umgesetzt und lokal belegt; neue Tests gegen finalen Stand. Ein Ausfall des Displays ist ein Prüfproblem mit offener GUI-Abnahme, kein bestandener GUI-Test. |
| M6-02 — Eigenes Bild | H L633–L648; L660 | Mindestens ein selbst erzeugtes Bild ist im GUI eingebunden. KI-Bildwerkzeuge sind erlaubt. PNG mit transparentem Hintergrund und fester Zweierpotenz-Kantenlänge (64/128/256), Ablage `bilder/`, Herkunft im README. Referenz muss über gesamte Tk-Nutzung leben. | **Konkreter Implementierungsauftrag:** ein passendes eigenes Schiffe-versenken-Asset erzeugen, Original speichern, im Tk-Hauptthread laden/anzeigen und Referenz halten, Herkunft/Werkzeug ehrlich dokumentieren. Reine Testscreenshots erfüllen die Bildgestaltungspflicht nicht. |
| M7-01 — Verteilung/Lobby/Abbruch | H L662–L669; L682–L688 | Ganze Partie auf mindestens drei realen Rechnern; Serveradresse konfigurierbar, permanentes Wartezimmer, dokumentierte Abbruchentscheidung. | Adresse/Port, permanente Accept-Schleife, Warten und Reset/Ersatz sind implementiert. Drei echte Rechner fehlen weiterhin und bleiben vertagt. |
| M7-02 — Nachrichten mit Zeitstempel | H L670; L687 | Jede ein-/ausgehende Nachricht wird mit Zeitstempel in eine Datei geschrieben; ganze Partie ist als Mitschnitt vorhanden. | **Konkrete Lücke:** `log_message` druckt nur Typ/Peer/ggf. Fehlercode ohne Zeitstempel; Datei entsteht derzeit erst durch Werkzeugumleitung. Einen expliziten dauerhaften Dateilog mit Zeit/Richtung/Verbindung/Typ für jede empfangene und gesendete Nachricht ergänzen. Keine gegnerischen Flotten oder freie Clienttexte in öffentliche Serverbelege schreiben; Geheimhaltung zusätzlich an isolierten tatsächlich empfangenen Clientansichten prüfen. |
| M7-03 — Gegenseitiger Fremdtest | H L671–L675; L688 | Partner erhält nur Protokoll und Serveradresse, baut eigenen einfachen Client und spielt; anschliessend Rollenwechsel; schriftliches Ergebnis samt Abweichungen. | Menschlicher Fremdtest fehlt. KI-eigener Client, In-Memory-Replay und interne Review-Agenten erfüllen dies nicht. Vorlage und Schrittfolge können vorbereitet werden. |
| M8-01 — Abgabedateien | H L690–L697 | Lauffähige Programme mit Standardbibliothek; Zusatzpakete ggf. README-Installationsbefehl. README mit Start/Bedienung/Bildherkunft; aktuelles Protokoll mit Gesamtpartie. | Programmbasis und Anleitungen vorhanden. Neues Asset/Logging/Tests in Paket aufnehmen. ZIP/Manifest/sauberer Entpacktest sind hilfreiche lokale Lieferform, kein als Pflicht erdachtes Dateiformat. |
| M8-02 — Abschlussbericht | H L696; L707–L718 | Architektur, Protokollentwurf mit Begründung, kritischer Abschnitt, sieben Angriffe, tatsächlicher Fremdtest, KI-Erklärung und persönliche Reflexion. | Material aus vorhandenen Dokumenten zusammenführen; KI-Einsatz exakt kenntlich machen. Offene externe Ergebnisse und persönliche Reflexion bleiben klar als offene Autor-/Personenaufgaben markiert, statt sie durch erfundene Prosa zu ersetzen. |
| M8-03 — Vorführung | H L697–L706; L713 | Live ganze Partie auf mindestens zwei Rechnern, sichtbare Ablehnung, Client hart schliessen, andere laufen weiter; beliebige Codefragen beantworten. | Technischer Ablauf lokal automatisiert nachgewiesen. Reproduzierbaren Leitfaden und Prüffragen vorbereiten. Liveleistung, Gerätezahl und persönliche Erklärung nicht behaupten. |
| M8-04 — Journal | H L786–L788 | Nach jeder Arbeitseinheit tatsächliche Änderungen, offene Punkte und Blockaden im Repository. | `journal.md` vorhanden. Neue Arbeit sachlich ergänzen; vergangene Belege nicht umschreiben und keine persönlichen Entscheidungen erfinden. |

### Präzisierungen aus der Spielwahl

S P058 nennt Vier gewinnt als Erstwunsch und Schiffe versenken als
Zweitwunsch. Die bestehende spätere Projektbestätigung und die tatsächlich
ausgearbeitete Schiffe-versenken-Lösung sind massgeblich; daraus wird kein
Wechsel des Spiels abgeleitet. S P081 nennt noch beispielhaft 30 Sekunden
Wiederverbindung mit anschliessendem kampflosem Sieg. `REGELN.md` dokumentiert
die spätere Änderung zum sofortigen Reset ausdrücklich. H L669 verlangt
eine entschiedene und dokumentierte Abbruchregel und schreibt Reconnect
nicht vor. Deshalb bleibt der vorhandene Reset bestehen.

K P127 verlangt, schriftlich festzulegen, ob Treffer einen weiteren Schuss
erlauben. `REGELN.md` und Protokoll legen bereits eindeutig fest: jeder
gültige Schuss wechselt den Spieler. Überlappung, Überstand und Übergang
Platzieren/Schiessen sind im Kern und den Tests erfasst. S P079 verlangt
Abwehr falscher Spieleridentität und selbst gemeldeter Treffer; der Server
verwendet den Slot der Verbindung und entscheidet Treffer selbst. Kein
neuer Authentifizierungsdienst ist daraus abzuleiten.

### Umsetzung in priorisierten Gruppen

| Priorität / Auftrag | Zuständigkeit / konkrete Lieferung | Abnahme |
|---|---|---|
| P1 / END-01 — Echte Pflichtlücken schliessen | Rolle 2: Nachrichten-Dateilog mit echten Zeitstempeln und vollständiger Ereignisabdeckung (M7-02); eigenes zulässiges Bild integrieren und Herkunft dokumentieren (M6-02). Falls Bildgenerierung separat erfolgt, nur dieses Asset übergeben. | Tests prüfen logische Logvollständigkeit, Datenschutz und Dateipfad; echtes Tk zeigt das tatsächliche Asset und hält die Referenz. Vorhandene Datenflüsse, Regelkern und alte Rohbelege bleiben erhalten. |
| P1 / END-02 — Nachweise abnahmefest machen | Rolle 2: strengen GUI-Modus und nachvollziehbare Testergebnisse wie V01/V02; sieben Pflichtangriffe und komplette Konsolenpartie frisch zugänglich machen. Rolle 3 prüft unabhängig. | Tatsächliche Testbefehle und Einzelergebnisse; echter GUI-/TCP-Lauf; belegte sieben Fälle; offenes LAN/Human-Review explizit sichtbar. |
| P2 / END-03 — Endabgabe vorbereiten | Rolle 2: technischen Berichtsentwurf/Materialsammlung, sachliche KI-Einsatzdoku, Vorführleitfaden, Quellen-/Belegindex, vollständiges lauffähiges Abgabepaket samt Entpackprüfung; README/Journal/Status aktualisieren. | Jede technische Aussage zeigt auf Code oder tatsächlichen Beleg. Persönliche Reflexion, ungeprüfte Fremdtestergebnisse und nicht ausgeführte Liveleistung sind als offene Autorleistungen kenntlich, nicht als Inhalt erfunden. |
| Offen / END-04 — Personen und fremde Geräte | Projektverantwortlicher und echte Partner: Lesepartnerschaft; Regel-/Protokollreview; Zwei-Personen-Lokalpartie; Echo/Handshake mit Rollenwechsel; Dreirechnerpartie samt Bild/IPs; gegenseitiger Fremdclienttest; Livevorführung und persönliches Erklären. | Tatsächliche Namen/Bestätigungen/Versuche mit Datum und Originalbelegen. Bis dahin bleibt Gesamtprojekt in diesen Punkten offen. Der bereits ausdrücklich verschobene Fremdrechnerversuch wird nicht erneut angefragt. |

### KI-Rolle und ehrliche Endabgabe

Der Benutzer hat ausdrücklich entschieden: **Die persönliche Reflexion
erledigt er selbst.** Dafür wird eine separate Datei vorbereitet und im
README klar als noch vom Benutzer zu ergänzen markiert. Die Vorbereitung
der Datei ist beauftragt; eine KI-formulierte persönliche Reflexion wäre
kein Ersatz für diese offene Autorenleistung.

H L710–L715 unterscheidet zulässige Bildgestaltung, erklärpflichtige
Oberflächengerüste/Hilfsfunktionen/Tests und vom Autor selbst zu verantwortende
Teile: Kern/Regeln, Nachrichtenkatalog, Sperrenentscheidung und Bericht.
Die vorhandene und neue KI-Unterstützung muss daher offen benannt werden.
Eine generierte technische Materialsammlung darf dem Autor helfen, wird
aber nicht als persönlich geschriebener und verstandener Abschlussbericht
oder persönliche Reflexion ausgegeben. Vor Abgabe muss er diese Teile
selbst prüfen, überarbeiten und erklären können. Das gilt auch dann, wenn
alle automatischen Tests grün sind.

Es fehlt keine weitere technische Grundsatzentscheidung, die jetzt den
Arbeitsfortschritt blockiert. Die dokumentierte Spielwahl, Flotte,
Zugwechselregel und Resetentscheidung werden beibehalten. Externe oder
persönliche Tatsachen, die noch nicht vorliegen, werden mit eindeutigen
Platzhaltern vorbereitet. Weder vollständige Abgabeerfüllung noch 100 Punkte
werden ohne die tatsächlichen Personen-/Fremdrechnerleistungen behauptet.
