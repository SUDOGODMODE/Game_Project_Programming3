# Feature Specification: Kursmeilenstein 6 – Testen und abschliessen

**Feature Branch**: `feature/testability-junior-clarity`  
**Created**: 2026-11-10  
**Status**: In Arbeit  
**Input**: Original `../Dokumente/Auftrag_Meilenstein6.docx`; Benutzerbestätigung, alle Lernziele auf das bestehende Schiffe versenken zu übertragen.

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Spiel über echte Verbindungen prüfen (Priority: P1)

Als Projektverantwortlicher kann ich die Strecke vom Spielkern über Server und Nachrichten bis zum Client automatisch prüfen. Jeder Fall beginnt mit einer frischen Partie und funktioniert auch allein.

**Why this priority**: Reine Regeltests bemerken fehlende Servermeldungen nicht.

**Independent Test**: Netztests werden zweimal gemeinsam und einzeln gestartet; jeder Fall verbindet sich mit einem eigenen Serverprozess.

**Acceptance Scenarios**:

1. Nach Beitritt und Platzierung erhalten beide Spieler ungefragt ihren eigenen Zustand.
2. Eine vollständige Partie führt nach dem letzten Schuss zu den Endmeldungen für beide.
3. Jede dokumentierte Ablehnung geht nur an den Verursacher und verändert den Spielstand nicht.
4. Nach hartem Verbindungsabbruch bleibt der Server erreichbar und vergibt den freien Platz erneut.

### User Story 2 – Aussagekraft der Tests belegen (Priority: P1)

Als Projektverantwortlicher sehe ich an absichtlich eingebauten Fehlern in isolierten Kopien, welche Netztests rot werden, und kann erklären, warum die Regeltests dabei grün bleiben.

**Independent Test**: Rot- und Grünläufe mit unverändertem Projektstand vergleichen.

### User Story 3 – Abgabe selbständig starten (Priority: P2)

Eine andere Person kann das Archiv entpacken, die Anleitung befolgen und Tests ohne manuell gestarteten Server ausführen.

**Independent Test**: Archiv in einen frischen Ordner entpacken, dokumentierte Test- und Startbefehle dort ausführen.

### Edge Cases

- Schiffe versenken hat kein Unentschieden; der Unterrichtsfall entfällt fachlich.
- Ein unbeschossenes Gegnerschiff bleibt auch nach Zustandsmeldungen verborgen.
- Der beschriebene fortlaufende Zahlenzähler existiert im aktuellen Server nicht; der Ersatzbeitritt ist ein Regressionstest, kein neu gefundener Produktionsfehler.
- Ein bereits belegter Standardport darf eigenständige Testprozesse nicht stören.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Der Server MUSS einen Testport über `PORT` akzeptieren und ohne Vorgabe auf Port 5000 starten; die bestehende CLI-Option bleibt gültig.
- **FR-002**: Ein fensterloser Testclient MUSS Nachrichten über das bestehende Protokoll senden, begrenzt auf Antworten warten und unerwartete Antworten sichtbar machen.
- **FR-003**: Jeder neue Netztest MUSS einen eigenen Serverprozess und echte TCP-Verbindungen verwenden und ihn auch bei Fehlern beenden.
- **FR-004**: Die neue Suite MUSS Beitritt, Zustands-Push, Platzierung, Schuss, Partieende, Abbruch und Ersatzbeitritt prüfen.
- **FR-005**: Alle elf in `PROTOKOLL.md` dokumentierten Fehlercodes MÜSSEN durch echte Verbindungen geprüft werden; Ablehnungen bleiben privat und verändern keinen Zustand.
- **FR-006**: Mindestens eine isolierte absichtliche Serveränderung MUSS einen passenden Netztest nachweislich rot machen; die Projektversion bleibt danach grün.
- **FR-007**: README und Abgabenachweis MÜSSEN Start, Test, Grenzen, tatsächliche Fehlerfunde und die Abweichung von der Tic-Tac-Toe-Zahl erklären.
- **FR-008**: Originalaufträge, Rohbelege und vorhandene Änderungen bleiben erhalten; es erfolgen keine Commits oder Pushes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Der einzeln gestartete Netztest und die gesamte Netzsuite bestehen wiederholt ohne manuellen Serverstart.
- **SC-002**: Die Suite deckt alle elf dokumentierten Ablehnungen und eine vollständig beendete Partie ab.
- **SC-003**: Mindestens eine gezielte Fehlerkopie lässt einen vorher grünen Netztest fehlschlagen.
- **SC-004**: Der dokumentierte Testbefehl und der Spielstart funktionieren aus einem frisch entpackten Archiv.

## Assumptions

- Die bestehenden 19 Regeltests bleiben bestehen; die Lehrzahl 12 und damit die Gesamtzahl 31 sind kein Ziel für dieses andere Spiel.
- `shoot`/`error`/Slot A-B entsprechen fachlich `move`/`rejected`/Spielernummer 1-2 im Unterrichtsbeispiel.
- Bestehende Startprofile, Regeln, Protokoll und GUI werden für M6 nicht umgestaltet.
