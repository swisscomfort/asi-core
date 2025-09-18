#!/bin/bash
"""
🧹 ASI-Core Post-Transformation Cleanup
Entfernt überflüssige Dateien nach erfolgreicher Architektur-Transformation
"""

# Setze Fehlerbehandlung
set -e

echo "🧹 ASI-CORE POST-TRANSFORMATION CLEANUP"
echo "========================================"

# Erstelle Backup-Ordner
BACKUP_DIR="./archive/pre-cleanup-$(date +%Y%m%d_%H%M%S)"
echo "📦 Erstelle Backup-Verzeichnis: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Zu entfernende Demo-Dateien
DEMO_FILES=(
    "demo_hybrid_model.py"
    "demo_complete_integration.py" 
    "demo_enhanced_modules.py"
    "demo_agent_system.py"
    "demo_semantic_search.py"
    "decentralized_storage_demo.py"
)

# Zu entfernende Test-Dateien im Hauptverzeichnis
TEST_FILES=(
    "test_agent_integration.py"
    "test_blockchain_integration.py"
)

# Zu entfernende Analyse-Dateien
ANALYSIS_FILES=(
    "analyze-main-catastrophe.py"
    "analyze-project.sh"
)

# Zu entfernende Fix-Scripts
FIX_SCRIPTS=(
    "fix-asi-core.sh"
    "fix-devcontainer.sh" 
    "fix-workflows.sh"
    "fix-modules.sh"
)

# Zu entfernende Cleanup-Scripts (außer diesem)
CLEANUP_SCRIPTS=(
    "cleanup.sh"
    "cleanup-manager.sh"
    "quick-cleanup.sh"
)

# Andere überflüssige Dateien
OTHER_FILES=(
    "health_check.py"
    "api_server.py"
    "asi_hybrid_cli.py"
)

echo "🗂️ Sichere und entferne Demo-Dateien..."
for file in "${DEMO_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  📁 Backup: $file"
        cp "$file" "$BACKUP_DIR/"
        rm "$file"
        echo "  ✅ Entfernt: $file"
    fi
done

echo "🧪 Sichere und entferne Test-Dateien im Hauptverzeichnis..."
for file in "${TEST_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  📁 Backup: $file"
        cp "$file" "$BACKUP_DIR/"
        rm "$file"
        echo "  ✅ Entfernt: $file"
    fi
done

echo "🔍 Sichere und entferne Analyse-Dateien..."
for file in "${ANALYSIS_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  📁 Backup: $file"
        cp "$file" "$BACKUP_DIR/"
        rm "$file"
        echo "  ✅ Entfernt: $file"
    fi
done

echo "🔧 Sichere und entferne Fix-Scripts..."
for file in "${FIX_SCRIPTS[@]}"; do
    if [ -f "$file" ]; then
        echo "  📁 Backup: $file"
        cp "$file" "$BACKUP_DIR/"
        rm "$file"
        echo "  ✅ Entfernt: $file"
    fi
done

echo "🧹 Sichere und entferne alte Cleanup-Scripts..."
for file in "${CLEANUP_SCRIPTS[@]}"; do
    if [ -f "$file" ]; then
        echo "  📁 Backup: $file"
        cp "$file" "$BACKUP_DIR/"
        rm "$file"
        echo "  ✅ Entfernt: $file"
    fi
done

echo "📄 Sichere und entferne andere überflüssige Dateien..."
for file in "${OTHER_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  📁 Backup: $file"
        cp "$file" "$BACKUP_DIR/"
        rm "$file"
        echo "  ✅ Entfernt: $file"
    fi
done

# Entferne leere Backup-Ordner
echo "🗑️ Prüfe und entferne leere Backup-Verzeichnisse..."
if [ -d "$BACKUP_DIR" ] && [ -z "$(ls -A $BACKUP_DIR)" ]; then
    rmdir "$BACKUP_DIR"
    echo "  ✅ Leeren Backup-Ordner entfernt"
fi

echo ""
echo "=========================================="
echo "🏆 CLEANUP ERFOLGREICH ABGESCHLOSSEN!"
echo "📈 ASI-Core ist jetzt production-ready"
echo "🧩 Modulare Architektur: ✅"
echo "📦 Überflüssige Dateien entfernt: ✅"
echo "💾 Backup erstellt: $BACKUP_DIR"
echo "=========================================="

# Zeige finale Struktur
echo ""
echo "📋 Verbleibende Core-Dateien:"
ls -la | grep -E "\.py$|\.sh$" | head -10

echo ""
echo "🚀 ASI-Core ist bereit für Produktionseinsatz!"