# Testen und Nutzung der Infrastruktur

Nachdem die Server- und Client-VMs erfolgreich eingerichtet wurden, beschreibt dieses Dokument, wie die Umgebung getestet und produktiv genutzt wird.

---

## 1. Den Webserver testen

Die Client-VM ist mit einer grafischen Oberfläche (`ubuntu-desktop`) und dem **Firefox-Browser** ausgestattet.

1. Starten Sie die **Client-VM**.
2. Öffnen Sie den vorinstallierten Browser **Firefox**.
3. Geben Sie in die Adresszeile die IP-Adresse des Servers ein: 
   `http://172.16.40.10`
4. Der Browser sollte nun die Standard-Testseite oder die gehostete Startseite ("Willkommen im Intranet der Müller & Partner GmbH") anzeigen.

---

## 2. Eigene Webseiten hosten

Der Apache-Webserver lädt standardmäßig alle Dateien, die im Verzeichnis `/var/www/html/` auf dem Server liegen. Um eine eigene Webseite zu veröffentlichen, müssen Sie Ihre HTML-, CSS- und Bild-Dateien in dieses Verzeichnis übertragen.

### 2.1 Hochladen per SFTP (z. B. mit FileZilla / WinSCP)
Da der Server einen SSH-Dienst betreibt, können Sie sich per SFTP verbinden:
- **Host / Server:** `172.16.40.10`
- **Benutzername:** `admin` (oder der eingerichtete Benutzer)
- **Passwort:** *Ihr festgelegtes Passwort*
- **Port:** `22`

Ziehen Sie Ihre fertigen Web-Dateien (z. B. `index.html`) per Drag & Drop in den Ordner `/var/www/html/`.

### 2.2 Hochladen per Kommandozeile (SCP)
Alternativ können Sie Dateien aus einem Terminal heraus auf den Server kopieren:
```bash
scp index.html admin@172.16.40.10:/var/www/html/
```

---

## 3. SSH-Zugriff und PuTTY

Um den Server aus der Ferne zu warten oder Befehle darauf auszuführen, nutzen wir **SSH**. 

### 3.1 Von der Client-VM (Linux Terminal)
Da die Client-VM auf Ubuntu basiert, ist ein SSH-Client bereits integriert. Öffnen Sie ein Terminal und tippen Sie:
```bash
ssh admin@172.16.40.10
```

### 3.2 Nutzung von PuTTY
Falls Sie das Netzwerk von einem Windows-Rechner aus administrieren möchten, können Sie das Programm **PuTTY** verwenden:
1. Tragen Sie unter *Host Name (or IP address)* die IP `172.16.40.10` ein.
2. Stellen Sie sicher, dass der *Port* auf `22` und der *Connection type* auf `SSH` steht.
3. Klicken Sie auf **Open**.
4. Loggen Sie sich mit dem Benutzernamen `admin` und Ihrem Passwort ein.

*(Hinweis: Auf der Ubuntu Client-VM ist PuTTY ebenfalls installiert und kann über das Anwendungsmenü gestartet werden, auch wenn das native Linux-Terminal oft komfortabler ist.)*
