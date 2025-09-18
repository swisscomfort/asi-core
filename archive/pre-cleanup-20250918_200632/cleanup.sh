#!/usr/bin/env bash

# ASI-Core Projekt-Bereinigung
# Entfernt unnötige Dateien und optimiert für Production

set -e

echo "🧹 ASI-Core Projekt-Bereinigung"
echo "================================"

# Funktion für sichere Löschung mit Bestätigung
safe_remove() {
    local path="$1"
    if [ -e "$path" ]; then
        echo "  ❌ Entferne: $path"
        rm -rf "$path"
    fi
}

# 1. Python Cache und Bytecode
echo ""
echo "📦 Entferne Python-Cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true

# 2. IDE und Editor Dateien
echo ""
echo "🔧 Entferne IDE-Dateien..."
safe_remove ".vscode"
safe_remove ".idea"
safe_remove "*.swp"
safe_remove "*.swo"
safe_remove "*~"
safe_remove ".DS_Store"

# 3. Test-Coverage und Reports
echo ""
echo "📊 Entferne Test-Reports..."
safe_remove "htmlcov"
safe_remove ".coverage"
safe_remove "coverage.xml"
safe_remove ".pytest_cache"
safe_remove ".mypy_cache"
safe_remove ".ruff_cache"

# 4. Build-Artefakte
echo ""
echo "🏗️ Entferne Build-Artefakte..."
safe_remove "build"
safe_remove "dist"
safe_remove "*.spec"

# 5. Node/Web Artefakte (falls vorhanden)
echo ""
echo "🌐 Entferne Web-Build-Artefakte..."
safe_remove "web/node_modules"
safe_remove "web/dist"
safe_remove "web/.parcel-cache"
safe_remove "web/.vite"

# 6. Temporäre und Test-Dateien
echo ""
echo "🗑️ Entferne temporäre Dateien..."
safe_remove "data/test_wallet.json"
safe_remove "data/wallet_backup.json"
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.bak" -delete 2>/dev/null || true
find . -type f -name "*.log" -delete 2>/dev/null || true

# 7. Leere Verzeichnisse
echo ""
echo "📁 Entferne leere Verzeichnisse..."
find . -type d -empty -delete 2>/dev/null || true

# 8. Große Dateien identifizieren
echo ""
echo "📏 Große Dateien (>1MB):"
find . -type f -size +1M -not -path "./.*" -not -path "./web/node_modules/*" -exec ls -lh {} \; 2>/dev/null | awk '{print $9, $5}'

# 9. Statistik
echo ""
echo "📊 Projekt-Statistik nach Bereinigung:"
echo "  Python-Dateien: $(find . -name "*.py" | wc -l)"
echo "  JS/JSX-Dateien: $(find . -name "*.js" -o -name "*.jsx" | wc -l)"
echo "  Gesamtgröße: $(du -sh . | cut -f1)"

echo ""
echo "✅ Bereinigung abgeschlossen!"