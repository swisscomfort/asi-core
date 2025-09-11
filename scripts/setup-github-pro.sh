#!/bin/bash

# ASI-Core GitHub Pro Setup Script
# Aktiviert und konfiguriert alle GitHub Pro Features

set -e

echo "🚀 ASI-Core GitHub Pro Setup"
echo "============================"

# Prüfe GitHub CLI Installation
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) nicht gefunden!"
    echo "💡 Installation: https://cli.github.com/"
    exit 1
fi

# Prüfe GitHub Authentication
if ! gh auth status &> /dev/null; then
    echo "🔐 GitHub Authentication erforderlich..."
    gh auth login
fi

echo "✅ GitHub CLI bereit"

# Repository Info
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
REPO_NAME=$(gh repo view --json name --jq '.name')
REPO_URL="https://github.com/$REPO_OWNER/$REPO_NAME"

echo "📂 Repository: $REPO_OWNER/$REPO_NAME"
echo "🔗 URL: $REPO_URL"
echo ""

# 1. GitHub Pages aktivieren
echo "📄 1. GitHub Pages Setup..."
if gh api repos/$REPO_OWNER/$REPO_NAME/pages &> /dev/null; then
    echo "✅ GitHub Pages bereits aktiviert"
else
    echo "🔧 Aktiviere GitHub Pages..."
    gh api repos/$REPO_OWNER/$REPO_NAME/pages \
        --method POST \
        --field source[branch]=gh-pages \
        --field source[path]="/" || echo "⚠️ Manuelle Aktivierung erforderlich"
fi

# 2. Branch Protection Rules
echo ""
echo "🛡️ 2. Branch Protection Setup..."
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection \
    --method PUT \
    --field required_status_checks[strict]=true \
    --field required_status_checks[contexts]='["CI/CD Pipeline"]' \
    --field enforce_admins=false \
    --field required_pull_request_reviews[required_approving_review_count]=1 \
    --field required_pull_request_reviews[dismiss_stale_reviews]=true \
    --field required_pull_request_reviews[require_code_owner_reviews]=false \
    --field restrictions=null || echo "⚠️ Branch Protection bereits konfiguriert"

# 3. Repository Labels erstellen
echo ""
echo "🏷️ 3. Repository Labels Setup..."
declare -a LABELS=(
    "beta-testing|FF6B6B|Beta testing related issues"
    "github-pro|FF9F43|GitHub Pro features"
    "priority-critical|FF3838|Critical priority"
    "priority-high|FF9F43|High priority"
    "priority-medium|FFA500|Medium priority"
    "priority-low|00D2D3|Low priority"
    "mobile|55A3FF|Mobile related"
    "desktop|5F27CD|Desktop related"
    "pwa|00D2D3|PWA related"
    "analytics|74B9FF|Analytics and metrics"
    "security|E17055|Security related"
    "performance|00B894|Performance improvements"
    "documentation|7F8C8D|Documentation updates"
    "deployment|6C5CE7|Deployment related"
    "automation|A55EEA|Automation features"
)

for LABEL in "${LABELS[@]}"; do
    IFS='|' read -r NAME COLOR DESCRIPTION <<< "$LABEL"
    gh label create "$NAME" --color "$COLOR" --description "$DESCRIPTION" --force || true
done

echo "✅ Labels erstellt"

# 4. Repository Topics
echo ""
echo "🏷️ 4. Repository Topics Setup..."
gh api repos/$REPO_OWNER/$REPO_NAME/topics \
    --method PUT \
    --field names='["asi-core","artificial-intelligence","pwa","blockchain","github-pro","beta-testing","mobile-app","reflection-system","decentralized-storage","knowledge-management"]' \
    || echo "⚠️ Topics bereits gesetzt"

# 5. Repository Settings
echo ""
echo "⚙️ 5. Repository Settings..."
gh api repos/$REPO_OWNER/$REPO_NAME \
    --method PATCH \
    --field has_issues=true \
    --field has_projects=true \
    --field has_wiki=true \
    --field has_pages=true \
    --field has_downloads=true \
    --field allow_squash_merge=true \
    --field allow_merge_commit=false \
    --field allow_rebase_merge=true \
    --field delete_branch_on_merge=true || echo "⚠️ Settings bereits konfiguriert"

# 6. Security Features aktivieren
echo ""
echo "🔒 6. Security Features Setup..."
echo "   Aktiviere in Repository Settings → Security & Analysis:"
echo "   ✅ Dependency graph"
echo "   ✅ Dependabot alerts"
echo "   ✅ Dependabot security updates"
echo "   ✅ Secret scanning"
echo "   ✅ Code scanning"

# 7. Secrets erstellen (Template)
echo ""
echo "🔐 7. Repository Secrets..."
echo "   Folgende Secrets sollten in Settings → Secrets → Actions hinzugefügt werden:"
echo "   - GITHUB_TOKEN (automatisch verfügbar)"
echo "   - NETLIFY_AUTH_TOKEN (für Netlify Deployment)"
echo "   - VERCEL_TOKEN (für Vercel Deployment)"
echo "   - DOCKER_USERNAME (für Docker Hub)"
echo "   - DOCKER_PASSWORD (für Docker Hub)"

# 8. GitHub Project erstellen
echo ""
echo "📋 8. GitHub Project Setup..."
echo "   🔧 Erstelle Project manuell unter:"
echo "   $REPO_URL/projects"
echo "   - Template: Table"
echo "   - Name: ASI-Core 30-Day Beta"

# 9. Beta Testing Workflow starten
echo ""
echo "🧪 9. Beta Testing Workflow..."
echo "   Starte Beta Project Setup:"
gh workflow run beta-project-setup.yml \
    --field project_name="ASI-Core 30-Day Beta" \
    --field start_date="$(date +%Y-%m-%d)" || echo "⚠️ Workflow manuell starten"

# 10. Analytics Workflow starten
echo ""
echo "📊 10. Analytics Setup..."
echo "   Teste GitHub Pro Analytics:"
if [ -n "$GITHUB_TOKEN" ]; then
    python3 scripts/github_pro_analytics.py --format text || echo "⚠️ Analytics manuell testen"
else
    echo "⚠️ GITHUB_TOKEN Environment Variable fehlt"
fi

# 11. Docker Package Test
echo ""
echo "🐳 11. Docker Package Test..."
echo "   Teste Docker Build:"
docker build -t asi-core-test . || echo "⚠️ Docker Build manuell testen"

# 12. PWA Test
echo ""
echo "📱 12. PWA Status Check..."
if [ -f "web/manifest.json" ]; then
    echo "✅ PWA Manifest gefunden"
else
    echo "⚠️ PWA Manifest fehlt"
fi

if [ -f "web/sw.js" ]; then
    echo "✅ Service Worker gefunden"
else
    echo "⚠️ Service Worker fehlt"
fi

# Summary
echo ""
echo "🎉 GitHub Pro Setup Complete!"
echo "=============================="
echo "📊 Live Analytics: $REPO_URL/insights/traffic"
echo "🔒 Security: $REPO_URL/security"
echo "🚀 Actions: $REPO_URL/actions"
echo "📦 Packages: https://github.com/$REPO_OWNER/$REPO_NAME/pkgs/container/$REPO_NAME"
echo "📋 Projects: $REPO_URL/projects"
echo "🌍 Live PWA: https://$REPO_OWNER.github.io/$REPO_NAME/"
echo ""
echo "🎯 Nächste Schritte:"
echo "1. Repository Settings → Security & Analysis aktivieren"
echo "2. GitHub Project manuell erstellen"
echo "3. Beta-Tester einladen"
echo "4. Secrets hinzufügen"
echo "5. Erste Analytics überprüfen"
echo ""
echo "🧪 30-Tage Beta kann starten! 🚀"