#!/bin/bash

echo "🔐 GitHub Fine-Grained Token Setup - Nach Erstellung"
echo "=================================================="
echo ""

# Schritt 1: Token als Repository Secret hinzufügen
echo "📋 SCHRITT 1: Repository Secret hinzufügen"
echo "==========================================="
echo "1. Gehe zu: https://github.com/swisscomfort/asi-core/settings/secrets/actions"
echo "2. Klicke 'New repository secret'"
echo "3. Name: GITHUB_TOKEN"
echo "4. Value: [Deinen kopierten Token hier einfügen]"
echo "5. Klicke 'Add secret'"
echo ""

# Schritt 2: Lokalen Token setzen
echo "📋 SCHRITT 2: Lokalen Token setzen"
echo "=================================="
echo "Führe diesen Befehl aus (ersetze YOUR_TOKEN):"
echo ""
echo "export GITHUB_TOKEN=\"ghp_xxxxxxxxxxxxxxxxxxxx\""
echo ""
echo "Für permanente Speicherung:"
echo "echo 'export GITHUB_TOKEN=\"ghp_xxxxxxxxxxxxxxxxxxxx\"' >> ~/.bashrc"
echo "source ~/.bashrc"
echo ""

# Schritt 3: GitHub Pages aktivieren
echo "📋 SCHRITT 3: GitHub Pages aktivieren"
echo "====================================="
echo "1. Gehe zu: https://github.com/swisscomfort/asi-core/settings/pages"
echo "2. Source: GitHub Actions (NICHT 'Deploy from a branch')"
echo "3. Speichern"
echo ""

# Schritt 4: Token testen
echo "📋 SCHRITT 4: Token testen"
echo "=========================="
echo "Führe aus: ./test-github-token.sh"
echo ""

# Schritt 5: PWA Deployment triggern
echo "📋 SCHRITT 5: PWA Deployment triggern"
echo "====================================="
echo "Nach erfolgreichem Setup:"
echo "1. Git push (automatisches Deployment)"
echo "2. Oder manuell: ./trigger-pwa-deploy.sh"
echo ""

echo "🎯 QUICK TEST:"
echo "=============="
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN ist gesetzt: ${GITHUB_TOKEN:0:8}..."
    
    # Test API Access
    response=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
        https://api.github.com/repos/swisscomfort/asi-core)
    
    if echo "$response" | grep -q '"name"'; then
        echo "✅ Repository-Zugriff funktioniert!"
        
        # Test Actions API
        actions_response=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
            https://api.github.com/repos/swisscomfort/asi-core/actions/runs?per_page=1)
        
        if echo "$actions_response" | grep -q '"workflow_runs"'; then
            echo "✅ Actions API funktioniert!"
            echo ""
            echo "🎉 TOKEN IST BEREIT!"
            echo ""
            echo "🚀 Triggere PWA Deployment:"
            echo "git add . && git commit -m 'Token setup' && git push"
        else
            echo "❌ Actions API Fehler"
        fi
    else
        echo "❌ Repository-Zugriff fehlgeschlagen"
        echo "Response: $response"
    fi
else
    echo "❌ Token noch nicht gesetzt"
    echo "Führe aus: export GITHUB_TOKEN=\"dein_token\""
fi

echo ""
echo "📞 HILFE BEI PROBLEMEN:"
echo "======================"
echo "1. Token Permissions prüfen"
echo "2. Repository richtig ausgewählt?"
echo "3. Token korrekt kopiert?"
echo "4. GitHub Pages auf 'GitHub Actions' gesetzt?"
echo ""