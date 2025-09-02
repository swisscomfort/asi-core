#!/bin/bash
# ASI-Core Storacha Upload Script
# Automatisiert den Upload wichtiger Dateien zu Storacha

set -e

echo "🚀 ASI-Core Storacha Upload gestartet..."

# Erstelle Upload-Verzeichnis
UPLOAD_DIR="upload-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$UPLOAD_DIR"

# Kopiere wichtige Dateien
echo "📁 Sammle wichtige Dateien..."
cp README.md "$UPLOAD_DIR/"
cp main.py "$UPLOAD_DIR/"
cp requirements.txt "$UPLOAD_DIR/"
cp -r src/ "$UPLOAD_DIR/"
cp -r config/ "$UPLOAD_DIR/"

# Upload zu Storacha
echo "⬆️ Upload zu Storacha..."
URL=$(storacha up "$UPLOAD_DIR" | grep "https://storacha.link" | tail -1)

echo "✅ Upload erfolgreich!"
echo "🌐 Verfügbar unter: $URL"

# Speichere URL für späteren Zugriff
echo "$(date): $URL" >> storacha-uploads.log

echo "📝 Upload-Log aktualisiert: storacha-uploads.log"

# Optional: Cleanup
read -p "🗑️ Upload-Verzeichnis löschen? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$UPLOAD_DIR"
    echo "🧹 Upload-Verzeichnis gelöscht"
fi

echo "🎉 ASI-Core Upload abgeschlossen!"
