# 🖥️ Gruppenarbeit 4 – Webserver mit SSH-Fernadministration

> **Team Gruppe 3:** Jan · Marian · Mathias · Marco

---

## 📋 Aufgabe

**Müller & Partner GmbH** – Einrichtung eines internen Intranets mit:
- 🌍 **Apache2 Webserver** (HTTP, Port 80)
- 🔒 **OpenSSH Server** (Fernadministration, Port 22)
- 🛡️ **UFW Firewall** (nur SSH + HTTP erlaubt)

---

## 🌐 Netzwerkplan – Gruppe 3

| Gerät | IP-Adresse | Hostname |
|-------|-----------|----------|
| **Server** | `172.16.30.10` | `server.gruppe3.local` |
| **Client** | `172.16.30.100` | `client.gruppe3.local` |
| **Netzwerk** | `172.16.30.0/24` | — |
| **Gateway** | `172.16.30.1` | — |

---

## 📁 Projektstruktur

```
Gruppenarbeit4/
├── docs/
│   ├── Team_Anleitung_Gruppenarbeit4.pdf       ← Schritt-für-Schritt Anleitung (für Windows-Nutzer)
│   ├── Projektdokumentation_Gruppenarbeit4.pdf  ← Vollständige Projektdoku (Wasserfallmodell)
│   └── Projektplan_Gruppenarbeit4.pdf           ← Aufgabenverteilung & Zeitplan
├── presentation/
│   └── Praesentation_Gruppenarbeit4.html        ← Interaktive Präsentation (im Browser öffnen)
└── scripts/
    ├── server_setup.sh                           ← Automatisches Server-Setup Script
    ├── client_setup.sh                           ← Automatisches Client-Setup Script
    └── generate_pdfs.py                          ← PDF-Generator
```

---

## 🚀 Schnellstart

### Server-VM einrichten (Ubuntu Server)
```bash
# Script herunterladen und ausführen:
sudo bash server_setup.sh
```

### Client-VM einrichten (Ubuntu Desktop)
```bash
sudo bash client_setup.sh
```

Das Script richtet automatisch ein:
- ✅ Netzwerk (statische IP)
- ✅ SSH-Server mit Banner
- ✅ Apache Webserver + Intranet-Seite
- ✅ UFW Firewall (Port 22 + 80)
- ✅ Admin-Benutzer

---

## 📄 Dokumente

| Datei | Beschreibung |
|-------|-------------|
| [Team_Anleitung.pdf](docs/Team_Anleitung_Gruppenarbeit4.pdf) | Schritt-für-Schritt für alle Teammitglieder |
| [Projektdokumentation.pdf](docs/Projektdokumentation_Gruppenarbeit4.pdf) | Vollständige Doku nach Wasserfallmodell |
| [Projektplan.pdf](docs/Projektplan_Gruppenarbeit4.pdf) | Aufgabenverteilung & Zeitplan |
| [Präsentation.html](presentation/Praesentation_Gruppenarbeit4.html) | Im Browser öffnen (Pfeiltasten zum Blättern) |

---

## 🔧 Manuelle Einrichtung

### Schritt 1: VirtualBox konfigurieren
- Beide VMs: **Netzwerk → Internes Netzwerk → Name: `intnet-gruppe3`**

#### 🌐 VirtualBox Netzwerkkonfiguration & Portweiterleitung (Windows-PC)

1. **Kommunikation VM ⟷ VM (Client-VM ⟷ Server-VM):**
   - **Netzwerktyp:** Internes Netzwerk (`intnet-gruppe3`)
   - **Portweiterleitung nötig?** ❌ **NEIN!** Im internen Netzwerk kommunizieren beide VMs direkt im Subnetz `172.16.30.0/24`. Alle Ports (22, 80) sind frei erreichbar.

2. **Direkter Zugriff vom Windows-Host-PC auf die Server-VM (Optional):**
   - Falls du direkt aus dem Windows-Browser oder Windows PowerShell/PuTTY auf die Server-VM zugreifen möchtest:
   - Server-VM → **Einstellungen → Netzwerk → Adapter 1 (NAT) → Erweitert → Portweiterleitung**:
     - Regel 1 (SSH): Host-Port `2222` ➔ Gast-Port `22`
     - Regel 2 (HTTP): Host-Port `8080` ➔ Gast-Port `80`
   - **Zugriff auf Windows:**
     - 🌍 Browser: `http://localhost:8080`
     - 💻 PowerShell / PuTTY: `ssh admin@localhost -p 2222` (Passwort: `Admin1234!`)

### Schritt 2: Server einrichten
```bash
# Netzwerk konfigurieren (IP: 172.16.30.10)
sudo nano /etc/netplan/00-installer-config.yaml
sudo netplan apply

# SSH installieren
sudo apt install openssh-server -y

# Apache installieren
sudo apt install apache2 -y

# Firewall einrichten
sudo ufw default deny incoming
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw enable
```

### Schritt 3: Client einrichten
```bash
# IP: 172.16.30.100
sudo netplan apply

# Server in /etc/hosts
echo "172.16.30.10 server.gruppe3.local" | sudo tee -a /etc/hosts

# SSH-Verbindung zum Server
ssh admin@172.16.30.10

# Browser: Webseite aufrufen
# http://172.16.30.10
```

---

## 🧪 Funktionstests

```bash
# Ping Client → Server
ping -c 4 172.16.30.10

# Webserver testen
curl http://172.16.30.10

# SSH testen
ssh admin@172.16.30.10

# Firewall-Status
sudo ufw status verbose

# Wireshark (HTTP-Pakete)
sudo tcpdump -i enp0s3 port 80 -v
```

---

## 👥 Team

| Name | Rolle |
|------|-------|
| **Jan** | Teamleiter |
| **Marian** | Teammitglied |
| **Mathias** | Teammitglied |
| **Marco** | Teammitglied |

---

*Projektarbeit 4 | IT-Systeme | Ausbildung | 2026*
