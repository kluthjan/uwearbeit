# VirtualBox & Netzwerk-Anleitung für Windows
## Gruppe 3 – Dateiserver Projektarbeit (Müller & Partner GmbH)
**Team:** Jan, Marian, Mathias & Marco  
**Netzwerk:** `172.16.30.0/24` | **Server-IP:** `172.16.30.10` | **Client-IP:** `172.16.30.100`

---

## 1. Übersicht & Zielsetzung

Hallo Team! Diese Anleitung hilft dir Schritt für Schritt, die **VirtualBox-Umgebung auf Windows** einzurichten, damit Server-VM und Client-VM sauber miteinander kommunizieren können.

### Unsere Netzwerkdaten (Gruppe 3):
- **Netzwerkadresse:** `172.16.30.0/24` (Subnetzmaske: `255.255.255.0`)
- **Server-VM (Linux Dateiserver):** `172.16.30.10`
- **Client-VM 1 (Windows Client):** `172.16.30.100`
- **Client-VM 2 (Linux Client / Zusatzaufgabe):** `172.16.30.101`
- **VirtualBox Netzwerktyp:** Internes Netzwerk (*Internal Network*) Name: `MuelleNetz`

---

## 2. Schritt 1: VirtualBox auf Windows vorbereiten

1. Lade **Oracle VM VirtualBox** (Version 7.0 oder höher) herunter und installiere es auf deinem Windows-Rechner.
2. Installiere auch das **VirtualBox Extension Pack** (Doppelklick auf die heruntergeladene `.vbox-extpack` Datei).

---

## 3. Schritt 2: Netzwerkeinstellungen in VirtualBox vornehmen

Damit die VMs untereinander isoliert wie in einer echten Firma kommunizieren können, nutzen wir ein **Internes Netzwerk**.

### Für jede VM (Server und Client) im Hauptfenster von VirtualBox:
1. Wähle die VM aus und klicke auf **Ändern (Settings)** $\rightarrow$ **Netzwerk**.
2. **Adapter 1 aktivieren**:
   - Angeschlossen an: **Internes Netzwerk** (Internal Network)
   - Name: `MuelleNetz` (bei allen VMs exakt den gleichen Namen eintragen!)
   - Promiscuous-Modus: *Zulassen für alle VMs* (Allow All)
3. **Adapter 2 aktivieren (Optional, für Internet/Updates)**:
   - Angeschlossen an: **NAT** oder **Netzwerkbrücke**
   - *Hinweis:* Dies ermöglicht während der Installation den Paketdownload (`apt update / apt install`).

---

## 4. Schritt 3: Server-VM einrichten (Ubuntu Server / Debian)

1. Starte die Server-VM und melde dich an.
2. **Statische IP-Adresse setzen (`172.16.30.10`)**:
   Öffne die Netplan-Konfiguration unter Ubuntu (`/etc/netplan/01-netcfg.yaml`):
   ```yaml
   network:
     version: 2
     ethernets:
       enp0s3:
         addresses:
           - 172.16.30.10/24
   ```
   Führe anschließend aus:
   ```bash
   sudo netplan apply
   ```
3. **Hostname setzen**:
   ```bash
   sudo hostnamectl set-hostname fileserver
   ```
4. **Samba-Server installieren & konfigurieren**:
   Führe einfach das mitgelieferte Skript `setup_samba_server.sh` auf dem Server aus:
   ```bash
   chmod +x setup_samba_server.sh
   sudo ./setup_samba_server.sh
   ```

---

## 5. Schritt 4: Client-VM unter Windows einrichten

1. Starte deine Client-VM (z.B. Windows 10/11 VM in VirtualBox).
2. Öffne unter Windows die **Systemsteuerung** $\rightarrow$ **Netzwerk- und Freigabecenter** $\rightarrow$ **Adaptereinstellungen ändern**.
3. Rechtsklick auf die Netzwerkverbindung $\rightarrow$ **Eigenschaften** $\rightarrow$ **Internetprotokoll, Version 4 (TCP/IPv4)**.
4. Folgende statische IP eintragen:
   - **IP-Adresse:** `172.16.30.100`
   - **Subnetzmaske:** `255.255.255.0`
   - **Standardgateway:** (leer lassen oder `172.16.30.10`)
   - **DNS-Server:** `172.16.30.10`

---

## 6. Schritt 5: Verbindung & Netzlaufwerke unter Windows testen

### A. Ping-Test durchführen (CMD)
Öffne die Eingabeaufforderung (`cmd.exe`) in Windows und gib ein:
```cmd
ping 172.16.30.10
```
*Erwartetes Ergebnis:* 4 Antworten vom Server `172.16.30.10` ohne Paketverlust!

---

### B. Freigaben in Windows Explorer einbinden

Öffne den **Windows Explorer** (Tastenkombination `Win + E`) und gib in die Adresszeile oben ein:
`\\172.16.30.10`

Du siehst nun die drei Ordner:
- `public`
- `mitarbeiter`
- `leitung`

---

### C. Netzlaufwerk mit verschiedenen Benutzern verbinden (CMD `net use`)

Um die Rechte zu testen, nutzen wir folgende Test-Logins (Passwort für alle ist `Start123!`):

| Benutzer | Passwort | Gruppe | Rechte |
| :--- | :--- | :--- | :--- |
| `anna` | `Start123!` | `mitarbeiter` | Lesen/Schreiben in `public` & `mitarbeiter`. **Kein** Zugriff auf `leitung`. |
| `bernd` | `Start123!` | `mitarbeiter` | Lesen/Schreiben in `public` & `mitarbeiter`. **Kein** Zugriff auf `leitung`. |
| `chef` | `Start123!` | `leitung`, `mitarbeiter` | Lesen/Schreiben in **allen** drei Freigaben (`public`, `mitarbeiter`, `leitung`). |

#### Befehle im CMD zum Verbinden & Trennen:

1. **Als `anna` verbinden**:
   ```cmd
   net use Z: \\172.16.30.10\mitarbeiter /user:anna Start123!
   ```
   - Versuch auf `\\172.16.30.10\leitung` zuzugreifen $\rightarrow$ **Zugriff verweigert** (Korrekt!).

2. **Verbindung trennen**:
   ```cmd
   net use * /delete /yes
   ```

3. **Als `chef` verbinden**:
   ```cmd
   net use Z: \\172.16.30.10\leitung /user:chef Start123!
   ```
   - Zugriff auf `\\172.16.30.10\leitung` $\rightarrow$ **Erfolgreich!**

---

## 7. Zusammenfassung & Checkliste

- [x] VirtualBox auf Windows installiert
- [x] Internes Netzwerk `MuelleNetz` für beide VMs aktiviert
- [x] Server-IP auf `172.16.30.10` gesetzt
- [x] Client-IP auf `172.16.30.100` gesetzt
- [x] Ping erfolgreich
- [x] Freigaben `public`, `mitarbeiter`, `leitung` unter Windows getestet
