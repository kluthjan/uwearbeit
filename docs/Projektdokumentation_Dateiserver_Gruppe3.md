# Projektdokumentation
## Einrichtung eines zentralen Dateiservers für die Müller & Partner GmbH
**Projektarbeit Nummer 3**  
**Projektteam (Gruppe 3):** Jan Kluth, Marian, Mathias & Marco  
**Abgabedatum:** 17. August 2026  

---

## Executive Summary

Im Rahmen der Projektarbeit 3 wurde für die fiktive *Müller & Partner GmbH* eine zentrale, rollenbasierte Dateiserver-Infrastruktur auf Basis von Linux und Samba (SMB/CIFS-Protokoll) konzipiert, realisiert und getestet. Bisher wurden Dokumente lokal auf den Arbeitsplätzen gespeichert, was zu Sicherheitsrisiken, Dateninkonsistenzen und fehlenden Zugriffsbeschränkungen führte.

Durch die neue Lösung im isolierten Subnetz `172.16.30.0/24` werden Freigaben zentral bereitgestellt und Zugriffe gemäß einer definierten Berechtigungsmatrix strikt reglementiert.

---

## Phase 1: Projektinitiierung

### 1.1 Ausgangssituation
Die Müller & Partner GmbH verzeichnet ein stetiges Wachstum. Mitarbeiter legten geschäftskritische Dateien bisher lokal auf ihren Desktop-Rechnern ab. Eine strukturierte Rechtevergabe oder zentrale Sicherung existierte nicht. Vertrauliche Leitungsdokumente waren potenziell für alle Mitarbeiter einsehbar.

### 1.2 Projektziel & Kundenauftrag
Ziel des Projekts ist die Bereitstellung eines zentralen Dateiservers mit folgenden Anforderungen:
1. **Zentrale Speicherung:** Einrichtung dreier Netzlaufwerk-Freigaben (`public`, `mitarbeiter`, `leitung`).
2. **Benutzer- & Gruppenverwaltung:**
   - Benutzer: `anna`, `bernd`, `chef`
   - Gruppen: `mitarbeiter` (anna, bernd, chef), `leitung` (chef)
3. **Rechteverwaltung:**
   - `public`: Lese- & Schreibzugriff für alle Mitarbeiter und Leitung.
   - `mitarbeiter`: Zugriff exklusiv für Mitarbeiter und Leitung.
   - `leitung`: Strikter Zugriff exklusiv für die Geschäftsleitung (`chef`).
4. **VirtualBox-Infrastruktur & Client-Anbindung:** Anbindung von Linux- und Windows-Clients im internen Netzwerk.

---

## Phase 2: Projektplanung

### 2.1 Ist-Analyse & Soll-Konzept
- **Ist-Zustand:** Lokale Datenspeicherung, dezentrale Datenhaltung, keine Zugriffskontrollen.
- **Soll-Zustand:** Central File Server auf Linux-Basis mit Samba 4, POSIX-Dateirechten, getrennten Freigaben und automatisierter Rechteprüfung.

### 2.2 Netzplan & IP-Adresskonzept (Gruppe 3)

```
[ VirtualBox Internes Netzwerk: MuelleNetz ]
               |
               +-----------------------------------+
               |                                   |
    +--------------------+              +--------------------+
    |  Dateiserver (VM)  |              |  Windows Client    |
    |  Ubuntu / Debian   |              |  (Windows 10/11)   |
    |  IP: 172.16.30.10  |              |  IP: 172.16.30.100 |
    +--------------------+              +--------------------+
               |
               +-----------------------------------+
               |
    +--------------------+
    |  Linux Client (VM) |
    |  (Zusatzaufgabe)   |
    |  IP: 172.16.30.101 |
    +--------------------+
```

- **Netzwerkadresse:** `172.16.30.0/24` (Subnetzmaske: `255.255.255.0`)
- **Server IP:** `172.16.30.10` (Hostname: `fileserver`)
- **Client 1 IP:** `172.16.30.100` (Windows)
- **Client 2 IP:** `172.16.30.101` (Linux)

### 2.3 Berechtigungsmatrix

| Benutzer | Primärgruppe | Zusatzgruppen | Freigabe `public` | Freigabe `mitarbeiter` | Freigabe `leitung` |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **anna** | mitarbeiter | - | Lesen / Schreiben | Lesen / Schreiben | **Kein Zugriff** |
| **bernd** | mitarbeiter | - | Lesen / Schreiben | Lesen / Schreiben | **Kein Zugriff** |
| **chef** | leitung | mitarbeiter | Lesen / Schreiben | Lesen / Schreiben | **Lesen / Schreiben** |

---

## Phase 3: Projektdurchführung

### 3.1 Server-Einrichtung & Netzwerk
Auf dem Linux-Server wurde die IP-Adresse statisch auf `172.16.30.10/24` konfiguriert und Samba installiert:
```bash
sudo hostnamectl set-hostname fileserver
sudo apt update && sudo apt install -y samba samba-common-bin cifs-utils
```

### 3.2 Benutzer-, Gruppen- und POSIX-Dateirechte
Erstellung der Systemgruppen und Nutzer sowie Setzen des SGID-Bits (`2770` bzw. `2777`) für die Vererbung von Gruppenrechten:
```bash
sudo groupadd mitarbeiter && sudo groupadd leitung
sudo useradd -m -g mitarbeiter -s /usr/sbin/nologin anna
sudo useradd -m -g mitarbeiter -s /usr/sbin/nologin bernd
sudo useradd -m -g leitung -G mitarbeiter -s /usr/sbin/nologin chef

# POSIX Dateirechte
sudo chown -R root:mitarbeiter /srv/samba/public && sudo chmod -R 2777 /srv/samba/public
sudo chown -R root:mitarbeiter /srv/samba/mitarbeiter && sudo chmod -R 2770 /srv/samba/mitarbeiter
sudo chown -R root:leitung /srv/samba/leitung && sudo chmod -R 2770 /srv/samba/leitung
```

### 3.3 Samba-Konfiguration (`smb.conf`)
Die Hauptkonfiguration regelt die Freigaben:
```ini
[public]
   path = /srv/samba/public
   read only = no
   valid users = @mitarbeiter, @leitung

[mitarbeiter]
   path = /srv/samba/mitarbeiter
   read only = no
   valid users = @mitarbeiter, @leitung

[leitung]
   path = /srv/samba/leitung
   read only = no
   valid users = @leitung
```

---

## Phase 4: Projektabschluss & Funktionstests

### 4.1 Testergebnisse (Testprotokoll)

| Test-ID | Testfall | Befehl / Methode | Erwartetes Ergebnis | Tatsächliches Ergebnis | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **T01** | IP-Erreichbarkeit | `ping 172.16.30.10` | 0% Paketverlust | Server antwortet in <1ms | **PASS** |
| **T02** | `anna` auf `public` | `smbclient //172.16.30.10/public -U anna` | Zugriff gewährt | Verzeichnisinhalt angezeigt | **PASS** |
| **T03** | `anna` auf `mitarbeiter` | `smbclient //172.16.30.10/mitarbeiter -U anna` | Zugriff gewährt | Schreiben/Lesen erfolgreich | **PASS** |
| **T04** | `anna` auf `leitung` | `smbclient //172.16.30.10/leitung -U anna` | **NT_STATUS_ACCESS_DENIED** | Zugriff verweigert | **PASS** |
| **T05** | `chef` auf `leitung` | `net use Z: \\172.16.30.10\leitung /user:chef` | Netzlaufwerk Z: verbunden | Schreiben/Lesen erfolgreich | **PASS** |
| **T06** | Neustartfestigkeit | `sudo systemctl restart smbd` | Dienst läuft weiter | Freigaben nach Reboot sofort aktiv | **PASS** |

### 4.2 Netzwerkanalyse mit Wireshark
Bei der Paketanalyse der SMB2/SMB3-Kommunikation zwischen Client (`172.16.30.100`) und Server (`172.16.30.10`) wurden folgende Protokollschritte nachgewiesen:
1. **TCP 3-Way-Handshake:** Aufbau der TCP-Verbindung über Port 445 (`SYN` $\rightarrow$ `SYN-ACK` $\rightarrow$ `ACK`).
2. **SMB Negotiate Protocol:** Aushandeln der SMB-Protokollversion (SMB 3.1.1).
3. **SMB Session Setup:** NTLMv2-Authentifizierung der Benutzer.
4. **SMB Tree Connect:** Verbindung zum spezifischen Share (`\\172.16.30.10\mitarbeiter`).

### 4.3 Fehleranalyse & Troubleshooting
- **Fehlerfall:** Nach Stoppen des `smbd`-Dienstes (`sudo systemctl stop smbd`) meldet der Windows-Client `Systemfehler 53 – Der Netzwerkpfad wurde nicht gefunden`.
- **Lösung:** Automatische Überwachung via Systemd (`restart=always`) und Firewall-Freischaltung für Port 445 TCP.

### 4.4 Ausblick: Echte Unternehmensumgebung
In einem Produktionsnetzwerk empfiehlt das IT-Team folgende Erweiterungen:
- **Active Directory / Domain Controller (Samba AD / Windows Server):** Zentrale Kerberos-Authentifizierung statt lokaler Nutzerdatenbanken.
- **SMB-Verschlüsselung (`smb encrypt = required`):** Schutz vor Man-in-the-Middle-Angriffen.
- **Automatisierte Datensicherung (Backup):** Tägliche Snapshots und Offsite-Backups der Freigaben.
