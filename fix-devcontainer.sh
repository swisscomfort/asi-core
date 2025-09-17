#!/usr/bin/env bash
echo "=== Codespace Recovery Mode Fix ==="

# 1. Check current devcontainer config
if [ -f .devcontainer/devcontainer.json ]; then
    echo "❌ Defekte devcontainer config gefunden"
    echo "📄 Backup erstellen..."
    cp .devcontainer/devcontainer.json .devcontainer/devcontainer.json.backup
    
    # 2. Minimal working config erstellen
    cat > .devcontainer/devcontainer.json << 'EOF'
{
    "name": "ASI-Core Development",
    "image": "mcr.microsoft.com/devcontainers/python:3.11",
    "features": {
        "ghcr.io/devcontainers/features/node:1": {
            "version": "18"
        }
    },
    "postCreateCommand": "./setup.sh",
    "customizations": {
        "vscode": {
            "extensions": [
                "ms-python.python",
                "bradlc.vscode-tailwindcss"
            ]
        }
    }
}
EOF
    echo "✅ Neue devcontainer.json erstellt"
else
    echo "ℹ️  Keine devcontainer config gefunden - Standard verwenden"
fi

echo "🔄 NÄCHSTER SCHRITT:"
echo "   Drücke Strg+Shift+P → 'Rebuild Container'"
echo "   Oder klicke 'Rebuild Container' im Popup"