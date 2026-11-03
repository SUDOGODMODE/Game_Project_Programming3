# Zwei Betriebsarten und zwei Ausgabepakete — Entwurf

Stand: 03.11.2026. Grundlage ist der neue Nutzerwunsch nach einer klaren
localhost-Version und einer Version für zwei Rechner sowie die unveränderte
Kursaufgabe [Meilenstein 5](../../assignments/05_assignment.txt). Die hier
beschriebene Form **zwei Startprofile und zwei eigenständige ZIP-Pakete aus
einer Codebasis** wurde dem Nutzer als Annahme mitgeteilt; eine Korrektur
durch ihn geht vor. Der echte Zweirechnerlauf bleibt bis zur tatsächlichen
Durchführung offen.

## Ziel und Struktur

- Ein Spielkern, ein Server, ein GUI-Client und ein Protokoll bleiben unter
  `src/` beziehungsweise `PROTOKOLL.md`. Beide Betriebsarten nutzen
  dieselben Regeln, Nachrichten und Bilder. Es entstehen keine zwei
  unabhängig gepflegten Kopien des Spielcodes.
- Das Repository bietet zwei klar benannte Einstiege unter
  `varianten/localhost/` und `varianten/zwei_rechner/`. Jeder Einstieg führt nur die
  zu seiner Betriebsart passenden Startbefehle aus oder gibt sie aus;
  Adressen werden nicht stillschweigend aus dem anderen Profil übernommen.
- Zwei getrennte Anleitungen unter `varianten/localhost/START.md` und
  `varianten/zwei_rechner/START.md` erklären Einrichtung, Geräte-/Terminal-
  Rollen, Startreihenfolge, Beenden und Fehlersuche. Das Wurzel-`README.md`
  dient als Auswahlseite und verlinkt beide. `docs/guides/setup.md` bleibt
  konsistent und verweist für den konkreten Start auf diese beiden.
- Ein reproduzierbarer Paketbau erstellt zwei neue, unterschiedlich benannte
  ZIPs: `Schiffe_versenken_localhost_<zeitstempel>.zip` und
  `Schiffe_versenken_zwei_rechner_<zeitstempel>.zip`. Jedes ZIP ist für seine
  Betriebsart eigenständig nutzbar und enthält `src/`, `bilder/`, die eigene
  Startanleitung, die nötigen Startdateien, `README.md`, `REGELN.md` und
  `PROTOKOLL.md`. Es verweist zur Laufzeit auf keine Datei aus dem anderen
  ZIP oder dem ursprünglichen Repository. Für Nachvollziehbarkeit gehören
  Tests und M5-Nachweise dazu; bestehende `.git`-, `.venv`-, Laufzeitlog-,
  Cache- und Diagnose-Ausschlüsse bleiben wirksam. Vorhandene ZIPs und
  Rohbelege werden nicht überschrieben.

## Startverhalten

| Profil | Ort | Server-Bind | Client-Ziel |
|---|---|---|---|
| localhost | ein Gerät, drei Prozesse | `127.0.0.1:5100` | Alice und Bob jeweils `127.0.0.1:5100` |
| zwei Rechner | Gerät 1: Server und Alice; Gerät 2: Bob | `0.0.0.0:5100` auf Gerät 1 | Alice `127.0.0.1:5100`; Bob `<server_ip>:5100` |

Im Zwei-Rechner-Profil muss Bob die **tatsächliche IPv4-Adresse von Gerät 1**
ausdrücklich eingeben; es gibt keinen erfundenen oder fest eingebauten
Wert. Eine leere Angabe, `127.0.0.1` und `0.0.0.0` sind dort kein gültiges
Ziel. `0.0.0.0` dient nur als Server-Bindeadresse. Der Server vergibt Slot
`A` an den ersten beigetretenen Client; die Anleitung startet deshalb Alice
vor Bob, wenn Alice Spieler A sein soll. Beide Geräte benötigen Python 3.12+
mit tkinter und Zugriff auf die mitgelieferten Bilder. Der Startweg muss
unter macOS/Linux mit `python3` und unter Windows nach Aktivierung der
virtuellen Umgebung mit `python` beschrieben sein; Windows wird dadurch
noch nicht als tatsächlich geprüft bezeichnet.

## Abnahme und Nachweisgrenzen

- Ein lokaler Start belegt durch die tatsächlich verwendete Bindeadresse,
  dass der Server nur auf Loopback lauscht. Beide lokalen Clients können
  eine vollständige Partie spielen.
- Das Zwei-Rechner-Paket lässt sich unabhängig vom localhost-ZIP entpacken
  und starten; Server- und Clientbefehle verwenden die oben genannten
  Adressen. Ein fehlendes oder ungültiges `<server_ip>` für Bob wird vor dem
  Verbindungsversuch verständlich abgelehnt. Lokale Prüfungen können diese
  Startlogik und einen TCP-Lauf mit zwei Prozessen auf demselben Rechner
  belegen, aber keinen echten Zweirechnerlauf.
- Beide ZIPs werden unabhängig auf Dateien, Manifest/Prüfsumme und
  Startbarkeit geprüft. Die fünf in M5 verlangten Quellen
  `spiel.py`, `test_spiel.py`, `netz.py`, `server.py`, `client_gui.py` und das
  aktuelle Protokoll mit Endnachricht sind enthalten. Die bisherigen M5-
  Kern-/GUI-Tests bleiben grün.
- Ein tatsächlicher M5-Zweirechnerbeleg erfordert später einen Serverlauf
  auf Gerät 1 mit Terminalausgabe und eine vollständige Partie mit Bob auf
  Gerät 2. Datum, Geräte, tatsächliche IPs und rohe Ausgaben werden erst
  nach Durchführung dokumentiert. ZIPs, Startanleitungen und ein lokaler
  Test werden nicht als dieser Beleg ausgegeben.
- Status und Pakettexte nennen weiterhin offen: den M5-Zweirechnerlauf,
  die älteren Dreirechner-/Fremdclient- und Personenleistungen sowie die
  persönliche Reflexion. Die LAN-Verbindung bleibt das vorhandene
  TCP-Protokoll ohne Authentifizierung oder Verschlüsselung und ist für ein
  vertrauenswürdiges Unterrichtsnetz vorgesehen.

## Offene externe Angaben

Die zwei Profile unter `varianten/` und zwei vollständige ZIPs aus einer
Codebasis sind die Arbeitsentscheidung. Eine spätere ausdrückliche
Nutzerkorrektur geht vor. Der tatsächliche Termin, die Geräte und die
Server-IP für den Zweirechnerlauf sind unbekannt und werden nicht ergänzt.
