#!/usr/bin/env bash

# Schnelle Bereinigung für ASI-Core
# Ein-Zeilen-Bereinigung der häufigsten unnötigen Dateien

echo "🚀 ASI-Core Quick Cleanup"
echo "========================="

# Zähle vorher
before_size=$(du -sh . | cut -f1)
before_files=$(find . -type f | wc -l)

echo "📊 Vorher:"
echo "  Größe: $before_size"
echo "  Dateien: $before_files"
echo ""

# Sofortige Bereinigung
echo "🧹 Bereinige..."

# Python Cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# IDE und Temporäre Dateien
rm -rf .vscode .idea 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.log" -delete 2>/dev/null || true

# Test und Coverage
rm -rf .pytest_cache .coverage htmlcov 2>/dev/null || true

# Build Artefakte
rm -rf build dist *.egg-info 2>/dev/null || true

# Web Artefakte (nur wenn sie leer oder klein sind)
if [ -d "web/node_modules" ] && [ $(du -s web/node_modules 2>/dev/null | cut -f1) -lt 1000 ]; then
    rm -rf web/node_modules
fi

# Leere Verzeichnisse
find . -type d -empty -delete 2>/dev/null || true

# Zähle nachher
after_size=$(du -sh . | cut -f1)
after_files=$(find . -type f | wc -l)

echo ""
echo "📊 Nachher:"
echo "  Größe: $after_size"
echo "  Dateien: $after_files"
echo "  Entfernte Dateien: $((before_files - after_files))"

echo ""
echo "✅ Quick Cleanup abgeschlossen!"