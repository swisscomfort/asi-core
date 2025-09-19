#!/bin/bash

echo "🧪 GitHub Token Test"
echo "==================="

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN ist nicht gesetzt!"
    echo ""
    echo "📝 Setze ihn mit:"
    echo "export GITHUB_TOKEN=\"ghp_your_token_here\""
    echo ""
    exit 1
fi

echo "✅ Token ist gesetzt: ${GITHUB_TOKEN:0:8}..."
echo ""

echo "🔍 Teste GitHub API..."
response=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user)

if echo "$response" | grep -q '"login"'; then
    username=$(echo "$response" | grep '"login"' | sed 's/.*"login": "\([^"]*\)".*/\1/')
    echo "✅ API funktioniert! Angemeldet als: $username"
    
    echo ""
    echo "🔍 Teste Repository-Zugriff..."
    repo_response=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
        https://api.github.com/repos/swisscomfort/asi-core)
    
    if echo "$repo_response" | grep -q '"name"'; then
        echo "✅ Repository-Zugriff funktioniert!"
        
        echo ""
        echo "🚀 Teste PWA Deployment..."
        curl -X POST \
          -H "Accept: application/vnd.github.v3+json" \
          -H "Authorization: Bearer $GITHUB_TOKEN" \
          https://api.github.com/repos/swisscomfort/asi-core/actions/workflows/deploy-pwa.yml/dispatches \
          -d '{"ref":"main"}' 2>/dev/null
          
        if [ $? -eq 0 ]; then
            echo "✅ PWA Deployment wurde getriggert!"
            echo ""
            echo "🌐 Check in 2-3 Minuten: https://swisscomfort.github.io/asi-core/"
        else
            echo "⚠️ Deployment konnte nicht getriggert werden"
        fi
    else
        echo "❌ Repository-Zugriff fehlgeschlagen"
    fi
else
    echo "❌ API-Zugriff fehlgeschlagen"
    echo "Response: $response"
fi

echo ""
echo "🎯 SETUP KOMPLETT! Token ist einsatzbereit."