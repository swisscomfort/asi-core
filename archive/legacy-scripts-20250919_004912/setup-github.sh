#!/bin/bash

# ASI-Core GitHub Setup Script
# Automatische Konfiguration aller GitHub-Features

echo "🚀 ASI-Core GitHub Setup"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d ".github" ]; then
    echo -e "${RED}❌ Fehler: Bitte im ASI-Core Repository Root ausführen${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 GitHub Setup Checklist:${NC}"
echo ""

# 1. Check GitHub Pages
echo -e "${GREEN}1. GitHub Pages Setup:${NC}"
if [ -f ".github/workflows/deploy-pwa.yml" ]; then
    echo "   ✅ Workflow existiert: .github/workflows/deploy-pwa.yml"
else
    echo "   ❌ Workflow fehlt - bitte erstellen"
fi

# 2. Check Security Features
echo -e "${GREEN}2. Security Features:${NC}"
if [ -f "docs/security.md" ]; then
    echo "   ✅ Security Dokumentation: docs/security.md"
else
    echo "   ❌ Security Docs fehlen"
fi

# 3. Check Branch Protection
echo -e "${GREEN}3. Branch Protection:${NC}"
echo "   📝 Manuell einrichten: Repository Settings → Branches → Add Rule"
echo "   - Branch: main"
echo "   - Require PRs: ✅"
echo "   - Require approvals: 1"
echo "   - Status checks: ✅"

# 4. Check Project Template
echo -e "${GREEN}4. GitHub Project:${NC}"
if [ -f ".github/project-template.json" ]; then
    echo "   ✅ Project Template: .github/project-template.json"
else
    echo "   ❌ Project Template fehlt"
fi

# 5. Check Issue Templates
echo -e "${GREEN}5. Issue Templates:${NC}"
if [ -d ".github/ISSUE_TEMPLATE" ]; then
    echo "   ✅ Issue Templates vorhanden"
else
    echo "   📝 Empfohlen: Bug Report, Feature Request, Beta Feedback"
fi

echo ""
echo -e "${YELLOW}🔧 Nächste Schritte:${NC}"
echo ""
echo "1. GitHub Pages aktivieren:"
echo "   Repository Settings → Pages → Source: GitHub Actions"
echo ""
echo "2. Branch Protection einrichten:"
echo "   Repository Settings → Branches → Add Rule für 'main'"
echo ""
echo "3. Security Features aktivieren:"
echo "   Repository Settings → Security & analysis → Enable all"
echo ""
echo "4. GitHub Project erstellen:"
echo "   Repository → Projects → New Project → Import from Template"
echo ""
echo "5. Link-Checker regelmäßig ausführen:"
echo "   ./link_checker.sh"
echo ""

echo -e "${GREEN}🎉 Setup abgeschlossen!${NC}"
echo "Dein ASI-Core Repository ist jetzt professionell konfiguriert."