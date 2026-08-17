#!/bin/bash
# ==============================================================================
# Skript: setup_samba_server.sh
# Beschreibung: Vollständiges Setup für den Samba-Dateiserver (Gruppe 3)
# Subnetz: 172.16.30.0/24 | Server-IP: 172.16.30.10
# Team: Jan, Marian, Mathias & Marco
# ==============================================================================

set -e

echo "=== [1/6] System-Aktualisierung & Paketinstallation ==="
if command -v apt &>/dev/null; then
    sudo apt update
    sudo apt install -y samba samba-common-bin cifs-utils ufw
elif command -v pacman &>/dev/null; then
    sudo pacman -Sy --noconfirm samba cifs-utils ufw || true
fi

echo "=== [2/6] Hostname & Netzwerkprüfung ==="
sudo hostnamectl set-hostname fileserver || true
echo "Hostname gesetzt: $(hostname)"

echo "=== [3/6] Erstellung der Linux-Gruppen & Benutzer ==="
# Gruppen anlegen
sudo groupadd -f mitarbeiter
sudo groupadd -f leitung

# Funktion zum Anlegen von Benutzern
create_user() {
    USERNAME=$1
    PASSWORD=$2
    PRIMARY_GROUP=$3
    
    if ! id "$USERNAME" &>/dev/null; then
        sudo useradd -m -g "$PRIMARY_GROUP" -s /usr/sbin/nologin "$USERNAME" 2>/dev/null || sudo useradd -m -g "$PRIMARY_GROUP" -s /bin/false "$USERNAME"
        echo "$USERNAME:$PASSWORD" | sudo chpasswd
        echo "Linux-Benutzer '$USERNAME' erstellt."
    else
        echo "Linux-Benutzer '$USERNAME' existiert bereits."
    fi

    # Samba-Passwort setzen
    (echo "$PASSWORD"; echo "$PASSWORD") | sudo smbpasswd -s -a "$USERNAME"
    sudo smbpasswd -e "$USERNAME"
    echo "Samba-Passwort für '$USERNAME' aktiviert."
}

# Benutzer laut Kundenauftrag anlegen (Standardpasswort: Start123!)
create_user "anna" "Start123!" "mitarbeiter"
create_user "bernd" "Start123!" "mitarbeiter"
create_user "chef" "Start123!" "leitung"

# Chef zusätzlich in die Gruppe 'mitarbeiter' aufnehmen
sudo usermod -aG mitarbeiter chef
echo "Benutzer 'chef' zur Gruppe 'mitarbeiter' hinzugefügt."

echo "=== [4/6] Anlegen der Freigabeverzeichnisse & POSIX-Rechte ==="
sudo mkdir -p /srv/samba/public
sudo mkdir -p /srv/samba/mitarbeiter
sudo mkdir -p /srv/samba/leitung

# Rechte setzen (mit SGID-Bit 2 für Gruppenvererbung)
sudo chown -R root:mitarbeiter /srv/samba/public
sudo chmod -R 2777 /srv/samba/public

sudo chown -R root:mitarbeiter /srv/samba/mitarbeiter
sudo chmod -R 2770 /srv/samba/mitarbeiter

sudo chown -R root:leitung /srv/samba/leitung
sudo chmod -R 2770 /srv/samba/leitung

echo "Dateirechte für /srv/samba erfolgreich konfiguriert."

echo "=== [5/6] Samba Konfiguration kopieren & prüfen ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config/smb.conf"

if [ -f "$CONFIG_FILE" ]; then
    sudo mkdir -p /etc/samba
    if [ -f /etc/samba/smb.conf ]; then
        sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak.$(date +%Y%m%d_%H%M%S)
    fi
    sudo cp "$CONFIG_FILE" /etc/samba/smb.conf
    echo "Neue smb.conf erfolgreich eingespielt."
fi

# Konfiguration testen
sudo testparm -s

echo "=== [6/6] Dienste neustarten ==="
if command -v systemctl &>/dev/null; then
    sudo systemctl restart smbd nmbd 2>/dev/null || sudo systemctl restart smb nmb 2>/dev/null || true
    sudo systemctl enable smbd nmbd 2>/dev/null || sudo systemctl enable smb nmb 2>/dev/null || true
fi

echo "=============================================================================="
echo "Samba-Server erfolgreich eingerichtet!"
echo "Server-IP: 172.16.30.10"
echo "Freigaben: \\172.16.30.10\public | \\172.16.30.10\mitarbeiter | \\172.16.30.10\leitung"
echo "=============================================================================="
