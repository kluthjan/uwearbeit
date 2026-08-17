# Präsentation: Einrichtung eines zentralen Dateiservers
## Müller & Partner GmbH – Projektarbeit 3 (Gruppe 3)
**Dauer:** 8–12 Minuten | **Team:** Jan Kluth, Marian, Mathias & Marco  
**Netzwerk:** `172.16.30.0/24` | **Server IP:** `172.16.30.10`

---

## Agenda & Rollenverteilung im Team

| Sprecher | Themenbereich | Folien |
| :--- | :--- | :---: |
| **Jan** | 1. Ausgangssituation, Aufgabenstellung & Netzplan | Folien 1–3 |
| **Marian** | 2. Server-Architektur, Samba & Berechtigungsmatrix | Folien 4–6 |
| **Mathias** | 3. Client-Anbindung (Windows/Linux) & Teststrategie | Folien 7–9 |
| **Marco** | 4. Wireshark-Analyse, Troubleshooting & Unternehmens-Ausblick | Folien 10–12 |

---

## TEIL 1: JAN (Folien 1–3)

### Folie 1: Ausgangssituation & Kundenauftrag
- **Unternehmen:** Müller & Partner GmbH
- **Problem:** Lokale Datenspeicherung auf Desktops $\rightarrow$ Keine zentrale Sicherung, Risiko von Datenverlust, keine Zugriffsbeschränkungen für vertrauliche Dokumente.
- **Auftrag:** Aufbau einer zentralen, sicheren Dateiserver-Infrastruktur mit abgestuften Zugriffsrechten.

*Sprechernotizen Jan:* "Guten Tag zusammen. Ich starte mit unserer Aufgabenstellung. Die Müller & Partner GmbH hatte bisher das Problem, dass jeder Mitarbeiter Dateien nur lokal speicherte. Unser Auftrag war es, einen zentralen Dateiserver aufzubauen..."

---

### Folie 2: Netzplan & IP-Adresskonzept (Gruppe 3)
- **Virtuelles Netzwerk:** VirtualBox *Internal Network* (`MuelleNetz`)
- **Subnetz:** `172.16.30.0/24` (Subnetzmaske `255.255.255.0`)
- **Server-VM:** `172.16.30.10` (Ubuntu Server / Samba Dateiserver)
- **Client-VM 1:** `172.16.30.100` (Windows 10/11 Workstation)
- **Client-VM 2:** `172.16.30.101` (Linux Client / Zusatzaufgabe)

*Sprechernotizen Jan:* "Für das Netzwerk haben wir uns für das Subnetz 172.16.30.0/24 entschieden. Der Server liegt statisch auf der IP .10, unsere Windows- und Linux-Clients verbinden sich isoliert über ein internes VirtualBox-Netzwerk..."

---

### Folie 3: Meilensteine nach dem Wasserfallmodell
1. **Initiierung & Planung:** Ist-Analyse, Soll-Konzept, Rollen-Matrix.
2. **Durchführung:** Server-Setup, Samba-Installation, POSIX-Dateirechte.
3. **Abschluss:** Wireshark-Analyse, automatisierte Tests & Projektdokumentation.

*Sprechernotizen Jan:* "Wir haben das Projekt strukturiert nach dem klassischen Wasserfallmodell umgesetzt. Nun übergebe ich an Marian für die technische Umsetzung auf dem Server."

---

## TEIL 2: MARIAN (Folien 4–6)

### Folie 4: Benutzer- & Gruppenstruktur
- **Benutzer:** `anna`, `bernd`, `chef`
- **Gruppen:** `mitarbeiter`, `leitung`
- **Zuordnung:**
  - `mitarbeiter`: anna, bernd, chef
  - `leitung`: chef

*Sprechernotizen Marian:* "Vielen Dank Jan. Auf dem Server haben wir zunächst das Gruppen- und Nutzerkonzept umgesetzt. Der Benutzer Chef ist Mitglied in beiden Gruppen..."

---

### Folie 5: Freigaben & Berechtigungsmatrix
- **`public` (`/srv/samba/public`):** Lesen & Schreiben für alle Mitarbeiter und Leitung (`chmod 2777`).
- **`mitarbeiter` (`/srv/samba/mitarbeiter`):** Lesen & Schreiben für Mitarbeiter und Leitung (`chmod 2770`).
- **`leitung` (`/srv/samba/leitung`):** Lesen & Schreiben **exklusiv** für Geschäftsleitung `chef` (`chmod 2770`).

*Sprechernotizen Marian:* "Die Verzeichnisrechte haben wir auf POSIX-Ebene mit dem SGID-Bit 2770 geschützt. Dadurch erben neu angelegte Dateien automatisch die korrekten Gruppenrechte..."

---

### Folie 6: Samba-Hauptkonfiguration (`smb.conf`)
- Einsatz von `security = user` und `tdbsam` Passwort-Datenbank.
- Konfiguration der Shares mit `valid users = @mitarbeiter, @leitung` und `force group`.
- Automatischer Syntax-Check mittels `sudo testparm`.

*Sprechernotizen Marian:* "In der smb.conf regelt Samba die Freigaben. Damit die Rechte greifen, müssen Samba-Filter und POSIX-Dateirechte handinhand gehen. Ich gebe weiter an Mathias für die Client-Anbindung."

---

## TEIL 3: MATHIAS (Folien 7–9)

### Folie 7: Client-Einrichtung unter Windows & Linux
- **Windows Client (`172.16.30.100`):**
  - Netzwerkarte im internen Netzwerk `MuelleNetz`.
  - Netzlaufwerke einbinden via Explorer (`\\172.16.30.10`) oder CMD (`net use`).
- **Linux Client (Zusatzaufgabe `172.16.30.101`):**
  - Mounten via `cifs-utils` und `smbclient`.

*Sprechernotizen Mathias:* "Danke Marian. Auf der Client-Seite haben wir die Netzwerkkarten auf das interne Netzwerk konfiguriert. Unter Windows erfolgt das Einbinden bequem über 'net use Z: \\172.16.30.10\public'..."

---

### Folie 8: Teststrategie & Testprotokoll
- **Positivtests:** `anna` greift erfolgreich auf `public` und `mitarbeiter` zu. `chef` greift auf alle drei Ordner zu.
- **Negativtest:** `anna` versucht Zugriff auf `leitung` $\rightarrow$ **NT_STATUS_ACCESS_DENIED** (Korrekt blockiert!).
- **Automatisierung:** Skript `run_tests.sh` führt alle Tests automatisch durch.

*Sprechernotizen Mathias:* "Besonders wichtig war uns das Testen verweigerter Zugriffe. Anna und Bernd werden beim Versuch, den Leitungsordner zu öffnen, sofort vom Server abgeblockt..."

---

### Folie 9: Neustart- & Stabilitätstest
- **Test:** Neustart des Serverdienste (`sudo systemctl restart smbd`).
- **Ergebnis:** Freigaben sind sofort wieder erreichbar. Keine Datenverluste.

*Sprechernotizen Mathias:* "Auch ein Serverneustart wurde getestet. Die Systemd-Services starten automatisch neu. Ich übergebe an Marco für die Netzwerkanalyse und das Fazit."

---

## TEIL 4: MARCO (Folien 10–12)

### Folie 10: Wireshark-Netzwerkanalyse (Port 445)
- TCP 3-Way-Handshake (`SYN` $\rightarrow$ `SYN-ACK` $\rightarrow$ `ACK`).
- SMB2/SMB3 Negotiate Protocol & NTLMv2 Session Setup.
- Sichtbarkeit der Datenpakete auf Port 445.

*Sprechernotizen Marco:* "Danke Mathias. Mit Wireshark haben wir den Datenverkehr analysiert. Man sieht deutlich den Verbindungsaufbau über TCP-Port 445 und das SMB-Protokoll..."

---

### Folie 11: Fehleranalyse & aufgetretene Probleme
- **Problem:** Windows meldete *Systemfehler 53* (Netzwerkpfad nicht gefunden).
- **Ursache:** Inkompatibles Subnetz / Firewall sperrte Port 445.
- **Lösung:** Freischaltung in UFW (`sudo ufw allow samba`) und konsistente IP-Vergabe (`172.16.30.0/24`).

*Sprechernotizen Marco:* "Ein wesentliches Problem bei den Tests war eine blockierende Firewall auf dem Server. Durch die Freischaltung des Samba-Dienstes in der UFW konnten wir den Fehler schnell beheben..."

---

### Folie 12: Ausblick für echte Unternehmen & Fazit
- **Empfehlung für die Praxis:**
  1. Integration in ein **Active Directory / LDAP** (Samba AD DC).
  2. Erzwingen von **SMB-Verschlüsselung** (`smb encrypt = required`).
  3. Automatisierte Snapshots & regelmäßige Auslagerung von Backups.
- **Fazit:** Das Ziel der Projektarbeit 3 wurde zu 100% erreicht!

*Sprechernotizen Marco:* "Zusammenfassend lässt sich sagen: Für eine echte Firma würden wir ein Active Directory und verschlüsselte Übertragung nachrüsten. Unser Testsystem funktioniert einwandfrei. Vielen Dank für eure Aufmerksamkeit – wir freuen uns auf eure Fragen!"
