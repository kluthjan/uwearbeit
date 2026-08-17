#!/bin/bash
# =============================================================================
# Gruppenarbeit 4 - CLIENT-Setup Script
# Webserver mit SSH-Fernadministration
# Gruppe 4 - Jan, Marian, Mathias, Marco
# Netzwerk: 172.16.40.0/24  |  Client: 172.16.40.100
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

CLIENT_IP="172.16.40.100"
SERVER_IP="172.16.40.10"
SUBNET="172.16.40.0/24"
GATEWAY="172.16.40.1"

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
    
    ACTUAL_IF=$(ip -o link show | awk -F': ' '{print $2}' | grep -v lo | head -1)
    echo -e "${YELLOW}Erkannte Netzwerkschnittstelle: $ACTUAL_IF${NC}"
    
    if [ -d /etc/netplan ]; then
        cat > /etc/netplan/01-netcfg.yaml <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    ${ACTUAL_IF}:
      addresses:
        - ${CLIENT_IP}/24
      routes:
        - to: default
          via: ${GATEWAY}
      nameservers:
        addresses: [${SERVER_IP}, 8.8.8.8]
      dhcp4: false
EOF
        netplan apply
        
    elif [ -f /etc/network/interfaces ]; then
        cat > /etc/network/interfaces <<EOF
auto lo
iface lo inet loopback

auto ${ACTUAL_IF}
iface ${ACTUAL_IF} inet static
    address ${CLIENT_IP}
    netmask 255.255.255.0
    gateway ${GATEWAY}
    dns-nameservers ${SERVER_IP} 8.8.8.8
EOF
        ifdown ${ACTUAL_IF} 2>/dev/null || true
        ifup ${ACTUAL_IF}
    fi
    
    # Hosts-Datei aktualisieren
    sed -i '/gruppe4.local/d' /etc/hosts
    echo "${SERVER_IP}  server.gruppe4.local intranet.gruppe4.local" >> /etc/hosts
    
    hostnamectl set-hostname client.gruppe4.local
    
    print_step "Client-IP gesetzt: ${CLIENT_IP}"
    print_step "Server in /etc/hosts eingetragen"
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
# SCHRITT 3: SSH-Client und Tools installieren
# =============================================================================
install_tools() {
    print_header "SCHRITT 3: Tools installieren"
    
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        openssh-client \
        curl \
        wget \
        net-tools \
        wireshark \
        tcpdump \
        firefox-esr \
        htop
    
    # Wireshark für normale User erlauben
    echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections
    dpkg-reconfigure -f noninteractive wireshark-common 2>/dev/null || true
    
    print_step "SSH-Client, Browser und Monitoring-Tools installiert"
}

# =============================================================================
# SCHRITT 4: Verbindung zum Server testen
# =============================================================================
test_connection() {
    print_header "SCHRITT 4: Verbindung zum Server testen"
    
    echo -e "${CYAN}Test 1: Ping zum Server...${NC}"
    if ping -c 4 ${SERVER_IP}; then
        print_step "Ping erfolgreich!"
    else
        print_warning "Ping fehlgeschlagen - prüfe Netzwerkkonfiguration"
    fi
    
    echo -e "\n${CYAN}Test 2: Webserver erreichbar?${NC}"
    if curl -s --connect-timeout 5 http://${SERVER_IP} | grep -q "Müller" 2>/dev/null; then
        print_step "Webserver antwortet! Intranet erreichbar."
    elif curl -s --connect-timeout 5 http://${SERVER_IP} > /dev/null 2>&1; then
        print_step "Webserver antwortet auf Port 80!"
    else
        print_warning "Webserver nicht erreichbar - prüfe ob Apache auf Server läuft"
    fi
    
    echo -e "\n${CYAN}Test 3: SSH-Port erreichbar?${NC}"
    if nc -zv ${SERVER_IP} 22 2>&1 | grep -q "succeeded\|open"; then
        print_step "SSH Port 22 erreichbar!"
    else
        print_warning "SSH Port nicht erreichbar"
    fi
}

# =============================================================================
# SSH-SCHLÜSSEL GENERIEREN (optional für kennwortlose Anmeldung)
# =============================================================================
generate_ssh_key() {
    print_header "SSH-Schlüssel generieren (für Fernadministration)"
    
    USER_HOME=$(eval echo ~${SUDO_USER:-$USER})
    SSH_DIR="${USER_HOME}/.ssh"
    
    mkdir -p ${SSH_DIR}
    chmod 700 ${SSH_DIR}
    
    if [ ! -f "${SSH_DIR}/id_rsa" ]; then
        sudo -u ${SUDO_USER:-$USER} ssh-keygen -t rsa -b 4096 \
            -C "gruppe4-client@${CLIENT_IP}" \
            -f "${SSH_DIR}/id_rsa" \
            -N ""
        print_step "SSH-Schlüsselpaar generiert"
        echo -e "${YELLOW}Öffentlicher Schlüssel - zum Server kopieren mit:${NC}"
        echo -e "${CYAN}ssh-copy-id admin@${SERVER_IP}${NC}"
    else
        print_warning "SSH-Schlüssel existiert bereits"
    fi
}

# =============================================================================
# ZUSAMMENFASSUNG
# =============================================================================
print_summary() {
    print_header "✅ CLIENT-SETUP ABGESCHLOSSEN"
    
    echo -e "${GREEN}Client-Konfiguration:${NC}"
    echo -e "  📍 Hostname:    client.gruppe4.local"
    echo -e "  🌐 IP-Adresse:  ${CLIENT_IP}"
    echo -e "  🔌 Netzwerk:    ${SUBNET}"
    echo -e ""
    echo -e "${GREEN}Verbindung zum Server:${NC}"
    echo -e "  💻 SSH:         ssh admin@${SERVER_IP}"
    echo -e "  🌐 Webseite:    http://${SERVER_IP}"
    echo -e "  🌐 Webseite:    http://server.gruppe4.local"
    echo -e ""
    echo -e "${GREEN}Netzwerkanalyse:${NC}"
    echo -e "  📡 Wireshark:   wireshark (grafisch)"
    echo -e "  📡 tcpdump:     sudo tcpdump -i eth0 port 80"
    echo -e "  📡 SSH-Monitor: sudo tcpdump -i eth0 port 22"
}

main() {
    print_header "Gruppenarbeit 4 - Client-Setup"
    echo -e "Team: Jan, Marian, Mathias, Marco (Gruppe 4)"
    echo -e "Netzwerk: ${SUBNET} | Client: ${CLIENT_IP}"
    
    check_root
    update_system
    configure_network
    install_tools
    test_connection
    generate_ssh_key
    print_summary
}

main "$@"
