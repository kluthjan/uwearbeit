#!/bin/bash
# ==============================================================================
# Skript: setup_client.sh
# Beschreibung: Einrichtung & Test der Client-VM (Linux Client)
# Client-IP: 172.16.30.100 | Server-IP: 172.16.30.10
# ==============================================================================

set -e

echo "=== [1/4] Client-Pakete installieren ==="
sudo apt update
sudo apt install -y cifs-utils smbclient ping

echo "=== [2/4] Netzwerkverbindung zum Dateiserver prüfen ==="
SERVER_IP="172.16.30.10"
if ping -c 3 "$SERVER_IP" &>/dev/null; then
    echo "[ERFOLG] Server $SERVER_IP ist über Ping erreichbar!"
else
    echo "[FEHLER] Server $SERVER_IP ist NICHT erreichbar. Bitte VirtualBox Netzwerkeinstellungen prüfen!"
    exit 1
fi

echo "=== [3/4] Verfügbare Freigaben auf dem Server auflisten ==="
smbclient -L "//$SERVER_IP" -N || echo "[HINWEIS] Anonymes Listing eingeschränkt. Verwende benutzerbezogenes Listing."
smbclient -L "//$SERVER_IP" -U anna%Start123!

echo "=== [4/4] Test-Mounting der Freigaben ==="
sudo mkdir -p /mnt/public_share
sudo mkdir -p /mnt/mitarbeiter_share
sudo mkdir -p /mnt/leitung_share

echo "Versuche Freigabe 'public' als 'anna' zu mounten..."
sudo mount -t cifs "//$SERVER_IP/public" /mnt/public_share -o username=anna,password=Start123!
echo "[ERFOLG] 'public' erfolgreich gemountet unter /mnt/public_share!"
sudo umount /mnt/public_share

echo "Client-Einrichtung und Verbindungstest erfolgreich abgeschlossen!"
