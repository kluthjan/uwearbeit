#!/bin/bash
# =============================================================================
# Gruppenarbeit 4 - Server-Setup Script
# Webserver (Apache) + SSH-Fernadministration
# Gruppe 4 - Jan, Marian, Mathias, Marco
# Netzwerk: 172.16.40.0/24  |  Server: 172.16.40.10
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

SERVER_IP="172.16.40.10"
SUBNET="172.16.40.0/24"
GATEWAY="172.16.40.1"
DNS_SERVER="8.8.8.8"
INTERFACE="eth0"
HOSTNAME_FQDN="server.gruppe4.local"
ZONE="gruppe4.local"
WEBROOT="/var/www/html"

print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
    exit 1
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Dieses Script muss als root ausgeführt werden! Benutze: sudo bash $0"
    fi
}

# =============================================================================
# SCHRITT 1: Netzwerk konfigurieren
# =============================================================================
configure_network() {
    print_header "SCHRITT 1: Netzwerk konfigurieren"
    
    # Detect actual interface name
    ACTUAL_IF=$(ip -o link show | awk -F': ' '{print $2}' | grep -v lo | head -1)
    echo -e "${YELLOW}Erkannte Netzwerkschnittstelle: $ACTUAL_IF${NC}"
    
    # Detect if using systemd-networkd or NetworkManager
    if [ -d /etc/netplan ]; then
        print_step "Konfiguriere Netzwerk via Netplan (Ubuntu/Debian modern)..."
        
        cat > /etc/netplan/01-netcfg.yaml <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    ${ACTUAL_IF}:
      addresses:
        - ${SERVER_IP}/24
      routes:
        - to: default
          via: ${GATEWAY}
      nameservers:
        addresses: [${DNS_SERVER}]
      dhcp4: false
EOF
        netplan apply
        print_step "Netplan-Konfiguration angewendet"
        
    elif [ -f /etc/network/interfaces ]; then
        print_step "Konfiguriere Netzwerk via /etc/network/interfaces (Debian classic)..."
        
        cat > /etc/network/interfaces <<EOF
# Loopback
auto lo
iface lo inet loopback

# Hauptnetzwerkschnittstelle
auto ${ACTUAL_IF}
iface ${ACTUAL_IF} inet static
    address ${SERVER_IP}
    netmask 255.255.255.0
    gateway ${GATEWAY}
    dns-nameservers ${DNS_SERVER}
EOF
        ifdown ${ACTUAL_IF} 2>/dev/null || true
        ifup ${ACTUAL_IF}
        print_step "Netzwerk-Schnittstelle neu gestartet"
    fi
    
    # Set hostname
    hostnamectl set-hostname server.gruppe4.local
    
    # Update /etc/hosts
    sed -i '/server.gruppe4.local/d' /etc/hosts
    echo "${SERVER_IP}  server.gruppe4.local server" >> /etc/hosts
    
    print_step "Hostname auf 'server.gruppe4.local' gesetzt"
    echo -e "\n${CYAN}Aktuelle IP-Konfiguration:${NC}"
    ip addr show ${ACTUAL_IF} 2>/dev/null || ip addr show
}

# =============================================================================
# SCHRITT 2: System aktualisieren
# =============================================================================
update_system() {
    print_header "SCHRITT 2: System aktualisieren"
    
    export DEBIAN_FRONTEND=noninteractive
    export NEEDRESTART_MODE=a
    apt-get update -y
    apt-get upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"
    print_step "System ist aktuell"
}

# =============================================================================
# SCHRITT 3: SSH-Server installieren und konfigurieren
# =============================================================================
configure_ssh() {
    print_header "SCHRITT 3: SSH-Server installieren & konfigurieren"
    
    apt-get install -y openssh-server
    
    # Backup original config
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
    
    cat > /etc/ssh/sshd_config <<EOF
# ============================================================
# SSH-Server Konfiguration - Gruppenarbeit 4
# Gruppe 4 - Jan, Marian, Mathias, Marco
# ============================================================

# Basis-Einstellungen
Port 22
AddressFamily inet
ListenAddress 0.0.0.0

# Protokoll und Host-Keys
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key

# Logging
SyslogFacility AUTH
LogLevel INFO

# Authentifizierung
LoginGraceTime 2m
PermitRootLogin no
StrictModes yes
MaxAuthTries 6
MaxSessions 10

# Passwort-Authentifizierung (erlaubt für Projekt)
PasswordAuthentication yes
PermitEmptyPasswords no
ChallengeResponseAuthentication no

# Weitere Optionen
UsePAM yes
X11Forwarding yes
PrintMotd no

# Erlaubte Verbindungen nur aus dem eigenen Netzwerk
AllowUsers *@172.16.40.*

# Sftp aktivieren
Subsystem sftp /usr/lib/openssh/sftp-server

# Banner anzeigen
Banner /etc/ssh/banner
EOF

    # SSH Banner erstellen
    cat > /etc/ssh/banner <<EOF

  ====================================================
   Müller & Partner GmbH - Internes Serversystem
   Server: server.gruppe4.local (${SERVER_IP})
   Gruppe 4: Jan, Marian, Mathias, Marco
   NUR autorisierter Zugriff!
  ====================================================

EOF

    systemctl enable ssh
    systemctl restart ssh
    
    print_step "SSH-Server konfiguriert und gestartet"
    print_step "Nur Verbindungen aus 172.16.40.0/24 erlaubt"
    print_step "Root-Login deaktiviert"
}

# =============================================================================
# SCHRITT 4: Apache Webserver installieren
# =============================================================================
configure_apache() {
    print_header "SCHRITT 4: Apache Webserver installieren & konfigurieren"
    
    apt-get install -y apache2
    
    # Apache konfigurieren
    cat > /etc/apache2/sites-available/intranet.conf <<EOF
<VirtualHost *:80>
    ServerName server.gruppe4.local
    ServerAlias intranet.gruppe4.local
    ServerAdmin admin@gruppe4.local
    DocumentRoot /var/www/html

    # Logging
    ErrorLog \${APACHE_LOG_DIR}/gruppe4_error.log
    CustomLog \${APACHE_LOG_DIR}/gruppe4_access.log combined

    # Sicherheitseinstellungen
    <Directory /var/www/html>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
    
    # Nur internes Netzwerk
    # Require ip 172.16.40.0/24
</VirtualHost>
EOF

    # Intranet-Webseite erstellen
    cat > /var/www/html/index.html <<'HTMLEOF'
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Müller & Partner GmbH - Intranet</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }
        header {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding: 20px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo {
            font-size: 1.8em;
            font-weight: bold;
            color: #4fc3f7;
            letter-spacing: 2px;
        }
        .logo span { color: #fff; }
        nav a {
            color: #90caf9;
            text-decoration: none;
            margin-left: 25px;
            font-size: 0.95em;
            transition: color 0.3s;
        }
        nav a:hover { color: #4fc3f7; }
        .hero {
            text-align: center;
            padding: 60px 20px 40px;
        }
        .hero h1 {
            font-size: 2.8em;
            color: #fff;
            margin-bottom: 10px;
        }
        .hero h1 span { color: #4fc3f7; }
        .hero p {
            font-size: 1.1em;
            color: #90caf9;
            margin-bottom: 30px;
        }
        .badge {
            display: inline-block;
            background: rgba(79,195,247,0.15);
            border: 1px solid #4fc3f7;
            color: #4fc3f7;
            padding: 6px 18px;
            border-radius: 20px;
            font-size: 0.85em;
            margin: 5px;
        }
        .cards {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            padding: 20px 40px 40px;
            max-width: 1100px;
            margin: 0 auto;
        }
        .card {
            flex: 1;
            min-width: 280px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 25px;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(79,195,247,0.2);
            border-color: #4fc3f7;
        }
        .card-icon { font-size: 2em; margin-bottom: 12px; }
        .card h3 { color: #4fc3f7; font-size: 1.1em; margin-bottom: 8px; }
        .card p { color: #bbb; font-size: 0.9em; line-height: 1.6; }
        .announcement {
            background: rgba(79,195,247,0.08);
            border-left: 4px solid #4fc3f7;
            border-radius: 0 8px 8px 0;
            padding: 15px 20px;
            margin: 10px 0;
        }
        .announcement h4 { color: #4fc3f7; margin-bottom: 5px; }
        .announcement p { color: #ccc; font-size: 0.9em; }
        .server-info {
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(79,195,247,0.3);
            border-radius: 8px;
            padding: 15px 20px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #a5d6a7;
            margin-top: 10px;
        }
        footer {
            text-align: center;
            padding: 20px;
            color: #555;
            font-size: 0.8em;
            border-top: 1px solid rgba(255,255,255,0.05);
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">MÜLLER <span>&</span> PARTNER</div>
        <nav>
            <a href="#">Startseite</a>
            <a href="#">Abteilungen</a>
            <a href="#">Dokumente</a>
            <a href="#">Kontakt</a>
        </nav>
    </header>

    <div class="hero">
        <h1>Willkommen im <span>Intranet</span></h1>
        <p>Internes Informationsportal der Müller &amp; Partner GmbH</p>
        <span class="badge">🌐 server.gruppe4.local</span>
        <span class="badge">📡 172.16.40.10</span>
        <span class="badge">🔒 Nur interner Zugriff</span>
    </div>

    <div class="cards">
        <div class="card">
            <div class="card-icon">📢</div>
            <h3>Ankündigungen</h3>
            <div class="announcement">
                <h4>Neues Intranet online!</h4>
                <p>Das interne Webportal wurde erfolgreich eingerichtet. SSH-Zugang für Administratoren aktiv.</p>
            </div>
            <div class="announcement">
                <h4>IT-Wartungsfenster</h4>
                <p>Jeden Sonntag von 02:00 - 04:00 Uhr findet routinemäßige Wartung statt.</p>
            </div>
        </div>
        <div class="card">
            <div class="card-icon">🖥️</div>
            <h3>Serverinformationen</h3>
            <div class="server-info">
                Hostname: server.gruppe4.local<br>
                IP-Adresse: 172.16.40.10<br>
                Netzwerk: 172.16.40.0/24<br>
                Dienste: Apache2, OpenSSH<br>
                Firewall: UFW (aktiv)<br>
                Ports: 22 (SSH), 80 (HTTP)
            </div>
        </div>
        <div class="card">
            <div class="card-icon">👥</div>
            <h3>IT-Team Gruppe 4</h3>
            <p>Projektarbeit 4 - Webserver mit SSH-Fernadministration</p>
            <br>
            <p>
                👤 Jan (Teamleiter)<br>
                👤 Marian<br>
                👤 Mathias<br>
                👤 Marco
            </p>
        </div>
    </div>

    <footer>
        <p>Müller &amp; Partner GmbH &bull; Intranet &bull; Gruppenarbeit 4 &bull; Gruppe 4</p>
        <p style="margin-top:5px;">Server: server.gruppe4.local | Apache/2 | Linux</p>
    </footer>
</body>
</html>
HTMLEOF

    # Apache aktivieren
    a2ensite intranet.conf 2>/dev/null || true
    a2dissite 000-default.conf 2>/dev/null || true
    a2enmod rewrite
    
    systemctl enable apache2
    systemctl restart apache2
    
    print_step "Apache Webserver installiert und konfiguriert"
    print_step "Intranet-Seite erstellt unter /var/www/html/index.html"
    print_step "Webseite erreichbar unter: http://${SERVER_IP}"
}

# =============================================================================
# SCHRITT 5: Firewall (UFW) einrichten
# =============================================================================
configure_firewall() {
    print_header "SCHRITT 5: Firewall (UFW) konfigurieren"
    
    apt-get install -y ufw
    
    # Firewall reset
    ufw --force reset
    
    # Standard-Policy: alles ablehnen
    ufw default deny incoming
    ufw default allow outgoing
    
    # Nur SSH und HTTP erlauben
    ufw allow 22/tcp comment 'SSH Fernadministration'
    ufw allow 80/tcp comment 'HTTP Webserver'
    
    # Firewall aktivieren
    ufw --force enable
    
    print_step "Firewall UFW aktiviert"
    print_step "Eingehend erlaubt: Port 22 (SSH) und Port 80 (HTTP)"
    print_step "Alle anderen eingehenden Verbindungen: BLOCKIERT"
    
    echo -e "\n${CYAN}Aktuelle Firewall-Regeln:${NC}"
    ufw status verbose
}

# =============================================================================
# SCHRITT 6: Adminbenutzer erstellen
# =============================================================================
create_admin_user() {
    print_header "SCHRITT 6: Admin-Benutzer erstellen"
    
    # Admin-Benutzer erstellen
    if ! id "admin" &>/dev/null; then
        useradd -m -s /bin/bash -G sudo admin
        echo "admin:Admin1234!" | chpasswd
        print_step "Benutzer 'admin' erstellt (Passwort: Admin1234!)"
    else
        print_warning "Benutzer 'admin' existiert bereits"
    fi
    
    # Webadmin-Gruppe
    groupadd webadmin 2>/dev/null || true
    usermod -aG webadmin admin
    
    # Admin darf /var/www/html bearbeiten
    chown -R www-data:webadmin /var/www/html
    chmod -R 775 /var/www/html
    
    print_step "Gruppe 'webadmin' erstellt"
    print_step "Webadmin-Rechte auf /var/www/html vergeben"
}

# =============================================================================
# SCHRITT 7: Wireshark installieren (für Tests)
# =============================================================================
install_monitoring() {
    print_header "SCHRITT 7: Monitoring-Tools installieren"
    
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        wireshark \
        tcpdump \
        net-tools \
        curl \
        wget \
        htop
    
    # Wireshark für alle Benutzer freigeben
    echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections
    dpkg-reconfigure -f noninteractive wireshark-common 2>/dev/null || true
    usermod -aG wireshark admin 2>/dev/null || true
    
    print_step "Wireshark, tcpdump und weitere Tools installiert"
}

# =============================================================================
# ABSCHLUSS: Zusammenfassung
# =============================================================================
print_summary() {
    print_header "✅ SETUP ABGESCHLOSSEN - ZUSAMMENFASSUNG"
    
    echo -e "${GREEN}Server-Konfiguration:${NC}"
    echo -e "  📍 Hostname:    server.gruppe4.local"
    echo -e "  🌐 IP-Adresse:  ${SERVER_IP}"
    echo -e "  🔌 Netzwerk:    ${SUBNET}"
    echo -e ""
    echo -e "${GREEN}Dienste:${NC}"
    echo -e "  🔒 SSH:         Port 22   (aktiv: $(systemctl is-active ssh))"
    echo -e "  🌍 Apache HTTP: Port 80   (aktiv: $(systemctl is-active apache2))"
    echo -e "  🛡️  UFW Firewall:          (aktiv: $(systemctl is-active ufw))"
    echo -e ""
    echo -e "${GREEN}Zugangsdaten:${NC}"
    echo -e "  👤 Benutzer:    admin"
    echo -e "  🔑 Passwort:    Admin1234!"
    echo -e ""
    echo -e "${GREEN}Erreichbar über:${NC}"
    echo -e "  🌐 Webseite:    http://${SERVER_IP}"
    echo -e "  🌐 Webseite:    http://server.gruppe4.local (nach DNS-Eintrag)"
    echo -e "  💻 SSH:         ssh admin@${SERVER_IP}"
    echo -e ""
    echo -e "${YELLOW}Hinweis: Bitte das Admin-Passwort in der Produktion ändern!${NC}"
}

# =============================================================================
# HAUPTPROGRAMM
# =============================================================================
main() {
    print_header "Gruppenarbeit 4 - Webserver + SSH Setup"
    echo -e "Team: Jan, Marian, Mathias, Marco (Gruppe 4)"
    echo -e "Netzwerk: ${SUBNET} | Server: ${SERVER_IP}"
    
    check_root
    update_system
    configure_network
    configure_ssh
    configure_apache
    configure_firewall
    create_admin_user
    install_monitoring
    print_summary
}

main "$@"
