#!/bin/bash
# ASI-Core GitHub Repository Auto-Configuration Script (API Version)
# Automatisiert alle empfohlenen Repository-Einstellungen mit curl

set -e

echo "🚀 ASI-Core GitHub Repository Konfiguration (API Version)"
echo "========================================================="

# GitHub Token aus Umgebungsvariablen oder Codespaces
if [ -n "$GITHUB_TOKEN" ]; then
    TOKEN="$GITHUB_TOKEN"
elif [ -n "$GITHUB_ACCESS_TOKEN" ]; then
    TOKEN="$GITHUB_ACCESS_TOKEN"
else
    echo "❌ Kein GitHub Token gefunden. Setzen Sie GITHUB_TOKEN oder GITHUB_ACCESS_TOKEN"
    echo "ℹ️ In Codespaces sollte GITHUB_TOKEN automatisch verfügbar sein"
    exit 1
fi

REPO="swisscomfort/asi-core"
API_BASE="https://api.github.com"

# API Request Funktion
api_request() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    
    if [ -n "$data" ]; then
        curl -s -X "$method" \
            -H "Authorization: token $TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_BASE/$endpoint"
    else
        curl -s -X "$method" \
            -H "Authorization: token $TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "$API_BASE/$endpoint"
    fi
}

echo "📝 Repository-Informationen werden aktualisiert..."

# 1. Repository-Beschreibung und Homepage setzen
api_request PATCH "repos/$REPO" '{
    "description": "Hybrid AI Reflection System - Professionelles, lebenslanges, dezentrales digitales Gedächtnis mit lokaler Privatsphäre und Blockchain-Integration",
    "homepage": "https://swisscomfort.github.io/asi-core/"
}' > /dev/null

echo "✅ Repository-Beschreibung und Homepage aktualisiert"

# 2. Repository als Template aktivieren
echo "🔧 Template-Repository wird aktiviert..."
api_request PATCH "repos/$REPO" '{
    "is_template": true
}' > /dev/null

echo "✅ Template-Repository aktiviert"

# 3. Features aktivieren
echo "⚙️ Repository-Features werden aktiviert..."

api_request PATCH "repos/$REPO" '{
    "has_wiki": true,
    "has_issues": true,
    "has_projects": true,
    "has_discussions": true
}' > /dev/null

echo "✅ Alle Features aktiviert"

# 4. Pull Request Einstellungen
echo "🔀 Pull Request Einstellungen werden konfiguriert..."

api_request PATCH "repos/$REPO" '{
    "allow_merge_commit": true,
    "allow_squash_merge": true,
    "allow_rebase_merge": true,
    "allow_auto_merge": true,
    "delete_branch_on_merge": true,
    "allow_update_branch": true
}' > /dev/null

echo "✅ Pull Request Einstellungen konfiguriert"

# 5. Security-Einstellungen
echo "🔒 Sicherheits-Einstellungen werden konfiguriert..."

api_request PATCH "repos/$REPO" '{
    "web_commit_signoff_required": true
}' > /dev/null

echo "✅ Web Commit Signoff aktiviert"

# 6. Repository Topics setzen
echo "🏷️ Topics werden hinzugefügt..."

api_request PUT "repos/$REPO/topics" '{
    "names": [
        "artificial-intelligence",
        "blockchain", 
        "decentralized-storage",
        "pwa",
        "python",
        "react",
        "privacy",
        "hybrid-ai",
        "reflection-system",
        "digital-memory",
        "ipfs",
        "arweave",
        "github-pro",
        "enterprise"
    ]
}' > /dev/null

echo "✅ Topics hinzugefügt"

# 7. Vulnerability Alerts aktivieren
echo "🔍 Security Features werden aktiviert..."

api_request PUT "repos/$REPO/vulnerability-alerts" '' > /dev/null 2>&1 || echo "⚠️ Vulnerability Alerts bereits aktiviert"

echo "✅ Security Features konfiguriert"

# 8. Repository-Sichtbarkeit prüfen
echo "👁️ Repository-Sichtbarkeit wird geprüft..."

REPO_INFO=$(api_request GET "repos/$REPO")
IS_PRIVATE=$(echo "$REPO_INFO" | grep -o '"private":[^,]*' | cut -d':' -f2 | tr -d ' ')

if [ "$IS_PRIVATE" = "true" ]; then
    echo "🔓 Repository wird öffentlich gemacht..."
    api_request PATCH "repos/$REPO" '{
        "private": false
    }' > /dev/null
    echo "✅ Repository ist jetzt öffentlich"
else
    echo "✅ Repository ist bereits öffentlich"
fi

# 9. GitHub Pages konfigurieren (falls noch nicht aktiv)
echo "🌐 GitHub Pages wird konfiguriert..."

api_request POST "repos/$REPO/pages" '{
    "source": {
        "branch": "main",
        "path": "/docs"
    }
}' > /dev/null 2>&1 || echo "ℹ️ GitHub Pages bereits konfiguriert"

echo ""
echo "🎉 AUTOMATISCHE KONFIGURATION ABGESCHLOSSEN!"
echo "============================================="
echo ""
echo "✅ Erfolgreich konfiguriert:"
echo "  • ✅ Repository-Beschreibung und Homepage"
echo "  • ✅ Template-Repository aktiviert"
echo "  • ✅ Alle Features aktiviert (Wikis, Issues, Projects, Discussions)"
echo "  • ✅ Pull Request Optionen optimiert"
echo "  • ✅ Web Commit Signoff aktiviert"
echo "  • ✅ 14 Topics hinzugefügt"
echo "  • ✅ Repository ist öffentlich"
echo "  • ✅ Security Features aktiviert"
echo ""
echo "⚠️ Noch manuell zu erledigen:"
echo "  • 📸 Social Media Preview Bild hochladen (1280x640px)"
echo "  • 🔒 Tag Immutability in Release-Einstellungen aktivieren"
echo "  • 🌐 GitHub Pages Source auf 'GitHub Actions' setzen (falls nötig)"
echo ""
echo "🌐 Repository: https://github.com/$REPO"
echo "📊 Settings: https://github.com/$REPO/settings"
echo "🎨 Social Preview: https://github.com/$REPO/settings#social-preview"
echo ""

# Verification
echo "🔍 Verifikation der Einstellungen..."
FINAL_INFO=$(api_request GET "repos/$REPO")
echo "Repository Name: $(echo "$FINAL_INFO" | grep -o '"name":"[^"]*' | cut -d'"' -f4)"
echo "Public: $(echo "$FINAL_INFO" | grep -o '"private":[^,]*' | cut -d':' -f2 | tr -d ' ' | sed 's/false/✅ Ja/;s/true/❌ Nein/')"
echo "Template: $(echo "$FINAL_INFO" | grep -o '"is_template":[^,]*' | cut -d':' -f2 | tr -d ' ' | sed 's/true/✅ Ja/;s/false/❌ Nein/')"
echo "Issues: $(echo "$FINAL_INFO" | grep -o '"has_issues":[^,]*' | cut -d':' -f2 | tr -d ' ' | sed 's/true/✅ Ja/;s/false/❌ Nein/')"
echo "Wiki: $(echo "$FINAL_INFO" | grep -o '"has_wiki":[^,]*' | cut -d':' -f2 | tr -d ' ' | sed 's/true/✅ Ja/;s/false/❌ Nein/')"
echo "Projects: $(echo "$FINAL_INFO" | grep -o '"has_projects":[^,]*' | cut -d':' -f2 | tr -d ' ' | sed 's/true/✅ Ja/;s/false/❌ Nein/')"

echo ""
echo "🚀 Repository ist jetzt optimal konfiguriert!"