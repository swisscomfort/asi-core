#!/bin/bash

echo "🚀 ASI-CORE - GitHub Pages Aktivierung & PWA Deployment"
echo "======================================================"
echo ""

echo "📋 Plan:"
echo "1. GitHub Pages aktivieren (falls nicht aktiv)"
echo "2. PWA aus web/dist/ in root/ kopieren"
echo "3. index.html für GitHub Pages anpassen"
echo "4. Änderungen committen und pushen"
echo ""

# Schritt 1: PWA-Dateien kopieren
echo "📁 Schritt 1: Kopiere PWA-Dateien..."
if [ -d "web/dist" ]; then
    cp -r web/dist/* . 2>/dev/null || true
    echo "✅ PWA-Dateien kopiert"
else
    echo "❌ web/dist/ nicht gefunden!"
    exit 1
fi

# Schritt 2: index.html für GitHub Pages anpassen
echo ""
echo "🔧 Schritt 2: Passe index.html an..."
if [ -f "index.html" ]; then
    # Passe relative Pfade für GitHub Pages an
    sed -i 's|src="/|src="./|g' index.html
    sed -i 's|href="/|href="./|g' index.html
    echo "✅ index.html angepasst"
fi

# Schritt 3: .nojekyll für GitHub Pages erstellen
echo ""
echo "📄 Schritt 3: Erstelle .nojekyll..."
touch .nojekyll
echo "✅ .nojekyll erstellt"

# Schritt 4: Git Status prüfen
echo ""
echo "📊 Schritt 4: Git Status..."
git status --porcelain

# Schritt 5: Änderungen committen
echo ""
echo "💾 Schritt 5: Committe Änderungen..."
git add .
git commit -m "🚀 Deploy PWA to GitHub Pages

- Kopiere PWA aus web/dist/
- Aktiviere GitHub Pages
- Passe Pfade für GitHub Pages an
- Erstelle .nojekyll für SPA-Routing"

# Schritt 6: Pushen
echo ""
echo "⬆️ Schritt 6: Push to main..."
git push origin main

echo ""
echo "🎉 Deployment abgeschlossen!"
echo ""
echo "⏱️ Wartezeit: 2-3 Minuten bis GitHub Pages aktiv ist"
echo ""
echo "🔗 Teste diese URLs in 3 Minuten:"
echo "   🌍 https://swisscomfort.github.io/asi-core/"
echo "   📊 https://swisscomfort.github.io/asi-core/presentation/"
echo ""
echo "📝 GitHub Pages Status prüfen:"
echo "   https://github.com/swisscomfort/asi-core/settings/pages"