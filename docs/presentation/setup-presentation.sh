#!/usr/bin/env bash
# Setup für ASI-Core Präsentation

set -e

echo "🎯 ASI-Core Präsentations-Setup"
echo "================================"

# Präsentations-Verzeichnis erstellen
echo "📁 Erstelle Präsentations-Struktur..."
mkdir -p docs/presentation/assets
mkdir -p docs/presentation/demo
mkdir -p docs/presentation/slides

# Live-Demo Umgebung
echo "🐍 Setup Python-Umgebung für Demo..."
if [ ! -d "presentation-env" ]; then
    python3 -m venv presentation-env
fi

echo "📦 Aktiviere Umgebung und installiere Dependencies..."
source presentation-env/bin/activate
pip install -r ../../requirements.txt

# Web-Demo vorbereiten
echo "🌐 Web-Demo Setup..."
cd ../../web
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "✅ Präsentations-Setup abgeschlossen!"
echo ""
echo "🚀 Quick-Start Commands:"
echo "  cd docs/presentation && python demo/demo_asi.py"
echo "  cd web && npm run dev"
echo "  ./start-pwa.sh"