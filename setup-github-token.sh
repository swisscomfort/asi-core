#!/bin/bash

echo "🔐 GitHub Token Setup Script"
echo "============================="
echo ""

# Prüfe ob Token bereits gesetzt ist
if [ -n "$GITHUB_TOKEN" ]; then
    echo "✅ GITHUB_TOKEN ist bereits gesetzt"
    echo "   Token: ${GITHUB_TOKEN:0:8}..."
    echo ""
else
    echo "❌ GITHUB_TOKEN ist nicht gesetzt"
    echo ""
fi

echo "📋 SETUP ANWEISUNGEN:"
echo "====================="
echo ""
echo "1. GitHub Personal Access Token erstellen:"
echo "   → https://github.com/settings/tokens"
echo "   → Generate new token (classic)"
echo "   → Scopes: repo, workflow, write:packages, read:org, admin:repo_hook"
echo ""
echo "2. Repository Secret hinzufügen:"
echo "   → https://github.com/swisscomfort/asi-core/settings/secrets/actions"
echo "   → New repository secret: GITHUB_TOKEN"
echo ""
echo "3. GitHub Pages aktivieren:"
echo "   → https://github.com/swisscomfort/asi-core/settings/pages"
echo "   → Source: GitHub Actions"
echo ""
echo "4. Lokalen Token setzen:"
echo "   export GITHUB_TOKEN=\"ghp_your_token_here\""
echo "   echo 'export GITHUB_TOKEN=\"ghp_your_token_here\"' >> ~/.bashrc"
echo ""

# Token-Test
echo "🧪 TOKEN TEST:"
echo "=============="
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Testing GitHub API access..."
    
    # Test GitHub API
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/user)
    
    if echo "$response" | grep -q '"login"'; then
        username=$(echo "$response" | grep '"login"' | sed 's/.*"login": "\([^"]*\)".*/\1/')
        echo "✅ Token funktioniert! Angemeldet als: $username"
        
        # Test Repository Access
        repo_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            https://api.github.com/repos/swisscomfort/asi-core)
        
        if echo "$repo_response" | grep -q '"name"'; then
            echo "✅ Repository-Zugriff funktioniert!"
            
            # Test Actions API
            actions_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
                https://api.github.com/repos/swisscomfort/asi-core/actions/runs?per_page=1)
            
            if echo "$actions_response" | grep -q '"workflow_runs"'; then
                echo "✅ Actions API funktioniert!"
                echo ""
                echo "🎉 SETUP KOMPLETT! Token ist voll funktionsfähig."
            else
                echo "❌ Actions API nicht erreichbar"
            fi
        else
            echo "❌ Repository-Zugriff fehlgeschlagen"
        fi
    else
        echo "❌ Token ungültig oder API-Fehler"
        echo "Response: $response"
    fi
else
    echo "❌ Kein Token gesetzt - kann nicht testen"
fi

echo ""
echo "📞 NÄCHSTE SCHRITTE:"
echo "==================="
echo "1. Token erstellen und als Repository Secret hinzufügen"
echo "2. Lokalen Token setzen: export GITHUB_TOKEN=\"dein_token\""
echo "3. Script erneut ausführen zum Testen"
echo "4. PWA Deployment triggern"
echo ""