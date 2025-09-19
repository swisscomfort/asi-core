#!/bin/bash
# ASI-Core GitHub Repository Configuration
# Konfiguriert Repository-Einstellungen mit verfügbaren Berechtigungen

set -e

echo "🚀 ASI-Core GitHub Repository Konfiguration..."
echo "=============================================="

REPO="swisscomfort/asi-core"

# GitHub CLI Auth prüfen
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ GitHub CLI nicht authentifiziert. Bitte ausführen: gh auth login"
    exit 1
fi

echo "📊 Aktueller Repository-Status:"
gh repo view $REPO --json name,description,url,visibility,isPrivate,hasIssues,hasProjects,hasWiki,hasDiscussions

echo ""
echo "🏷️ Topics werden hinzugefügt..."

# Topics hinzufügen (sollte mit gh auth token funktionieren)
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
    "enterprise",
    "asi-core"
]' 2>/dev/null || echo "⚠️ Topics: Benötigt erweiterte Berechtigungen"

echo ""
echo "📋 Repository-Features Status (manuell zu aktivieren):"
echo "  ✅ Issues - sollten bereits aktiviert sein"
echo "  🔧 Wikis - in Repository Settings > Features aktivieren"
echo "  🔧 Projects - in Repository Settings > Features aktivieren" 
echo "  🔧 Discussions - in Repository Settings > Features aktivieren"
echo "  🔧 Sponsorship - in Repository Settings > Features aktivieren"

echo ""
echo "🔀 Pull Request Empfehlungen:"
echo "  • Allow merge commits: ✅"
echo "  • Allow squash merging: ✅"
echo "  • Allow rebase merging: ✅"
echo "  • Automatically delete head branches: ✅"

echo ""
echo "🛡️ Branch Protection Empfehlungen:"
echo "  • Require a pull request before merging"
echo "  • Require approvals: mindestens 1"
echo "  • Dismiss stale PR reviews when new commits are pushed"
echo "  • Require status checks to pass before merging"

echo ""
echo "🌐 GitHub Pages Setup:"
echo "  • Source: GitHub Actions"
echo "  • Verzeichnis: /docs"

echo ""
echo "📸 Social Media Preview:"
echo "  • Logo hochladen: ASI-Core-Logo.png (1280x640px)"
echo "  • In Repository Settings > Social Preview"

echo ""
echo "🎉 NÄCHSTE SCHRITTE:"
echo "================================"
echo ""
echo "📝 Manuell zu konfigurieren in GitHub UI:"
echo "  1. Gehe zu: https://github.com/$REPO/settings"
echo "  2. Features aktivieren:"
echo "     ☐ Wikis"
echo "     ☐ Projects" 
echo "     ☐ Discussions"
echo "     ☐ Sponsorships"
echo "  3. Pull Requests & Merges konfigurieren"
echo "  4. Branch Protection Rules für main branch"
echo "  5. Social Media Preview Bild hochladen"
echo "  6. GitHub Pages aktivieren"
echo ""
echo "🔗 Wichtige Links:"
echo "  • Repository: https://github.com/$REPO"
echo "  • Settings: https://github.com/$REPO/settings"
echo "  • Actions: https://github.com/$REPO/actions"
echo ""