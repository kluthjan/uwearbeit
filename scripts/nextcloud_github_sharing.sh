#!/bin/bash
# ==============================================================================
# Skript: nextcloud_github_sharing.sh
# Beschreibung: Git-Repository Initialisierung & Nextcloud WebDAV-Upload-Guide
# ==============================================================================

echo "=============================================================================="
echo " GITHUB & NEXTCLOUD SHARING HELPER (MÜLLER & PARTNER GMBH - GRUPPE 3)"
echo "=============================================================================="

PROJECT_DIR="/home/jank/Schreibtisch/uweprojekt"

echo "=== [1/2] Git-Repository vorbereiten ==="
cd "$PROJECT_DIR"
if [ ! -d ".git" ]; then
    git init
    echo "Neues Git-Repository initialisiert."
fi

# .gitignore erstellen
cat << 'EOF' > .gitignore
*.tmp.html
*.log
.DS_Store
EOF

git add .
git commit -m "Projektarbeit 3: Dateiserver - Skripte, Dokumentation & Präsentation" || echo "Keine neuen Änderungen zu committen."

echo ""
echo "[HINWEIS FÜR GITHUB UPLOAD]:"
echo "1. Erstelle auf GitHub ein neues Repository namens 'uweprojekt'."
echo "2. Führe im Terminal folgende Befehle aus:"
echo "   git remote add origin https://github.com/DEIN-BENUTZERNAME/uweprojekt.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo "=============================================================================="

echo ""
echo "=== [2/2] Nextcloud Upload (decents.org) ==="
echo "Deine generierten PDF-Dateien bereit zum Versenden:"
echo " 1. $PROJECT_DIR/docs/Windows_VirtualBox_Setup_Anleitung.pdf (FÜR MARIAN, MATHIAS, MARCO)"
echo " 2. $PROJECT_DIR/docs/Projektdokumentation_Dateiserver_Gruppe3.pdf"
echo " 3. $PROJECT_DIR/docs/Lernhilfe_und_Erklaerung_Dateiserver.pdf"
echo " 4. $PROJECT_DIR/presentation/Dozentenfragen_Vorbereitung.pdf"
echo ""
echo "[BEISPIEL BEFEHL FÜR AUTOMATISCHEN NEXTCLOUD UPLOAD VIA WEBDAV]:"
echo "Ersetze 'DEIN_BENUTZER' und 'DEIN_PASSWORT/TOKEN' durch deine Nextcloud-Daten:"
echo ""
echo "curl -u 'BENUTZER:PASSWORT' -T '$PROJECT_DIR/docs/Windows_VirtualBox_Setup_Anleitung.pdf' 'https://decents.org/remote.php/dav/files/BENUTZER/Windows_VirtualBox_Setup_Anleitung.pdf'"
echo "=============================================================================="
