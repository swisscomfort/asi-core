#!/usr/bin/env bash

# Bereitet ASI-Core für Production vor
# Entfernt ALLE nicht essentiellen Dateien

echo "🚀 Production-Vorbereitung für ASI-Core"
echo "========================================"
echo ""
echo "⚠️  WARNUNG: Dies entfernt alle Entwicklungs- und Test-Dateien!"
read -p "Fortfahren? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Abgebrochen."
    exit 1
fi

# Backup erstellen
echo "💾 Erstelle Backup..."
tar -czf ../asi-core-backup-$(date +%Y%m%d-%H%M%S).tar.gz .

# Entferne Entwicklungs-Dateien
echo ""
echo "🗑️ Entferne Entwicklungs-Dateien..."

# Test-Dateien
rm -rf tests/
rm -rf test_*.py
rm -f */test_*.py

# Dokumentation (optional behalten)
# rm -rf docs/

# GitHub-spezifische Dateien
rm -rf .github/
rm -f .gitignore
rm -f .gitattributes

# Entwicklungs-Configs
rm -f .editorconfig
rm -f .prettierrc
rm -f .eslintrc*
rm -f tsconfig.json
rm -f jest.config.js

# Example/Template Dateien
rm -f .env.example
rm -f config/secrets.example.json
rm -f */example_*.py

# Docker (falls nicht benötigt)
# rm -f Dockerfile
# rm -f docker-compose*.yml

# Scripts (selektiv)
rm -f setup.sh  # Setup nur einmal nötig
# start.sh behalten für Production

# README und Lizenz (optional behalten)
# rm -f README.md
# rm -f LICENSE

# Minimiere requirements.txt
echo ""
echo "📦 Optimiere Dependencies..."
cat > requirements_prod.txt << 'EOF'
# ASI Core - Production Dependencies Only
flask>=3.0.0
flask-cors>=4.0.0
requests>=2.31.0
numpy>=1.26.0
python-dotenv>=1.0.0
web3>=6.11.0
eth-account>=0.9.0
ipfshttpclient>=0.7.0
EOF

mv requirements_prod.txt requirements.txt

echo ""
echo "✅ Production-Vorbereitung abgeschlossen!"
echo ""
echo "📊 Finale Größe: $(du -sh . | cut -f1)"