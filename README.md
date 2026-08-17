# Projektarbeit 3: Einrichtung eines zentralen Dateiservers
## Müller & Partner GmbH – IT-Projekt (Gruppe 3)
**Projektteam:** Jan Kluth, Marian, Mathias & Marco  
**Netzwerk:** `172.16.30.0/24` | **Server IP:** `172.16.30.10` | **Client IP:** `172.16.30.100`

---

## Projektinhalte & Dateistruktur

```
uweprojekt/
  ├── README.md                                    <- Hauptübersicht & Schnellstart
  ├── config/
  │     └── smb.conf                               <- Samba Hauptkonfiguration (public, mitarbeiter, leitung)
  ├── docs/
  │     ├── Linux_VirtualBox_Setup_Anleitung.md    <- Linux Host & Client Guide mit Download-Links
  │     ├── Linux_VirtualBox_Setup_Anleitung.pdf   <- Generiertes PDF für Linux Setup
  │     ├── Windows_VirtualBox_Setup_Anleitung.md  <- Windows Setup Guide
  │     ├── Windows_VirtualBox_Setup_Anleitung.pdf  <- Generiertes PDF für Windows Setup
  │     ├── Projektdokumentation_Dateiserver_Gruppe3.md <- Doku nach Wasserfallmodell
  │     ├── Projektdokumentation_Dateiserver_Gruppe3.pdf <- Projektdoku als PDF
  │     ├── Lernhilfe_und_Erklaerung_Dateiserver.md  <- Ausführliches Lern- & Erklärdokument
  │     └── Lernhilfe_und_Erklaerung_Dateiserver.pdf <- Lern-PDF für das Team
  ├── presentation/
  │     ├── Praesentation_Dateiserver_Gruppe3.md    <- 8-12 Min Präsentation mit Sprechernotizen
  │     ├── Dozentenfragen_Vorbereitung.md        <- 5 Min Dozentenfragen & Antworten
  │     └── Dozentenfragen_Vorbereitung.pdf        <- Dozentenfragen als PDF
  └── scripts/
        ├── setup_samba_server.sh                  <- Automatisiertes Server Setup Skript (apt & pacman)
        ├── setup_client.sh                        <- Linux Client Setup Skript
        ├── run_tests.sh                           <- Automatisches Rechte-Testskript
        ├── build_pdf.py                           <- PDF Generator via WeasyPrint
        └── nextcloud_github_sharing.sh            <- Sharing-Helper für GitHub & Nextcloud
```

---

## 📥 Offizielle Download-Links für das Team:
- **Oracle VM VirtualBox:** [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)
- **Ubuntu Server 24.04 LTS (für Server-VM):** [https://ubuntu.com/download/server](https://ubuntu.com/download/server)
- **Ubuntu Desktop 24.04 LTS (für Client-VM):** [https://ubuntu.com/download/desktop](https://ubuntu.com/download/desktop)

---

## 🚀 Schnellstart

### 1. Dateiserver einrichten (Server-VM)
Führe auf der Server-VM (`172.16.30.10`) folgendes Skript aus:
```bash
sudo ./scripts/setup_samba_server.sh
```

### 2. Rechte-Tests durchführen
Führe das automatisierte Testprotokoll aus:
```bash
./scripts/run_tests.sh
```
