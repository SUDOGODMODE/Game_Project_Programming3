# Journal

## 13.10.2026 — Kursmeilenstein 3, lokale Überarbeitung

**Umgesetzt:** Dauerhafter Lobbyclient, Servermeldungen `waiting`, `gameStart` und `opponentLeft`, Freigabe des Slots und Rundenreset bei Abgang. Der netzwerkfreie Kern `board.BattleshipGame` kapselt Spielzustand und Regeln; der Server verwaltet Verbindungen und die gemeinsame Sperre. Fachliche Durchsicht und Gegenlesen stehen aus.

**Dokumentation:** README und Nachrichtenkatalog Version 0.4 aktualisiert, `PROTOKOLL.md` mit Pflichtfeldern und Ablaufbeispiel ergänzt. Kursaufgabe und drei Kontextquellen unverändert kopiert. Unterschiedliche Nummerierung von Kursmeilenstein und Projektphasen erläutert, Schulnetz-Check vorbereitet und ältere Nachweise unverändert belassen.

**Prüfungen:** 47 Prüfungen bestanden (9 Brett-, 12 Spielkern-, 26 TCP-/CLI-Tests); die vier Lobbyfälle, q, harter Abbruch und Ersatzbeitritt sind aufgezeichnet. Ergebnisse, Angriffstabelle und Rohlogs stehen in `docs/evidence/03_local_output.md`. Lokale Umgebung: Python 3.15.0; Kursvorgabe: 3.12 oder neuer. Eine eigene Ausführung unter 3.12 ist noch nicht belegt.

**Offen:** Lesepartnerschaft mit Namen, fachliche Durchsicht, Regelblatt/Freigabe, manuelle Tischpartie und Schulnetzversuch mit zwei fremden Client-Rechnern. Für spätere Projektphasen: Zustands-Pushes nach Spielaktionen, GUI, zeitgestempelte Nachrichtendateien, Fremdclient-Test in beide Richtungen und Bericht/Vorführung. Reflexion und KI-Erklärung sind im Bericht noch zu ergänzen.

## 13.10.2026 — Abgleich beider Meilenstein-Nummerierungen

- Ursprünglichen Katalog und ausgefüllten Spielvorschlag gelesen; Spielwahl Schiffe versenken bestätigt. Kein vorhandener Fremdrechner- oder Gegenlese-Nachweis gefunden.
- Echo-Programme für M0 und eine Partie ohne Netz für M2 ergänzt. Regelblatt mit Flotte, ungültigen Aktionen, Abbruchregel und Oberflächenskizze angelegt. Der sofortige Reset ersetzt die ältere Idee einer Wartefrist mit Aufgabe.
- Transporttests für gemeinsame und zerstückelte Nachrichten ergänzt. Erwartungen vor dem erneuten Prüflauf festgehalten.
- Wiederholte Kommentare und Absätze gekürzt, Dokumentationssprache vereinheitlicht, ungenutzten Verbindungsstatus und überflüssige Zusatzsperren entfernt.
- In der Projektumgebung Python 3.14.8 bestehen 57 Prüfungen. Echo, Lobbyfälle und die vollständige geskriptete lokale Partie sind separat aufgezeichnet.
- Offen bis M3: Lesepartnerschaft und Gegenlesen, Zweipersonenpartie an einer Tastatur, Echo/Handschlag mit Rollenwechsel sowie Lobbyversuch mit zwei fremden Clients.

## 13.10.2026 — Platzhalter in der Dokumentation

Beispieladressen und offene Einträge auf `<beispiel_art>` vereinheitlicht, unter anderem `<server_ip>`, `<tcp_port>`, `<lesepartner_name>` und `<beobachtung>`. Platzhalter in Shell-Befehlen sind in Anführungszeichen gesetzt. Die Protokollvorlage verwendet `<feld>`; tatsächliche JSON-Beispiele und Testausgaben bleiben erhalten.

## 13.10.2026 — Paket für Kursmeilenstein 3

Meilenstein_3.zip auf dem Desktop gespeichert. Enthalten sind die drei verlangten Programme, board.py als Serverabhängigkeit, das aktuelle Protokoll, Regelblatt, Aufgabenstellung, lokale Ausgaben der vier Fälle und die Schulnetz-Checkliste. 16 Dateien; Archivintegrität, unveränderte Quellen und Ausgaben, Startparameter und Dokumentlinks geprüft. Der Nachweis mit zwei fremden Client-Rechnern bleibt offen und ist im Paket gekennzeichnet.


## 27.10.2026 — Kursmeilenstein 4, GUI und Zustandsverteilung

- Drei neue Word-Unterlagen inhaltlich abgeglichen und unveränderte Textauszüge abgelegt. Die erwähnte Servervorbereitung ist in der vorhandenen Anleitung enthalten. Neue Kursaufgabe 4 und ältere Projektphasen unterschieden; vorhandene Regeln beibehalten.
- Aufgaben auf Anforderungsanalyse, Server/Transport, GUI, Protokoll und unabhängiges Review verteilt. DOCX-, Planungs-, TDD-, Debugging- und Review-Skills angewendet.
- Gefilterte vollständige Zustände nach join/place/shoot/reset und shotsAtSelf ergänzt. Private Ablehnungen, Geheimhaltung, sichere Metadatenlogs und harte Socketabbrüche geprüft. Protokoll auf 0.5 aktualisiert, dokumentierte ganze Partie automatisiert gegen server.handle geprüft.
- Schiffe-versenken-GUI mit zwei 10×10-Rastern, individuellen Platzierungsvorschlägen, Bearbeitung und Bestätigung, Schussknöpfen und Status erstellt. Empfang und Versand laufen über Worker/Queues; alle Widgets bleiben im Hauptthread.
- Gesamtlauf deckte Tk-Freigabe aus einem sterbenden Worker auf. Worker von Tk-Objekten entkoppelt und Freigabe der 11 Tk-Variablen im Hauptthread mit echtem Regressionstest abgesichert. Review-Hinweis zu synthetischen Leerzuständen korrigiert: Start/Abgang ändern nur Status bis zur tatsächlichen state-Nachricht.
- Auf Benutzerwunsch Tests nach Meilenstein geordnet, gemischte Echo-/lokale Werkzeugtests aufgeteilt und gemeinsamen Starter ergänzt. README, Setup, Spielanleitung, Architektur, Testablauf, Übergabe und Anforderungsabgleich aktualisiert.
- Benutzer möchte je nach Infrastruktur lokal oder verteilt spielen: Anleitungen erklären ein, zwei oder drei Geräte; lokal laufen Server und beide Clients über 127.0.0.1 ohne Internet/WLAN nach der Einrichtung.
- Prüfung auf macOS mit Python 3.14.10 / Tk 9.1: 81 Tests bestanden, keine Fehler/Skips; vollständige echte lokale GUI/TCP-Partie mit 33 gültigen Schüssen, beiden privaten Ablehnungen, Sieg, Fensterkreuz, Reset und Ersatz: PASS. M2-Starter zusätzlich aus /private/tmp: 26 bestanden. Rohlogs und echte Fensteraufnahmen unter docs/evidence/04_local/; Ergebnisbericht erklärt Art und Grenzen.
- Automatische Gesamtbildaufnahme war nicht verfügbar. Fehlgeschlagener Teilversuch getrennt erhalten; beide Originalfenster derselben angehaltenen Partie über native Fensteransicht aufgenommen, nicht nachgezeichnet. Gemeinsames Schulnetzbild und fremde IPs bleiben offen.
- Schulnetzversuch auf ausdrücklichen Benutzerwunsch für später vorbereitet. Ältere menschliche Nachweise/Gegenlesen weiter offen. Keine Commits, Staging-, Push-, PR- oder GitHub-Änderungen durchgeführt.


## 27.10.2026 — Abschlussreview und sichere Nachweise

Das abschliessende unabhängige Review fand im Nachweiswerkzeug zwei Probleme:
Der alte Standardausgabeordner konnte vorhandene Rohlogs überschreiben, und
PASS wurde vor dem letzten Serverlogcheck gespeichert. Beide Fälle zuerst
mit roten Regressionstests belegt, danach korrigiert. Vorhandene Ordner werden
jetzt vor dem Öffnen abgelehnt; Standard sind neue Zeitstempelordner, der
Gesamtstatus wird erst nach den letzten Prüfungen gespeichert.

Abschliessender Gesamtlauf: **84 Tests bestanden, keine Fehler/Skips**,
5.107 Sekunden. Danach vollständige echte GUI-/TCP-Partie erneut erfolgreich,
33 Schüsse mit Privatheit, Abbruch und Ersatz. Neue Rohlogs unter
`docs/evidence/04_final_run/`, letzter Testlog unter
`docs/evidence/04_local/tests_final.txt`; frühere erfolgreiche Ausgaben und
Originalbilder erhalten. Ein historischer Berichtslink wurde auf den neuen
Testpfad umgestellt; ursprüngliche Rohlogs und Ergebnisse sind unverändert.
Keine weiteren Codefehler im Abschlussreview. Keine Git-Änderungsoperationen.


## 27.10.2026 — Python-3-Aufrufe und Gitignore vor Benutzertest

Aktuelle macOS-/Linux-Anleitungen auf `python3` vereinheitlicht und die
Aktivierung der `.venv` in jedem Server-/Clientterminal ausdrücklich ergänzt.
Windows verwendet nach Aktivierung weiterhin `python`; Erstellung über
`py -3` ist getrennt beschrieben. Tatsächlich geprüft: ausserhalb der
Umgebung fehlt `python` auf diesem Mac; in der aktivierten Projektumgebung
starten sowohl `python` als auch `python3` Python 3.14.10.

`.venv/` und `venv/` waren bereits ausgeschlossen. Gitignore um weitere
Umgebungsnamen, Test-/Analyse-/Coverage-Caches, Buildausgaben, lokale
`.env`-Konfigurationen, temporäre Logs und OS-Dateien ergänzt. Beispielvorlagen
und Kursnachweise bleiben versionierbar. Mit `git check-ignore` wurden
18 Ausschlüsse und 7 erhaltene Quellen/Vorlagen/Nachweise geprüft; keine
virtuelle Umgebung ist bereits getrackt. Quellen und ursprüngliche Nachweise
erhalten, keine Staging-/Commit-/Push-Operationen.

Mit aktiviertem `python3` CLI-Hilfe von Server, GUI und Teststarter erfolgreich
aufgerufen; 26 Kern-/Lokale-Partie-Tests bestanden. Dies ist eine Anleitung- und
Ignore-Korrektur, kein neuer vollständiger GUI-/Netzwerkprüflauf. Der Benutzer
probiert das System anschliessend selbst aus und gibt Feedback.


## 27.10.2026 — Bewertung zuerst, Rollback und Erweiterung bis Endabgabe

Auf Benutzerauftrag zuerst den kompletten aktuellen Stand einschliesslich
Git-Metadaten, Venv und Originalunterlagen gesichert. Archiv:
`Gaming_Backups/Schiffe_versenken_vor_Bewertungsverbesserung_2026-10-27_17-33-09.zip`
auf dem Desktop, SHA256
`bdcaf95c318fd800da0d82bf8cfa3847664030b2fc5cc342440df4c7084a2129`.
2’532 Einträge isoliert wiederhergestellt, Datei-/Linkhashes, Git-Arbeitsstand
und Kernimport geprüft. Kein Rollback auf die laufende Arbeitskopie angewendet.

Rolle 1 las zuerst die Originalbewertung und leitete die Anforderungen ab.
Der Benutzer erweiterte den Umfang ausdrücklich auf spätere Meilensteine bis
Endabgabe. Die sechs ungewichteten M4-Kriterien und das originale
100-Punkte-Raster bleiben getrennt. Der Widerspruch 55 statt tabellarisch60
im Original wurde nicht in eine erfundene Gewichtung verwandelt.
Rolle 2 setzte um, Rolle 3 schrieb und bewertete Tests unabhängig. Die neuen
Abnahmetests waren vor Umsetzung rot; konkrete Subtest-Grenzfälle führten
anschliessend zu gezielten Reporter-Korrekturen.

Ergänzt: eigenes transparentes ImageGen-Schiff mit Herkunft, freigegebene
256-Pixel-Skalierung und 64-Pixel-Tk-Anzeige; persistente private Metadatenlogs
mit Zeitstempeln; strenger GUI-Testmodus und geschützte Einzeltest-JSON-Berichte;
Abgabe-ZIP-Werkzeug mit Manifest/Prüfsumme und offenem Personenstatus;
technische Berichtsmaterialien, Vorführleitfaden und separate Reflexionsdatei.
Der Benutzer will die persönliche Reflexion selbst schreiben; README markiert
sie als offen. Bildskalierung war als Entwurf voreilig vor Methodenfreigabe
angelaufen; nach transparenter Mitteilung gab der Benutzer sips ausdrücklich
frei. Die endgültige Ableitung wurde erneut aus dem erhaltenen Original erzeugt.

Unabhängiger neuer Stand: 101/101 Tests, 16 echte GUI-Prüfungen, keine Skips.
Sieben Pflichtangriffe und echte 33-Schuss-Konsolen-/GUI-Partien bestanden.
Ein erster Abgabekandidat wurde vollständig entpackt und aus frischer Venv
mit fremdem Arbeitsverzeichnis geprüft: 101/101, sieben Angriffe und ganze
Konsolenpartie erneut bestanden. Rohlogs, tatsächlicher automatisierter
Prüfer und Grenzen sind unter `docs/evidence/final_assessment_tests/` erfasst.
Endgültiges ZIP wird nach Abschluss der Dokumentation separat erneut geprüft.

Frühere Rohbelege und Spielkern zum Backup bytegleich erhalten. Keine
Staging-/Commit-/Push-/GitHub-Änderungen. Echte fremde Rechner, Gegenlesen,
Fremdclienttest, Livevorführung, persönliches Verständnis und eigene Reflexion
bleiben offen; automatisierte Agentenprüfung ersetzt diese Leistungen nicht.


## 29.10.2026 — Meerblaue Oberfläche, SVG-Flotte und Sprengung

Der Benutzer beauftragte eine grafische Überarbeitung mit SVG-Schiffen,
wählte „Maritim in Meerblau“ und ergänzte eine kleine Sprengung für den
Besitzer eines vollständig getroffenen Schiffes. Arbeit aufgeteilt in
Koordination/Integration, SVG-Entwicklung, Anforderungs-/Testprüfung,
unabhängiges Review und Dokumentationspflege. Vorhandene Änderungen erhalten;
keine Staging-, Commit-, Push- oder GitHub-Operationen.

Fünf SVG-Schiffstypen und ein Renderer für ihre Grundformen ergänzt.
Gleich grosse Canvas-Raster, grafische Schusszeichen, Schiffssilhouetten,
Flottenminiaturen, Zähler und Tastaturbedienung ersetzen die alte Feldoptik.
Das ursprüngliche ImageGen-PNG bleibt im Kopfbereich erhalten.
`ShipEffects` erkennt ausschliesslich einen neuen vollständig getroffenen
eigenen Schiffszustand und zeichnet für etwa 1,15 Sekunden Blitz,
Druckring, Funken und Rauch. Effekte abschaltbar, kein Wiederholen alter
Verluste; Reset, Disconnect und Schliessen entfernen alle Effekt-Callbacks.
Das Review fand einen Grenzfall beim schnellen Aus-/Einschalten: Stoppen
bewahrt jetzt die bestätigte Schiffshistorie. Ein Integrationstest deckt ihn.

Sieben Effektprüfungen wurden vor dem Effektemodul tatsächlich rot ausgeführt.
Abschliessend **114/114 Tests bestanden, davon 28 echte GUI-Prüfungen,
keine Fehler oder Skips**; zusätzlich vollständige lokale 33-Schuss-TCP-Partie
mit zwei Fenstern PASS. Oberfläche und Explosionsmoment tatsächlich per
Bildschirmaufnahme betrachtet. Nachweise und Grenzen:
[SVG-/Grafikprüfung](docs/evidence/06_graphics_2026-10-29/README.md).
Keine neuen Fremdrechner-/Personenleistungen oder Windows-/Linux-Prüfungen.

Auf Nachfrage den lokalen Schnellstart in README und Setup nochmals eindeutig
in Terminal 1 (Server), Terminal 2 (Alice) und Terminal 3 (Bob) gegliedert,
jeweils mit eigener Venv-Aktivierung und `127.0.0.1:5100`. Startreihenfolge,
Warteanzeige, Flottenversand in beiden Fenstern und Beenden beschrieben.
Dokumentierte Befehle gegen die CLI-Hilfe geprüft; der vollständige lokale
Spielnachweis ist oben verlinkt. Setup nennt jetzt auch die SVG-Dateien als
mitzuliefernde Assets.


## 03.11.2026 — Kursmeilenstein 5, Anforderungsabgleich und Vorlauf

Die Originalaufgabe `../Dokumente/auftrag_Meilenstein5` gelesen und als
bytegleiche Kopie unter `docs/assignments/05_assignment.txt` abgelegt
(SHA256 beider Dateien:
`0d89c071e7e6862a2148aeedca3227fe63f5056d09028251c265335920141e34`). Der
Projektverantwortliche bestätigte, die Tic-Tac-Toe-Lehrschritte auf das
bestehende Schiffe versenken zu übertragen. Der echte Zweirechnerlauf bleibt
auf seinen Wunsch verschoben. Die Abgabefrist im Original ist leer und wurde
nicht ergänzt. Die Zuordnung der Anforderungen und Nachweise steht in
`docs/status/05_requirements.md`.

Vor Änderungen bestand der tatsächliche lokale Tk/TCP-Vorlauf mit zwei
Fenstern, individueller Flotte, 33 Schüssen, Sieg/Niederlage, privaten
Ablehnungen, Abbruch und Ersatzbeitritt. Der Ergebnisbericht liegt unter
`docs/evidence/05_preflight_2026-11-03/result.json`. Das ist ein lokaler
technischer Beleg, kein Fremdrechnerlauf.

Die schriftlichen Vorhersagen stehen in `docs/evidence/05_predictions_2026-11-03.md`.
Ein tatsächlicher interaktiver Python-REPL-Versuch unter
`docs/evidence/05_final_2026-11-03/interactive_core.txt` folgte dieser
Vorhersage: 33 Züge, A gewinnt, falscher Spieler, Doppelbeschuss und
Schuss nach Ende werden ohne Zustandsänderung abgelehnt. Der Kernimport
zog laut `core_import.txt` keine der verbotenen Netz-, Thread- oder
GUI-Module nach. Zuvor gab es zwei geskriptete ergänzende Kernläufe.
Die erste geskriptete Ausgabe in
`docs/evidence/05_handspiel_2026-11-03.txt` endete nach 33 Zügen mit A als
Sieger; falsche Zugfolge, Doppelbeschuss und Schuss nach Ende wurden
abgelehnt, ohne den Zustand zu ändern. Die Vorhersage nannte für B bei Zug 2
`J10`, im ersten Lauf wurde `J1` verwendet; beides ergab Wasser. Ein zweiter
separater Handlauf unter
`docs/evidence/05_handspiel_2026-11-03_prediction_match.txt` verwendete das
vorhergesagte `J10` und erreichte denselben Sieg mit denselben Ablehnungen.
Beide Rohausgaben und die frühere Vorhersage bleiben erhalten.

Zwei zuvor beschriebene absichtliche Kernfehler wurden ausschliesslich in
isolierten Kopien ausgeführt. Ohne Versenkungserkennung wurde genau der
vorhergesagte Test rot. Ohne Spielerwechsel wurden die sieben vorhergesagten
Tests rot oder brachen wegen der falschen Zugfolge ab. Mutationsübersicht
und rohe `unittest`-Ausgaben liegen unter
`docs/evidence/05_mutation_2026-11-03/`. Danach bestand der unveränderte
Projektkern mit dem Originalbefehl 19/19 Tests; der erste vollständige
Prüflauf bestand 137/137 Tests einschliesslich 29 echter GUI-Prüfungen
ohne Fehler oder Skips. Nach der Korrektur des Bildwerkzeugs bestand der
abschliessende strenge Lauf 139/139 Tests, darunter 29 echte GUI-Prüfungen,
ohne Fehler oder Skips. Beide Ausgaben bleiben getrennt unter
`docs/evidence/05_final_2026-11-03/` erhalten; `full_final.json` war der
Abschlussstand vor der nachfolgenden Paketstatuskorrektur.

Für die beauftragte Endfolge wurde der Nachrichtenkatalog als Version 0.6
aktualisiert: Nach siegreichem `result` folgen die individuellen Endzustände
an beide und dann `gameOver` an beide. Die automatischen Server- und
Protokollbeispieltests der grünen Gesamtsuite vergleichen diese Reihenfolge
mit dem Code. Die alten 0.5-Nachweise bleiben mit ihrer damaligen
Reihenfolge erhalten.

Der erste M5-GUI-Lauf (lokal erhalten unter
`logs/diagnostics/05_gui_final_2026-11-03/`) hat
eine vollständige lokale Partie mit Sieg/Niederlage und ein visuell
geprüftes gemeinsames Endbild geliefert. Das Bild ist breit und enthält
zwischen den beiden Tk-Fenstern weitere Desktopfenster. Ein zweiter
kompakter Lauf (lokal erhalten unter
`logs/diagnostics/05_gui_final_compact_2026-11-03/`)
bestand die Spielablaufprüfung einschliesslich eines echten Klicks nach
Spielende mit privater Ablehnung. Seine vermeintliche Endbilddatei zeigte
jedoch Discord statt Tk und zählt **nicht** als Bildnachweis. Sie wurde
bytegleich nach `logs/diagnostics/05_gui_final_compact_2026-11-03_invalid_discord.png`
verschoben, wo sie lokal ignoriert und nicht ins Abgabepaket aufgenommen
wird. Die unveränderte Ergebnisdatei verweist noch auf ihren früheren
Bildpfad und meldete für diesen Bildpunkt voreilig PASS. Dieser Teilbefund
bleibt als erkannter Werkzeugfehler dokumentiert. Die erste breite Aufnahme
enthält weitere Desktop-/Chat-Inhalte und wird vor einer Abgabe gesondert
beurteilt.

Nach Korrektur der Bildaufnahme bestand der erneute lokale Lauf unter
`docs/evidence/05_gui_verified_2026-11-03/`: 33 Schüsse, Alice gewinnt,
Bob verliert, echter Zielbutton-Klick nach Ende mit privater
`WRONG_PHASE`-Ablehnung ohne Zustandsänderung und weiterlaufender Server.
Das neue gemeinsame Endbild wurde tatsächlich angesehen; beide Tk-Fenster
stehen eng nebeneinander mit lesbarem Sieg-/Niederlagestatus. Es ist der
primäre M5-Bildnachweis. Der fehlerhafte Zwischenlauf bleibt anhand seiner
unveränderten Ergebnisdatei und des lokal isolierten Fehlbildes als
Diagnose nachvollziehbar, jedoch nicht als gültiger Bildbeleg.

Ein neuer lokaler M5-Paketkandidat wurde als
`dist/Schiffe_versenken_Meilenstein_5_2026-11-03.zip` erstellt. Die daneben
abgelegte unabhängige Prüfung verglich ZIP-SHA256, alle 234 Manifestdateien
und die geforderten M5-Dateien. Aus dem frisch entpackten Paket bestanden
139/139 Tests, davon 29 echte GUI-Prüfungen, sowie der Originalbefehl für
`test_spiel.py`. Die Bestätigung steht unter
`dist/Schiffe_versenken_Meilenstein_5_2026-11-03.verification/result.json`.

Zum Schluss wurde der Abgabestatus im Paketwerkzeug an M5 angepasst: Er
nennt den weiterhin offenen Zweirechnerlauf mit Server-Terminalausgabe
und verweist auf `docs/status/05_requirements.md`. Der zugehörige Pakettest
war vor der Änderung rot; danach bestanden beide M8-Pakettests. Nach dieser
Korrektur bestand der strenge Release-Gesamtlauf erneut 139/139 Tests,
darunter 29 echte GUI-Prüfungen, ohne Fehler oder Skips. Die massgebenden
Ausgaben sind `docs/evidence/05_final_2026-11-03/full_release.json` und
`full_release.txt`; `full_final` und frühere Reports bleiben als tatsächlich
ausgeführte Zwischenstände erhalten.


## 03.11.2026 — Zwei Startvarianten, lokaler Zwischenstand

Der neue Benutzerauftrag verlangt eine klar unterscheidbare localhost-
Variante und eine für zwei Rechner vorbereitete Variante. Zwei getrennte
Startanleitungen beschreiben jeweils Repo- und Profil-ZIP-Befehle für
macOS/Linux und Windows. Der gemeinsame Launcher nimmt beide Clientnamen
aus `--name`; im Zwei-Rechner-Profil braucht Bob zusätzlich die echte
IPv4-Adresse von Rechner 1. Die README führt zu beiden Anleitungen, und
`docs/status/two_versions.md` hält Nachweise und offene Punkte getrennt.

Die CLI-Hilfen beider neuen Profil-Einstiege wurden gelesen. Der neue
strenge Gesamtlauf unter `docs/evidence/two_versions_2026-11-03/full.json`
bestand 153/153 Tests, darunter 29 echte GUI-Prüfungen, ohne Fehler oder
Skips. Ein tatsächlicher lokaler Start über
`varianten/localhost/start.py` startete Server und zwei Tk-Clientprozesse;
das Serverterminal unter
`docs/evidence/two_versions_2026-11-03/localhost_startup_server.txt`
zeigt zwei Beitritte und `gameStart`. Die beiden Clientausgaben liegen
daneben. Dieser Start belegt noch keine vollständige Partie über den neuen
Einstieg. Der echte Zweirechnerlauf mit realen Geräten und Serverterminal
bleibt wie vereinbart offen. Die beiden Profil-ZIPs und ihre unabhängige
Entpack-/Startprüfung sind zu diesem Zeitpunkt noch ausstehend.

Zusätzlich startete der Zwei-Rechner-Profil-Wrapper lokal einen LAN-bindenden
Server; der korrigierte Prüfablauf las die TCP-Antwort als JSON und bestätigte
`join`/`welcome`. Der Rohlog liegt unter
`docs/evidence/two_versions_2026-11-03/lan_server_local_smoke_validated.txt`.
Der erste Versuch unter `lan_server_local_smoke.txt` zeigte dieselbe gültige
Antwort, wurde aber wegen eines whitespace-empfindlichen Stringvergleichs
im Prüfskript fälschlich als Fehler gemeldet und bleibt als Fehlversuch
erhalten. `lan_invalid_ip.json` hält drei vor dem Netzwerkversuch
abgewiesene Bob-IP-Aufrufe fest. Alle diese Versuche liefen auf einem Gerät;
sie belegen keinen echten Zweirechnerbetrieb.

Danach wurden zwei Profil-ZIP-Kandidaten separat erstellt und unabhängig
entpackt geprüft. Die Ergebnisdateien unter
`dist/Schiffe_versenken_localhost_2026-11-03_candidate.verification/result.json`
und
`dist/Schiffe_versenken_zwei_rechner_2026-11-03_candidate.verification/result.json`
melden jeweils PASS: ZIP-Hash und 257 Manifestdateien korrekt, 153/153 Tests
aus dem entpackten Paket, 29 echte GUI-Prüfungen, Kerntest und
`start.py --help`. Zusätzliche lokale Startprüfungen aus beiden entpackten
Paketen liegen als `startup_result.json` daneben: localhost mit Server und
zwei Tk-Clients bis `gameStart`, LAN-Serverprofil mit TCP-`welcome` auf
demselben Gerät. Dies ist weder eine vollständige Partie über die neuen
Pakete noch ein Fremdrechnernachweis. Der endgültige Paketbau folgt erst
nach diesem Kandidatenstand.

Anschliessend bestand unter
`docs/evidence/two_versions_2026-11-03/localhost_full_profile_game/result.json`
eine vollständige lokale TCP-Partie mit 33 Schüssen und zwei echten
Tk-Fenstern. Der Server wurde dabei über `varianten/localhost/start.py`
gestartet. Der Lauf prüfte auch private Ablehnungen ohne Zustandsänderung,
den echten Klick nach Spielende, weiterlaufenden Server, Reset und
Ersatzbeitritt. Die beiden Clientwrapper waren in einem separaten
Startversuch bis `gameStart` geprüft, nicht in dieser vollständigen Partie.
Ein neuer strenger Gesamtlauf unter
`docs/evidence/two_versions_2026-11-03/full_final.json` bestand danach
155/155 Tests, davon 29 echte GUI-Prüfungen, ohne Fehler oder Skips. Der
erste Profil-Gesamtlauf mit 153/153 bleibt als historischer Zwischenstand.
Die zuvor gebauten Kandidatenarchive bleiben ebenfalls historisch.

Die endgültigen Profile wurden als
`dist/Schiffe_versenken_localhost_2026-11-03_freigabe.zip` und
`dist/Schiffe_versenken_zwei_rechner_2026-11-03_freigabe.zip` gebaut.
Jedes Archiv wurde separat entpackt; SHA256 und alle Manifestdateien,
`start.py --help`, direkter Kerntest und die strenge Suite bestanden mit
155/155 Tests, darunter 29 echte GUI-Prüfungen. Die Berichte liegen jeweils
im gleichnamigen `.verification/`-Verzeichnis neben dem ZIP. Aus dem
entpackten Localhost-Paket bestand eine ganze lokale Tk/TCP-Partie mit
33 Schüssen und Serverstart über den Profilwrapper. Aus dem entpackten
Zwei-Rechner-Paket bestand ein lokaler TCP-Beitritt am Serverprofil.
Dieser letzte Test fand auf einem einzigen Gerät statt. Der echte
Zweirechnerlauf samt Server-Terminalbeleg bleibt wie vereinbart offen.

Bei einem vorangehenden Localhost-Archiv mit Suffix `_release` fiel ein
GUI-Tastaturtest im ersten Paket-Gesamtlauf einmal aus: 154/155, weil drei
statt zwei Aufrufe registriert wurden, jeweils auf dem Tk-Hauptthread.
Ein fokussierter Test und ein unveränderter vollständiger Wiederholungslauf
bestanden (155/155). Die Ursache des einmaligen zusätzlichen Aufrufs ist
unbekannt. `full.json` und `full_retry.json` im zugehörigen
`.verification/`-Ordner bleiben erhalten; die Vergleichsliste nennt dies
als Beobachtung zur Testrobustheit.
