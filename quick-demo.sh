#!/bin/bash
"""
🎬 ASI-Core Interactive Demo
Schneller Einstieg für neue Entwickler - Erfolg in 2 Minuten!
"""

set -e

echo "🎬 ASI-Core Interactive Demo starting..."
echo "=================================="
echo ""

# Überprüfe ob System bereit ist
if [ ! -f "main.py" ]; then
    echo "❌ main.py nicht gefunden. Bitte aus dem asi-core Verzeichnis ausführen."
    exit 1
fi

# Erstelle Demo-Daten Verzeichnis falls nicht vorhanden
mkdir -p data/demo

echo "🚀 Starte ASI-Core Demo-Modus..."
echo ""

# Starte interaktive Demo
python main.py minimal

echo ""
echo "🎉 Demo erfolgreich abgeschlossen!"
echo ""
echo "💡 Nächste Schritte für Entwickler:"
echo "   📖 Lies CONTRIBUTING.md"
echo "   🎯 Finde Good First Issues: https://github.com/swisscomfort/asi-core/issues"
echo "   🛠️  Erstelle deine erste Contribution!"
echo ""
echo "🌟 Happy Coding! 🌟"