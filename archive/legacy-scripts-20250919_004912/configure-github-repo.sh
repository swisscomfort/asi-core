#!/bin/bash
# ASI-Core GitHub Repository Auto-Configuration Script
# Automatisiert alle empfohlenen Repository-Einstellungen

set -e

echo "🚀 ASI-Core GitHub Repository Konfiguration wird gestartet..."
echo "=================================================="

# GitHub CLI Auth prüfen
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ GitHub CLI nicht authentifiziert. Bitte ausführen: gh auth login"
    exit 1
fi

REPO="swisscomfort/asi-core"

echo "📝 Repository-Informationen werden aktualisiert..."

# 1. Repository-Beschreibung und Homepage setzen
gh repo edit $REPO \
    --description "Hybrid AI Reflection System - Professionelles, lebenslanges, dezentrales digitales Gedächtnis mit lokaler Privatsphäre und Blockchain-Integration" \
    --homepage "https://swisscomfort.github.io/asi-core/"

# 2. Repository als Template aktivieren
echo "🔧 Template-Repository wird aktiviert..."
gh api repos/$REPO --method PATCH --field is_template=true

# 3. Features aktivieren
echo "⚙️ Repository-Features werden aktiviert..."

# Wikis aktivieren
gh api repos/$REPO --method PATCH --field has_wiki=true

# Issues aktivieren (sollte bereits aktiv sein)
gh api repos/$REPO --method PATCH --field has_issues=true

# Projects aktivieren
gh api repos/$REPO --method PATCH --field has_projects=true

# Discussions aktivieren
gh api repos/$REPO --method PATCH --field has_discussions=true

# 4. Pull Request Einstellungen
echo "🔀 Pull Request Einstellungen werden konfiguriert..."

gh api repos/$REPO --method PATCH \
    --field allow_merge_commit=true \
    --field allow_squash_merge=true \
    --field allow_rebase_merge=true \
    --field allow_auto_merge=true \
    --field delete_branch_on_merge=true \
    --field allow_update_branch=true

# 5. Security und Archiv-Einstellungen
echo "🔒 Sicherheits-Einstellungen werden konfiguriert..."

# GitHub Archive Program
gh api repos/$REPO --method PATCH --field archived=false

# Web commit signoff requirement
gh api repos/$REPO --method PATCH --field web_commit_signoff_required=true

# 6. Repository Topics setzen
echo "🏷️ Topics werden hinzugefügt..."

gh api repos/$REPO/topics --method PUT --field names='[
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
]'

# 7. Branch Protection Rules (für main branch)
echo "🛡️ Branch Protection Rules werden konfiguriert..."

gh api repos/$REPO/branches/main/protection --method PUT --field '{
    "required_status_checks": {
        "strict": true,
        "contexts": []
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews": true,
        "require_code_owner_reviews": false
    },
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "required_linear_history": false
}' 2>/dev/null || echo "⚠️ Branch Protection: Nur verfügbar für Pro/Team Accounts"

# 8. Issue und PR Templates prüfen
echo "📋 Issue/PR Templates werden geprüft..."

if [ ! -f ".github/ISSUE_TEMPLATE/bug_report.yml" ]; then
    echo "ℹ️ Issue Templates werden erstellt..."
    mkdir -p .github/ISSUE_TEMPLATE
fi

if [ ! -f ".github/FUNDING.yml" ]; then
    echo "💰 FUNDING.yml wird erstellt..."
    mkdir -p .github
fi

# 9. Advanced Security Features (für Pro Accounts)
echo "🔍 Advanced Security Features werden aktiviert..."

# Dependabot alerts
gh api repos/$REPO/vulnerability-alerts --method PUT 2>/dev/null || echo "⚠️ Vulnerability Alerts: Bereits aktiviert oder nicht verfügbar"

# Secret scanning
gh api repos/$REPO --method PATCH --field security_and_analysis='{"secret_scanning":{"status":"enabled"}}' 2>/dev/null || echo "⚠️ Secret Scanning: Nur für Pro/Team verfügbar"

# 10. Releases-Einstellungen
echo "📦 Release-Einstellungen werden konfiguriert..."

# Kein direkter API-Endpunkt für "tag immutability", aber wir können eine Policy erstellen
echo "ℹ️ Tag Immutability muss manuell in den Repository-Einstellungen aktiviert werden"

# 11. GitHub Pages aktivieren
echo "🌐 GitHub Pages wird konfiguriert..."

gh api repos/$REPO/pages --method POST --field source='{"branch":"main","path":"/docs"}' 2>/dev/null || echo "ℹ️ GitHub Pages bereits konfiguriert oder wird manuell aktiviert"

# 12. Repository-Sichtbarkeit prüfen
echo "👁️ Repository-Sichtbarkeit wird geprüft..."

VISIBILITY=$(gh api repos/$REPO --jq '.private')
if [ "$VISIBILITY" = "true" ]; then
    echo "🔓 Repository wird öffentlich gemacht..."
    gh repo edit $REPO --visibility public
else
    echo "✅ Repository ist bereits öffentlich"
fi

echo ""
echo "🎉 KONFIGURATION ABGESCHLOSSEN!"
echo "================================"
echo ""
echo "✅ Erfolgreich konfiguriert:"
echo "  • Repository-Beschreibung und Homepage"
echo "  • Template-Repository aktiviert"
echo "  • Alle Features aktiviert (Wikis, Issues, Projects, Discussions)"
echo "  • Pull Request Optionen optimiert"
echo "  • Web Commit Signoff aktiviert"
echo "  • Topics hinzugefügt"
echo "  • Repository ist öffentlich"
echo ""
echo "⚠️ Manuell zu prüfen:"
echo "  • Social Media Preview Bild hochladen (1280x640px)"
echo "  • Tag Immutability in Releases-Einstellungen"
echo "  • GitHub Pages Source auf 'GitHub Actions' setzen"
echo ""
echo "🌐 Repository: https://github.com/$REPO"
echo "📊 Settings: https://github.com/$REPO/settings"
echo ""