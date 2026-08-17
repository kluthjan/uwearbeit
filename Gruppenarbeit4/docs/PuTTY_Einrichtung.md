# PuTTY Einrichtung und Nutzung

PuTTY ist ein kostenloser SSH-Client für Windows, mit dem man sich sicher auf Linux-Server (wie unsere Server-VM) aufschalten kann.

## 1. PuTTY herunterladen und starten
1. Laden Sie PuTTY von der offiziellen Webseite herunter: [putty.org](https://www.putty.org/)
2. Installieren Sie das Programm oder starten Sie die portable `.exe`-Datei.

## 2. Verbindung zum Server herstellen
Da sich unser Server in einem internen VirtualBox-Netzwerk (`172.16.40.0/24`) befindet, muss PuTTY in der Regel auf einer Maschine ausgeführt werden, die Zugriff auf dieses Netz hat (z.B. ein Windows-Client innerhalb des Netzwerks oder durch Port-Forwarding vom Host-PC).

1. Starten Sie PuTTY.
2. Es öffnet sich das Fenster **PuTTY Configuration**.
3. **Host Name (or IP address):** Geben Sie die IP des Servers ein: `172.16.40.10`
4. **Port:** Belassen Sie diesen auf `22`.
5. **Connection type:** Stellen Sie sicher, dass **SSH** ausgewählt ist.
6. (Optional) Unter **Saved Sessions** können Sie einen Namen (z.B. "Intranet-Server") eintragen und auf **Save** klicken, um die IP für das nächste Mal zu speichern.
7. Klicken Sie ganz unten auf **Open**.

## 3. Der Login-Prozess
1. Beim allerersten Verbindungsaufbau erscheint eine Sicherheitswarnung (Security Alert). PuTTY fragt, ob Sie dem kryptografischen Fingerabdruck des Servers vertrauen. Klicken Sie auf **Accept** (Akzeptieren).
2. Ein schwarzes Konsolenfenster öffnet sich mit der Frage: `login as:`
3. Tippen Sie den Benutzernamen ein (z.B. `admin` oder `server`) und drücken Sie Enter.
4. Nun wird das Passwort abgefragt. **Wichtig:** Unter Linux wird bei der Passworteingabe aus Sicherheitsgründen *nichts* angezeigt (auch keine Sternchen). Tippen Sie das Passwort blind ein und drücken Sie Enter.
5. Sie sind nun erfolgreich mit dem Server verbunden und können Befehle ausführen.
