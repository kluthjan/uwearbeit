# VirtualBox & Netzwerk-Anleitung (Linux Host & Linux Client)
## Gruppe 3 – Dateiserver Projektarbeit (Müller & Partner GmbH)
**Team:** Jan, Marian, Mathias & Marco  
**Netzwerk:** `172.16.30.0/24` | **Server-IP:** `172.16.30.10` | **Client-IP:** `172.16.30.100`

---

## 1. Übersicht & Download-Links

Hallo Team! Diese Anleitung zeigt euch Schritt für Schritt, wie ihr den **Linux-Dateiserver (Host-VM)** und den **Linux-Client (Client-VM)** in VirtualBox einrichtet und zum Laufen bringt.

### 📥 Offizielle Download-Links:
- **Oracle VM VirtualBox:** [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)
- **Ubuntu Server 24.04 LTS (für Server-VM):** [https://ubuntu.com/download/server](https://ubuntu.com/download/server)
- **Ubuntu Desktop 24.04 LTS / Linux Mint (für Client-VM):** [https://ubuntu.com/download/desktop](https://ubuntu.com/download/desktop) oder [https://linuxmint.com/download.php](https://linuxmint.com/download.php)
- **Wireshark (Netzwerkanalyse):** [https://www.wireshark.org/download.html](https://www.wireshark.org/download.html)

---

## 2. Netzwerkkonzept (Gruppe 3)

- **Netzwerkbereich:** `172.16.30.0/24` (Subnetzmaske `255.255.255.0`)
- **Server-VM (Linux Dateiserver):** `172.16.30.10` (Hostname: `fileserver`)
- **Client-VM 1 (Linux Client):** `172.16.30.100` (Hostname: `client1`)
- **Client-VM 2 (Zusatzaufgabe / Windows Client):** `172.16.30.101`
- **VirtualBox Netzwerktyp:** Internes Netzwerk (*Internal Network*) Name: `MuelleNetz`

---

## 3. Schritt 1: VirtualBox Netzwerk-Konfiguration

Für **beide VMs** (Server und Client) müssen die Netzwerkkarten in VirtualBox wie folgt eingestellt werden:

1. Wähle die VM aus $\rightarrow$ **Einstellungen (Settings)** $\rightarrow$ **Netzwerk**.
2. **Adapter 1 (Internes Netz für die Kommunikation):**
   - Angeschlossen an: **Internes Netzwerk** (Internal Network)
   - Name: `MuelleNetz` (Exakt gleicher Name bei allen VMs!)
   - Promiscuous-Modus: **Zulassen für alle VMs** (Allow All)
3. **Adapter 2 (NAT – nur für den Server zum Herunterladen von Paketen):**
   - Angeschlossen an: **NAT**

---

## 4. Schritt 2: Server-VM einrichten (Host `172.16.30.10`)

### A. Netzwerkkonfiguration auf der Server-VM
Öffne das Terminal auf der Server-VM und konfiguriere die statische IP in Netplan (`/etc/netplan/01-netcfg.yaml`):
```yaml
network:
  version: 2
  ethernets:
    enp0s3:
      addresses:
        - 172.16.30.10/24
```
Wende die Einstellungen an:
```bash
sudo netplan apply
```

### B. Das automatische Setup-Skript ausführen
Lade euer Projekt von GitHub herunter und starte das Skript:
```bash
git clone https://github.com/kluthjan/uwearbeit.git
cd uwearbeit
sudo ./scripts/setup_samba_server.sh
```

*Was das Skript automatisch erledigt:*
1. Installiert Samba (`apt install samba cifs-utils`).
2. Erstellt die Gruppen `mitarbeiter` und `leitung`.
3. Erstellt die Benutzer `anna`, `bernd` und `chef` mit Passwort `Start123!`.
4. Richtet die Ordner `/srv/samba/public`, `/srv/samba/mitarbeiter`, `/srv/samba/leitung` ein.
5. Verfährt die POSIX-Dateirechte (`chmod 2777` für public, `chmod 2770` für mitarbeiter/leitung).
6. Spielt die Samba-Konfiguration `smb.conf` ein und startet den Dienst (`smbd`).

---

## 5. Schritt 3: Linux-Client-VM einrichten (`172.16.30.100`)

### A. Statische IP auf dem Linux-Client setzen
Öffne die Netzwerkeinstellungen auf dem Linux-Client oder editiere Netplan / NetworkManager:
- **IP-Adresse:** `172.16.30.100`
- **Subnetzmaske:** `255.255.255.0`
- **Gateway / DNS:** `172.16.30.10`

### B. Notwendige Pakete installieren
```bash
sudo apt update && sudo apt install -y cifs-utils smbclient ping wireshark
```

### C. Verbindung prüfen (Ping-Test)
```bash
ping -c 3 172.16.30.10
```
*Erwartetes Ergebnis:* 3 erfolgreiche Antworten ohne Paketverlust!

---

## 6. Schritt 4: Samba-Freigaben auf dem Linux-Client mounten & testen

### A. Vorhandene Freigaben anzeigen
```bash
smbclient -L //172.16.30.10 -U anna%Start123!
```

### B. Mount-Ordner auf dem Client anlegen
```bash
sudo mkdir -p /mnt/public_share
sudo mkdir -p /mnt/mitarbeiter_share
sudo mkdir -p /mnt/leitung_share
```

### C. Freigaben einbinden & Rechte prüfen

1. **Als `anna` (Gruppe: mitarbeiter) mounten:**
   ```bash
   # 1. Public Freigabe mounten (Erfolgreich):
   sudo mount -t cifs //172.16.30.10/public /mnt/public_share -o username=anna,password=Start123!

   # 2. Mitarbeiter Freigabe mounten (Erfolgreich):
   sudo mount -t cifs //172.16.30.10/mitarbeiter /mnt/mitarbeiter_share -o username=anna,password=Start123!

   # 3. Leitung Freigabe mounten (FEHLER ERWARTET - Zugriff verweigert!):
   sudo mount -t cifs //172.16.30.10/leitung /mnt/leitung_share -o username=anna,password=Start123!
   ```
   *Erwartetes Ergebnis für `leitung`:* `mount error(13): Permission denied`. **Korrekt!**

2. **Als `chef` (Gruppe: leitung) mounten:**
   ```bash
   sudo mount -t cifs //172.16.30.10/leitung /mnt/leitung_share -o username=chef,password=Start123!
   ```
   *Erwartetes Ergebnis:* **Erfolgreich gemountet!** Chef darf in allen Ordnern lesen und schreiben.

---

## 7. Schritt 5: Automatischer Test-Durchlauf & Wireshark

1. Starte **Wireshark** auf dem Client:
   ```bash
   sudo wireshark
   ```
   Wähle das Netzwerkinterface aus und filtere nach `smb2`.

2. Führe auf der Server-VM das automatisierte Test-Skript aus:
   ```bash
   ./scripts/run_tests.sh
   ```

---

## 8. Zusammenfassung & Checkliste

- [x] ISOs heruntergeladen (Ubuntu Server & Desktop)
- [x] VirtualBox Internes Netzwerk `MuelleNetz` für beide VMs konfiguriert
- [x] Server-IP auf `172.16.30.10` & Client-IP auf `172.16.30.100` gesetzt
- [x] Server-Skript `./scripts/setup_samba_server.sh` ausgeführt
- [x] Client-Mounts für `anna`, `bernd` und `chef` erfolgreich getestet
- [x] Test-Skript `./scripts/run_tests.sh` fehlerfrei bestanden
