# Lernhilfe & Erklärung: Dateiserver & Samba von A bis Z
## Für Jan, Marian, Mathias und Marco (Gruppe 3)

---

## 1. Einleitung & Ziel dieser Lernhilfe

Liebes Team! Dieses Dokument ist euer persönlicher **Spickzettel & Lern-Guide**. Hier erfahrt ihr in einfacher, klarer Sprache ohne unverständliches Fachchinesisch, wie unser Samba-Dateiserver funktioniert, warum wir bestimmte Befehle nutzen und wie ihr im Dozentengespräch jede Frage souverän beantwortet.

---

## 2. Grundkonzepte: Was ist was?

### A. Was ist ein Dateiserver?
Ein Dateiserver ist ein Rechner im Netzwerk, der zentral Speicherplatz für andere Computer (Clients) bereitstellt. Anstatt dass jeder Mitarbeiter Dateien auf seinem eigenen USB-Stick oder Desktop speichert, liegen alle Daten zentral auf dem Server.

### B. Was ist Samba und SMB?
- **SMB (Server Message Block):** Das Standard-Protokoll, mit dem Windows-Betriebssysteme über das Netzwerk auf Dateien und Drucker zugreifen. Es läuft typischerweise über **TCP-Port 445**.
- **Samba:** Eine Open-Source-Software für Linux, die das Windows-SMB-Protokoll "spricht". Samba sorgt dafür, dass ein Linux-Server für Windows-Clients genau wie ein echter Windows-Server aussieht!

---

## 3. Das Benutzer- und Rechtesystem verstehen

Ein häufiger Stolperstein in Prüfungen ist das Zusammenspiel von **Linux-Rechten** und **Samba-Rechten**. 

> **Die goldene Regel:** Damit ein Benutzer auf eine Datei zugreifen darf, müssen **SOWOHL** die Samba-Rechte (`smb.conf`) **ALS AUCH** die Linux-Dateirechte (`POSIX`) den Zugriff erlauben! Das strengere Recht gewinnt immer!

```
               Client-Anfrage (z.B. anna)
                          |
                          v
         [ 1. Ebene: Samba (smb.conf) ]
         Darf 'anna' den Share 'mitarbeiter' nutzen?
                          | (JA)
                          v
     [ 2. Ebene: Linux-Dateisystem (POSIX) ]
     Hat der Linux-User 'anna' Schreibrechte auf /srv/samba/mitarbeiter?
                          | (JA)
                          v
               Zugriff ERLAUBT!
```

---

### A. Warum braucht man Linux-Nutzer UND Samba-Nutzer?
Samba speichert die Passwörter aus Sicherheitsgründen in einer eigenen verschlüsselten Datenbank (`tdbsam`).
- `useradd -m -s /usr/sbin/nologin anna` $\rightarrow$ Erstellt den Linux-Benutzer. Das `-s /usr/sbin/nologin` verhindert, dass sich der Nutzer direkt per Terminal am Server einloggen kann (Sicherheit!).
- `smbpasswd -a anna` $\rightarrow$ Erstellt den Passworteintrag in Samba.

---

### B. POSIX-Dateirechte verständlich erklärt (`chmod` & `chown`)

Im Linux-Dateisystem hat jede Datei und jeder Ordner drei Rechtsebenen:
1. **User (Besitzer):** `u`
2. **Group (Gruppe):** `g`
3. **Others (Alle anderen):** `o`

Rechte bestehen aus:
- **r (read / lesen):** Wert = 4
- **w (write / schreiben):** Wert = 2
- **x (execute / ausführen):** Wert = 1

#### Die Rechte unserer Ordner im Detail:

1. **`chmod 2777 /srv/samba/public`**:
   - `7` (User): lesen(4) + schreiben(2) + ausführen(1) = 7
   - `7` (Group): lesen(4) + schreiben(2) + ausführen(1) = 7
   - `7` (Others): lesen(4) + schreiben(2) + ausführen(1) = 7
   - `2` am Anfang = **SGID-Bit (Set Group ID)**. Das sorgt dafür, dass neu erstellte Dateien automatisch der Gruppe des Ordners gehören.

2. **`chmod 2770 /srv/samba/mitarbeiter`**:
   - `7` (User): root darf alles.
   - `7` (Group): Mitglieder der Gruppe `mitarbeiter` dürfen alles.
   - `0` (Others): Alle anderen bekommen gar nichts! Strikter Schutz!

---

## 4. Die VirtualBox Netzwerkeinstellungen

Warum nutzen wir das **Interne Netzwerk** (*Internal Network*)?
- **NAT:** Die VM kann nach draußen ins Internet greifen, aber andere VMs können sie nicht direkt erreichen.
- **Netzwerkbrücke (Bridged):** Die VM ist direkt im echten Heim-/Schulnetzwerk. Gefährlich für Tests!
- **Internes Netzwerk (Internal Network):** Erstellt ein isoliertes, virtuelles Kabel zwischen Server und Client. Perfekt und sicher für Labor- und Projektarbeiten!

---

## 5. Wireshark & Netzwerkanalyse (Port 445)

In Teil 5 der Projektarbeit sollen wir Netzwerkpakete mit **Wireshark** beobachten. Was passiert da?

1. **TCP Handshake (Verbindungsaufbau):**
   - Client sendet `SYN` an Server Port 445.
   - Server antwortet mit `SYN-ACK`.
   - Client bestätigt mit `ACK`.
2. **SMB Negotiate Protocol:**
   - Client fragt: "Welche SMB-Version verstehst du?"
   - Server antwortet: "SMB 3.1.1".
3. **SMB Session Setup:**
   - Authentifizierung des Benutzers (`anna`, `chef`) mittels NTLMv2-Hash.
4. **SMB Tree Connect:**
   - Verbinden mit der Freigabe `\\172.16.30.10\mitarbeiter`.

---

## 6. Befehls-Spickzettel für das Terminal

| Befehl | Erklärung / Bedeutung |
| :--- | :--- |
| `ip a` oder `ifconfig` | Zeigt alle Netzwerkkarten und die aktuellen IP-Adressen an. |
| `ping 172.16.30.10` | Prüft, ob der Server über das Netzwerk erreichbar ist. |
| `sudo systemctl status smbd` | Prüft, ob der Samba-Dienst aktiv läuft. |
| `sudo testparm` | Überprüft die Datei `smb.conf` auf Syntaxfehler. |
| `smbclient -L //172.16.30.10 -U anna` | Listet alle Freigaben des Servers als Benutzer `anna` auf. |
| `net use Z: \\172.16.30.10\public /user:anna` | Bindet unter Windows die Freigabe als Laufwerk Z: ein. |
| `net use * /delete /yes` | Trennt alle Netzlaufwerke unter Windows. |
