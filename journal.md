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
