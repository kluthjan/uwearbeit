# Manuelle Installationsanleitung: Webserver & SSH

Diese Anleitung beschreibt detailliert die manuellen Schritte zur Einrichtung der Server-VM (Ubuntu 22.04 LTS), wie sie auch von unseren automatisierten Skripten (`server_setup.sh`) durchgeführt werden. Sie dient als Referenz und Leitfaden für die manuelle Konfiguration.

---

## 1. System aktualisieren

Bevor neue Pakete installiert werden, sollte das System auf den neuesten Stand gebracht werden.

```bash
# Paketlisten aktualisieren
sudo apt-get update

# Installierte Pakete aktualisieren
sudo apt-get upgrade -y
```

---

## 2. SSH-Server installieren & konfigurieren

Um die Fernwartung zu ermöglichen und abzusichern, wird OpenSSH installiert.

### Installation
```bash
sudo apt-get install -y openssh-server
```

### Konfiguration anpassen
Die Hauptkonfigurationsdatei von SSH liegt unter `/etc/ssh/sshd_config`. Wir empfehlen, vorab ein Backup zu erstellen:

```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo nano /etc/ssh/sshd_config
```

**Wichtige Anpassungen in der Datei:**
```ini
# Port 22 beibehalten
Port 22

# Root-Login aus Sicherheitsgründen verbieten
PermitRootLogin no

# Passwort-Authentifizierung erlauben (für unser Projekt)
PasswordAuthentication yes

# Leere Passwörter verbieten
PermitEmptyPasswords no
```

### SSH-Banner (Willkommensnachricht) erstellen
Um Benutzern beim Login einen Hinweis anzuzeigen:
```bash
sudo nano /etc/ssh/banner
```
Inhalt:
```text
  ====================================================
   Müller & Partner GmbH - Internes Serversystem
   NUR autorisierter Zugriff!
  ====================================================
```
Anschließend in der `/etc/ssh/sshd_config` aktivieren:
```ini
Banner /etc/ssh/banner
```

### SSH-Dienst neu starten
```bash
sudo systemctl enable ssh
sudo systemctl restart ssh
```

---

## 3. Apache Webserver installieren & konfigurieren

### Installation
```bash
sudo apt-get install -y apache2
```

### Intranet-Seite anlegen
Wir erstellen eine einfache Startseite im Web-Verzeichnis:

```bash
sudo nano /var/www/html/index.html
```
*Beispiel-Inhalt:*
```html
<!DOCTYPE html>
<html>
<head>
    <title>Intranet | Gruppe 4</title>
</head>
<body>
    <h1>Willkommen im Intranet der Müller & Partner GmbH</h1>
    <p>Diese Seite wird von Apache2 auf Ubuntu bereitgestellt.</p>
</body>
</html>
```

### Apache VirtualHost konfigurieren (Optional, aber empfohlen)
```bash
sudo nano /etc/apache2/sites-available/intranet.conf
```
*Beispiel-Inhalt:*
```apache
<VirtualHost *:80>
    ServerName server.gruppe4.local
    DocumentRoot /var/www/html
    
    <Directory /var/www/html>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```
Konfiguration aktivieren und Apache neu starten:
```bash
sudo a2ensite intranet.conf
sudo systemctl reload apache2
```

---

## 4. Firewall (UFW) einrichten

UFW (Uncomplicated Firewall) blockiert alle eingehenden Verbindungen, außer jenen, die wir explizit erlauben.

```bash
# Standard-Regeln festlegen
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Benötigte Ports freigeben
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP Webserver
sudo ufw allow 443/tcp     # HTTPS Webserver (optional)

# Nur Zugriff aus dem internen Netz für Port 80 erlauben (Beispiel)
sudo ufw allow from 172.16.40.0/24 to any port 80

# Firewall aktivieren
sudo ufw enable
```

---

## 5. Neuen Benutzer (Administrator) erstellen

Es ist eine Best Practice, einen speziellen Admin-Benutzer anzulegen und diesem Rechte für das Web-Verzeichnis zu geben.

### Benutzer anlegen
```bash
# Benutzer 'admin' erstellen und Home-Verzeichnis anlegen
sudo useradd -m -s /bin/bash admin

# Passwort für 'admin' setzen
sudo passwd admin
```

### Sudo-Rechte vergeben
Damit der Benutzer administrative Aufgaben übernehmen kann:
```bash
sudo usermod -aG sudo admin
```

### Rechte für das Web-Verzeichnis vergeben
Damit der Admin-Nutzer die Webseite bearbeiten kann, erstellen wir eine Gruppe und weisen Rechte zu:

```bash
# Neue Gruppe für Web-Administratoren
sudo groupadd webadmin

# Benutzer 'admin' zur Gruppe hinzufügen
sudo usermod -aG webadmin admin

# Das Web-Verzeichnis der neuen Gruppe übergeben
sudo chown -R www-data:webadmin /var/www/html

# Schreibrechte für die Gruppe setzen (chmod 775)
sudo chmod -R 775 /var/www/html
```

---

## 6. Webseite hochladen (SFTP / SCP)

Um eine selbst erstellte Webseite auf den Server hochzuladen, empfiehlt sich die Nutzung von SFTP (Secure File Transfer Protocol). Da der SSH-Server bereits konfiguriert ist, funktioniert SFTP out-of-the-box.

### Option 1: Hochladen mit grafischen Programmen (z. B. FileZilla / WinSCP)
1. **Host:** IP des Servers (z. B. `172.16.40.10`)
2. **Benutzername:** `admin` (oder der zuvor erstellte Benutzer)
3. **Passwort:** *Das festgelegte Passwort*
4. **Port:** `22` (oder Ihr spezifischer SSH-Port)

Nach der Verbindung navigieren Sie auf der Server-Seite in das Verzeichnis `/var/www/html` und ziehen Ihre HTML/CSS/JS-Dateien (z. B. eine fertige `index.html`) per Drag & Drop in das Verzeichnis.

### Option 2: Hochladen über die Kommandozeile (SCP)
Von einem Client-Rechner (z. B. der Client-VM oder Ihrem Host-PC) aus können Sie Dateien auch per Befehlszeile kopieren:

```bash
# Kopiert eine lokale Datei index.html auf den Server in das Web-Verzeichnis
scp /pfad/zur/lokalen/index.html admin@172.16.40.10:/var/www/html/
```
*Hinweis: Der Benutzer `admin` benötigt Schreibrechte auf `/var/www/html`, wie in Schritt 5 konfiguriert.*

---

## 7. Überprüfung der Dienste

Nach Abschluss der Installation sollten Sie den Status der Dienste überprüfen:

```bash
# Apache Status prüfen
sudo systemctl status apache2

# SSH Status prüfen
sudo systemctl status ssh

# Firewall Status prüfen
sudo ufw status verbose
```
