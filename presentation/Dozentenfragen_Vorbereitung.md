# Vorbereitung auf das Dozentengespräch (Fragen & Antworten)
## Projektarbeit 3 – Dateiserver (Gruppe 3)
**Team:** Jan, Marian, Mathias & Marco

---

## 1. Übersicht

Nach der 8-12 minütigen Präsentation stellt der Dozent ca. 5 Minuten lang Fachfragen zum Thema Dateiserver, Netzwerke und Samba. Hier findet ihr die wahrscheinlichsten Fragen inklusive der perfekten Antworten!

---

## 2. Fragen & Antworten Katalog

### Frage 1: "Warum haben Sie Samba und nicht NFS für das Projekt gewählt?"
- **Antwort:** "Da unser Hauptclient ein Windows-System ist, ist SMB/Samba der native Standard für Microsoft Windows. NFS (Network File System) stammt aus der Unix/Linux-Welt und erfordert auf Windows-Clients zusätzliche Konfiguration. Samba bietet zudem eine hervorragende Rechteverwaltung, die direkt mit Windows kompatibel ist."

---

### Frage 2: "Über welche Ports und Protokolle kommuniziert Samba?"
- **Antwort:** "Samba nutzt hauptsächlich **TCP-Port 445** für das moderne SMB-Protokoll (Direct Hosted SMB over TCP/IP). Ältere NetBIOS-Dienste nutzen zusätzlich **UDP-Ports 137, 138** (Namensauflösung/Datagramme) und **TCP-Port 139** (Session Service)."

---

### Frage 3: "Was passiert, wenn auf Linux-Ebene Schreibrechte bestehen (`chmod 777`), aber in der `smb.conf` 'read only = yes' eingestellt ist?"
- **Antwort:** "Der Zugriff wird **verweigert** (bzw. die Datei kann nur gelesen werden). Es gilt immer das **restriktivste (strengste) Recht**. Sowohl Samba als auch das POSIX-Dateisystem müssen den Zugriff erlauben."

---

### Frage 4: "Wozu dient das SGID-Bit (`chmod 2770`), das Sie auf die Ordner angewendet haben?"
- **Antwort:** "Das SGID-Bit (Set Group ID) sorgt dafür, dass neu erstellte Dateien und Unterordner automatisch die **Gruppe des übergeordneten Ordners** erben (z.B. `mitarbeiter`) und nicht die Primärgruppe des jeweiligen Nutzers. Das ist essenziell für Gruppenfreigaben."

---

### Frage 5: "Was ist der Unterschied zwischen NTLMv2 und Kerberos?"
- **Antwort:** "NTLMv2 ist ein Challenge-Response-Authentifizierungsverfahren für Standalone-Server. Kerberos hingegen ist der Standard in Active Directory Domänen, der mit fälschungssicheren Tickets (Ticket Granting Tickets) arbeitet und deutlich sicherer gegen Replay-Angriffe ist."

---

### Frage 6: "Wie kann man den SMB-Datenverkehr vor Abhören im Netzwerk schützen?"
- **Antwort:** "Durch das Erzwingen von SMB-Verschlüsselung (SMB Encryption). In Samba aktiviert man dies global oder pro Freigabe mit `smb encrypt = required`. Dadurch wird der gesamte Nutzdatenverkehr ab SMB3 AES-verschlüsselt."

---

### Frage 7: "Wie haben Sie die Freigaben getestet?"
- **Antwort:** "Wir haben sowohl Positivtests als auch Negativtests durchgeführt: Ein Positivtest prüft, ob `anna` auf `public` zugreifen darf. Ein Negativtest prüft, ob `anna` beim Zugriff auf `leitung` die Fehlermeldung `NT_STATUS_ACCESS_DENIED` erhält."
