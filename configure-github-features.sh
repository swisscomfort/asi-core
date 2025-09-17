#!/bin/bash

# ASI-Core GitHub Features Konfiguration
# Professionelle Repository-Setup für maximale Sichtbarkeit

echo "🚀 ASI-Core GitHub Features werden konfiguriert..."
echo "==========================================="

# Repository Info
REPO="swisscomfort/asi-core"

# 1. Repository Features konfigurieren
echo "📝 Repository Features werden aktiviert..."

# Wikis aktivieren
echo "• Wikis aktivieren..."
gh api repos/${REPO} --method PATCH --field has_wiki=true || echo "  ⚠️  Wiki konnte nicht aktiviert werden"

# Issues aktivieren (falls deaktiviert)
echo "• Issues aktivieren..."
gh api repos/${REPO} --method PATCH --field has_issues=true || echo "  ⚠️  Issues konnte nicht aktiviert werden"

# Projects aktivieren
echo "• Projects aktivieren..."
gh api repos/${REPO} --method PATCH --field has_projects=true || echo "  ⚠️  Projects konnte nicht aktiviert werden"

# Discussions aktivieren
echo "• Discussions aktivieren..."
gh api repos/${REPO} --method PATCH --field has_discussions=true || echo "  ⚠️  Discussions konnte nicht aktiviert werden"

# Security Features
echo "🔒 Security Features werden konfiguriert..."

# Vulnerability alerts aktivieren
echo "• Vulnerability alerts aktivieren..."
gh api repos/${REPO}/vulnerability-alerts --method PUT || echo "  ⚠️  Vulnerability alerts konnten nicht aktiviert werden"

# Automated security fixes aktivieren
echo "• Automated security fixes aktivieren..."
gh api repos/${REPO}/automated-security-fixes --method PUT || echo "  ⚠️  Security fixes konnten nicht aktiviert werden"

# 2. Repository Einstellungen optimieren
echo "⚙️ Repository-Einstellungen werden optimiert..."

# Merge-Strategien konfigurieren
echo "• Merge-Strategien konfigurieren..."
gh api repos/${REPO} --method PATCH \
  --field allow_squash_merge=true \
  --field allow_merge_commit=true \
  --field allow_rebase_merge=true \
  --field delete_branch_on_merge=true || echo "  ⚠️  Merge-Strategien konnten nicht konfiguriert werden"

# 3. Branch Protection Rules
echo "🛡️ Branch Protection Rules werden erstellt..."
echo "• Main Branch Protection aktivieren..."

# Branch Protection für main branch
gh api repos/${REPO}/branches/main/protection --method PUT \
  --field required_status_checks='{"strict":false,"contexts":[]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":false}' \
  --field restrictions=null || echo "  ⚠️  Branch Protection konnte nicht konfiguriert werden"

# 4. Repository Topics verwalten
echo "🏷️ Topics werden aktualisiert..."
gh api repos/${REPO}/topics --method PUT \
  --field names='["artificial-intelligence","blockchain","decentralized-storage","privacy","open-source","asi","reflection-system","ipfs","ethereum","pwa","python","react","vite"]' || echo "  ⚠️  Topics konnten nicht aktualisiert werden"

# 5. Repository Beschreibung setzen
echo "📄 Repository-Beschreibung wird aktualisiert..."
gh api repos/${REPO} --method PATCH \
  --field description="🧠 ASI-Core: Hybrid AI Reflection System combining local privacy with decentralized storage. Open-source, blockchain-enabled, PWA-ready." \
  --field homepage="https://swisscomfort.github.io/asi-core" || echo "  ⚠️  Beschreibung konnte nicht aktualisiert werden"

# 6. Social Preview (falls Logo verfügbar)
echo "🖼️ Social Preview wird konfiguriert..."
if [ -f "ASI-Core-Logo-HiRes.png" ]; then
    echo "  ✓ Logo gefunden: ASI-Core-Logo-HiRes.png"
    echo "  ℹ️  Social Preview muss manuell über GitHub Web Interface gesetzt werden"
else
    echo "  ⚠️  Logo nicht gefunden - wurde bereits generiert?"
fi

# 7. GitHub Pages konfigurieren
echo "🌐 GitHub Pages wird konfiguriert..."
gh api repos/${REPO}/pages --method POST \
  --field source='{"branch":"main","path":"/docs"}' || echo "  ⚠️  GitHub Pages bereits konfiguriert oder Fehler"

# 8. Repository Stats anzeigen
echo ""
echo "📊 Repository Status:"
echo "===================="
gh repo view ${REPO} --json name,description,visibility,isPrivate,hasWiki,hasIssues,hasProjects,hasDiscussions,url,homepageUrl

echo ""
echo "✅ GitHub Features Konfiguration abgeschlossen!"
echo "🔗 Repository: https://github.com/${REPO}"
echo ""
echo "📋 Nächste Schritte:"
echo "• Logo manuell als Social Preview hochladen"
echo "• Wiki-Startseite erstellen"
echo "• Erste Discussion starten"
echo "• GitHub Sponsors einrichten (falls gewünscht)"