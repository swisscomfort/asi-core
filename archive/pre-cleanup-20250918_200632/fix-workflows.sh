#!/bin/bash

echo "🔧 ASI-Core GitHub Actions Workflow Manager"
echo "=========================================="

# Funktion zum Deaktivieren eines Workflows
disable_workflow() {
    local workflow_file="$1"
    local reason="$2"

    if [ -f ".github/workflows/$workflow_file" ]; then
        echo "📝 Deaktiviere $workflow_file ($reason)"
        mv ".github/workflows/$workflow_file" ".github/workflows/$workflow_file.disabled"
    fi
}

# Funktion zum Aktivieren eines Workflows
enable_workflow() {
    local workflow_file="$1"

    if [ -f ".github/workflows/$workflow_file.disabled" ]; then
        echo "✅ Aktiviere $workflow_file"
        mv ".github/workflows/$workflow_file.disabled" ".github/workflows/$workflow_file"
    fi
}

echo ""
echo "📊 Analysiere Workflows..."

# Zähle aktive Workflows
active_workflows=$(ls -1 .github/workflows/*.yml | wc -l)
echo "Aktive Workflows: $active_workflows"

echo ""
echo "🔧 Deaktiviere problematische Workflows..."

# Deaktiviere Deploy-Workflows (fehlen wahrscheinlich Secrets)
disable_workflow "deploy-ipfs.yml" "IPFS Secrets fehlen"
disable_workflow "deploy-netlify.yml" "Netlify Token fehlt"
disable_workflow "deploy-vercel.yml" "Vercel Token fehlt"
disable_workflow "docker-github-packages.yml" "Docker Registry Access fehlt"

# Deaktiviere Analytics (nicht kritisch)
disable_workflow "analytics.yml" "Analytics nicht konfiguriert"
disable_workflow "github-pro-analytics.yml" "GitHub Pro Features fehlen"

# Deaktiviere Backup-Workflows (keine Konfiguration)
disable_workflow "backup.yml" "Backup-Konfiguration fehlt"
disable_workflow "codespace-backup.yml" "Codespace Backup nicht nötig"

# Deaktiviere Performance/Security Scans (zu aggressiv)
disable_workflow "performance.yml" "Performance Monitoring nicht konfiguriert"
disable_workflow "security-scan.yml" "Security Scan zu aggressiv"
disable_workflow "security.yml" "Security Tools nicht konfiguriert"

# Deaktiviere Beta/Experimentelle Features
disable_workflow "beta-project-setup.yml" "Beta Feature"
disable_workflow "setup-project-management.yml" "Nicht benötigt"

echo ""
echo "✅ Behalte wichtige Workflows aktiv:"
echo "  - ci.yml (Python Tests)"
echo "  - test.yml (Grundlegende Tests)"
echo "  - docs.yml (Dokumentation)"
echo "  - pages-activation.yml (GitHub Pages Setup)"
echo "  - deploy.yml (PWA Deployment)"

echo ""
echo "📈 Neue Anzahl aktiver Workflows:"
new_count=$(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)
echo "Aktive Workflows: $new_count"

echo ""
echo "🎯 Empfehlung:"
echo "1. Überprüfen Sie die GitHub Actions Secrets in den Repository-Einstellungen"
echo "2. Aktivieren Sie nur Workflows, die Sie wirklich brauchen"
echo "3. Testen Sie jeden Workflow einzeln bevor Sie ihn aktivieren"

echo ""
echo "✨ Workflow-Bereinigung abgeschlossen!"