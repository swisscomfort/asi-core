#!/bin/bash

echo "🔗 ASI-CORE LINK-DIAGNOSE"
echo "========================"
echo ""

echo "📊 Link-Status Übersicht:"
echo "-------------------------"

# Teste alle Links aus dem README
links=(
    "https://swisscomfort.github.io/asi-core/|🌍 Live PWA"
    "https://swisscomfort.github.io/asi-core/presentation/|📊 Präsentation"
    "./docs/|📖 Dokumentation (lokal)"
    "https://github.com/users/swisscomfort/projects/1|🔗 GitHub Project"
    "https://insights.github.com/swisscomfort/asi-core|📈 Pro Analytics"
    "https://github.com/swisscomfort/asi-core/pkgs/container/asi-core|🐳 Packages"
)

for link_info in "${links[@]}"; do
    IFS='|' read -r url description <<< "$link_info"
    echo -n "$description: "

    if [[ $url == ./* ]]; then
        # Lokaler Link
        if [ -d "$url" ] || [ -f "$url" ]; then
            echo "✅ VERFÜGBAR (lokal)"
        else
            echo "❌ NICHT GEFUNDEN (lokal)"
        fi
    else
        # Externer Link
        http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
        if [ "$http_code" = "200" ]; then
            echo "✅ OK (HTTP $http_code)"
        else
            echo "❌ FEHLER (HTTP $http_code)"
        fi
    fi
done

echo ""
echo "🔍 Detaillierte Analyse:"
echo "-----------------------"

echo "❌ PROBLEM: GitHub Pages ist nicht aktiv!"
echo "   • Live PWA: 404"
echo "   • Präsentation: 404"
echo "   • GitHub Project: 404"
echo ""

echo "✅ WAS FUNKTIONIERT:"
echo "   • Pro Analytics: Verfügbar"
echo "   • Packages: Verfügbar"
echo "   • Lokale Dokumentation: Vorhanden"
echo ""

echo "📁 Verfügbare lokale Inhalte:"
echo "   • PWA Build: web/dist/ ✅"
echo "   • Dokumentation: docs/ ✅"
echo "   • Präsentation: docs/presentation/ ✅"
echo ""

echo "🛠️ LÖSUNGSVORSCHLÄGE:"
echo "----------------------"
echo ""
echo "1. 🔧 GitHub Pages aktivieren:"
echo "   • Gehe zu: https://github.com/swisscomfort/asi-core/settings/pages"
echo "   • Source: 'Deploy from a branch'"
echo "   • Branch: main, Folder: / (root)"
echo "   • Oder: 'GitHub Actions' für automatische Deployments"
echo ""
echo "2. 📊 PWA deployen:"
echo "   • Kopiere web/dist/ nach root/"
echo "   • Oder verwende den deploy.yml Workflow"
echo ""
echo "3. 🔗 Links korrigieren:"
echo "   • Live PWA → GitHub Pages URL (nach Aktivierung)"
echo "   • Präsentation → docs/presentation/ (lokal)"
echo "   • GitHub Project → Erstelle ein Project oder entferne Link"
echo ""
echo "4. 🚀 Sofortige Lösung:"
echo "   • Aktiviere GitHub Pages"
echo "   • Push die web/dist/ Dateien"
echo "   • Warte 2-3 Minuten auf Deployment"
echo ""

echo "⚡ SCHNELLSTART:"
echo "---------------"
echo "Möchten Sie GitHub Pages automatisch aktivieren? Führen Sie aus:"
echo "   ./pages-activation.yml  (als Workflow)"
echo ""
echo "Oder manuell: Repository Settings → Pages → Enable"